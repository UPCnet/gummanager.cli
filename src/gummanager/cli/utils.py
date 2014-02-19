import os
import json
import prettytable
from blessings import Terminal
from functools import partial
import re

term = Terminal()

UNKNOWN_OPTION = object()
DEFAULT_VALUE = object()


def ask_confirmation(message):
    print term.yellow(message)
    value = raw_input('    Proceed?  (Y, N): ')
    return value.strip().upper() == 'Y'


def askOption(option_name):
    return raw_input('Enter value for required "{}" option: '.format(option_name))


def getOptionFrom(options, option_name, default=DEFAULT_VALUE):

    # Try to get literal option name from options:
    option = options.get(option_name, UNKNOWN_OPTION)

    # If option exists but is False, treat like if not was there
    if option is False:
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
    if option is UNKNOWN_OPTION or option is False:
        if default is not DEFAULT_VALUE:
            option = default
        else:
            option = askOption(option_name)

    return option


def getConfiguration(config_file_option):
    config_file = config_file_option if config_file_option else '{}/.gum.conf'.format(os.path.expanduser('~'))
    return json.loads(open(config_file).read())


def padded_success(string):
    print term.bold_green + '    {}'.format(string) + term.normal


def padded_error(string):
    print term.bold_red + '    {}\n'.format(string) + term.normal


def padded_log(string, filters=[]):
    print term.normal + '    {}'.format(string) + term.normal


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
        super(GUMTable, self).__init__(*args, **kwargs)
        self.table_header_style = term.bold

        self.hrules = prettytable.ALL
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
