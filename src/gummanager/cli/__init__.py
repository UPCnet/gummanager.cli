# -*- coding: utf-8 -*-
"""GUM Manager.

Usage:
    gum (-vh)
    gum ldap info [-c]
    gum ldap add branch <branch-name>[-c]
    gum ldap get branch <branch-name> [-c]
    gum ldap <branch-name> add user <ldap-username> [--password=<ldap-password>][-c]
    gum ldap <branch-name> check user <ldap-username> [--password=<ldap-password>][-c]
    gum ldap list branches [-c]
    gum oauth info [-c]
    gum oauth add instance <instance-name> [--port-index=<port-index> --ldap-branch=<ldap-name>] [-c]
    gum oauth list instances [-c]
    gum oauth status [<instance-name>] [-c]
    gum oauth test <instance-name> [-c]
    gum oauth get available port [-c]
    gum oauth <instance-name> (start|stop) [-c]
    gum oauth reload nginx [-c]
    gum max info [-c]
    gum max add instance <instance-name> [--port-index=<port-index> --oauth-instance=<oauth-name>] [-c]
    gum max list instances [-c]
    gum max status [<instance-name>] [-c]
    gum max get available port [-c]
    gum max <instance-name> (start|stop) [-c]
    gum max reload nginx [-c]
    gum genweb list instances [-c]
    gum genweb add instance <instance-name> [(--env=<server> --mpoint=<mpoint-name>) --ldap-branch=<ldap-name>] [-c -f]
    gum genweb get available mountpoint [-c]
    gum ulearn list instances [-c]
    gum ulearn add instance <instance-name> [(--env=<server> --mpoint=<mpoint-name>) --max=<max-name>] [-c -f]
    gum ulearn get available mountpoint [-c]
    gum ulearn reload nginx [-c]
    gum utalk test <domain> [-c]


Options:
  -h --help           Show this screen.
  -v --version        Show version.
  -c --config         Use this file for default settings.
"""

import docopt
from gummanager.cli.ldap import LdapTarget
from gummanager.cli.oauth import OauthTarget
from gummanager.cli.max import MaxTarget
from gummanager.cli.genweb import GenwebTarget
from gummanager.cli.ulearn import ULearnTarget
from gummanager.cli.utalk import UTalkTarget

from gummanager.cli.utils import getConfiguration
import sys
import patches

patches = patches

TARGETS = {
    'ldap': LdapTarget,
    'oauth': OauthTarget,
    'max': MaxTarget,
    'genweb': GenwebTarget,
    'ulearn': ULearnTarget,
    'utalk': UTalkTarget,

}

SUBTARGETS = {

}


def main():
    arguments = docopt.docopt(__doc__, version='GUM Cli 1.0')

    targets = [arg_name for arg_name, arg_value in arguments.items() if arg_name in TARGETS and arg_value is True]
    if targets == []:
        print 'No such target "{}"'.format(sys.argv[1])
        sys.exit(1)
    target_name = targets[0]

    config = getConfiguration(arguments['--config'])
    target_config = config.get(target_name, {})
    target = TARGETS[target_name](target_config)

    action_method_name = target.forge_command_from_arguments(arguments)

    target_method = getattr(target, action_method_name, None)
    if target_method is None:
        sys.exit('Not Implemented: {}'.format(action_method_name))

    target_method(**arguments)
