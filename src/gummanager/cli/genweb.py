from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter
from gummanager.libs import GenwebServer
from pprint import pprint

class GenwebTarget(Target):
    actions = ['add', 'list', 'del', 'info', 'get', 'status']
    subtargets = ['instance', 'instances', 'available']
    extratargets = ['port']

    def list_instances(self, **kwargs):
        genweb = GenwebServer(**params)
        genweb.list_instances()
       
    def info(self, **kwargs):
        print
        pprint(self.config)
        print