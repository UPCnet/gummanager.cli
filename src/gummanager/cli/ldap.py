from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.libs import LdapServer
from pprint import pprint


class LdapTarget(Target):
    actions = ['add', 'list', 'del', 'info']
    subtargets =  ['branch']

    def add_branch(self, **kwargs):
        branch_name = getOptionFrom(kwargs, 'ldap-branch-name')

        ld = LdapServer(**self.config)    
        ld.connect()    
        ld.addOU(branch_name)
        ld.cd('ou={}'.format(branch_name))
        ld.addUser('ldap', 'LDAP Access User', 'connldapnexio')
        ld.addUser('restricted', 'Restricted User', '{}LidT8'.format(branch_name))
        ld.addGroup('Managers')
        ld.addOU('groups')
        ld.addOU('users')
        ld.disconnect()

    def info(self, **kwargs):
        print
        pprint(self.config)
        print