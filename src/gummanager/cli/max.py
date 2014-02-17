from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter
from gummanager.libs import MaxServer
from pprint import pprint


class MaxTarget(Target):
    actions = ['add', 'list', 'del', 'info', 'get', 'status']
    subtargets = ['instance', 'instances', 'available']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')

        params = {'ldap_config': getConfiguration(kwargs['--config'])['ldap']}
        params.update(self.config)
        maxserver = MaxServer(**params)
        maxserver.new_instance(instance_name)

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
                'circus':' Circus'
            })
        print table.sorted('port_index')


    def info(self, **kwargs):
        print
        pprint(self.config)
        print
