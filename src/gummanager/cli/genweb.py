from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter
from gummanager.cli.utils import getOptionFrom, print_message, ask_confirmation
from gummanager.libs import GenwebServer
from pprint import pprint


class GenwebTarget(Target):
    server_klass = GenwebServer
    actions = ['add', 'list', 'del', 'info', 'get', 'status']
    subtargets = ['instance', 'instances', 'available']
    extratargets = ['mountpoint']

    def get_available_mountpoint(self, **kwargs):
        available = self.Server.get_available_mountpoint()
        if available:
            print 'Available mountpoint at http://{environment}:{port}/{id}'.format(**available)
        else:
            print "There's no available mountpoint in any environment"

    def list_instances(self, **kwargs):
        instances = self.Server.get_instances()
        table = GUMTable()
        table.from_dict_list(
            instances,
            formatters={
                'environment': highlighter(default='bold_yellow'),
            },
            titles={
                'name': 'Name',
            })
        print table.sorted('environment')

    def add_instance(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'instance-name')
        environment = getOptionFrom(kwargs, 'env', default='')
        mountpoint = getOptionFrom(kwargs, 'mpoint', default='')
        ldap_branch = getOptionFrom(kwargs, 'ldap-branch', instance_name)
        allow_shared_mountpoint = getOptionFrom(kwargs, 'f', False)
        create = False

        if environment and mountpoint:
            if not self.Server.is_mountpoint_available(environment, mountpoint, allow_shared=allow_shared_mountpoint):
                print "This mountpoint is unavailable"
                return
            create = True
        else:
            available_mountpoint = self.Server.get_available_mountpoint()
            if available_mountpoint:
                environment = available_mountpoint['environment']
                mountpoint = available_mountpoint['id']
                create = True
            else:
                print "There's no available mountpoint in any environment"
                return

        if create:
            siteid = instance_name
            title = siteid.capitalize()
            language = 'ca'

            message = """
        Adding a new Ulearn:
            name: "{}"
            server: "{}"
            mountpoint: "{}"
            ldap_branch: "{}"

            """.format(siteid, environment, mountpoint, ldap_branch)
            if ask_confirmation(message):

                for code, message in self.Server.new_instance(instance_name, environment, mountpoint, title, language, ldap_branch):
                    print_message(code, message)
                    if code == 0:
                        return None

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
