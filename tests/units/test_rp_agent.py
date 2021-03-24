import os

import mock
import pytest
from delayed_assert import assert_expectations, expect
from prettytable import PrettyTable
from reportportal_client import ReportPortalService

from behave_reportportal.behave_agent import BehaveAgent, create_rp_service
from behave_reportportal.config import Config


@pytest.fixture()
def config():
    return Config(
        endpoint="endpoint",
        token="token",
        project="project",
        launch_name="launch_name",
        launch_description="launch_description",
    )


@pytest.mark.parametrize(
    "status,expected",
    [
        ("passed", "PASSED"),
        ("skipped", "SKIPPED"),
        ("failed", "FAILED"),
        ("xyz", "PASSED"),
    ],
)
def test_convert_to_rp_status(status, expected):
    actual = BehaveAgent.convert_to_rp_status(status)
    assert (
        actual == expected
    ), "Incorrect status:\nActual: {}\nExpected:{}".format(actual, expected)


def test_attributes(config):
    mock_item = mock.Mock()
    mock_item.tags = None
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    expect(ba._attributes(mock_item) == [], "Attributes is not empty")
    mock_item.tags = ["a", "b", "attribute(k1:v1,v2)"]
    exp = [
        {"value": "a"},
        {"value": "b"},
        {"key": "k1", "value": "v1"},
        {"value": "v2"},
    ]
    act = ba._attributes(mock_item)
    expect(
        act == exp,
        "Attributes are incorrect:\nActual: {}\nExpected: {}".format(act, exp),
    )
    assert_expectations()


@pytest.mark.parametrize(
    "tags,exp_attrs",
    [
        (["attribute( k1: v1,  v2,v3 )"], ["k1: v1", "v2", "v3"]),
        (["attribute(k1:v1,k2:v2)"], ["k1:v1", "k2:v2"]),
        (["attribute(v1,v2)"], ["v1", "v2"]),
        (["attribute(v1)"], ["v1"]),
        (["attribute(v1)", "attribute(k2:v2,v3)"], ["v1", "k2:v2", "v3"]),
        (["attr(v1)"], []),
        (["attribute"], []),
        (["attribute)"], []),
        (["attribute("], []),
        (["attribute()"], []),
        (["attribute(some_text"], []),
        (["attributesome_text)"], []),
    ],
)
def test_get_attributes_from_tags(tags, exp_attrs):
    act_attrs = BehaveAgent._get_attributes_from_tags(tags)
    assert act_attrs == exp_attrs


def test_code_ref():
    mock_item = mock.Mock()
    mock_item.location = None
    expect(BehaveAgent._code_ref(mock_item) is None, "code_ref is not None")
    mock_location = mock.Mock()
    mock_location.filename = "filename"
    mock_location.line = 24
    mock_item.location = mock_location
    expect(
        BehaveAgent._code_ref(mock_item) == "filename:24",
        "code_ref is incorrect:\nActual: {}\nExpected: {}".format(
            BehaveAgent._code_ref(mock_item), "filename:24"
        ),
    )
    assert_expectations()


def test_get_parameters():
    mock_item = mock.Mock()
    mock_item._row = None
    expect(
        BehaveAgent._get_parameters(mock_item) is None,
        "parameters is not None",
    )
    mock_row = mock.Mock()
    mock_row.headings = ["A", "B"]
    mock_row.cells = [1, 2]
    mock_item._row = mock_row
    expect(
        BehaveAgent._get_parameters(mock_item) == {"A": 1, "B": 2},
        "parameters are incorrect:\nActual: {}\nExpected: {}".format(
            BehaveAgent._get_parameters(mock_item), {"A": 1, "B": 2}
        ),
    )
    assert_expectations()


def test_create_rp_service_disabled_rp():
    assert (
        create_rp_service(Config()) is None
    ), "Service is not None for disabled integration with RP in config"


def test_create_rp_service_enabled_rp():
    rp = create_rp_service(Config(endpoint="A", token="B", project="C"))
    assert isinstance(
        rp, ReportPortalService
    ), "Invalid initialization of RP ReportPortalService"


