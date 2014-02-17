import os
import json
import prettytable
from blessings import Terminal
from functools import partial
import re

term = Terminal()


def askOption(option_name):
    return raw_input('Enter value for required "{}" option: '.format(option_name))


def getOptionFrom(options, option_name, default=None):
    option = options.get(option_name, options.get('<{}>'.format(option_name), options.get('--{}'.format(option_name), None)))
    return option if option is not None else (default if default is not None else askOption(option_name))


def getConfiguration(config_file_option):
    config_file = config_file_option if config_file_option else '{}/.gum.conf'.format(os.path.expanduser('~'))
    return json.loads(open(config_file).read())


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
