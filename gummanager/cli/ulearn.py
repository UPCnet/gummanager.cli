# -*- coding: utf-8 -*-
from gummanager.cli.genweb import GenwebTarget
from gummanager.cli.utils import LogEcho
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import padded_error
from gummanager.cli.utils import padded_log
from gummanager.cli.utils import run_recipe_with_confirmation
from gummanager.cli.utils import step_log
from gummanager.libs import MaxServer
from gummanager.libs import OauthServer
from gummanager.libs import ULearnServer

import re


class ULearnTarget(GenwebTarget):
    """
    """
    server_klass = ULearnServer
    subtargets = GenwebTarget.subtargets + ['users']
    _actions = GenwebTarget._actions + ['subscribe']

    def reload_nginx(self, **kwargs):
        self.Server.reload_nginx_configuration()

    def add_users(self, **kwargs):
        """
            Add users from a file to a ulearn instance. User will be added to the
            related ldap branch and max instance.
        """
        step_log('Checking instance')
        padded_log('Loading existing instances')
        instances = self.Server.get_instances()

        instance_name = getOptionFrom(kwargs, 'instance-name')
        environment = getOptionFrom(kwargs, 'env', default='')
        mountpoint = getOptionFrom(kwargs, 'mpoint', default='')
        usersfile = getOptionFrom(kwargs, 'users-file')

        # Get all instances matching instance name
        matched_instances = [instance for instance in instances if instance['plonesite'].replace('bqdc', 'mediolanum') == instance_name]

        # Try to filter by env and mountpoint if provided
        if environment:
            matched_instances = [instance for instance in matched_instances if instance['environment'] == environment]

        if mountpoint:
            matched_instances = [instance for instance in matched_instances if instance['mountpoint'] == mountpoint]

        if not matched_instances:
            padded_error("No instance named {}".format(instance_name))
        elif len(matched_instances) > 1:
            padded_error("More than 1 instance named {}".format(instance_name))
            padded_log("Try again specifying one or both of --mpoint and --env options")

        instance = matched_instances[0]

        run_recipe_with_confirmation(
            'Batch create users from file',
            {
                'server': instance['environment'],
                'mountpoint': instance['mountpoint'],
                'plonesite': instance['plonesite'],
                'url': instance['url']

            },
            self.Server.batch_add_users,
            instance,
            usersfile,
            stop_on_errors=False
        )

    def subscribe_users(self, **kwargs):
        """
            Subscribe users to a bunch of ulearn instance communities.
            User will be subscribed in the accorded roles
        """
        step_log('Checking instance')
        padded_log('Loading existing instances')
        instances = self.Server.get_instances()

        instance_name = getOptionFrom(kwargs, 'instance-name')
        environment = getOptionFrom(kwargs, 'env', default='')
        mountpoint = getOptionFrom(kwargs, 'mpoint', default='')
        subscriptionsfile = getOptionFrom(kwargs, 'subscriptions-file')

        # Get all instances matching instance name
        matched_instances = [instance for instance in instances if instance['plonesite'].replace('bqdc', 'mediolanum') == instance_name]

        # Try to filter by env and mountpoint if provided
        if environment:
            matched_instances = [instance for instance in matched_instances if instance['environment'] == environment]

        if mountpoint:
            matched_instances = [instance for instance in matched_instances if instance['mountpoint'] == mountpoint]

        if not matched_instances:
            padded_error("No instance named {}".format(instance_name))
        elif len(matched_instances) > 1:
            padded_error("More than 1 instance named {}".format(instance_name))
            padded_log("Try again specifying one or both of --mpoint and --env options")

        instance = matched_instances[0]

        run_recipe_with_confirmation(
            'Batch subscribe users to communities',
            {
                'server': instance['environment'],
                'mountpoint': instance['mountpoint'],
                'plonesite': instance['plonesite'],
                'url': instance['url']

            },
            self.Server.batch_subscribe_users,
            instance,
            subscriptionsfile,
            stop_on_errors=False
        )

    def add_instance(self, **kwargs):

        step_log('Checking parameters consistency')

        instance_name = getOptionFrom(kwargs, 'instance-name')
        environment = getOptionFrom(kwargs, 'env', default='')
        mountpoint = getOptionFrom(kwargs, 'mpoint', default='')
        max_instance_name = getOptionFrom(kwargs, 'max', default=instance_name)

        padded_log('Checking max server ...')
        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(max_config)
        max_instance = maxserver.get_instance(max_instance_name)

        if not max_instance:
            padded_error("There's no defined max server named {}".format(max_instance_name))
            return None

        padded_log('Checking oauth server ...')
        oauth_server_url = max_instance['oauth']
        oauth_instance_name = oauth_server_url.split('/')[-1]

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(oauth_config)
        oauth_instance = oauthserver.get_instance(oauth_instance_name)

        if not oauth_instance:
            padded_error("Max server {} is bound to an oauth {} that doesn't exist".format(max_instance_name, oauth_instance_name))
            return None

        ldap_branch = re.search(r'ou=(\w+),', oauth_instance['ldap']['basedn']).groups()[0]

        allow_shared_mountpoint = getOptionFrom(kwargs, 'f', False)
        create = False

        padded_log('Checking mountpoint ...')
        if environment and mountpoint:
            if not self.Server.is_mountpoint_available(environment, mountpoint, allow_shared=allow_shared_mountpoint):
                padded_error("This mountpoint is unavailable")
                return
            create = True
        else:
            available_mountpoint = self.Server.get_available_mountpoint()
            if available_mountpoint:
                environment = available_mountpoint['environment']
                mountpoint = available_mountpoint['id']
                create = True
            else:
                padded_error("There's no available mountpoint in any environment")
                return

        ldap_config = getConfiguration(kwargs['--config'])['ldap']
        ldap_password = ldap_config['branch_admin_password']

        if create:
            siteid = instance_name
            title = siteid.capitalize()
            language = 'ca'

            env_params = self.Server.get_environment(environment)
            logecho = LogEcho(
                env_params.ssh_user,
                env_params.server,
                '{}/{}.log'.format(env_params.log_folder, env_params.instance_name),
                target_lines=359,
                filters=['INFO GenericSetup']
            )

            run_recipe_with_confirmation(
                "Adding a new Ulearn",
                {
                    "name": siteid,
                    "server": environment,
                    "mountpoint": mountpoint,
                    "oauth_instance": max_instance['oauth'],
                    "ldap_branch": ldap_branch,
                    "max": max_instance['server']['dns']
                },
                self.Server.new_instance,
                *[instance_name, environment, mountpoint, title, language, max_instance_name, max_instance['server']['direct'], oauth_instance_name, ldap_branch, ldap_password, logecho]
            )
