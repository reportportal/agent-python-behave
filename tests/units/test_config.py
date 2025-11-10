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

import warnings
from unittest import mock

# noinspection PyPackageRequirements
import pytest
from behave.userdata import UserData
from delayed_assert import assert_expectations, expect
from reportportal_client import ClientType, OutputType

from behave_reportportal.config import DEFAULT_CFG_FILE, DEFAULT_LAUNCH_NAME, RP_CFG_SECTION, LogLayout, read_config


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
    mock_cp().__getitem__.return_value = {
        "endpoint": "endpoint",
        "project": "project",
        "api_key": "api_key",
        "launch_name": "launch_name",
        "launch_description": "launch_description",
        "launch_attributes": "X Y Z",
        "debug_mode": "False",
        "log_layout": "Step",
        "is_skipped_an_issue": "True",
        "retries": "2",
        "rerun": "True",
        "rerun_of": "launch_id",
    }
    cfg = read_config(mock_context)
    expect(cfg.endpoint == "endpoint")
    expect(cfg.api_key == "api_key")
    expect(cfg.project == "project")
    expect(cfg.launch_name == "launch_name")
    expect(cfg.debug_mode is False)
    expect(cfg.log_layout is LogLayout.STEP)
    expect(cfg.is_skipped_an_issue is True)
    expect(cfg.launch_attributes == ["X", "Y", "Z"])
    expect(cfg.launch_description == "launch_description")
    expect(cfg.retries == 2)
    expect(cfg.rerun is True)
    expect(cfg.rerun_of == "launch_id")
    expect(cfg.enabled is True)
    assert_expectations()


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_config_from_cmd(mock_cp):
    mock_cp().has_section.return_value = False
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make(
        {
            "config_file": "some_path",
            "endpoint": "endpoint",
            "project": "project",
            "api_key": "api_key",
            "launch_name": "launch_name",
            "launch_attributes": "A B C",
            "launch_description": "launch_description",
            "debug_mode": "True",
            "log_layout": "Nested",
            "is_skipped_an_issue": "False",
            "retries": 3,
            "rerun": "True",
            "rerun_of": "launch_id",
        }
    )
    cfg = read_config(mock_context)
    expect(cfg.endpoint == "endpoint")
    expect(cfg.api_key == "api_key")
    expect(cfg.project == "project")
    expect(cfg.launch_name == "launch_name")
    expect(cfg.debug_mode is True)
    expect(cfg.log_layout is LogLayout.NESTED)
    expect(cfg.launch_attributes == ["A", "B", "C"])
    expect(cfg.launch_description == "launch_description")
    expect(cfg.is_skipped_an_issue is False)
    expect(cfg.retries == 3)
    expect(cfg.rerun is True)
    expect(cfg.rerun_of == "launch_id")
    expect(cfg.enabled is True)
    assert_expectations()


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_config_override_from_cmd(mock_cp):
    mock_cp().has_section.return_value = True
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make(
        {
            "config_file": "some_path",
            "endpoint": "endpoint",
            "project": "project",
            "api_key": "api_key",
            "launch_name": "launch_name",
            "launch_attributes": "A B C",
            "launch_description": "launch_description",
            "debug_mode": "True",
            "log_layout": "Nested",
            "is_skipped_an_issue": "False",
            "retries": 3,
            "rerun": "False",
            "rerun_of": "rerun_launch_id",
        }
    )
    mock_cp().__getitem__.return_value = {
        "endpoint": "endpoint",
        "project": "project",
        "api_key": "api_key",
        "launch_name": "launch_name",
        "launch_description": "launch_description",
        "launch_attributes": "X Y Z",
        "debug_mode": "False",
        "log_layout": "Step",
        "is_skipped_an_issue": "True",
        "retries": "2",
        "rerun": "True",
        "rerun_of": "launch_id",
    }
    cfg = read_config(mock_context)
    expect(cfg.endpoint == "endpoint")
    expect(cfg.api_key == "api_key")
    expect(cfg.project == "project")
    expect(cfg.launch_name == "launch_name")
    expect(cfg.debug_mode is True)
    expect(cfg.log_layout is LogLayout.NESTED)
    expect(cfg.launch_attributes == ["A", "B", "C"])
    expect(cfg.launch_description == "launch_description")
    expect(cfg.is_skipped_an_issue is False)
    expect(cfg.retries == 3)
    expect(cfg.rerun is False)
    expect(cfg.rerun_of == "rerun_launch_id")
    expect(cfg.enabled is True)
    assert_expectations()


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_read_config_default_values(mock_cp):
    mock_cp().has_section.return_value = False
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    cfg = read_config(mock_context)
    expect(cfg.endpoint is None)
    expect(cfg.api_key is None)
    expect(cfg.project is None)
    expect(cfg.launch_name == DEFAULT_LAUNCH_NAME)
    expect(cfg.debug_mode is False)
    expect(cfg.log_layout is LogLayout.SCENARIO)
    expect(cfg.launch_attributes is None)
    expect(cfg.launch_description is None)
    expect(cfg.is_skipped_an_issue is False)
    expect(cfg.retries is None)
    expect(cfg.rerun is False)
    expect(cfg.rerun_of is None)
    expect(cfg.enabled is True)
    expect(cfg.launch_uuid_print is False)
    expect(cfg.launch_uuid_print_output is None)
    expect(cfg.client_type is ClientType.SYNC)
    assert_expectations()


