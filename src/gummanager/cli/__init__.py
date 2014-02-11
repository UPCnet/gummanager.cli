# -*- coding: utf-8 -*-
"""GUM Manager.

Usage:
  gum (-vh)
  gum ldap info [-c]
  gum ldap add branch <ldap-branch-name>[-c]
  gum ldap del branch <ldap-branch-name> [-c]
  gum ldap info branch <ldap-branch-name> [-c]
  

Options:
  -h --help           Show this screen.
  -v --version        Show version.
  -c --config         Use this file for default settings.

"""

from docopt import docopt
from gummanager.cli.ldap import LdapTarget
from gummanager.cli.utils import getConfiguration
import sys

ACTIONS = ['add', 'list', 'del', 'info']
TARGETS = {
    'ldap': LdapTarget
}

SUBTARGETS = {
    
}

def main():
    arguments = docopt(__doc__, version='GUM Cli 1.0')

    targets = [arg_name for arg_name, arg_value in arguments.items() if arg_name in TARGETS and arg_value == True]
    target_name = targets[0]

    config = getConfiguration(arguments['--config'])
    target_config = config.get(target_name, {})
    target = TARGETS[target_name](target_config)

    actions = [arg_name for arg_name, arg_value in arguments.items() if arg_name in target.actions and arg_value == True]
    action_name = actions[0]
    
    subtarget = [arg_name for arg_name, arg_value in arguments.items() if arg_name in target.subtargets and arg_value == True]
    if subtarget:
        subtarget_name = subtarget[0]
        action_method_name = "{}_{}".format(action_name, subtarget_name)
    else:
        action_method_name = action_name
        
    target_method = getattr(target, action_method_name, None)
    if target_method is None:
        sys.exit('Not Implemented: {} {} {}'.format(action_name, target_name, subtarget_name))

    target_method(**arguments)




