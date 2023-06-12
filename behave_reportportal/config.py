"""Config is structure for configuration of behave Report Portal agent."""

#  Copyright (c) 2023 EPAM Systems
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License

from configparser import ConfigParser
from enum import Enum
from warnings import warn

from reportportal_client.logs.log_manager import MAX_LOG_BATCH_PAYLOAD_SIZE

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
            api_key=None,
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
            log_batch_size=None,
            log_batch_payload_size=None,
            **kwargs
    ):
        """Initialize instance attributes."""
        self.endpoint = endpoint
        self.project = project
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
        self.log_batch_size = (log_batch_size and int(
            log_batch_size)) or 20
        self.log_batch_payload_size = (log_batch_payload_size and int(
            log_batch_payload_size)) or MAX_LOG_BATCH_PAYLOAD_SIZE

        if step_based and not log_layout:
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

        self.api_key = api_key
        if not self.api_key:
            if 'token' in kwargs:
                warn(
                    message="Argument `token` is deprecated since 2.0.4 and "
                            "will be subject for removing in the next major "
                            "version. Use `api_key` argument instead.",
                    category=DeprecationWarning,
                    stacklevel=2
                )
                self.api_key = kwargs['token']

            if not self.api_key:
                warn(
                    message="Argument `api_key` is `None` or empty string, "
                            "that's not supposed to happen because Report "
                            "Portal is usually requires an authorization key. "
                            "Please check your code.",
                    category=RuntimeWarning,
                    stacklevel=2
                )
        self.enabled = all([self.endpoint, self.project, self.api_key])


def read_config(context):
    """Read config from file and return instance of Config."""
    cp = ConfigParser()
    cmd_data = context._config.userdata
    path = cmd_data.get("config_file")
    cp.read(path or DEFAULT_CFG_FILE)
    rp_cfg = {}
    if cp.has_section(RP_CFG_SECTION):
        rp_cfg.update(cp[RP_CFG_SECTION])
    rp_cfg.update(cmd_data)

    return Config(**rp_cfg)


def get_bool(value):
    """Convert string value to bool."""
    if value is None or value == '':
        return
    if isinstance(value, bool):
        return value
    if str(value).lower() in ('true', '1'):
        return True
    if str(value).lower() in ('false', '0'):
        return False