@pytest.mark.parametrize(
    "val,exp",
    [
        ("step", LogLayout.STEP),
        ("STEP", LogLayout.STEP),
        ("Step", LogLayout.STEP),
        (None, LogLayout.SCENARIO),
        (2, LogLayout.NESTED),
        (0, LogLayout.SCENARIO),
    ],
)
def test_log_layout_parse(val, exp):
    assert LogLayout(val) == exp


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_deprecated_step_based(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {"step_based": "True", "api_key": "api_key"}

    with warnings.catch_warnings(record=True) as w:
        cfg = read_config(mock_context)
        assert cfg.log_layout is LogLayout.STEP
        assert len(w) == 1


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_empty_api_key(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {
        "api_key": "",
        "endpoint": "endpoint",
        "project": "project",
        "launch_name": "launch_name",
    }

    cfg = read_config(mock_context)
    assert cfg.api_key == ""
    assert cfg.enabled is True


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_launch_uuid_print(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {
        "api_key": "api_key",
        "endpoint": "endpoint",
        "project": "project",
        "launch_name": "launch_name",
        "launch_uuid_print": "True",
    }

    cfg = read_config(mock_context)
    assert cfg.launch_uuid_print
    assert cfg.launch_uuid_print_output is None


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_launch_uuid_print_stderr(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {
        "api_key": "api_key",
        "endpoint": "endpoint",
        "project": "project",
        "launch_name": "launch_name",
        "launch_uuid_print": "True",
        "launch_uuid_print_output": "stderr",
    }

    cfg = read_config(mock_context)
    assert cfg.launch_uuid_print
    assert cfg.launch_uuid_print_output is OutputType.STDERR


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_launch_uuid_print_invalid_output(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {
        "api_key": "api_key",
        "endpoint": "endpoint",
        "project": "project",
        "launch_name": "launch_name",
        "launch_uuid_print": "True",
        "launch_uuid_print_output": "something",
    }
    with pytest.raises(KeyError):
        read_config(mock_context)


@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_no_launch_uuid_print(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {
        "api_key": "api_key",
        "endpoint": "endpoint",
        "project": "project",
        "launch_name": "launch_name",
    }

    cfg = read_config(mock_context)
    assert not cfg.launch_uuid_print
    assert cfg.launch_uuid_print_output is None


@pytest.mark.parametrize(
    "connect_value, read_value, expected_result",
    [("5", "15", (5.0, 15.0)), ("5.5", "15.5", (5.5, 15.5)), (None, None, None), (None, "5", 5), ("5", None, 5)],
)
@mock.patch("behave_reportportal.config.ConfigParser", autospec=True)
def test_client_timeouts(mock_cp, connect_value, read_value, expected_result):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({"config_file": "some_path"})
    mock_cp().__getitem__.return_value = {
        "api_key": "api_key",
        "endpoint": "endpoint",
        "project": "project",
        "launch_name": "launch_name",
        "connect_timeout": connect_value,
        "read_timeout": read_value,
    }

    cfg = read_config(mock_context)
    assert cfg.http_timeout == expected_result
