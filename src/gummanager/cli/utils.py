import os
import json


def getOptionFrom(options, option_name):
        return options.get(option_name, options.get('<{}>'.format(option_name), None))


def getConfiguration(config_file_option):
    config_file = config_file_option if config_file_option else '{}/.gum.conf'.format(os.path.expanduser('~'))
    return json.loads(open(config_file).read())

