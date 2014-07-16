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

    def test(self, **kwargs):
        instance_name = getOptionFrom(kwargs, 'domain')

        max_config = getConfiguration(kwargs['--config'])['max']
        maxserver = MaxServer(**max_config)

        oauth_config = getConfiguration(kwargs['--config'])['oauth']
        oauthserver = OauthServer(**oauth_config)

        configuration = dict(self.config)
        configuration.update(dict(
            maxserver=maxserver,
            oauthserver=oauthserver
        ))

        self.Server.test(instance_name)
