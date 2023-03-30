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
from enum import Enum
from typing import Any, Optional, List, Union

from behave.runner import Context

RP_CFG_SECTION: str
DEFAULT_LAUNCH_NAME: str
DEFAULT_CFG_FILE: str


class LogLayout(Enum):
    SCENARIO = ...
    STEP = ...
    NESTED = ...


class Config(object):
    endpoint: Optional[str]
    project: Optional[str]
    token: Optional[str]
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

    def __init__(
            self,
            endpoint: Optional[str] = ...,
            project: Optional[str] = ...,
            token: Optional[str] = ...,
            launch_id: Optional[str] = ...,
            launch_name: Optional[str] = ...,
            launch_description: Optional[str] = ...,
            launch_attributes: Optional[str] = ...,
            debug_mode: Optional[Union[str, bool]] = ...,
            log_layout: Optional[Union[str, LogLayout]] = ...,
            step_based: Optional[str] = ...,
            is_skipped_an_issue: Optional[Union[str, bool]] = ...,
            retries: Optional[str] = ...,
            rerun: Optional[Union[str, bool]] = ...,
            rerun_of: Optional[str] = ...,
            log_batch_size: Optional[str] = ...,
            log_batch_payload_size: Optional[str] = ...,
            **kwargs: Any
    ) -> None: ...


def read_config(context: Context) -> Config: ...


def get_bool(value: Any) -> Optional[bool]: ...
