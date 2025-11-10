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

"""Functionality for integration of Behave tests with ReportPortal."""

import mimetypes
import os
import traceback
from functools import wraps
from os import PathLike
from typing import Any, Callable, Dict, List, Optional, Union

from behave.model import Feature, Scenario, Step
from behave.model_core import BasicStatement, TagAndStatusStatement, TagStatement
from behave.runner import Context
from prettytable import MARKDOWN, PrettyTable
from reportportal_client import RP, create_client

# noinspection PyProtectedMember
from reportportal_client._internal.static.defines import NOT_SET
from reportportal_client.helpers import (
    dict_to_payload,
    gen_attributes,
    get_launch_sys_attrs,
    get_package_version,
    timestamp,
)

from behave_reportportal.config import Config, LogLayout
from behave_reportportal.utils import Singleton


def check_rp_enabled(func: Callable) -> Callable:
    """Verify is RP is enabled in config."""

    @wraps(func)
    def wrap(*args, **kwargs):
        if args and isinstance(args[0], BehaveAgent):
            # noinspection PyProtectedMember
            if not args[0]._rp:
                return None

        return func(*args, **kwargs)

    return wrap


def create_rp_service(cfg: Config) -> Optional[RP]:
    """Create instance of ReportPortalService."""
    if cfg.enabled:
        return create_client(
            client_type=cfg.client_type,
            endpoint=cfg.endpoint,
            project=cfg.project,
            api_key=cfg.api_key,
            is_skipped_an_issue=cfg.is_skipped_an_issue,
            launch_uuid=cfg.launch_uuid,
            retries=cfg.retries,
            mode="DEBUG" if cfg.debug_mode else "DEFAULT",
            log_batch_size=cfg.log_batch_size,
            log_batch_payload_limit=cfg.log_batch_payload_limit,
            launch_uuid_print=cfg.launch_uuid_print,
            print_output=cfg.launch_uuid_print_output,
            http_timeout=cfg.http_timeout,
            # OAuth 2.0 parameters
            oauth_uri=cfg.oauth_uri,
            oauth_username=cfg.oauth_username,
            oauth_password=cfg.oauth_password,
            oauth_client_id=cfg.oauth_client_id,
            oauth_client_secret=cfg.oauth_client_secret,
            oauth_scope=cfg.oauth_scope,
        )
    return None


