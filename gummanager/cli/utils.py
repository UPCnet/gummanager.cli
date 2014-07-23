import os
import json
import prettytable
from blessings import Terminal
from functools import partial
from getpass import getpass
import re
import sys
import threading

from gummanager.libs.utils import RemoteConnection
from gummanager.cli.pacmanprogressbar import Pacman

term = Terminal()

UNKNOWN_OPTION = object()
DEFAULT_VALUE = object()


def json_pretty_print(data, mask_passwords=False):
    config = json.dumps(data, sort_keys=True, indent=4)[1:-1]
    config = re.sub(r'([\{\}\[\]])', term.blue + r'\1' + term.normal, config)
    if mask_passwords:
        config = re.sub(r'"(.*?password.*?)": "(.*?)"', r'"\1": "***********"', config)
    config = re.sub(r'"(.*?)":', r'{}\1{}:'.format(term.bold_yellow, term.normal), config)
    return config


def run_recipe_with_confirmation(title, params, recipe_method, *args, **kwargs):
    message = '\n    ' + term.green + title + '\n' + term.normal + json_pretty_print(params)
    if ask_confirmation(message):
        for yielded in recipe_method(*args, **kwargs):
            if not isinstance(yielded, list):
                yielded = [yielded, ]
            for code, message in yielded:
                print_message(code, message)
                if code == 0:
                    return None
    print
    return True


class ConfigWrapper(dict):

    @classmethod
    def from_dict(cls, config):
        wrapper = cls()

        def wrap(wvalue):
            if isinstance(wvalue, dict):
                return ConfigWrapper.from_dict(wvalue)
            elif isinstance(wvalue, list):
                wrapped_list = []
                for item in wvalue:
                    wrapped_list.append(wrap(item))
                return wrapped_list
            else:
                return wvalue

        for key, value in config.items():
            wrapped = wrap(value)
            wrapper[key] = wrapped

        return wrapper

    def __getattr__(self, key):
        if self.get(key):
            return self[key]

        is_password = 'password' in key.lower()
        value = askOption(key, is_password)
        self[key] = value
        return value


def ask_confirmation(message):
    print term.yellow(message)
    value = raw_input('    Proceed?  (Y, N): ')
    return value.strip().upper() == 'Y'


def askOption(option_name, mask=False):
    input_getter = getpass if mask else raw_input
    return input_getter('Enter value for required "{}" option: '.format(option_name))


def getOptionFrom(options, option_name, default=DEFAULT_VALUE, mask=False):

    # Try to get literal option name from options:
    option = options.get(option_name, UNKNOWN_OPTION)

    # If option exists but is False, treat like if not was there
    if option in [False, None]:
        option = UNKNOWN_OPTION

    # if option is unknown, try to get as a <variable>
    if option is UNKNOWN_OPTION:
        option = options.get('<{}>'.format(option_name), UNKNOWN_OPTION)

    # if option is unknown, try to get as a --doubledashed option
    if option is UNKNOWN_OPTION:
        option = options.get('--{}'.format(option_name), UNKNOWN_OPTION)

    # if option is unknown, try to get as a -dashed option
    if option is UNKNOWN_OPTION:
        option = options.get('-{}'.format(option_name), UNKNOWN_OPTION)

    # if option is unknown or has a false value
    if option is UNKNOWN_OPTION or option in [False, None]:
        if default is not DEFAULT_VALUE:
            option = default
        else:
            option = askOption(option_name, mask)

    return option


def getConfiguration(config_file_option):
    config_file = config_file_option if config_file_option else '{}/.gum.conf'.format(os.path.expanduser('~'))
    try:
        parsed_config = json.loads(open(config_file).read())
    except:
        padded_error('\nError loading {}, check json syntax'.format(config_file))
        sys.exit(1)
    else:
        return ConfigWrapper.from_dict(parsed_config)


def padded_success(string):
    print term.bold_green + '    {}'.format(string) + term.normal


def padded_error(string):
    print term.bold_red + '    {}\n'.format(string) + term.normal


