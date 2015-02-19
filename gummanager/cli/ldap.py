from blessings import Terminal
from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import get_length
from gummanager.cli.utils import highlighter
from gummanager.cli.utils import run_recipe_with_confirmation
from gummanager.cli.utils import run_recipe_without_confirmation
from gummanager.libs import LdapServer

term = Terminal()


class LdapTarget(Target):
    server_klass = LdapServer
    _actions = ['add', 'list', 'delete', 'check', 'get']
    subtargets = ['branch', 'branches', 'user', 'users']

    def add_branch(self, **kwargs):
        """
            Adds a new branch named <branch-name> on the root of the ldap server
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')

        run_recipe_with_confirmation(
            "Adding a new branch",
            {
                "server": self.Server.ldap_uri,
                "branch_name": branch_name
            },
            self.Server.add_branch,
            branch_name)

    def list_branches(self, **kwargs):
        """
            Prints a list of all the branches on the ldap server
            For each branch, a count of users and groups is displayed
        """
        branches = run_recipe_without_confirmation(
            self.Server.list_branches
        )

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

    def add_user(self, **kwargs):
        """
            Adds a new user on the users folder of the branch specified by <branch-name>
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')
        password = getOptionFrom(kwargs, 'password', mask=True)

        run_recipe_with_confirmation(
            "Adding a new user to branch",
            {
                "server": self.Server.ldap_uri,
                "branch_name": branch_name,
                "username": username
            },
            self.Server.add_user,
            branch_name, username, password)

    def add_users(self, **kwargs):
        """
            Batch add users from a file of users. <users-file> is expected to
            contain a

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
            ld.add_users,
            branch_name,
            usersfile,
            stop_on_errors=False
        )

    def list_users(self, **kwargs):
        """
            Prints a list of all the users of the branch specified by <branch-name>, sorted by username
            You can filter the results (case insensitive) with the --filter=<text> option
        """

        branch_name = getOptionFrom(kwargs, 'branch-name')
        u_filter = getOptionFrom(kwargs, 'filter', default=None)

        users = run_recipe_without_confirmation(
            self.Server.list_users,
            branch_name,
            filter=u_filter
        )

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

    def delete_user(self, **kwargs):
        """
            Deletes a single user from the users folder of the branch specified by <branch-name>
        """
        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')

        run_recipe_with_confirmation(
            "Adding a new user to branch",
            {
                "server": self.Server.ldap_uri,
                "branch_name": branch_name,
                "username": username
            },
            self.Server.delete_user,
            branch_name, username)

    def check_user(self, **kwargs):
        """
            Checks existence and password of a user on the users folder of the branch specified by <branch-name>
        """

        branch_name = getOptionFrom(kwargs, 'branch-name')
        username = getOptionFrom(kwargs, 'ldap-username')
        password = getOptionFrom(kwargs, 'password', mask=True)

        run_recipe_without_confirmation(
            self.Server.check_user,
            branch_name, username, password)

