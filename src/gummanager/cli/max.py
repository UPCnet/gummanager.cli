from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter, ask_confirmation
from gummanager.libs import MaxServer
from gummanager.cli.utils import getConfiguration
from gummanager.libs import OauthServer
from pprint import pprint


class MaxTarget(Target):
    actions = ['add', 'list', 'del', 'info', 'get', 'status', 'start', 'stop', 'reload', 'configure', 'test']
    subtargets = ['instance', 'instances', 'available', 'nginx']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        maxserver = MaxServer(**self.config)

        instance_name = getOptionFrom(kwargs, 'instance-name')
        port_index = getOptionFrom(kwargs, 'port-index', maxserver.get_available_port())

        instance = maxserver.instance_by_port_index(port_index)
        if instance:
            print 'The specified port index is already in use by  "{}" oauth'.format(instance['name'])

        oauth_instance = getOptionFrom(kwargs, 'oauth-instance', instance_name)
        message = """
    Adding a new max/bigmax server:
        name: "{}"
        server: "{}"
        port_index: "{}"
        oauth_server: "{}"

        """.format(instance_name, self.config['server'], port_index, oauth_instance)
        if ask_confirmation(message):
            maxserver.new_instance(instance_name, port_index, oauth_instance=oauth_instance)

    def test(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')

        maxserver = MaxServer(**self.config)
        instance_info = maxserver.get_instance(instance_name)

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(**oauth_config)
        oauth_info = oauthserver.instance_by_dns(instance_info['oauth'])
        ldap_branch = oauth_info['ldap']['branch']
        ldap_branch = oauth_info['ldap']['branch']

        maxserver.test(instance_name, ldap_branch)

    def start(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = MaxServer(**self.config)
        status = maxserver.get_status(instance_name)
        if status['status']['max'] == 'active':
            print '\nAlready running\n'
        if status['status']['max'] in ['stopped', 'unknown']:
            maxserver.start(instance_name)

    def stop(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        maxserver = MaxServer(**self.config)
        status = maxserver.get_status(instance_name)
        if status['status'] == 'stopped':
            print '\nAlready stopped\n'
        if status['status'] == 'active':
            maxserver.stop(instance_name)

    def reload_nginx(self, **kwargs):
        maxserver = MaxServer(**self.config)
        maxserver.reload_nginx_configuration()

    def get_available_port(self, **kwargs):
        maxserver = MaxServer(**self.config)
        port = maxserver.get_available_port()
        print port

    def status(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name', default='all')

        oauth = MaxServer(**self.config)
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
                    'active': 'green',
                    'unknown': 'red',
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
        maxserver = MaxServer(**self.config)
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

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
