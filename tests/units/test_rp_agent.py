import pytest
from delayed_assert import assert_expectations, expect
from reportportal_client import ReportPortalService
from six.moves import mock

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
    [("passed", "PASSED"), ("skipped", "SKIPPED"), ("failed", "FAILED")],
)
def test_convert_to_rp_status(status, expected):
    actual = BehaveAgent.convert_to_rp_status(status)
    assert (
        actual == expected
    ), "Incorrect status:\nActual: {}\nExpected:{}".format(actual, expected)


def test_tags():
    mock_item = mock.Mock()
    mock_item.tags = None
    expect(BehaveAgent._tags(mock_item) is None, "Tags is not None")
    mock_item.tags = ["a", "b"]
    expect(
        BehaveAgent._tags(mock_item) == [{"value": "a"}, {"value": "b"}],
        "Tags are incorrect:\nActual: {}\nExpected: {}".format(
            BehaveAgent._tags(mock_item), [{"value": "a"}, {"value": "b"}]
        ),
    )
    assert_expectations()


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
        attributes=BehaveAgent._tags(mock_feature),
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
        attributes=BehaveAgent._tags(mock_scenario),
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
    ba = BehaveAgent(config, mock_rps)
    ba._scenario_id = "scenario_id"
    ba.finish_scenario(mock_context, mock_scenario, some_key="some_value")
    mock_rps.finish_test_item.assert_called_once_with(
        item_id="scenario_id",
        end_time=123,
        status=expected_status,
        some_key="some_value",
    )


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
    mock_step.exception.args = ["Error message"]
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
    mock_rps.log.assert_called_once_with(
        item_id="step_id",
        time=123,
        level="ERROR",
        message="Step [keyword]: name was finished with "
        "exception:\nError message",
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
    mock_step.exception.args = ["Error message"]
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
            message="Step [keyword]: name was finished with "
            "exception:\nError message",
        ),
        mock.call(
            item_id="scenario_id",
            time=123,
            level="INFO",
            message="[keyword]: name. ",
        ),
    ]
    mock_rps.log.assert_has_calls(calls, any_order=True)


def test_log_exception_without_message():
    mock_step = mock.Mock()
    mock_step.exception = None
    mock_rps = mock.create_autospec(ReportPortalService)
    ba = BehaveAgent(config, mock_rps)
    ba._log_step_exception(mock_step, "step_id")
    mock_rps.log.assert_not_called()
