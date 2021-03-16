from behave.userdata import UserData
from delayed_assert import assert_expectations, expect

from behave_reportportal.config import (
    DEFAULT_CFG_FILE,
    RP_CFG_SECTION,
    read_config,
)


try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


@patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_config_with_specified_path(mock_cp):
    mock_cp().sections().__contains__.return_value = False
    mock_context = Mock()
    mock_context._config.userdata = UserData.make(
        {
            "config_file": "some_path",
            "endpoint": "endpoint",
            "project": "project",
            "token": "token",
        }
    )
    cfg = read_config(mock_context)
    expect(mock_cp().read.call_count == 1)
    expect(mock_cp().read.call_args[0][0] == "some_path")
    expect(mock_cp().sections.called)
    expect(mock_cp().sections().__contains__.call_count == 1)
    expect(mock_cp().sections().__contains__.call_args[0][0] == RP_CFG_SECTION)
    expect(cfg.endpoint == "endpoint")
    expect(cfg.token == "token")
    expect(cfg.project == "project")
    expect(cfg.enabled)
    assert_expectations()


@patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_invalid_config_file(mock_cp):
    mock_cp().sections().__contains__.return_value = False
    mock_context = Mock()
    mock_context._config.userdata = UserData.make({})
    cfg = read_config(mock_context)
    expect(mock_cp().read.call_count == 1)
    expect(mock_cp().read.call_args[0][0] == DEFAULT_CFG_FILE)
    expect(mock_cp().sections.called)
    expect(mock_cp().sections().__contains__.call_count == 1)
    expect(mock_cp().sections().__contains__.call_args[0][0] == RP_CFG_SECTION)
    expect(not cfg.enabled)
    assert_expectations()
