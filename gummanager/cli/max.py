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
        self.extra_config = {
            'rabbitmq': getConfiguration(kwargs['--config'])['rabbitmq'],
            'maxbunny': getConfiguration(kwargs['--config'])['maxbunny']
        }
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

    def test(self, **kwargs):
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

    def start(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = self.Server
        status = maxserver.get_status(instance_name)
        if status['status'] == 'running':
            padded_success("Already running")
        else:
            maxserver.start(instance_name)

    def stop(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = self.Server
        status = maxserver.get_status(instance_name)

        if status['status'] == 'running':
            maxserver.stop(instance_name)
        else:
            padded_success("Already stopped")

    def reload_nginx(self, **kwargs):
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
        maxserver = self.Server
        port = maxserver.get_available_port()
        print port

    def status(self, **kwargs):
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

    def list_instances(self, **kwargs):
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

    def upgrade(self, **kwargs):
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
