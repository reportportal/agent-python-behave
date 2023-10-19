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

from os import PathLike
from typing import Optional, Dict, Any, List, Union, Callable

from behave.model import Scenario, Feature, Step
from behave.model_core import BasicStatement, TagAndStatusStatement, \
    TagStatement
from behave.runner import Context
from reportportal_client import RP

from .config import Config


def check_rp_enabled(func: Callable) -> Callable: ...


def create_rp_service(cfg: Config) -> Optional[RP]: ...


class BehaveAgent:
    _rp: Optional[RP]
    _cfg: Config
    _handle_lifecycle: bool
    agent_name: str
    agent_version: str
    _feature_id: Optional[str]
    _scenario_id: Optional[str]
    _step_id: Optional[str]
    _log_item_id: Optional[str]
    _ignore_tag_prefixes: [List[str]]

    def __init__(self, cfg: Config,
                 rp_service: Optional[RP] = ...) -> None: ...

    def start_launch(self, context: Context, **kwargs: Any) -> None: ...

    def _get_launch_attributes(self) -> List[Dict[str, str]]: ...

    def _attributes(self, item: Union[TagAndStatusStatement,
    TagStatement]) -> List[Dict[str, str]]: ...

    def finish_launch(self, context: Context, **kwargs: Any) -> None: ...

    def start_feature(self, context: Context, feature: Feature,
                      **kwargs: Any) -> None: ...

    def finish_feature(self, context: Context, feature: Feature,
                       status: Optional[str] = ...,
                       **kwargs: Any) -> None: ...

    def start_scenario(self, context: Context, scenario: Scenario,
                       **kwargs: Any) -> None: ...

    def finish_scenario(self, context: Context, scenario: Scenario,
                        status: Optional[str] = ...,
                        **kwargs: Any) -> None: ...

    def start_step(self, context: Context, step: Step,
                   **kwargs: Any) -> None: ...

    def finish_step(self, context: Context, step: Step,
                    **kwargs: Any) -> None: ...

    def _log_step_exception(self, step: Step,
                            item_id: Optional[str]) -> None: ...

    def _log_exception(self, initial_msg: str, exc_holder: BasicStatement,
                       item_id: Optional[str]) -> None: ...

    def post_log(
            self, message: str, level: Optional[Union[int, str]] = ...,
            item_id: Optional[str] = ...,
            file_to_attach: Optional[Union[PathLike, str]] = ...,
    ) -> None: ...

    def post_launch_log(self, message: str,
                        level: Optional[Union[int, str]] = ...,
                        file_to_attach: Optional[
                            Union[PathLike, str]] = ...) -> None: ...

    def _log(self, message: str, level: Optional[Union[int, str]],
             file_to_attach: Optional[Union[PathLike, str]] = ...,
             item_id: Optional[str] = ...) -> None: ...

    def _log_scenario_exception(self, scenario: Scenario) -> None: ...

    def _log_fixtures(self, item: Union[TagAndStatusStatement,
    TagStatement], item_type: str, parent_item_id: str): ...

    def _log_cleanups(self, context: Context, scope: str) -> None: ...

    def _finish_step_step_based(self, step: Step, status: Optional[str] = ...,
                                **kwargs: Any) -> None: ...

    def _log_skipped_steps(self, context: Context,
                           scenario: Scenario) -> None: ...

    def _finish_step_scenario_based(self, step: Step,
                                    **kwargs: Any) -> None: ...

    @staticmethod
    def _build_step_content(step: Step) -> str: ...

    @staticmethod
    def _get_attributes_from_tags(tags: List[str]) -> List[str]: ...

    @staticmethod
    def _test_case_id(scenario: Scenario) -> str: ...

    @staticmethod
    def _item_description(context: Context, item: Union[Scenario, Feature]) -> str: ...

    @staticmethod
    def convert_to_rp_status(behave_status: str) -> str: ...

    @staticmethod
    def _code_ref(item: BasicStatement) -> Optional[str]: ...

    @staticmethod
    def _get_parameters(scenario: Scenario) -> Optional[
        Dict[str, Any]]: ...
