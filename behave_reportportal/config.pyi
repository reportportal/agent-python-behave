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
from typing import Any, Optional, Text, List, Dict, Union

from behave.runner import Context


class LogLayout(Enum):
    SCENARIO = ...
    STEP = ...
    NESTED = ...


class Config(object):
    endpoint: Optional[Text]
    project: Optional[Text]
    token: Optional[Text]
    enabled: bool
    launch_id: Optional[Text]
    launch_name: Text
    launch_description: Optional[Text]
    launch_attributes: Optional[List[Text]]
    debug_mode: bool
    is_skipped_an_issue: bool
    retries: Optional[int]
    rerun: bool
    rerun_of: Optional[Text]
    log_batch_size: int
    log_batch_payload_size: int
    log_layout: LogLayout

    def __init__(
            self,
            endpoint: Optional[Text]=...,
            project: Optional[Text]=...,
            token: Optional[Text]=...,
            launch_id: Optional[Text]=...,
            launch_name: Optional[Text]=...,
            launch_description: Optional[Text]=...,
            launch_attributes: Optional[Text]=...,
            debug_mode: Optional[Union[Text, bool]]=...,
            log_layout: Optional[Text]=...,
            step_based: Optional[Text]=...,
            is_skipped_an_issue: Optional[Union[Text, bool]]=...,
            retries: Optional[Text]=...,
            rerun: Optional[Union[Text, bool]]=...,
            rerun_of: Optional[Text]=...,
            log_batch_size: Optional[Text]=...,
            log_batch_payload_size: Optional[Text]=...,
            **kwargs: Any
    ) -> None: ...


def read_config(context: Context) -> Config: ...


def get_bool(value: Any) -> Optional[bool]: ...