@mock.patch("behave_reportportal.behave_agent.ReportPortalService")
def test_create_rp_service_init(mock_rps):
    create_rp_service(Config(endpoint="A", token="B", project="C"))
    mock_rps.assert_has_calls(
        [
            mock.call(
                endpoint="A",
                token="B",
                project="C",
                is_skipped_an_issue=False,
                retries=None,
            )
        ],
        any_order=True,
    )


def test_init_invalid_config():
    cfg = Config()
    ba = BehaveAgent(cfg)
    assert ba._rp is None, "Incorrect initialization of agent"


def test_init_valid_config():
    cfg = Config(endpoint="endpoint", token="token", project="project")
    mock_rp = mock.Mock()
    ba = BehaveAgent(cfg, mock_rp)
    cfg.endpoint = "122"
    expect(ba._cfg is not None, "Config is None")
    expect(ba._rp is not None, "Incorrect initialization of agent")
    assert_expectations()


def test_item_description():
    mock_item = mock.Mock()
    mock_item.description = None
    expect(
        BehaveAgent._item_description(mock_item) is None,
        "Description is not None",
    )
    mock_item.description = ["a", "b"]
    expect(
        BehaveAgent._item_description(mock_item) == "Description:\na\nb",
        "Description is incorrect:\nActual: {}\nExpected: {}".format(
            BehaveAgent._item_description(mock_item), "Description:\na\nb"
        ),
    )
    assert_expectations()


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_launch(mock_timestamp, config):
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba.start_launch(mock_context, some_key="some_value")
    mock_rps.start_launch.assert_called_once_with(
        name=config.launch_name,
        start_time=123,
        attributes=ba._get_launch_attributes(),
        description=config.launch_description,
        some_key="some_value",
        rerun=False,
        rerunOf=None,
    )


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_launch_with_rerun(mock_timestamp):
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    cfg = Config(
        endpoint="endpoint",
        token="token",
        project="project",
        launch_name="launch_name",
        launch_description="launch_description",
        retun=True,
        rerun_of="launch_id",
    )
    ba = BehaveAgent(cfg, mock_rps)
    ba.start_launch(mock_context, some_key="some_value")
    mock_rps.start_launch.assert_called_once_with(
        name=cfg.launch_name,
        start_time=123,
        attributes=ba._get_launch_attributes(),
        description=cfg.launch_description,
        some_key="some_value",
        rerun=cfg.rerun,
        rerunOf=cfg.rerun_of,
    )


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_finish_launch(mock_timestamp, config):
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba.finish_launch(mock_context, some_key="some_value")
    mock_rps.finish_launch.assert_called_once_with(
        end_time=123, some_key="some_value"
    )
    mock_rps.terminate.assert_called_once()


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_skipped_feature(mock_timestamp, config):
    mock_feature = mock.Mock()
    mock_feature.tags = ["some_tag", "skip"]
    mock_timestamp.return_value = 123
    verify_start_feature(mock_feature, config)
    mock_feature.skip.assert_called_once_with("Marked with @skip")


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_feature(mock_timestamp, config):
    mock_feature = mock.Mock()
    mock_feature.tags = None
    mock_timestamp.return_value = 123
    verify_start_feature(mock_feature, config)


