"""Functionality for integration of Behave tests with Report Portal."""
import mimetypes
import os
from functools import wraps
from os import getenv

from prettytable import PrettyTable
from reportportal_client import ReportPortalService
from reportportal_client.external.google_analytics import send_event
from reportportal_client.helpers import (
    gen_attributes,
    get_launch_sys_attrs,
    get_package_version,
    timestamp,
)
from reportportal_client.service import _dict_to_payload

from behave_reportportal.utils import Singleton


def check_rp_enabled(func):
    """Verify is RP is enabled in config."""

    @wraps(func)
    def wrap(*args, **kwargs):
        if args and isinstance(args[0], BehaveAgent):
            if not args[0]._rp:
                return

        func(*args, **kwargs)

    return wrap


def create_rp_service(cfg):
    """Create instance of ReportPortalService."""
    if cfg.enabled:
        return ReportPortalService(
            endpoint=cfg.endpoint,
            project=cfg.project,
            token=cfg.token,
            is_skipped_an_issue=cfg.is_skipped_an_issue,
            retries=cfg.retries,
        )


class BehaveAgent(metaclass=Singleton):
    """Functionality for integration of Behave tests with Report Portal."""

    def __init__(self, cfg, rp_service=None):
        """Initialize instance attributes."""
        self._rp = rp_service
        self._cfg = cfg
        self._launch_id = None
        self._feature_id = None
        self._scenario_id = None
        self._step_id = None
        self._log_item_id = None
        self._skip_analytics = getenv("AGENT_NO_ANALYTICS")
        self.agent_name = "behave-reportportal"
        self.agent_version = get_package_version(self.agent_name)
        # these tags are ignored during collection of test attributes
        # there are other rules for processing of these tags
        self._ignore_tag_prefixes = ["attribute", "fixture", "test_case_id"]

    @check_rp_enabled
    def start_launch(self, context, **kwargs):
        """Start launch in Report Portal."""
        self._launch_id = self._rp.start_launch(
            name=self._cfg.launch_name,
            start_time=timestamp(),
            attributes=self._get_launch_attributes(),
            description=self._cfg.launch_description,
            rerun=self._cfg.rerun,
            rerunOf=self._cfg.rerun_of,
            **kwargs
        )
        if not self._skip_analytics:
            send_event(self.agent_name, self.agent_version)

    @check_rp_enabled
    def finish_launch(self, context, **kwargs):
        """Finish launch in Report Portal."""
        self._rp.finish_launch(end_time=timestamp(), **kwargs)
        self._rp.terminate()

    @check_rp_enabled
    def start_feature(self, context, feature, **kwargs):
        """Start feature in Report Portal."""
        if feature.tags and "skip" in feature.tags:
            feature.skip("Marked with @skip")
        self._feature_id = self._rp.start_test_item(
            name=feature.name,
            start_time=timestamp(),
            item_type="SUITE",
            description=self._item_description(feature),
            code_ref=self._code_ref(feature),
            attributes=self._attributes(feature),
            **kwargs
        )
        self._log_fixtures(feature, "BEFORE_SUITE", self._feature_id)
        self._log_item_id = self._feature_id

    @check_rp_enabled
    def finish_feature(self, context, feature, status=None, **kwargs):
        """Finish feature in Report Portal."""
        if feature.tags and "skip" in feature.tags:
            status = "SKIPPED"
        self._log_cleanups(context, "feature")
        self._rp.finish_test_item(
            item_id=self._feature_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(feature.status.name),
            **kwargs
        )

    @check_rp_enabled
    def start_scenario(self, context, scenario, **kwargs):
        """Start scenario in Report Portal."""
        if scenario.tags and "skip" in scenario.tags:
            scenario.skip("Marked with @skip")
        self._scenario_id = self._rp.start_test_item(
            name=scenario.name,
            start_time=timestamp(),
            item_type="STEP",
            parent_item_id=self._feature_id,
            code_ref=self._code_ref(scenario),
            attributes=self._attributes(scenario),
            parameters=self._get_parameters(scenario),
            description=self._item_description(scenario),
            test_case_id=self._test_case_id(scenario),
            **kwargs
        )
        self._log_fixtures(scenario, "BEFORE_TEST", self._scenario_id)
        self._log_item_id = self._scenario_id

    @check_rp_enabled
    def finish_scenario(self, context, scenario, status=None, **kwargs):
        """Finish scenario in Report Portal."""
        if scenario.tags and "skip" in scenario.tags:
            status = "SKIPPED"
        if scenario.status.name == "failed":
            self._log_scenario_exception(scenario)
        self._log_cleanups(context, "scenario"),
        self._rp.finish_test_item(
            item_id=self._scenario_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(scenario.status.name),
            **kwargs
        )
        self._log_item_id = self._feature_id

    @check_rp_enabled
    def start_step(self, context, step, **kwargs):
        """Start test in Report Portal."""
        if self._cfg.step_based:
            description = step.text or ""
            self._step_id = self._rp.start_test_item(
                name="[{keyword}]: {name}".format(
                    keyword=step.keyword, name=step.name
                ),
                start_time=timestamp(),
                item_type="STEP",
                parent_item_id=self._scenario_id,
                code_ref=self._code_ref(step),
                description=description
                + self._build_table_content(step.table),
                **kwargs
            )
            self._log_item_id = self._step_id

    @check_rp_enabled
    def finish_step(self, context, step, **kwargs):
        """Finish test in Report Portal."""
        if self._cfg.step_based:
            self._finish_step_step_based(step, **kwargs)
            return
        self._finish_step_scenario_based(step, **kwargs)

    @check_rp_enabled
    def post_log(
        self, message, level="INFO", item_id=None, file_to_attach=None
    ):
        """Post log message to current test item."""
        self._log(
            message,
            level,
            file_to_attach=file_to_attach,
            item_id=item_id or self._log_item_id,
        )

    @check_rp_enabled
    def post_launch_log(self, message, level="INFO", file_to_attach=None):
        """Post log message to launch."""
        self._log(message, level, file_to_attach=file_to_attach)

    def _log(self, message, level, file_to_attach=None, item_id=None):
        attachment = None
        if file_to_attach:
            with open(file_to_attach, "rb") as f:
                attachment = {
                    "name": os.path.basename(file_to_attach),
                    "data": f.read(),
                    "mime": mimetypes.guess_type(file_to_attach)[0]
                    or "application/octet-stream",
                }
        self._rp.log(
            time=timestamp(),
            message=message,
            level=level,
            attachment=attachment,
            item_id=item_id,
        )

    def _get_launch_attributes(self):
        """Return launch attributes in the format supported by the rp."""
        attributes = self._cfg.launch_attributes or []
        system_attributes = get_launch_sys_attrs()
        system_attributes["agent"] = "{}-{}".format(
            self.agent_name, self.agent_version
        )
        return attributes + _dict_to_payload(system_attributes)

    @staticmethod
    def _build_table_content(table):
        if not table:
            return ""

        pt = PrettyTable(field_names=table.headings)
        [pt.add_row(row.cells) for row in table.rows]
        return "\n" + pt.get_string()

    def _finish_step_step_based(self, step, status=None, **kwargs):
        if step.status.name == "failed":
            self._log_step_exception(step, self._step_id)
        self._rp.finish_test_item(
            item_id=self._step_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(step.status.name),
            **kwargs
        )
        self._log_item_id = self._scenario_id

    def _finish_step_scenario_based(self, step, **kwargs):
        self._rp.log(
            item_id=self._scenario_id,
            time=timestamp(),
            message="[{keyword}]: {name}. {text}{table}".format(
                keyword=step.keyword,
                name=step.name,
                text=step.text or "",
                table=self._build_table_content(step.table),
            ),
            level="INFO",
            **kwargs
        )
        if step.status.name == "failed":
            self._log_step_exception(step, self._scenario_id)

    def _log_step_exception(self, step, item_id):
        message = [
            "Step [{keyword}]: {name} was finished with exception.".format(
                keyword=step.keyword, name=step.name
            )
        ]
        if step.exception:
            message.append(", ".join(step.exception.args))
        if step.error_message:
            message.append(step.error_message)

        self._rp.log(
            item_id=item_id,
            time=timestamp(),
            level="ERROR",
            message="\n".join(message),
        )

    def _log_scenario_exception(self, scenario):
        message = ["Scenario '{}' finished with error.".format(scenario.name)]
        if scenario.exception:
            message.append(", ".join(scenario.exception.args))
        if scenario.error_message:
            message.append(scenario.error_message)

        self._rp.log(
            item_id=self._scenario_id,
            time=timestamp(),
            level="ERROR",
            message="\n".join(message),
        )

    def _log_fixtures(self, item, item_type, parent_item_id):
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
            msg = "Using of '{}' fixture".format(tag[len("fixture.") :])
            if self._cfg.step_based:
                self._step_id = self._rp.start_test_item(
                    name=msg,
                    start_time=timestamp(),
                    item_type=item_type,
                    parent_item_id=parent_item_id,
                )
                self._rp.finish_test_item(self._step_id, timestamp(), "PASSED")
                continue
            self._rp.log(
                timestamp(),
                msg,
                level="INFO",
                item_id=parent_item_id,
            )

    def _log_cleanups(self, context, scope):
        layer = next(
            iter(
                [
                    level
                    for level in context._stack
                    if level.get("@layer") == scope
                ]
            ),
            None,
        )
        if not layer:
            return
        item_type = "AFTER_SUITE" if scope == "feature" else "AFTER_TEST"
        item_id = self._feature_id if scope == "feature" else self._scenario_id
        for cleanup in layer.get("@cleanups", []):
            msg = "Execution of '{}' cleanup function".format(cleanup.__name__)
            if self._cfg.step_based:
                self._step_id = self._step_id = self._rp.start_test_item(
                    name=msg,
                    start_time=timestamp(),
                    item_type=item_type,
                    parent_item_id=item_id,
                )
                self._rp.finish_test_item(self._step_id, timestamp(), "PASSED")
                continue
            self._rp.log(
                timestamp(),
                msg,
                level="INFO",
                item_id=item_id,
            )

    @staticmethod
    def _item_description(item):
        if item.description:
            return "Description:\n{}".format("\n".join(item.description))

    @staticmethod
    def _get_parameters(scenario):
        return (
            scenario._row
            and {
                r[0]: r[1]
                for r in zip(scenario._row.headings, scenario._row.cells)
            }
            or None
        )

    @staticmethod
    def _code_ref(item):
        if item.location:
            return "{file}:{line}".format(
                file=item.location.filename,
                line=item.location.line,
            )

    def _attributes(self, item):
        attrs = []
        if item.tags:
            significant_tags = [
                t
                for t in item.tags
                if not any(t.startswith(p) for p in self._ignore_tag_prefixes)
            ]
            attrs.extend(significant_tags)
            attrs.extend(self._get_attributes_from_tags(item.tags))

        return gen_attributes(attrs)

    @staticmethod
    def _get_attributes_from_tags(tags):
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
    def _test_case_id(scenario):
        if scenario.tags:
            tc_tag = next(
                iter(
                    [t for t in scenario.tags if t.startswith("test_case_id(")]
                ),
                None,
            )
            if not tc_tag:
                return
            start, end = tc_tag.find("("), tc_tag.find(")")
            if start == -1 or end == -1:
                return
            tc_id = tc_tag[start + 1 : end]
            if not tc_id:
                return
            return tc_id

    @staticmethod
    def convert_to_rp_status(behave_status):
        """
        Convert behave test result status to Report Portal status.

        :param behave_status: behave test result status
        :return: report portal test result status
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
