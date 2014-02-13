import os
import json
import prettytable
from blessings import Terminal

term = Terminal()

def getOptionFrom(options, option_name):
        return options.get(option_name, options.get('<{}>'.format(option_name), None))


def getConfiguration(config_file_option):
    config_file = config_file_option if config_file_option else '{}/.gum.conf'.format(os.path.expanduser('~'))
    return json.loads(open(config_file).read())


class GUMTable(prettytable.PrettyTable):

    def __init__(self, *args, **kwargs):
        super(GUMTable, self).__init__(*args, **kwargs)
        self.table_header_style = term.bold
        self.first_col_style = term.bold_yellow

        self.hrules = prettytable.ALL        
        self.vertical_char = term.black('|')
        self.horizontal_char = term.black('-')
        self.junction_char = term.black('-')
        self.titles = {}


    def from_dict_list(self, data, hide=[], titles={}):
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
                    if col_num == 0:
                        rowdata.append(self.first_col_style(value))
                    else:
                        if isinstance(value, dict):
                            subheader_length = max([len(key) for key in value.keys()])
                            format_string = '{{:<{}}} : {{}}'.format(subheader_length)
                            value = '\n'.join([format_string.format(key, subvalue) for key, subvalue in value.items()])
                        rowdata.append(value)
            self.add_row(rowdata)

    def sorted(self, column_id):
        self.align = 'l'
        column_name = self.titles.get(column_id, column_id)
        return self.get_string(sortby=self.table_header_style(column_name))