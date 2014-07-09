import sys
import json
import re
from blessings import Terminal

term = Terminal()


class Target(object):

    _actions = []
    subtargets = []
    extratargets = []
    server_klass = object

    @property
    def Server(self):
        return self.server_klass(**self.config)

    def __init__(self, config):
        self.config = config

    @property
    def actions(self):
        return list(set(self._actions + ['help', 'info']))

    def help(self, method_name):

        method = getattr(self, method_name)
        docstring = getattr(method, '__doc__')
        print docstring.replace('\n        ', '\n    ') if docstring is not None else '\n    No help available for this command\n'

    def info(self, **kwargs):
        print
        config = json.dumps(self.config, sort_keys=True, indent=4)
        config = re.sub(r'([\{\}\[\]])', term.blue + r'\1' + term.normal, config)
        config = re.sub(r'"(.*?password.*?)": "(.*?)"', r'"\1": "***********"', config)
        config = re.sub(r'"(.*?)":', r'"{}\1{}":'.format(term.bold_yellow, term.normal), config)
        print config
        print

    def forge_command_from_arguments(self, arguments):
        actions = [arg_name for arg_name, arg_value in arguments.items() if arg_name in self.actions and arg_value is True]

        if not actions:
            print '\nUndefined action "{}"\n'.format(sys.argv[2])
            sys.exit(1)

        action_name = actions[0]

        action_method_name = action_name

        subtarget = [arg_name for arg_name, arg_value in arguments.items() if arg_name in self.subtargets and arg_value is True]
        if subtarget:
            subtarget_name = subtarget[0]
            action_method_name += "_{}".format(subtarget_name)

        extratarget = [arg_name for arg_name, arg_value in arguments.items() if arg_name in self.extratargets and arg_value is True]
        if extratarget:
            extratarget_name = extratarget[0]
            action_method_name += "_{}".format(extratarget_name)

        return action_method_name
