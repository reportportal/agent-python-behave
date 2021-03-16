"""Config is structure for configuration of behave Report Portal agent."""

import six
from six.moves import configparser


if six.PY2:
    ConfigParser = configparser.SafeConfigParser
else:
    ConfigParser = configparser.ConfigParser


RP_CFG_SECTION = "report_portal"
DEFAULT_LAUNCH_NAME = "Python Behave Launch"
DEFAULT_CFG_FILE = "behave.ini"


class Config(object):
    """Class for configuration of behave Report Portal agent."""

    def __init__(
        self,
        endpoint=None,
        project=None,
        token=None,
        launch_name=None,
        launch_description=None,
        launch_attributes=None,
        step_based=None,
    ):
        """Initialize instance attributes."""
        self.endpoint = endpoint
        self.project = project
        self.token = token
        self.enabled = all([self.endpoint, self.project, self.token])
        self.launch_name = launch_name or DEFAULT_LAUNCH_NAME
        self.launch_description = launch_description
        self.launch_attributes = launch_attributes and launch_attributes.split(
            " "
        )
        self.step_based = step_based or False


def read_config(context):
    """Read config from file and return instance of Config."""
    cp = ConfigParser()
    cmd_data = context._config.userdata
    path = cmd_data.get("config_file")
    cp.read(path or DEFAULT_CFG_FILE)
    cfg = Config(
        endpoint=cmd_data.get("endpoint"),
        project=cmd_data.get("project"),
        token=cmd_data.get("token"),
        launch_name=cmd_data.get("launch_name"),
        launch_description=cmd_data.get("launch_description"),
        launch_attributes=cmd_data.get("launch_attributes"),
        step_based=cmd_data.getbool("step_based"),
    )

    if RP_CFG_SECTION not in cp.sections():
        return cfg

    rp_cfg = cp[RP_CFG_SECTION]
    return Config(
        endpoint=cfg.endpoint or rp_cfg.get("endpoint"),
        project=cfg.project or rp_cfg.get("project"),
        token=cfg.token or rp_cfg.get("token"),
        launch_name=cfg.launch_name or rp_cfg.get("launch_name"),
        launch_description=cfg.launch_description
        or rp_cfg.get("launch_description"),
        launch_attributes=cfg.launch_attributes
        or rp_cfg.get("launch_attributes"),
        step_based=cfg.step_based or rp_cfg.getboolean("step_based"),
    )
