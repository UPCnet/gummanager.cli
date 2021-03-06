# -*- coding: utf-8 -*-
from gummanager.cli.target import Target
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import LogEcho
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import highlighter
from gummanager.cli.utils import run_recipe_with_confirmation, getConfiguration
from gummanager.libs import GenwebServer


class GenwebTarget(Target):
    name = 'genweb'
    server_klass = GenwebServer
    _actions = ['add', 'list', 'del', 'get', 'status', 'reload']
    subtargets = ['instance', 'instances', 'available', 'nginx']
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

        self.extra_config = {'ldap_config': getConfiguration(kwargs['--config'])['ldap']}
        genweb_server = self.Server

        if environment and mountpoint:
            if not genweb_server.is_mountpoint_available(environment, mountpoint, allow_shared=allow_shared_mountpoint):
                print "This mountpoint is unavailable"
                return
            create = True
        else:
            available_mountpoint = genweb_server.get_available_mountpoint()
            if available_mountpoint:
                environment = available_mountpoint['environment']
                mountpoint = available_mountpoint['id']
                create = True
            else:
                print "There's no available mountpoint in any environment"
                return

        ldap_config = getConfiguration(kwargs['--config'])['ldap']
        ldap_password = ldap_config['branch_admin_password']

        if create:
            siteid = instance_name
            title = siteid.capitalize()
            language = 'ca'

            env_params = genweb_server.get_environment(environment)
            logecho = LogEcho(
                env_params.ssh_user,
                env_params.server,
                '{}/zc1.log'.format(env_params.log_folder),
                target_lines=326,
                filters=['INFO']
            )

            run_recipe_with_confirmation(
                "Adding a new Genweb",
                {
                    "name": siteid,
                    "server": environment,
                    "mountpoint": mountpoint,
                    "ldap_branch": ldap_branch,
                },
                genweb_server.new_instance,
                *[instance_name, environment, mountpoint, title, language, ldap_branch, ldap_password, logecho]
            )
