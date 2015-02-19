from gummanager.cli.target import Target
from gummanager.cli.utils import padded_success
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import highlighter, LogEcho
from gummanager.cli.utils import run_recipe_with_confirmation
from gummanager.libs import MaxServer
from gummanager.libs import OauthServer


class MaxTarget(Target):
    name = 'max'
    server_klass = MaxServer
    _actions = ['add', 'list', 'del', 'get', 'status', 'start', 'stop', 'reload', 'configure', 'test', 'upgrade']
    subtargets = ['instance', 'instances', 'available', 'nginx']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        """
            Adds a new max instance.

            If only <instance-name> is given, gum will pick the first available <port-index>
            based on the existing instances, and assume <oauth-name> named as the <instance-name>.
            If you want to use a specific port index or oauth instance please specify it.
        """
        maxserver = self.Server

        instance_name = getOptionFrom(kwargs, 'instance-name')
        port_index = getOptionFrom(kwargs, 'port-index', maxserver.get_available_port())

        instance = maxserver.instance_by_port_index(port_index)
        if instance:
            print 'The specified port index is already in use by  "{}" oauth'.format(instance['name'])

        oauth_instance = getOptionFrom(kwargs, 'oauth-instance', instance_name)

        logecho = LogEcho(
            self.config['ssh_user'],
            self.config['server'],
            '{}/{}/var/log/buildout.log'.format(self.config['instances_root'], instance_name),
            filters=['Installing', 'Generated', 'Got', 'Updating'],
        )

        run_recipe_with_confirmation(
            'Adding a new max server',
            {
                'name': instance_name,
                'server': self.config['server'],
                'port_index': port_index,
                'oauth_server': oauth_instance
            },
            maxserver.new_instance,
            instance_name, port_index,
            logecho=logecho,
            oauth_instance=oauth_instance,
        )

    def list_instances(self, **kwargs):
        """
            Lists all existing max instances.

            This list will include instances that are not actually running and instances
            that are not even loaded on supervisor, for example old instances that are
            pending to delete.
        """
        maxserver = self.Server
        instances = maxserver.get_instances()
        table = GUMTable()
        table.from_dict_list(
            instances,
            hide=["circus_tcp", "mongo_database"],
            formatters={
                'name': highlighter(default='bold_yellow'),
            },
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
            Lists status for one or all active max instances.

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
                    'backoff': 'red',
                    'fatal': 'red',
                    'not found': 'cyan',
                    'stopped': 'red'}

                )
            },
            titles={
                'name': 'Name',
                'status': 'Status',
                'pid': 'PID',
                'uptime': 'Started',
                'server': 'Server access'
            })
        print table.sorted('name')

    def start(self, **kwargs):
        """
            Starts a max instance.

            If the instance is not loaded on supervisor, it will be loaded and started.
            In every other case the instance will be started from the prior status.
            Supervisord process must be running in order to use this command
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = self.Server
        status = maxserver.get_status(instance_name)
        if status['status'] == 'running':
            padded_success("Already running")
        else:
            maxserver.start(instance_name)

    def stop(self, **kwargs):
        """
            Stops a max instance.

            Supervisord process must be running in order to use this command
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = self.Server
        status = maxserver.get_status(instance_name)

        if status['status'] == 'running':
            maxserver.stop(instance_name)
        else:
            padded_success("Already stopped")

    def test(self, **kwargs):
        """
            Tests that a max instance is working as expected.

            An username and a password of an existing user has to be provided.
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')

        maxserver = self.Server
        instance_info = maxserver.get_instance(instance_name)

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(**oauth_config)
        oauth_info = oauthserver.instance_by_dns(instance_info['oauth'])
        ldap_branch = oauth_info['ldap']['branch']
        ldap_branch = oauth_info['ldap']['branch']

        maxserver.test(instance_name, ldap_branch)

        print 'Test end'

    def upgrade(self, **kwargs):
        """
            Upgrades a max server.

            The versions used in the upgrade will be the ones defined in the versions.cfg
            of the buildout used in the instance.
        """
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = self.Server

        logecho = LogEcho(
            self.config['ssh_user'],
            self.config['server'],
            '{}/{}/var/log/buildout.log'.format(self.config['instances_root'], instance_name),
            filters=['Installing', 'Got', 'Updating', 'Error'],
        )

        run_recipe_with_confirmation(
            'Upgrading an existing max server',
            {
                'name': instance_name,
                'server': self.config['server'],
                'running': maxserver.get_running_version(instance_name),
            },
            maxserver.upgrade,
            instance_name,
            logecho=logecho,
        )

    def reload_nginx(self, **kwargs):
        """
            Reloads the nginx server running the max instances.

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

    def get_available_port(self, **kwargs):
        """
            Returns the first available port index for a max server.

            The port returned will not take into account any gaps  in the port
            assignation, so the number will be the next port after the highest used port.

        """
        maxserver = self.Server
        port = maxserver.get_available_port()
        print port
