import warnings
from unittest import mock

# noinspection PyPackageRequirements
import pytest
from behave.userdata import UserData
from delayed_assert import assert_expectations, expect

from behave_reportportal.config import (DEFAULT_CFG_FILE, DEFAULT_LAUNCH_NAME,
                                        RP_CFG_SECTION, LogLayout, get_bool,
                                        read_config)


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
    expect(cfg.enabled is False)
    assert_expectations()


@pytest.mark.parametrize(
    "val,exp",
    [
        ('True', True),
        ('true', True),
        ('False', False),
        ('false', False),
        (True, True),
        (False, False),
        (None, None),
        ('other_value', None),
    ],
)
def test_get_bool(val, exp):
    act = get_bool(val)
    assert act == exp, f'Actual:{act}\nExpected: {exp}'


@pytest.mark.parametrize(
    'val,exp',
    [
        ('step', LogLayout.STEP),
        ('STEP', LogLayout.STEP),
        ('Step', LogLayout.STEP),
        (None, LogLayout.SCENARIO),
        (2, LogLayout.NESTED),
        (0, LogLayout.SCENARIO),
    ],
)
def test_log_layout_parse(val, exp):
    assert LogLayout(val) == exp


@mock.patch('behave_reportportal.config.ConfigParser', autospec=True)
def test_deprecated_step_based(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({'config_file': 'some_path'})
    mock_cp().__getitem__.return_value = {
        'step_based': 'True',
        'api_key': 'api_key'
    }

    with warnings.catch_warnings(record=True) as w:
        cfg = read_config(mock_context)
        assert cfg.log_layout is LogLayout.STEP
        assert len(w) == 1


@mock.patch('behave_reportportal.config.ConfigParser', autospec=True)
def test_deprecated_token_param(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({'config_file': 'some_path'})
    mock_cp().__getitem__.return_value = {
        'token': 'api_key',
        'endpoint': 'endpoint',
        'project': 'project',
        'launch_name': 'launch_name'
    }

    with warnings.catch_warnings(record=True) as w:
        cfg = read_config(mock_context)
        assert cfg.api_key == 'api_key'
        assert len(w) == 1


@mock.patch('behave_reportportal.config.ConfigParser', autospec=True)
def test_api_key_token_param_priority(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({'config_file': 'some_path'})
    mock_cp().__getitem__.return_value = {
        'api_key': 'api_key',
        'token': 'token',
        'endpoint': 'endpoint',
        'project': 'project',
        'launch_name': 'launch_name'
    }

    with warnings.catch_warnings(record=True) as w:
        cfg = read_config(mock_context)
        assert cfg.api_key == 'api_key'
        assert len(w) == 0


@mock.patch('behave_reportportal.config.ConfigParser', autospec=True)
def test_empty_api_key(mock_cp):
    mock_context = mock.Mock()
    mock_context._config.userdata = UserData.make({'config_file': 'some_path'})
    mock_cp().__getitem__.return_value = {
        'api_key': '',
        'endpoint': 'endpoint',
        'project': 'project',
        'launch_name': 'launch_name'
    }

    with warnings.catch_warnings(record=True) as w:
        cfg = read_config(mock_context)
        assert cfg.api_key == ''
        assert cfg.enabled is False
        assert len(w) == 1
