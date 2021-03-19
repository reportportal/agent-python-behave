"""Config is structure for configuration of behave Report Portal agent."""

from configparser import ConfigParser


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
        is_skipped_an_issue=None,
        tests_attributes=None,
        retries=None,
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
        self.is_skipped_an_issue = is_skipped_an_issue or False
        self.tests_attributes = tests_attributes and tests_attributes.split(
            " "
        )
        self.retries = retries


def read_config(context):
    """Read config from file and return instance of Config."""
    cp = ConfigParser()
    cmd_data = context._config.userdata
    path = cmd_data.get("config_file")
    cp.read(path or DEFAULT_CFG_FILE)
    endpoint = cmd_data.get("endpoint")
    project = cmd_data.get("project")
    token = cmd_data.get("token")
    launch_name = cmd_data.get("launch_name")
    launch_description = cmd_data.get("launch_description")
    launch_attributes = cmd_data.get("launch_attributes")
    step_based = cmd_data.getbool("step_based", None)
    is_skipped_an_issue = cmd_data.getbool("is_skipped_an_issue", None)
    tests_attributes = cmd_data.get("tests_attributes")
    retries = cmd_data.getint("retries", None)

    if not cp.has_section(RP_CFG_SECTION):
        return Config(
            endpoint=endpoint,
            project=project,
            token=token,
            launch_name=launch_name,
            launch_description=launch_description,
            launch_attributes=launch_attributes,
            step_based=step_based,
            is_skipped_an_issue=is_skipped_an_issue,
            tests_attributes=tests_attributes,
            retries=retries,
        )

    rp_cfg = cp[RP_CFG_SECTION]
    return Config(
        endpoint=endpoint or rp_cfg.get("endpoint"),
        project=project or rp_cfg.get("project"),
        token=token or rp_cfg.get("token"),
        launch_name=launch_name or rp_cfg.get("launch_name"),
        launch_description=launch_description
        or rp_cfg.get("launch_description"),
        launch_attributes=launch_attributes or rp_cfg.get("launch_attributes"),
        step_based=step_based
        if step_based is not None
        else rp_cfg.getboolean("step_based"),
        is_skipped_an_issue=is_skipped_an_issue
        if is_skipped_an_issue is not None
        else rp_cfg.getboolean("is_skipped_an_issue"),
        tests_attributes=tests_attributes or rp_cfg.get("tests_attributes"),
        retries=retries or rp_cfg.getint("retries"),
    )
