"""Config is structure for configuration of behave Report Portal agent."""
from configparser import ConfigParser
from enum import Enum
from warnings import simplefilter, warn


RP_CFG_SECTION = "report_portal"
DEFAULT_LAUNCH_NAME = "Python Behave Launch"
DEFAULT_CFG_FILE = "behave.ini"


class LogLayout(Enum):
    """Enum holding the different log layout styles that are possible."""

    SCENARIO = 0
    STEP = 1
    NESTED = 2

    @classmethod
    def _missing_(cls, value):
        if value:
            value_upper = str(value).upper()
            for member in cls:
                if member.name == value_upper:
                    return member
        return cls.SCENARIO


class Config(object):
    """Class for configuration of behave Report Portal agent."""

    def __init__(
        self,
        endpoint=None,
        project=None,
        token=None,
        launch_id=None,
        launch_name=None,
        launch_description=None,
        launch_attributes=None,
        debug_mode=None,
        log_layout=None,
        step_based=None,
        is_skipped_an_issue=None,
        retries=None,
        rerun=None,
        rerun_of=None,
        **kwargs
    ):
        """Initialize instance attributes."""
        self.endpoint = endpoint
        self.project = project
        self.token = token
        self.enabled = all([self.endpoint, self.project, self.token])
        self.launch_id = launch_id
        self.launch_name = launch_name or DEFAULT_LAUNCH_NAME
        self.launch_description = launch_description
        self.launch_attributes = launch_attributes and launch_attributes.split(
            " "
        )
        self.debug_mode = get_bool(debug_mode) or False
        self.is_skipped_an_issue = get_bool(is_skipped_an_issue) or False
        self.retries = retries and int(retries)
        self.rerun = get_bool(rerun) or False
        self.rerun_of = rerun_of

        if step_based and not log_layout:
            simplefilter("default")
            warn(
                "'step_based' config setting has been deprecated"
                "in favor of the new log_layout configuration.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.log_layout = (
                LogLayout.STEP if get_bool(step_based) else LogLayout.SCENARIO
            )
        else:
            self.log_layout = LogLayout(log_layout)


def read_config(context):
    """Read config from file and return instance of Config."""
    cp = ConfigParser()
    cmd_data = context._config.userdata
    path = cmd_data.get("config_file")
    cp.read(path or DEFAULT_CFG_FILE)
    rp_cfg = {}
    if cp.has_section(RP_CFG_SECTION):
        rp_cfg = cp[RP_CFG_SECTION]
    rp_cfg.update(cmd_data)

    return Config(**rp_cfg)


def get_bool(value):
    """Convert string value to bool."""
    if value is None:
        return
    if isinstance(value, bool):
        return value
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
