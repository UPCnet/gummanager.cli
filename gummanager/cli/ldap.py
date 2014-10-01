from blessings import Terminal
from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import get_length
from gummanager.cli.utils import highlighter
from gummanager.cli.utils import run_recipe_with_confirmation
from gummanager.libs import LdapServer
from gummanager.libs._ldap import LDAP_INVALID_CREDENTIALS
from gummanager.libs._ldap import LDAP_USER_NOT_FOUND

term = Terminal()


class LdapTarget(Target):
    server_klass = LdapServer
    _actions = ['add', 'list', 'delete', 'check']
    subtargets = ['branch', 'branches', 'user', 'users']

    def add_branch(self, **kwargs):
        """
            Adds a new branch named <branch-name> on the root of the ldap server
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')

        ld = self.Server
        ld.connect()

        ld.add_branch(branch_name)
        ld.disconnect()

    def add_users(self, **kwargs):
        """
            Batch add users from a file of users. File is expected to be:

            CSV with columns: username, display name, password
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')
        usersfile = getOptionFrom(kwargs, '<users-file>')

        ld = self.Server
        # Configure a different server for batch if present
        if 'batch_server' in self.config:
            ld.set_server(server=self.config['batch_server'], port=self.config['port'])

        run_recipe_with_confirmation(
            'Batch create users from file',
            {
                'server': ld.ldap_uri,
                'branch': branch_name,

            },
            ld.batch_add_users,
            branch_name,
            usersfile,
            stop_on_errors=False
        )

    def add_user(self, **kwargs):
        """
            Adds a new user on the users folder of the branch specified by <branch-name>
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')
        password = getOptionFrom(kwargs, 'password', mask=True)

        ld = self.Server
        ld.connect(auth=False)
        ld.authenticate(
            username=self.config['branch_admin_cn'],
            password=self.config['branch_admin_password'],
            branch=branch_name,
            userdn=False)

        ld.cd('/')
        ld.cd('ou=users,ou={}'.format(branch_name))
        ld.addUser(username, username, password)
        ld.disconnect()

    def delete_user(self, **kwargs):
        """
            Deletes a single user from the users folder of the branch specified by <branch-name>
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')

        ld = self.Server
        ld.connect()

        ld.cd('/')
        ld.cd('ou=users,ou={}'.format(branch_name))
        ld.delUser(username)
        ld.disconnect()

    def check_user(self, **kwargs):
        """
            Checks existence and password of a user on the users folder of the branch specified by <branch-name>
        """

        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')
        password = getOptionFrom(kwargs, 'password', mask=True)
        ld = self.Server
        ld.connect()
        result = ld.authenticate(username, password, branch=branch_name, userdn=True)
        ld.disconnect()

        if result is True:
            print term.green, "\n    User {} exists and matches provided password".format(username)
        elif result is LDAP_USER_NOT_FOUND:
            print term.red, "\n    User {} doesn't exists in branch {}".format(username, branch_name)
        elif result is LDAP_INVALID_CREDENTIALS:
            print term.red, "\n    User {} exists but passwords do not match".format(username)

        print term.normal

    def list_users(self, **kwargs):
        """
            Prints a list of all the users of the branch specified by <branch-name>, sorted by username
            You can filter the results (case insensitive) with the --filter=<text> option
        """

        ld = self.Server
        branch_name = getOptionFrom(kwargs, 'branch-name')
        u_filter = getOptionFrom(kwargs, 'filter', default=None)
        ld.connect()

        users = ld.get_branch_users(branch_name, filter=u_filter)
        table = GUMTable(hrules='FRAME')
        table.from_dict_list(
            users,
            formatters={
                'name': highlighter(default='bold_yellow')
            },
            titles={
                'name': 'Username',
                'sn': 'SN'
            })
        print table.sorted('name')

        ld.disconnect()

    def list_branches(self, **kwargs):
        """
            Prints a list of all the branches on the ldap server
            For each branch, a count of users and groups is dusplayed
        """

        ld = self.Server
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
