from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import getOptionFrom, padded_success
from gummanager.cli.utils import highlighter, run_recipe_with_confirmation, LogEcho, run_recipe_without_confirmation
from gummanager.libs import OauthServer


class OauthTarget(Target):
    name = 'oauth'
    server_klass = OauthServer
    _actions = ['add', 'list', 'del', 'get', 'status', 'start', 'stop', 'reload', 'test', 'upgrade']
    subtargets = ['instance', 'instances', 'available', 'nginx']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        """
            Adds a new oauth instance.

            If only <instance-name> is given, gum will pick the first available <port-index>
            based on the existing instances, and assume branch <ldap-name> named as the <instance-name>.
            If you want to use a specific port index or ldap name, please specify it.
        """
        oauth = self.Server

        instance_name = getOptionFrom(kwargs, 'instance-name')
        port_index = getOptionFrom(kwargs, 'port-index', oauth.get_available_port())

        instance = oauth.instance_by_port_index(port_index)
        if instance:
            print 'The specified port index is already in use by  "{}" oauth'.format(instance['name'])

        ldap_name = getOptionFrom(kwargs, 'ldap-branch', instance_name)

        logecho = LogEcho(
            self.config['ssh_user'],
            self.config['server'],
            '{}/{}/var/log/buildout.log'.format(self.config['instances_root'], instance_name),
            filters=['Installing', 'Generated', 'Got', 'Updating'],
        )

        run_recipe_with_confirmation(
            'Adding a new osiris OAuth server',
            {
                'name': instance_name,
                'server': self.config['server'],
                'port_index': port_index,
                'ldap_branch': ldap_name
            },
            oauth.new_instance,
            instance_name, port_index,
            logecho=logecho,
            ldap_branch=ldap_name
        )

    def list_instances(self, **kwargs):
        """
            Lists all existing oauth instances.

            This list will include instances that are not actually running and instances
            that are not even loaded on supervisor, for example old instances that are
            pending to delete.
        """

        oauth = self.Server
        instances = oauth.get_instances()
        table = GUMTable()
        table.from_dict_list(
            instances,
            hide=["circus_tcp", "mongo_database"],
            titles={
                'name': 'Name',
                'port_index': 'Index',
                'server': 'Server access',
                'ldap': 'Ldap configuration',
                'circus': ' Circus'
            })
        print table.sorted('port_index')

    def status(self, **kwargs):
        """
            Lists status for one or all active oauth instances.

            The status listed here is the status reported by supervisor. There's
            a special status 'not found'. Instances on this state are  that are created,
            but already not loaded into supervisor.
        """
        instance_name = getOptionFrom(kwargs, 'instance-name', default='all')

        oauth = self.Server
        instances = oauth.get_instances()
        if instance_name != 'all':
            instances = [instance for instance in instances if instance['name'] == instance_name]

        statuses = []
        for instance in instances:
            status = oauth.get_status(instance['name'])
            statuses.append(status)

        table = GUMTable()
        table.from_dict_list(
            statuses,
            formatters={
                'name': highlighter(default='bold_yellow'),
                'status': highlighter(values={
                    'running': 'green',
                    'unknown': 'red',
                    'down': 'red',
                    'not found': 'cyan',
                    'stopped': 'red'}
                )
            },
            titles={
                'name': 'Name',
                'status': 'Osiris Status',
                'pid': 'PID',
                'uptime': 'Started',
                'server': 'Server access'
            })
        print table.sorted('name')

    def start(self, **kwargs):
        """
            Starts a oauth instance.

            If the instance is not loaded on supervisor, it will be loaded and started.
            In every other case the instance will be started from the prior status.
            Supervisord process must be running in order to use this command
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauth = self.Server
        status = oauth.get_status(instance_name)
        if status['status'] == 'running':
            padded_success('Already running')
        else:
            oauth.start(instance_name)

    def stop(self, **kwargs):
        """
            Stops an oauth instance.

            Supervisord process must be running in order to use this command
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauth = self.Server
        status = oauth.get_status(instance_name)
        if status['status'] == 'running':
            oauth.stop(instance_name)
        else:
            padded_success("Already stopped")
        if status['status'] == 'stopped':
            print '\nAlready stopped\n'

    def test(self, **kwargs):
        """
            Tests that oauth instance is working as expected.

            An username and a password of an existing user has to be provided.
        """
        instance_name = getOptionFrom(kwargs, 'instance-name', default='all')
        username = getOptionFrom(kwargs, 'username')
        password = getOptionFrom(kwargs, 'password')
        oauth = self.Server

        run_recipe_without_confirmation(
            oauth.test,
            instance_name, username, password,
            stop_on_errors=False
        )

    def reload_nginx(self, **kwargs):
        """
            Reloads the nginx server running the oauth instances.

            Configuration test will be performed prior to restarting. If any
            errors found, nginx won't be restarted.
        """
        maxserver = self.Server

        run_recipe_with_confirmation(
            'Reload nginx httpd server ?',
            {
                'server': self.config['server'],
            },
            maxserver.reload_nginx_configuration,
        )

        maxserver.reload_nginx_configuration()

    def upgrade(self, **kwargs):
        """
            Upgrades a oauth server.

            The versions used in the upgrade will be the ones defined in the versions.cfg
            of the buildout used in the instance.
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauthserver = self.Server

        logecho = LogEcho(
            self.config['ssh_user'],
            self.config['server'],
            '{}/{}/var/log/buildout.log'.format(self.config['instances_root'], instance_name),
            filters=['Installing', 'Got', 'Updating', 'Error'],
        )

        run_recipe_with_confirmation(
            'Upgrading an existing oauth server',
            {
                'name': instance_name,
                'server': self.config['server'],
            },
            oauthserver.upgrade,
            instance_name,
            logecho=logecho,
        )

    def get_available_port(self, **kwargs):
        """
            Returns the first available port index for an oauth server.

            The port returned will not take into account any gaps  in the port
            assignation, so the number will be the next port after the highest used port.

        """
        oauth = self.Server
        port = oauth.get_available_port()
        print port
