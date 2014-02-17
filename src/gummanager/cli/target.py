import sys


class Target(object):

    actions = []
    subtargets = []
    extratargets = []

    def __init__(self, config):
        self.config = config

    def forge_command_from_arguments(self, arguments):
        actions = [arg_name for arg_name, arg_value in arguments.items() if arg_name in self.actions and arg_value == True]

        if not actions:
            print '\nUndefined action "{}"\n'.format(sys.argv[2])
            sys.exit(1)

        action_name = actions[0]

        action_method_name = action_name

        subtarget = [arg_name for arg_name, arg_value in arguments.items() if arg_name in self.subtargets and arg_value == True]
        if subtarget:
            subtarget_name = subtarget[0]
            action_method_name += "_{}".format(subtarget_name)

        extratarget = [arg_name for arg_name, arg_value in arguments.items() if arg_name in self.extratargets and arg_value == True]
        if extratarget:
            extratarget_name = extratarget[0]
            action_method_name += "_{}".format(extratarget_name)

        return action_method_name
