from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.libs.ldap import LdapServer

class LdapTarget(Target):
    subtargets =  ['branch', 'branches']

    def add_branch(self, config, **kwargs):
        branch_name = getOptionFrom(kwargs, 'ldap-branch-name')

        ld = LdapServer(**config)    
        ld.connect()    
        ld.addOU(branch_name)
        ld.cd('ou={}'.format(branch_name))
        ld.addUser('ldap', 'LDAP Access User', 'connldapnexio')
        ld.addUser('restricted', 'Restricted User', '{}LidT8'.format(branch_name))
        ld.addGroup('Managers')
        ld.addOU('groups')
        ld.addOU('users')
        ld.disconnect()