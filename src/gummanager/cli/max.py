from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import GUMTable
from gummanager.libs import MaxServer
from pprint import pprint

class MaxTarget(Target):
    actions = ['add', 'list', 'del', 'info', 'get']
    subtargets = ['instance', 'instances', 'available']
    extratargets = ['port']

    def add_instance(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')

        params = {'ldap_config': getConfiguration(kwargs['--config'])['ldap']}
        params.update(self.config)
        oauth = MaxServer(**params)
        oauth.new_instance(instance_name)

    def get_available_port(self, **kwargs):
        oauth = MaxServer(**self.config)
        port = oauth.get_available_port()
        print port

    def list_instances(self, **kwargs):
        oauth = MaxServer(**self.config)
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
                'circus':' Circus'
            })
        print table.sorted('port_index')

        
    def info(self, **kwargs):
        print
        pprint(self.config)
        print