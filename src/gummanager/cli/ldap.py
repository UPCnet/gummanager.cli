from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom, GUMTable, get_length
from gummanager.libs import LdapServer
from pprint import pprint


class LdapTarget(Target):
    actions = ['add', 'list', 'del', 'info']
    subtargets = ['branch', 'branches', 'user']

    def add_branch(self, **kwargs):
        branch_name = getOptionFrom(kwargs, 'branch-name')

        ld = LdapServer(**self.config)
        ld.connect()

        ld.add_branch(branch_name)
        ld.disconnect()

    def add_user(self, **kwargs):
        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')

        # password opcional a demanar o passat per parametres
        password = getOptionFrom(kwargs, 'password')
        ld = LdapServer(**self.config)
        ld.connect()

        ld.cd('/')
        ld.cd('ou={}'.format(branch_name))
        ld.addUser(username, username, password)
        ld.disconnect()

    def list_branches(self, **kwargs):
        ld = LdapServer(**self.config)
        ld.connect()

        branches = ld.get_branches()
        table = GUMTable()
        table.from_dict_list(
            branches,
            formatters={
                'groups': get_length,
                'users': get_length
            },
            titles={
                'name': 'Name',
                'groups': 'Groups',
                'users': 'Users'
            })
        print table.sorted('name')

        ld.disconnect()

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
