"""Functionality for integration of Behave tests with Report Portal."""
from functools import wraps

from prettytable import PrettyTable
from reportportal_client import ReportPortalService
from reportportal_client.helpers import (
    gen_attributes,
    get_launch_sys_attrs,
    get_package_version,
)
from reportportal_client.service import _dict_to_payload

from behave_reportportal.utils import timestamp


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
            endpoint=cfg.endpoint, project=cfg.project, token=cfg.token
        )


class BehaveAgent(object):
    """Functionality for integration of Behave tests with Report Portal."""

    def __init__(self, cfg, rp_service=None):
        """Initialize instance attributes."""
        self._rp = rp_service
        self._cfg = cfg
        self._launch_id = None
        self._feature_id = None
        self._scenario_id = None
        self._step_id = None
        self.agent_name = "behave-reportportal"
        self.agent_version = get_package_version(self.agent_name)

    @check_rp_enabled
    def start_launch(self, context, **kwargs):
        """Start launch in Report Portal."""
        self._launch_id = self._rp.start_launch(
            name=self._cfg.launch_name,
            start_time=timestamp(),
            attributes=self._get_launch_attributes(),
            description=self._cfg.launch_description,
            **kwargs
        )

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
            attributes=self._tags(feature),
            **kwargs
        )

    @check_rp_enabled
    def finish_feature(self, context, feature, status=None, **kwargs):
        """Finish feature in Report Portal."""
        if feature.tags and "skip" in feature.tags:
            status = "SKIPPED"
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
            attributes=self._tags(scenario),
            parameters=self._get_parameters(scenario),
            description=self._item_description(scenario),
            **kwargs
        )

    @check_rp_enabled
    def finish_scenario(self, context, scenario, status=None, **kwargs):
        """Finish scenario in Report Portal."""
        if scenario.tags and "skip" in scenario.tags:
            status = "SKIPPED"
        self._rp.finish_test_item(
            item_id=self._scenario_id,
            end_time=timestamp(),
            status=status or self.convert_to_rp_status(scenario.status.name),
            **kwargs
        )

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

    @check_rp_enabled
    def finish_step(self, context, step, **kwargs):
        """Finish test in Report Portal."""
        if self._cfg.step_based:
            self._finish_step_step_based(step, **kwargs)
            return
        self._finish_step_scenario_based(step, **kwargs)

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
        if step.exception:
            self._rp.log(
                item_id=item_id,
                time=timestamp(),
                level="ERROR",
                message="Step [{keyword}]: {name} was finished with "
                "exception:\n{exception}".format(
                    keyword=step.keyword,
                    name=step.name,
                    exception=", ".join(step.exception.args),
                ),
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

    @staticmethod
    def _tags(item):
        if item.tags:
            return gen_attributes(item.tags)

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
