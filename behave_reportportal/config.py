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

"""Config is structure for configuration of behave ReportPortal agent."""

from configparser import ConfigParser
from enum import Enum
from typing import Optional, List, Union, Tuple
from warnings import warn

from behave.runner import Context
from reportportal_client import OutputType, ClientType
from reportportal_client.helpers import to_bool
from reportportal_client.logs import MAX_LOG_BATCH_PAYLOAD_SIZE

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
    """Class for configuration of behave ReportPortal agent."""

    endpoint: Optional[str]
    project: Optional[str]
    api_key: Optional[str]
    enabled: bool
    launch_id: Optional[str]
    launch_name: str
    launch_description: Optional[str]
    launch_attributes: Optional[List[str]]
    debug_mode: bool
    is_skipped_an_issue: bool
    retries: Optional[int]
    rerun: bool
    rerun_of: Optional[str]
    log_batch_size: int
    log_batch_payload_size: int
    log_layout: LogLayout
    launch_uuid_print: bool
    launch_uuid_print_output: Optional[OutputType]
    client_type: ClientType
    http_timeout: Optional[Union[Tuple[float, float], float]]

    def __init__(
            self,
            endpoint: Optional[str] = None,
            project: Optional[str] = None,
            api_key: Optional[str] = None,
            launch_id: Optional[str] = None,
            launch_name: Optional[str] = None,
            launch_description: Optional[str] = None,
            launch_attributes: Optional[str] = None,
            debug_mode: Optional[Union[str, bool]] = None,
            log_layout: Optional[Union[str, LogLayout]] = None,
            step_based: Optional[str] = None,
            is_skipped_an_issue: Optional[Union[str, bool]] = None,
            retries: Optional[str] = None,
            rerun: Optional[Union[str, bool]] = None,
            rerun_of: Optional[str] = None,
            log_batch_size: Optional[str] = None,
            log_batch_payload_size: Optional[str] = None,
            launch_uuid_print: Optional[str] = None,
            launch_uuid_print_output: Optional[str] = None,
            client_type: Optional[str] = None,
            connect_timeout: Optional[Union[str, float]] = None,
            read_timeout: Optional[Union[str, float]] = None,
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
        self.debug_mode = to_bool(debug_mode or 'False')
        self.is_skipped_an_issue = to_bool(is_skipped_an_issue or 'False')
        self.retries = retries and int(retries)
        self.rerun = to_bool(rerun or 'False')
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
                LogLayout.STEP if to_bool(step_based) else LogLayout.SCENARIO
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
                            "that's not supposed to happen because ReportPortal "
                            "is usually requires an authorization key. "
                            "Please check your code.",
                    category=RuntimeWarning,
                    stacklevel=2
                )
        self.enabled = all([self.endpoint, self.project, self.api_key])
        self.launch_uuid_print = to_bool(launch_uuid_print or 'False')
        self.launch_uuid_print_output = OutputType[launch_uuid_print_output.upper()] \
            if launch_uuid_print_output else None
        self.client_type = ClientType[client_type.upper()] if client_type else ClientType.SYNC

        connect_timeout = float(connect_timeout) if connect_timeout else None
        read_timeout = float(read_timeout) if read_timeout else None

        if connect_timeout is None and read_timeout is None:
            self.http_timeout = None
        elif connect_timeout is not None and read_timeout is not None:
            self.http_timeout = (connect_timeout, read_timeout)
        else:
            self.http_timeout = connect_timeout or read_timeout


def read_config(context: Context) -> Config:
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