def padded_log(string, filters=[]):
    string = string.rstrip()
    # apply padding to rewrite lines (starting with \r)
    string = re.sub(r'([\r])', r'\1    ', string)
    lines = string.split('\n')
    for line in lines:
        matched_filter = re.search(r'({})'.format('|'.join(filters)), line)
        do_print = matched_filter or filters == []
        if do_print:
            print '    ' + line.rstrip()


def step_log(string):
    print term.bold_cyan + '\n> {}\n'.format(string) + term.normal


def print_message(code, message):
    if code == 0:
        padded_error(message)
    elif code == 1:
        padded_success(message)
    elif code == 2:
        padded_log(message)
    elif code == 3:
        step_log(message)


class GUMTable(prettytable.PrettyTable):

    def __init__(self, *args, **kwargs):
        hrules = kwargs.get('hrules', 'ALL')
        kwargs['hrules'] = getattr(prettytable, hrules)

        super(GUMTable, self).__init__(*args, **kwargs)

        self.table_header_style = term.bold

        self.vertical_char = term.black('|')
        self.horizontal_char = term.black('-')
        self.junction_char = term.black('-')
        self.titles = {}

    def from_dict_list(self, data, hide=[], titles={}, formatters={}):
        self.titles = titles

        for row_num, row in enumerate(data):
            if row_num == 0:
                for col_id in row.keys():
                    if col_id not in hide:
                        col_name = titles.get(col_id, col_id)
                        self.add_column(self.table_header_style(col_name), [])
            rowdata = []
            for col_num, col_id in enumerate(row):
                if col_id not in hide:
                    value = row[col_id]
                    if isinstance(value, dict):
                        subheader_length = max([len(key) for key in value.keys()])
                        format_string = '{{:<{}}} : {{}}'.format(subheader_length)
                        value = '\n'.join([format_string.format(key, subvalue) for key, subvalue in value.items()])
                    formatter = formatters.get(col_id, default_formatter)
                    rowdata.append(formatter(value))
            self.add_row(rowdata)

    def sorted(self, column_id):
        self.align = 'l'
        if self._rows:
            column_name = self.titles.get(column_id, column_id)
            return self.get_string(sortby=self.table_header_style(column_name))
        else:
            return term.yellow("\nSorry, There's nothing to see here...\n")


def default_formatter(value):
    return value


def highlighter(**kwargs):
    def highlight(value, default='normal', values={}):
        default_formatter = getattr(term, default)
        for key, format in values.items():
            formatter = getattr(term, format)
            value = re.sub(r'({})'.format(key), r'{}\1{}'.format(formatter, default_formatter), value)

        return default_formatter + value + default_formatter
    return partial(highlight, **kwargs)


def get_length(value):
    return len(value)


class LogEcho(threading.Thread):
    def __init__(self, user, server, filename, target_lines=None, filters=[]):
        self.logfile = filename
        threading.Thread.__init__(self)
        self.remote = RemoteConnection(user, server)
        self.count = 0
        self.target_lines = target_lines
        self.show_progress_bar = self.target_lines is not None
        self.process = None
        self.finished = False
        self.filters = filters
        print self.logfile

    def stop(self):
        print
        self.process.kill()

    def run(self):
        def tail_log(line, stdin, process):
            # At first line reception, store echo logger process
            # and instantiate progress bar if needed
            if self.process is None:
                self.process = process
                if self.show_progress_bar:
                    self.pacman = Pacman(text='    Progress')

            # Determine if we want to count/print the line based on filters setting
            matched_filter = re.search(r'({})'.format('|'.join(self.filters)), line)
            this_line_is_good = matched_filter or self.filters == []

            # If line is good and we're not reached the 100%
            if this_line_is_good and not self.finished:
                # Update progress bar if in progressbar mode
                if self.show_progress_bar:
                    self.count += 1
                    percent = (100 * self.count) / self.target_lines
                    percent = percent if percent <= 100 else 100
                    self.finished = percent == 100
                    self.pacman.progress(percent)
                # or print line
                else:
                    print '    ' + line.rstrip()

        try:
            code, stdout = self.remote.execute(
                'tail -F -n0 {}'.format(self.logfile),
                _out=tail_log
            )
        except:
            pass