def verify_start_feature(mock_feature, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_rps.start_test_item.return_value = "feature_id"
    mock_context = mock.Mock()
    mock_feature.name = "feature_name"
    mock_feature.description = ["A", "B"]
    ba = BehaveAgent(config, mock_rps)
    ba.start_feature(mock_context, mock_feature, some_key="some_value")
    mock_rps.start_test_item.assert_called_once_with(
        name="feature_name",
        start_time=123,
        item_type="SUITE",
        description=BehaveAgent._item_description(mock_feature),
        code_ref=BehaveAgent._code_ref(mock_feature),
        attributes=ba._attributes(mock_feature),
        some_key="some_value",
    )
    assert (
        ba._feature_id == "feature_id"
    ), "Invalid feature_id:\nActual: {}\nExpected: {}\n".format(
        ba._feature_id, "feature_id"
    )


@pytest.mark.parametrize(
    "tags,expected_status", [(None, "PASSED"), (["skip"], "SKIPPED")]
)
@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_finish_feature(mock_timestamp, config, tags, expected_status):
    mock_feature = mock.Mock()
    mock_feature.tags = tags
    mock_feature.status.name = "passed"
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    mock_context._stack = []
    ba = BehaveAgent(config, mock_rps)
    ba._feature_id = "feature_id"
    ba.finish_feature(mock_context, mock_feature, some_key="some_value")
    mock_rps.finish_test_item.assert_called_once_with(
        item_id="feature_id",
        end_time=123,
        status=expected_status,
        some_key="some_value",
    )


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_skipped_scenario(mock_timestamp, config):
    mock_scenario = mock.Mock()
    mock_scenario.tags = ["some_tag", "skip"]
    mock_timestamp.return_value = 123
    verify_start_scenario(mock_scenario, config)
    mock_scenario.skip.assert_called_once_with("Marked with @skip")


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_scenario(mock_timestamp, config):
    mock_scenario = mock.Mock()
    mock_scenario.tags = None
    mock_timestamp.return_value = 123
    verify_start_scenario(mock_scenario, config)


def verify_start_scenario(mock_scenario, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_rps.start_test_item.return_value = "scenario_id"
    mock_context = mock.Mock()
    mock_scenario.name = "scenario_name"
    mock_scenario._row = None
    mock_scenario.description = ["A", "B"]
    ba = BehaveAgent(config, mock_rps)
    ba._feature_id = "feature_id"
    ba.start_scenario(mock_context, mock_scenario, some_key="some_value")
    mock_rps.start_test_item.assert_called_once_with(
        name="scenario_name",
        start_time=123,
        item_type="STEP",
        parent_item_id="feature_id",
        description=BehaveAgent._item_description(mock_scenario),
        code_ref=BehaveAgent._code_ref(mock_scenario),
        parameters=BehaveAgent._get_parameters(mock_scenario),
        attributes=ba._attributes(mock_scenario),
        some_key="some_value",
    )
    assert (
        ba._scenario_id == "scenario_id"
    ), "Invalid scenario_id:\nActual: {}\nExpected: {}\n".format(
        ba._scenario_id, "scenario_id"
    )


@pytest.mark.parametrize(
    "tags,expected_status", [(None, "PASSED"), (["skip"], "SKIPPED")]
)
@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_finish_scenario(mock_timestamp, config, tags, expected_status):
    mock_scenario = mock.Mock()
    mock_scenario.tags = tags
    mock_scenario.status.name = "passed"
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    mock_context._stack = []
    ba = BehaveAgent(config, mock_rps)
    ba._scenario_id = "scenario_id"
    ba.finish_scenario(mock_context, mock_scenario, some_key="some_value")
    mock_rps.finish_test_item.assert_called_once_with(
        item_id="scenario_id",
        end_time=123,
        status=expected_status,
        some_key="some_value",
    )


@mock.patch.object(BehaveAgent, "_log_scenario_exception")
def test_finish_failed_scenario(mock_log, config):
    mock_scenario = mock.Mock()
    mock_scenario.tags = []
    mock_scenario.status.name = "failed"
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    mock_context._stack = []
    ba = BehaveAgent(config, mock_rps)
    ba.finish_scenario(mock_context, mock_scenario)
    mock_log.assert_called_once_with(mock_scenario)


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_start_step_step_based(mock_timestamp, config):
    config.step_based = True
    mock_step = mock.Mock()
    mock_step.keyword = "keyword"
    mock_step.name = "name"
    mock_step.text = None
    mock_step.table = None
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_rps.start_test_item.return_value = "step_id"
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba._scenario_id = "scenario_id"
    ba.start_step(mock_context, mock_step, some_key="some_value")
    mock_rps.start_test_item.assert_called_once_with(
        name="[keyword]: name",
        start_time=123,
        item_type="STEP",
        parent_item_id="scenario_id",
        description="",
        code_ref=BehaveAgent._code_ref(mock_step),
        some_key="some_value",
    )
    ba._step_id = "step_id"


def test_start_step_scenario_based(config):
    config.step_based = False
    mock_step = mock.Mock()
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba.start_step(mock_context, mock_step, some_key="some_value")
    mock_rps.start_test_item.assert_not_called()


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_finish_passed_step_step_based(mock_timestamp, config):
    config.step_based = True
    mock_step = mock.Mock()
    mock_step.status.name = "passed"
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba._step_id = "step_id"
    ba.finish_step(mock_context, mock_step, some_key="some_value")
    mock_rps.finish_test_item.assert_called_once_with(
        item_id="step_id", end_time=123, status="PASSED", some_key="some_value"
    )


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_finish_failed_step_step_based(mock_timestamp, config):
    config.step_based = True
    mock_step = mock.Mock()
    mock_step.keyword = "keyword"
    mock_step.name = "name"
    mock_step.status.name = "failed"
    mock_step.exception.args = ["Exception message"]
    mock_step.error_message = "Error massage"
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba._step_id = "step_id"
    ba._scenario_id = "step_id"
    ba.finish_step(mock_context, mock_step, some_key="some_value")
    mock_rps.finish_test_item.assert_called_once_with(
        item_id="step_id", end_time=123, status="FAILED", some_key="some_value"
    )
    mock_rps.log.assert_has_calls(
        [
            mock.call(
                item_id="step_id",
                time=123,
                level="ERROR",
                message="Step [keyword]: name was finished with exception.\n"
                "Exception message\nError massage",
            )
        ]
    )


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_finish_failed_step_scenario_based(mock_timestamp, config):
    config.step_based = False
    mock_step = mock.Mock()
    mock_step.keyword = "keyword"
    mock_step.name = "name"
    mock_step.status.name = "failed"
    mock_step.text = None
    mock_step.table = None
    mock_step.exception.args = ["Exception message"]
    mock_step.error_message = "Error message"
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba._scenario_id = "scenario_id"
    ba.finish_step(mock_context, mock_step)
    calls = [
        mock.call(
            item_id="scenario_id",
            time=123,
            level="ERROR",
            message="Step [keyword]: name was finished with exception.\n"
            "Exception message\nError message",
        ),
        mock.call(
            item_id="scenario_id",
            time=123,
            level="INFO",
            message="[keyword]: name. ",
        ),
    ]
    mock_rps.log.assert_has_calls(calls, any_order=True)


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_log_exception_without_message(mock_timestamp):
    mock_timestamp.return_value = 123
    mock_step = mock.Mock()
    mock_step.exception = None
    mock_step.error_message = None
    mock_step.keyword = "keyword"
    mock_step.name = "name"
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    ba._log_step_exception(mock_step, "step_id")
    mock_rps.log.assert_called_once_with(
        item_id="step_id",
        time=123,
        level="ERROR",
        message="Step [keyword]: name was finished with exception.",
    )


@mock.patch.dict(os.environ, {"AGENT_NO_ANALYTICS": "1"})
@mock.patch("behave_reportportal.behave_agent.send_event")
def test_skip_analytics(mock_send_event, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba.start_launch(mock_context)
    mock_send_event.assert_not_called()


@mock.patch("behave_reportportal.behave_agent.send_event")
def test_analytics(mock_send_event, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    ba = BehaveAgent(config, mock_rps)
    ba.start_launch(mock_context)
    mock_send_event.assert_called_once_with(ba.agent_name, ba.agent_version)


def test_rp_is_none():
    ba = BehaveAgent(Config(), None)
    ba.start_step(mock.Mock(), mock.Mock)
    assert ba._step_id is None


@mock.patch.object(BehaveAgent, "_log")
def test_post_log(mock_log, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    ba._log_item_id = "log_item_id"
    ba.post_log("message", file_to_attach="filepath")
    mock_log.assert_called_once_with(
        "message", "INFO", item_id="log_item_id", file_to_attach="filepath"
    )


@mock.patch.object(BehaveAgent, "_log")
def test_post_launch_log(mock_log, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    ba._log_item_id = "log_item_id"
    ba.post_launch_log("message", file_to_attach="filepath")
    mock_log.assert_called_once_with(
        "message", "INFO", file_to_attach="filepath"
    )


@mock.patch("behave_reportportal.behave_agent.mimetypes")
@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_post__log(mock_timestamp, mock_mime, config):
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    mock_mime.guess_type.return_value = ("mime_type", None)
    with mock.patch("builtins.open", mock.mock_open(read_data="data")):
        ba._log(
            "message", "ERROR", file_to_attach="filepath", item_id="item_id"
        )
        mock_rps.log.assert_called_once_with(
            time=123,
            message="message",
            level="ERROR",
            attachment={
                "name": "filepath",
                "data": "data",
                "mime": "mime_type",
            },
            item_id="item_id",
        )


@mock.patch.object(PrettyTable, "__init__")
@mock.patch.object(PrettyTable, "add_row")
@mock.patch.object(PrettyTable, "get_string")
def test_build_table_content(mock_get_string, mock_add_row, mock_init):
    mock_init.return_value = None
    mock_table = mock.Mock()
    mock_table.headings = ["A", "B"]
    mock_rows = mock.Mock()
    mock_rows.cells = ["c", "d"]
    mock_table.rows = [mock_rows]
    BehaveAgent._build_table_content(mock_table)
    mock_init.assert_called_once_with(field_names=["A", "B"])
    mock_add_row.assert_called_once_with(["c", "d"])
    mock_get_string.assert_called_once()


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_log_scenario_exception_default_message(mock_timestamp, config):
    mock_timestamp.return_value = 123
    mock_scenario = mock.Mock()
    mock_scenario.exception = None
    mock_scenario.error_message = None
    mock_scenario.name = "scenario_name"
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    ba._scenario_id = "scenario_id"
    ba._log_scenario_exception(mock_scenario)
    mock_rps.log.assert_called_once_with(
        item_id="scenario_id",
        time=123,
        level="ERROR",
        message="Scenario 'scenario_name' finished with error.",
    )


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_log_scenario_exception(mock_timestamp, config):
    mock_timestamp.return_value = 123
    mock_scenario = mock.Mock()
    mock_scenario.exception.args = ["Exception arg1", "Exception arg2"]
    mock_scenario.error_message = "Error message"
    mock_scenario.name = "scenario_name"
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    ba._scenario_id = "scenario_id"
    ba._log_scenario_exception(mock_scenario)
    mock_rps.log.assert_called_once_with(
        item_id="scenario_id",
        time=123,
        level="ERROR",
        message="Scenario 'scenario_name' finished with error.\n"
        "Exception arg1, Exception arg2\nError message",
    )


@pytest.mark.parametrize("tags", [None, ["A", "B"]])
def test_log_fixtures_without_fixture_tags(tags, config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_item = mock.Mock()
    mock_item.tags = tags
    BehaveAgent(config, mock_rps)._log_fixtures(mock_item, "type", "item_id")
    mock_rps.log.assert_not_called()
    mock_rps.start_test_item.assert_not_called()


@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_log_fixtures(mock_timestamp):
    mock_timestamp.return_value = 123
    cfg = Config(
        endpoint="endpoint",
        token="token",
        project="project",
        step_based="False",
    )
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_item = mock.Mock()
    mock_item.tags = ["fixture.A", "fixture.B"]
    BehaveAgent(cfg, mock_rps)._log_fixtures(mock_item, "type", "item_id")
    mock_rps.log.assert_has_calls(
        [
            mock.call(
                123, "Using of 'A' fixture", level="INFO", item_id="item_id"
            ),
            mock.call(
                123, "Using of 'B' fixture", level="INFO", item_id="item_id"
            ),
        ],
        any_order=True,
    )
    cfg.step_based = True
    BehaveAgent(cfg, mock_rps)._log_fixtures(mock_item, "type", "item_id")
    mock_rps.start_test_item.assert_has_calls(
        [
            mock.call(
                start_time=123,
                name="Using of 'A' fixture",
                item_type="type",
                parent_item_id="item_id",
            ),
            mock.call(
                start_time=123,
                name="Using of 'B' fixture",
                item_type="type",
                parent_item_id="item_id",
            ),
        ],
        any_order=True,
    )
    assert mock_rps.finish_test_item.call_count == 2


def test_log_cleanup_no_layer(config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context, mock_func = mock.Mock(), mock.Mock()
    mock_func.__name__ = "cleanup_func"
    mock_context._stack = [{"@layer": "scenario", "@cleanups": [mock_func]}]
    BehaveAgent(config, mock_rps)._log_cleanups(mock_context, "feature")
    mock_rps.start_test_item.assert_not_called()
    mock_context._stack = [{"@layer": "feature"}]
    BehaveAgent(config, mock_rps)._log_cleanups(mock_context, "scenario")
    mock_rps.start_test_item.assert_not_called()


def test_log_cleanup_no_cleanups(config):
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context = mock.Mock()
    mock_context._stack = [{"@layer": "feature"}]
    BehaveAgent(config, mock_rps)._log_cleanups(mock_context, "feature")
    mock_rps.start_test_item.assert_not_called()


@pytest.mark.parametrize(
    "scope,item_type,item_id",
    [
        ("feature", "AFTER_SUITE", "feature_id"),
        ("scenario", "AFTER_TEST", "scenario_id"),
    ],
)
@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_log_cleanup_step_based(mock_timestamp, scope, item_type, item_id):
    cfg = Config(endpoint="E", token="T", project="P", step_based=True)
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context, mock_func1, mock_func2 = mock.Mock(), mock.Mock, mock.Mock()
    mock_func1.__name__ = "cleanup_func1"
    mock_func2.__name__ = "cleanup_func2"
    mock_context._stack = [
        {"@layer": scope, "@cleanups": [mock_func1, mock_func2]}
    ]
    ba = BehaveAgent(cfg, mock_rps)
    ba._feature_id = "feature_id"
    ba._scenario_id = "scenario_id"
    ba._log_cleanups(mock_context, scope)
    calls = [
        mock.call(
            name="Execution of '{}' cleanup function".format(f_name),
            start_time=123,
            item_type=item_type,
            parent_item_id=item_id,
        )
        for f_name in ("cleanup_func1", "cleanup_func2")
    ]
    mock_rps.start_test_item.assert_has_calls(calls)
    assert mock_rps.finish_test_item.call_count == 2


@pytest.mark.parametrize(
    "scope,item_id", [("feature", "feature_id"), ("scenario", "scenario_id")]
)
@mock.patch("behave_reportportal.behave_agent.timestamp")
def test_log_cleanup_scenario_based(mock_timestamp, config, scope, item_id):
    mock_timestamp.return_value = 123
    mock_rps = mock.create_autospec(ReportPortalService)
    mock_context, mock_func1, mock_func2 = mock.Mock(), mock.Mock, mock.Mock()
    mock_func1.__name__ = "cleanup_func1"
    mock_func2.__name__ = "cleanup_func2"
    mock_context._stack = [
        {"@layer": scope, "@cleanups": [mock_func1, mock_func2]}
    ]
    ba = BehaveAgent(config, mock_rps)
    ba._feature_id = "feature_id"
    ba._scenario_id = "scenario_id"
    ba._log_cleanups(mock_context, scope)
    calls = [
        mock.call(
            123,
            "Execution of '{}' cleanup function".format(f_name),
            level="INFO",
            item_id=item_id,
        )
        for f_name in ("cleanup_func1", "cleanup_func2")
    ]
    mock_rps.log.assert_has_calls(calls)
