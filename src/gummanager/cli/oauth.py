from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter
from gummanager.libs import OauthServer
from pprint import pprint


class OauthTarget(Target):
    actions = ['add', 'list', 'del', 'info', 'get', 'status', 'start', 'stop', 'reload']
    subtargets = ['instance', 'instances', 'available', 'nginx']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        params = {'ldap_config': getConfiguration(kwargs['--config'])['ldap']}
        params.update(self.config)
        oauth = OauthServer(**params)

        instance_name = getOptionFrom(kwargs, 'instance-name')
        port_index = getOptionFrom(kwargs, 'port-index', oauth.get_available_port())

        instance = oauth.instance_by_port_index(port_index)
        if instance:
            print 'The specified port index is already in use by  "{}" oauth'.format(instance['name'])

        ldap_name = getOptionFrom(kwargs, 'ldap-branch', instance_name)
        oauth.new_instance(instance_name, port_index, ldap_branch=ldap_name)

    def start(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauth = OauthServer(**self.config)
        status = oauth.get_status(instance_name)
        if status['status'] == 'active':
            print '\nAlready running\n'
        if status['status'] in ['stopped', 'unknown']:
            oauth.start(instance_name)

    def stop(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        oauth = OauthServer(**self.config)
        status = oauth.get_status(instance_name)
        if status['status'] == 'stopped':
            print '\nAlready stopped\n'
        if status['status'] == 'active':
            oauth.stop(instance_name)

    def reload_nginx(self, **kwargs):
        oauth = OauthServer(**self.config)
        oauth.reload_nginx_configuration()

    def get_available_port(self, **kwargs):
        oauth = OauthServer(**self.config)
        port = oauth.get_available_port()
        print port

    def status(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name', default='all')

        oauth = OauthServer(**self.config)
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
                'status': 'Osiris Status',
                'pid': 'PID',
                'uptime': 'Started',
                'server': 'Server access'
            })
        print table.sorted('name')

    def list_instances(self, **kwargs):

        oauth = OauthServer(**self.config)
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

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
