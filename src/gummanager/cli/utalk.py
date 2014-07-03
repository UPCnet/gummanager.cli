from gummanager.cli.target import Target
from gummanager.cli.utils import getOptionFrom
from gummanager.cli.utils import GUMTable
from gummanager.cli.utils import highlighter, ask_confirmation
from gummanager.libs import MaxServer
from gummanager.cli.utils import getConfiguration
from gummanager.libs import OauthServer
from gummanager.libs import UTalkServer
from pprint import pprint


class UTalkTarget(Target):
    actions = ['test', 'info']
    subtargets = []

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

        utalk = UTalkServer(**configuration)
        utalk.test(instance_name)

    def info(self, **kwargs):
        print
        pprint(self.config)
        print
