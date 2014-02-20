from gummanager.cli.genweb import GenwebTarget
from gummanager.cli.utils import ask_confirmation
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import padded_error
from gummanager.cli.utils import padded_log
from gummanager.cli.utils import print_message
from gummanager.cli.utils import step_log
from gummanager.libs import MaxServer
from gummanager.libs import OauthServer
from gummanager.libs import ULearnServer

import re


class ULearnTarget(GenwebTarget):
    """
    """
    server_klass = ULearnServer

    def reload_nginx(self, **kwargs):
        self.Server.reload_nginx_configuration()

    def add_instance(self, **kwargs):

        step_log('Checking parameters consistency')

        instance_name = getOptionFrom(kwargs, 'instance-name')
        environment = getOptionFrom(kwargs, 'env', default='')
        mountpoint = getOptionFrom(kwargs, 'mpoint', default='')
        max_instance_name = getOptionFrom(kwargs, 'max', default=instance_name)

        padded_log('Checking max server ...')
        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(**max_config)
        max_instance = maxserver.get_instance(max_instance_name)

        if not max_instance:
            padded_error("There's no defined max server named {}".format(max_instance_name))
            return None

        padded_log('Checking oauth server ...')
        oauth_server_url = max_instance['oauth']
        oauth_instance_name = oauth_server_url.split('/')[-1]

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(**oauth_config)
        oauth_instance = oauthserver.get_instance(oauth_instance_name)

        if not max_instance:
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

        if create:
            siteid = instance_name
            title = siteid.capitalize()
            language = 'ca'

            message = """
    Adding a new Ulearn:
        name: "{}"
        server: "{}"
        mountpoint: "{}"
        oauth_instance: "{}"
        ldap_branch: "{}"
        max: "{}"

            """.format(siteid, environment, mountpoint, max_instance['oauth'], ldap_branch, max_instance['server']['dns'])
            if ask_confirmation(message):
                for code, message in self.Server.new_instance(instance_name, environment, mountpoint, title, language, max_instance_name, max_instance['server']['direct'], oauth_instance_name, ldap_branch):
                    print_message(code, message)
                    if code == 0:
                        return None
