from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import ask_confirmation
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import highlighter, run_recipe_with_confirmation, LogEcho
from gummanager.libs import OauthServer


class OauthTarget(Target):
    server_klass = OauthServer
    _actions = ['add', 'list', 'del', 'get', 'status', 'start', 'stop', 'reload', 'test']
    subtargets = ['instance', 'instances', 'available', 'nginx']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        """
            Adds a new oauth instance.

            If only <instance-name> is given, gum will pick the first available <port-index>
            based on the existing instances, and assume branch <ldap-name> named as the <instance-name>.
            If you want to use a specific port index or ldap name, please specify it.
        """
        self.extra_config = {'ldap_config': getConfiguration(kwargs['--config'])['ldap']}
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

    def start(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauth = self.Server
        status = oauth.get_status(instance_name)
        if status['status'] == 'running':
            print '\nAlready running\n'
        if status['status'] in ['stopped', 'unknown']:
            oauth.start(instance_name)

    def stop(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauth = self.Server
        status = oauth.get_status(instance_name)
        if status['status'] == 'stopped':
            print '\nAlready stopped\n'
        if status['status'] == 'running':
            oauth.stop(instance_name)

    def reload_nginx(self, **kwargs):
        oauth = self.Server
        oauth.reload_nginx_configuration()

    def get_available_port(self, **kwargs):
        oauth = self.Server
        port = oauth.get_available_port()
        print port

    def test(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name', default='all')
        oauth = self.Server
        oauth.test(instance_name)

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

    def list_instances(self, **kwargs):

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
