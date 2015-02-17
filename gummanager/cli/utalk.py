from gummanager.cli.target import Target
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom, step_log, padded_log, padded_error
from gummanager.libs import MaxServer
from gummanager.libs import OauthServer
from gummanager.libs import UTalkServer
from gummanager.cli.utils import json_pretty_print, run_recipe_with_confirmation


class UTalkTarget(Target):
    server_klass = UTalkServer
    _actions = ['test', 'add']
    subtargets = ['instance']

    def info(self, **kwargs):
        shared_config = {
            'rabbitmq': getConfiguration(kwargs['--config'])['rabbitmq'],
            'maxbunny': getConfiguration(kwargs['--config'])['maxbunny']
        }
        print
        print json_pretty_print(shared_config, mask_passwords=True)
        print

    def add_instance(self, **kwargs):
        """
            Adds a existing max instance to the list used by utalk to
            know to which max route incoming messages and tweets
        """
        step_log('Checking parameters consistency')

        instance_name = getOptionFrom(kwargs, 'domain')
        hashtag = getOptionFrom(kwargs, 'hashtag', '')
        language = getOptionFrom(kwargs, 'language', 'ca')

        padded_log('Checking max server ...')
        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(max_config)
        max_instance = maxserver.get_instance(instance_name)

        if not max_instance:
            padded_error("There's no defined max server named {}".format(instance_name))
            return None

        padded_log('Checking oauth server ...')
        oauth_server_url = max_instance['oauth']
        oauth_instance_name = oauth_server_url.split('/')[-1]

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(oauth_config)
        oauth_instance = oauthserver.get_instance(oauth_instance_name)

        if not oauth_instance:
            padded_error("Max server {} is bound to an oauth {} that doesn't exist".format(instance_name, oauth_instance_name))
            return None

        self.extra_config = {
            'max': maxserver,
            'oauth': oauthserver,
            'rabbitmq': getConfiguration(kwargs['--config'])['rabbitmq'],
            'maxbunny': getConfiguration(kwargs['--config'])['maxbunny']

        }

        run_recipe_with_confirmation(
            'Adding a new utalk domain',
            {
                'server': max_instance['server']['dns'],
                'name': instance_name,
                'hashtag': hashtag,
                'language': language,
            },
            self.Server.add_instance,
            name=instance_name,
            server=max_instance['server']['dns'],
            oauth_server=oauth_instance['server']['dns'],
            hashtag=hashtag,
            restricted_user='restricted',
            language=language)

    def test(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'domain')

        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(max_config)

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(oauth_config)

        self.extra_config = {
            'max': maxserver,
            'oauth': oauthserver
        }

        self.Server.test(instance_name)
