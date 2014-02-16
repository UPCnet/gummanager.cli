from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.libs import LdapServer
from pprint import pprint


class LdapTarget(Target):
    actions = ['add', 'list', 'del', 'info']
    subtargets =  ['branch']

    def add_branch(self, **kwargs):
        branch_name = getOptionFrom(kwargs, 'branch-name')

        ld = LdapServer(**self.config)
        ld.connect()

        ld.add_branch(branch_name)
        ld.disconnect()

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
