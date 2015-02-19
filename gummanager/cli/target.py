import sys

from blessings import Terminal
from gummanager.cli.utils import json_pretty_print, ConfigWrapper


term = Terminal()


class Target(object):

    _actions = []
    subtargets = []
    extratargets = []
    server_klass = object

    @property
    def Server(self):
        config = {}
        config.update(self.extra_config)
        config.update(self.config)
        return self.server_klass(ConfigWrapper.from_dict(config))

    def __init__(self, config):
        self.extra_config = {}
        self.config = config

    @property
    def actions(self):
        return list(set(self._actions + ['help', 'info']))

    def help(self, method_name, definition):

        method = getattr(self, method_name)
        docstring = getattr(method, '__doc__')
        print term.bold + term.yellow + '\n    ' + definition + term.normal
        print docstring.replace('\n        ', '\n') if docstring is not None else '\n    No help available for this command\n'

    def info(self, **kwargs):
        print
        print json_pretty_print(self.config, mask_passwords=True)
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