class BehaveAgent(metaclass=Singleton):
    """Functionality for integration of Behave tests with ReportPortal."""

    _rp: Optional[RP]
    _cfg: Config
    _handle_lifecycle: bool
    agent_name: str
    agent_version: str
    _launch_id: Optional[str]
    _feature_id: Optional[str]
    _scenario_id: Optional[str]
    _step_id: Optional[str]
    _log_item_id: Optional[str]
    _ignore_tag_prefixes: List[str]

    def __init__(self, cfg: Config, rp_service: Optional[RP] = NOT_SET) -> None:
        """Initialize instance attributes."""
        if rp_service is NOT_SET:
            self._rp = create_rp_service(cfg)
        else:
            self._rp = rp_service
        self._cfg = cfg
        self._handle_lifecycle = True
        self._launch_id = None
        self._feature_id = None
        self._scenario_id = None
        self._step_id = None
        self._log_item_id = None
        self.agent_name = "behave-reportportal"
        self.agent_version = get_package_version(self.agent_name)
        # these tags are ignored during collection of test attributes
        # there are other rules for processing of these tags
        self._ignore_tag_prefixes = ["attribute", "fixture", "test_case_id"]

    @check_rp_enabled
    def start_launch(self, _: Context, **kwargs: Any) -> None:
        """Start launch in ReportPortal."""
        self._handle_lifecycle = False if self._rp.launch_uuid else True
        self._launch_id = self._rp.launch_uuid or self._rp.start_launch(
            name=self._cfg.launch_name,
            start_time=timestamp(),
            attributes=self._get_launch_attributes(),
            description=self._cfg.launch_description,
            rerun=self._cfg.rerun,
            rerun_of=self._cfg.rerun_of,
            **kwargs,
        )

    @check_rp_enabled
    def finish_launch(self, _: Context, **kwargs: Any) -> None:
        """Finish launch in ReportPortal."""
        if self._handle_lifecycle:
            self._rp.finish_launch(end_time=timestamp(), **kwargs)
        self._rp.close()

    @check_rp_enabled
    def start_feature(self, context: Context, feature: Feature, **kwargs: Any) -> None:
        """Start feature in ReportPortal."""
        if feature.tags and "skip" in feature.tags:
            feature.skip("Marked with @skip")
        self._feature_id = self._rp.start_test_item(
            name=feature.name,
            start_time=timestamp(),
            item_type="SUITE",
            description=self._item_description(context, feature),
            code_ref=self._code_ref(feature),
            attributes=self._attributes(feature),
            **kwargs,
        )
        self._log_fixtures(feature, "BEFORE_SUITE", self._feature_id)
        self._log_item_id = self._feature_id

    @check_rp_enabled
    def finish_feature(self, context: Context, feature: Feature, status: Optional[str] = None, **kwargs: Any) -> None:
        """Finish feature in ReportPortal."""
        if feature.tags and "skip" in feature.tags:
            status = "SKIPPED"
        self._log_cleanups(context, "feature")
        self._rp.finish_test_item(
            item_id=self._feature_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(feature.status.name),
            **kwargs,
        )

    @check_rp_enabled
    def start_scenario(self, context: Context, scenario: Scenario, **kwargs: Any) -> None:
        """Start scenario in ReportPortal."""
        if scenario.tags and "skip" in scenario.tags:
            scenario.skip("Marked with @skip")
        self._scenario_id = self._rp.start_test_item(
            name=scenario.name,
            start_time=timestamp(),
            item_type="STEP",
            parent_item_id=self._feature_id,
            code_ref=self._code_ref(scenario),
            attributes=self._attributes(scenario),
            parameters=self._get_parameters(context),
            description=self._item_description(context, scenario),
            test_case_id=self._test_case_id(scenario),
            **kwargs,
        )
        self._log_fixtures(scenario, "BEFORE_TEST", self._scenario_id)
        self._log_item_id = self._scenario_id

    @check_rp_enabled
    def finish_scenario(
        self,
        context: Context,
        scenario: Scenario,
        status: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Finish scenario in ReportPortal."""
        if scenario.tags and "skip" in scenario.tags:
            status = "SKIPPED"
        if scenario.status.name == "failed":
            self._log_skipped_steps(context, scenario)
            self._log_scenario_exception(scenario)
        self._log_cleanups(context, "scenario")
        self._rp.finish_test_item(
            item_id=self._scenario_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(scenario.status.name),
            **kwargs,
        )
        self._log_item_id = self._feature_id

    def _log_skipped_steps(self, context: Context, scenario: Scenario) -> None:
        if self._cfg.log_layout is not LogLayout.SCENARIO:
            skipped_steps = [step for step in scenario.steps if step.status.name == "skipped"]
            for step in skipped_steps:
                self.start_step(context, step)
                self.finish_step(context, step)

    @check_rp_enabled
    def start_step(self, _: Context, step: Step, **kwargs: Any) -> None:
        """Start test in ReportPortal."""
        if self._cfg.log_layout is not LogLayout.SCENARIO:
            step_content = self._build_step_content(step)
            self._step_id = self._rp.start_test_item(
                name=f"[{step.keyword}]: {step.name}",
                start_time=timestamp(),
                item_type="STEP",
                parent_item_id=self._scenario_id,
                code_ref=self._code_ref(step),
                description=step_content,
                has_stats=False if self._cfg.log_layout is LogLayout.NESTED else True,
                **kwargs,
            )
            self._log_item_id = self._step_id
            if self._cfg.log_layout is LogLayout.NESTED and step_content:
                self.post_log(step_content)

    @check_rp_enabled
    def finish_step(self, _: Context, step: Step, **kwargs: Any) -> None:
        """Finish test in ReportPortal."""
        if self._cfg.log_layout is not LogLayout.SCENARIO:
            self._finish_step_step_based(step, **kwargs)
            return
        self._finish_step_scenario_based(step, **kwargs)

    @check_rp_enabled
    def post_log(
        self,
        message: str,
        level: Optional[Union[int, str]] = "INFO",
        item_id: Optional[str] = None,
        file_to_attach: Optional[Union[PathLike, str]] = None,
    ) -> None:
        """Post log message to current test item."""
        self._log(
            message,
            level,
            file_to_attach=file_to_attach,
            item_id=item_id or self._log_item_id,
        )

    @check_rp_enabled
    def post_launch_log(
        self,
        message: str,
        level: Optional[Union[int, str]] = "INFO",
        file_to_attach: Optional[Union[PathLike, str]] = None,
    ) -> None:
        """Post log message to launch."""
        self._log(message, level, file_to_attach=file_to_attach)

    def _log(
        self,
        message: str,
        level: Optional[Union[int, str]],
        file_to_attach: Optional[Union[PathLike, str]] = None,
        item_id: Optional[str] = None,
    ) -> None:
        attachment = None
        if file_to_attach:
            try:
                with open(file_to_attach, "rb") as f:
                    attachment = {
                        "name": os.path.basename(file_to_attach),
                        "data": f.read(),
                        "mime": mimetypes.guess_type(file_to_attach)[0] or "application/octet-stream",
                    }
            except OSError:
                self._rp.log(
                    time=timestamp(), message=f"Attachment not found: {file_to_attach}", level="WARN", item_id=item_id
                )
        self._rp.log(
            time=timestamp(),
            message=message,
            level=level,
            attachment=attachment,
            item_id=item_id,
        )

    def _get_launch_attributes(self) -> List[Dict[str, str]]:
        """Return launch attributes in the format supported by the rp."""
        launch_attributes = self._cfg.launch_attributes
        attributes = gen_attributes(launch_attributes) if launch_attributes else []
        system_attributes = get_launch_sys_attrs()
        system_attributes["agent"] = f"{self.agent_name}|{self.agent_version}"
        return attributes + dict_to_payload(system_attributes)

    @staticmethod
    def _build_step_content(step: Step) -> str:
        txt = ""
        if step.text:
            txt += f"```\n{step.text}\n```\n"
        if step.table:
            pt = PrettyTable(field_names=step.table.headings)
            for row in step.table.rows:
                pt.add_row(row.cells)
            pt.set_style(MARKDOWN)
            txt += pt.get_string()
        return txt

    def _finish_step_step_based(self, step: Step, status: Optional[str] = None, **kwargs: Any) -> None:
        if step.status.name == "failed":
            self._log_step_exception(step, self._step_id)
        self._rp.finish_test_item(
            item_id=self._step_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(step.status.name),
            **kwargs,
        )
        self._log_item_id = self._scenario_id

    def _finish_step_scenario_based(self, step: Step, **kwargs: Any) -> None:
        step_content = self._build_step_content(step)
        self._rp.log(
            item_id=self._scenario_id,
            time=timestamp(),
            message=f"[{step.keyword}]: {step.name}." + (f"\n\n{step_content}" if step_content else ""),
            level="INFO",
            **kwargs,
        )
        if step.status.name == "failed":
            self._log_step_exception(step, self._scenario_id)

    def _log_step_exception(self, step: Step, item_id: Optional[str]) -> None:
        self._log_exception(
            f"Step [{step.keyword}]: {step.name} was finished with exception.",
            step,
            item_id,
        )

    def _log_scenario_exception(self, scenario: Scenario) -> None:
        self._log_exception(
            f"Scenario '{scenario.name}' finished with error.",
            scenario,
            self._scenario_id,
        )

    def _log_exception(self, initial_msg: str, exc_holder: BasicStatement, item_id: Optional[str]) -> None:
        message = [initial_msg]
        if exc_holder.exception and exc_holder.exc_traceback:
            message.append(
                "".join(
                    traceback.format_exception(
                        type(exc_holder.exception),
                        exc_holder.exception,
                        exc_holder.exc_traceback,
                    )
                )
            )
        if exc_holder.error_message:
            message.append(exc_holder.error_message)

        self._rp.log(
            item_id=item_id,
            time=timestamp(),
            level="ERROR",
            message="\n".join(message),
        )

    def _log_fixtures(
        self,
        item: Union[TagAndStatusStatement, TagStatement],
        item_type: str,
        parent_item_id: str,
    ) -> None:
        """
        Log used fixtures for item.

        It will log records for scenario based approach
        and step for step based.
        """
        if not item.tags:
            return
        for tag in item.tags:
            if not tag.startswith("fixture."):
                continue
            msg = f"Using of '{tag[len('fixture.'):]}' fixture"
            if self._cfg.log_layout is not LogLayout.SCENARIO:
                self._step_id = self._rp.start_test_item(
                    name=msg,
                    start_time=timestamp(),
                    item_type=item_type,
                    parent_item_id=parent_item_id,
                    has_stats=False if self._cfg.log_layout is LogLayout.NESTED else True,
                )
                self._rp.finish_test_item(item_id=self._step_id, end_time=timestamp(), status="PASSED")
                continue
            self._rp.log(
                timestamp(),
                msg,
                level="INFO",
                item_id=parent_item_id,
            )

    def _log_cleanups(self, context: Context, scope: str) -> None:
        # noinspection PyProtectedMember
        layer = next((level for level in context._stack if level.get("@layer") == scope), None)
        if not layer:
            return
        item_type = "AFTER_SUITE" if scope == "feature" else "AFTER_TEST"
        item_id = self._feature_id if scope == "feature" else self._scenario_id
        for cleanup in layer.get("@cleanups", []):
            msg = f"Execution of '{cleanup.__name__}' cleanup function"
            if self._cfg.log_layout is not LogLayout.SCENARIO:
                self._step_id = self._rp.start_test_item(
                    name=msg,
                    start_time=timestamp(),
                    item_type=item_type,
                    parent_item_id=item_id,
                    has_stats=False if self._cfg.log_layout is LogLayout.NESTED else True,
                )
                self._rp.finish_test_item(item_id=self._step_id, end_time=timestamp(), status="PASSED")
                continue
            self._rp.log(
                timestamp(),
                msg,
                level="INFO",
                item_id=item_id,
            )

    @staticmethod
    def _item_description(context: Context, item: Union[Scenario, Feature]) -> str:
        desc = ""
        if item.description:
            text_desc = "\n".join(item.description)
            desc = f"Description:\n{text_desc}"
        if context.active_outline:
            pt = PrettyTable(field_names=context.active_outline.headings)
            pt.add_row(context.active_outline.cells)
            pt.set_style(MARKDOWN)
            desc += "\n\n" if desc else ""
            desc += pt.get_string()
        return desc

    @staticmethod
    def _get_parameters(context: Context) -> Optional[Dict[str, Any]]:
        if context.active_outline:
            return {r[0]: r[1] for r in zip(context.active_outline.headings, context.active_outline.cells)}
        return None

    @staticmethod
    def _code_ref(item: BasicStatement) -> Optional[str]:
        if item.location:
            return f"{item.location.filename}:{item.location.line}"
        return None

    def _attributes(self, item: Union[TagAndStatusStatement, TagStatement]) -> List[Dict[str, str]]:
        attrs = []
        if item.tags:
            significant_tags = [t for t in item.tags if not any(t.startswith(p) for p in self._ignore_tag_prefixes)]
            attrs.extend(significant_tags)
            attrs.extend(self._get_attributes_from_tags(item.tags))

        return gen_attributes(attrs)

    @staticmethod
    def _get_attributes_from_tags(tags: List[str]) -> List[str]:
        result = []
        attr_tags = [t for t in tags if t.startswith("attribute")]

        for attr_tag in attr_tags:
            start = attr_tag.find("(")
            end = attr_tag.find(")")
            if start == -1 or end == -1:
                continue
            attr_str = attr_tag[start + 1 : end]
            if not attr_str:
                continue
            result.extend([a.strip() for a in attr_str.split(",")])

        return result

    @staticmethod
    def _test_case_id(scenario: Scenario) -> Optional[Any]:
        if scenario.tags:
            tc_tag = next((t for t in scenario.tags if t.startswith("test_case_id(")), None)
            if not tc_tag:
                return None
            start, end = tc_tag.find("("), tc_tag.find(")")
            if start == -1 or end == -1:
                return None
            tc_id = tc_tag[start + 1 : end]
            if not tc_id:
                return None
            return tc_id
        return None

    @staticmethod
    def convert_to_rp_status(behave_status: str) -> str:
        """
        Convert behave test result status to ReportPortal status.

        :param behave_status: behave test result status
        :return: ReportPortal test result status
        """
        if behave_status == "passed":
            return "PASSED"
        elif behave_status == "failed":
            return "FAILED"
        elif behave_status == "skipped":
            return "SKIPPED"
        else:
            # todo define what to do
            return "PASSED"
