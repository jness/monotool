import os
from ConfigParser import ConfigParser

def get_config(app_name):
    """
    Uses configuration from /etc/monotool.conf or
    ~/.monotool.conf, the latter trumps the former.
    """
    system_path = os.path.expanduser('/etc/%s.conf' % app_name)
    home_path = os.path.expanduser('~/.%s.conf' % app_name)
    if os.path.exists(home_path):
        config_file = home_path
    elif os.path.exists(system_path):
        config_file = system_path
    else:
        raise Exception('Unable to find config in %s or %s' %
                (system_path, home_path))

    config = ConfigParser()
    config.readfp(open(config_file))
    return dict(config.items('default'))  # shouldn't be hard coded.
