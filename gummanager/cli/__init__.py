# -*- coding: utf-8 -*-
"""GUM Manager.

Usage:
    gum (-vh)
    gum ldap info
    gum ldap add branch <branch-name>
    gum ldap list branches
    gum ldap <branch-name> add user <ldap-username> [--password=<ldap-password>]
    gum ldap <branch-name> add users <users-file>
    gum ldap <branch-name> list users [--filter=<text>]
    gum ldap <branch-name> delete user <ldap-username>
    gum ldap <branch-name> check user <ldap-username> [--password=<ldap-password>]
    gum ldap help <command>...

    gum oauth info
    gum oauth add instance <instance-name> [--port-index=<port-index> --ldap-branch=<ldap-name>]
    gum oauth list instances
    gum oauth status [<instance-name>]
    gum oauth test <instance-name> [--username=<oauth-username> --password=<oauth-password>]
    gum oauth get available port
    gum oauth (start|stop) <instance-name>
    gum oauth reload nginx
    gum oauth help <command>...

    gum max info
    gum max help <command>...
    gum max add instance <instance-name> [--port-index=<port-index> --oauth-instance=<oauth-name>]
    gum max list instances
    gum max get available port
    gum max status [<instance-name>]
    gum max (start|stop) <instance-name>
    gum max upgrade <instance-name>
    gum max reload nginx
    gum max help <command>...

    gum genweb info
    gum genweb list instances
    gum genweb add instance <instance-name> [(--env=<server> --mpoint=<mpoint-name>) --ldap-branch=<ldap-name>] [-f]
    gum genweb get available mountpoint
    gum genweb help <command>...

    gum ulearn info
    gum ulearn list instances
    gum ulearn add instance <instance-name> [(--env=<server> --mpoint=<mpoint-name>) --max=<max-name>] [-f]
    gum ulearn get available mountpoint
    gum ulearn reload nginx
    gum ulearn <instance-name> add users <users-file> [--env=<server> --mpoint=<mpoint-name>]
    gum ulearn <instance-name> subscribe users <subscriptions-file> [--env=<server> --mpoint=<mpoint-name>]
    gum ulearn help <command>...

    gum utalk info
    gum utalk add instance <domain> [--hashtag=<hashtag> --language=<lang>]
    gum utalk test <domain>
    gum utalk help <command>...


Options:
  -v --version        Show version.
  -c --config         Use this file for default settings.
"""

from gummanager.cli.max import MaxTarget
from gummanager.cli.genweb import GenwebTarget
from gummanager.cli.ldap import LdapTarget
from gummanager.cli.oauth import OauthTarget
from gummanager.cli.ulearn import ULearnTarget
from gummanager.cli.utalk import UTalkTarget
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom

import docopt
import patches
import pkg_resources
import re
import sys
import warnings


warnings.filterwarnings('ignore')
patches = patches

TARGET_CLASSES = [
    LdapTarget,
    OauthTarget,
    MaxTarget,
    GenwebTarget,
    ULearnTarget,
    UTalkTarget,
]

TARGETS = {klass.name: klass for klass in TARGET_CLASSES}
SUBTARGETS = {}


def main():

    doc_with_config_options = re.sub(r'gum (\w+) (?!help)(.*)', r'gum \1 \2 [-c]', __doc__)
    doc_with_config_options = doc_with_config_options.replace('\n\n    gum', '\n    gum')
    arguments = docopt.docopt(doc_with_config_options, version='GUM Cli ' + pkg_resources.require("gummanager.cli")[0].version)

    help_mode = False
    if sys.argv[2] == 'help':
        help_mode = True
        arguments['help'] = False
        for cmd in getOptionFrom(arguments, 'command'):
            if cmd in arguments:
                arguments[cmd] = True

    targets = [arg_name for arg_name, arg_value in arguments.items() if arg_name in TARGETS and arg_value is True]
    if targets == []:
        print 'No such target "{}"'.format(sys.argv[1])
        sys.exit(1)
    target_name = targets[0]

    config = getConfiguration(arguments['--config'])
    target = TARGETS[target_name](config)
    action_method_name = target.forge_command_from_arguments(arguments)

    target_method = getattr(target, action_method_name, None)
    if target_method is None:
        sys.exit('Not Implemented: {}'.format(action_method_name))

    if help_mode:
        command_line = ' .*?'.join([a for a in ['gum'] + sys.argv[1:] if a != 'help'])
        command_definition = re.search(r'\n\s*({}.*?)\n'.format(command_line), __doc__).groups()[0]
        target.help(action_method_name, definition=command_definition)
    else:
        target_method(**arguments)
