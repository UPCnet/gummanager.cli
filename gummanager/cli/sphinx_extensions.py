from sphinx.roles import nodes
from gummanager.libs import config_files
from gummanager.cli.utils import getConfiguration
from gummanager.libs import ports


def setup(app):
    """
    """
    app.add_role('cfgfile', cfgfile_role)
    return


def cfgfile_role(name, rawtext, text, lineno, inliner, options={}, content=[]):

    configuration = getConfiguration()
    common_config = {
        'server_dns': configuration.max.server_dns,
        'bigmax_port': ports.BIGMAX_BASE_PORT,
        'instance_folder': configuration.max.instances_root + '/{instance_name}',
        'oauth_dns': configuration.max.default_oauth_server_dns,
        'instance_name': '{instance_name}',
        'oauth_name': '{oauth_name}',
        'max_port': '{max_port}',
        'circus_nginx_port': '{circus_nginx_port}',
        'circus_httpd_endpoint': '{circus_httpd_endpoint}',
        'port_index': '{port_index}',


    }

    filename, format = text.split(',')
    configfile = config_files.__dict__.get(filename, 'Config file {} not found'.format(filename))
    configfile = configfile.replace('\n    ', '\n')
    configfile = configfile.format(**common_config)

    node = nodes.literal_block(configfile, configfile)
    node['language'] = format
    return [node], []
