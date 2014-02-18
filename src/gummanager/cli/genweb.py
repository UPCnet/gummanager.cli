from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter
from gummanager.cli.utils import getOptionFrom
from gummanager.libs import GenwebServer
from pprint import pprint


class GenwebTarget(Target):
    server_klass = GenwebServer
    actions = ['add', 'list', 'del', 'info', 'get', 'status']
    subtargets = ['instance', 'instances', 'available']
    extratargets = ['port']

    def list_instances(self, **kwargs):
        instances = self.Server.get_instances()
        table = GUMTable()
        table.from_dict_list(
            instances,
            formatters={
                'name': highlighter(default='bold_yellow'),
            },
            titles={
                'name': 'Name',
            })
        print table.sorted('environment')

    def add_instance(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        self.Server.new_instance(instance_name)

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
