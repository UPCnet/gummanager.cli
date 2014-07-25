from gummanager.cli.target import Target
from gummanager.cli.utils import getConfiguration
from gummanager.cli.utils import getOptionFrom
from gummanager.libs import MaxServer
from gummanager.libs import OauthServer
from gummanager.libs import UTalkServer


class UTalkTarget(Target):
    server_klass = UTalkServer
    _actions = ['test', 'add']
    subtargets = ['instance']

    def add_instance(self, **kwargs):
        """
            Adds a existing max instance to the list used by utalk to
            know to which max route incoming messages and tweets
        """
        instance_name = getOptionFrom(kwargs, 'domain')
        hashtag = getOptionFrom(kwargs, 'hashtag', '')
        language = getOptionFrom(kwargs, 'language', 'ca')

        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(max_config)

        max_instance = maxserver.get_instance(instance_name)

        self.Server.add_instance(
            name=instance_name,
            server=max_instance['server']['dns'],
            oauth_server=max_instance['oauth'],
            hashtag=hashtag,
            restricted_user='restricted',
            language=language)

    def test(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'domain')

        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(max_config)

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(**oauth_config)

        configuration = dict(self.config)
        configuration.update(dict(
            maxserver=maxserver,
            oauthserver=oauthserver
        ))

        self.Server.test(instance_name)
