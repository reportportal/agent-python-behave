import mock
import pytest
from behave.userdata import UserData
from delayed_assert import assert_expectations, expect

from behave_reportportal.config import (
    DEFAULT_CFG_FILE,
    RP_CFG_SECTION,
    read_config,
)


@pytest.mark.parametrize(
    "cmd_args,path",
    [({"config_file": "some_path"}, "some_path"), (None, DEFAULT_CFG_FILE)],
)
@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_config_file_path(mock_cp, cmd_args, path):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make(cmd_args)
    read_config(mock_context)
    expect(mock_cp().read.call_count == 1)
    expect(mock_cp().read.call_args[0][0] == path)
    expect(mock_cp().has_section.call_count == 1)
    expect(mock_cp().has_section.call_args[0][0] == RP_CFG_SECTION)
    assert_expectations()


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_from_file(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().has_section.return_value = True
    mock_content = mock.Mock()
    mock_content.get.return_value = "some data"
    mock_content.getboolean.return_value = True
    mock_cp().__getitem__.return_value = mock_content
    cfg = read_config(mock_context)
    expect(cfg.endpoint == "some data")
    expect(cfg.token == "some data")
    expect(cfg.project == "some data")
    expect(cfg.launch_name == "some data")
    expect(cfg.step_based)
    expect(cfg.is_skipped_an_issue)
    expect(cfg.launch_attributes == ["some", "data"])
    expect(cfg.launch_description == "some data")
    expect(cfg.enabled)
    assert_expectations()


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_config_override_from_cmd(mock_cp):
    mock_cp().sections().__contains__.return_value = False
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make(
        {
            "config_file": "some_path",
            "endpoint": "endpoint",
            "project": "project",
            "token": "token",
            "launch_name": "launch_name",
            "launch_attributes": "A B C",
            "launch_description": "launch_description",
            "step_based": "True",
            "is_skipped_an_issue": "False",
        }
    )
    mock_cp().has_section.return_value = True
    mock_content = mock.Mock()
    mock_content.get.return_value = "some data"
    mock_content.getboolean.return_value = True
    mock_cp().__getitem__.return_value = mock_content
    cfg = read_config(mock_context)
    expect(cfg.endpoint == "endpoint")
    expect(cfg.token == "token")
    expect(cfg.project == "project")
    expect(cfg.launch_name == "launch_name")
    expect(cfg.step_based)
    expect(cfg.launch_attributes == ["A", "B", "C"])
    expect(cfg.launch_description == "launch_description")
    expect(not cfg.is_skipped_an_issue)
    expect(cfg.enabled)
    assert_expectations()
