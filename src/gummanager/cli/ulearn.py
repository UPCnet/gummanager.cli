from gummanager.cli.genweb import GenwebTarget
from gummanager.cli.utils import getOptionFrom
from gummanager.libs import ULearnServer


class ULearnTarget(GenwebTarget):
    """
    """
    server_klass = ULearnServer

    def add_instance(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        self.Server.new_instance(instance_name)
