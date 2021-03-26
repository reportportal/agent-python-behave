from logging import Logger

from delayed_assert import assert_expectations, expect
from mock import Mock, patch

from behave_reportportal.logger import RPHandler, RPLogger


@patch.object(Logger, "_log")
def test_log(mock_log):
    rp_log = RPLogger("name")
    mock_args = Mock()
    extra = {"a": "A"}
    rp_log._log(
        1,
        "msg",
        mock_args,
        extra=extra,
        file_to_attach="file",
        is_launch_log=True,
    )
    mock_log.assert_called_once_with(
        1,
        "msg",
        mock_args,
        None,
        {"a": "A", "file_to_attach": "file", "is_launch_log": True},
        False,
        1,
    )


@patch.object(Logger, "makeRecord")
def test_make_record(mock_make_record):
    rp_log = RPLogger("name")
    mock_fn, mock_lno, mock_args, mock_exc = Mock(), Mock(), Mock(), Mock()
    extra = {"a": "A", "file_to_attach": "file", "is_launch_log": True}
    record = rp_log.makeRecord(
        "name", 1, mock_fn, mock_lno, "msg", mock_args, mock_exc, extra=extra
    )
    mock_make_record.assert_called_once_with(
        "name",
        1,
        mock_fn,
        mock_lno,
        "msg",
        mock_args,
        mock_exc,
        None,
        extra,
        None,
    )
    expect(
        getattr(record, "file_to_attach", None) == "file",
        "'file_to_attach' field is not set properly",
    )
    expect(
        getattr(record, "is_launch_log", None) is True,
        "'is_launch_log' field is not set properly",
    )
    assert_expectations()


@patch.object(RPHandler, "format")
def test_emit_for_launch(mock_format):
    mock_format.return_value = "msg"
    mock_rp, mock_record = Mock(), Mock()
    mock_record.is_launch_log = True
    mock_record.levelname = "INFO"
    mock_record.file_to_attach = "file"
    RPHandler(mock_rp).emit(mock_record)
    mock_rp.post_launch_log.assert_called_once_with(
        "msg", "INFO", file_to_attach="file"
    )


@patch.object(RPHandler, "format")
def test_emit(mock_format):
    mock_format.return_value = "msg"
    mock_rp, mock_record = Mock(), Mock()
    mock_record.is_launch_log = False
    mock_record.levelname = "INFO"
    mock_record.file_to_attach = "file"
    RPHandler(mock_rp).emit(mock_record)
    mock_rp.post_log.assert_called_once_with(
        "msg", "INFO", file_to_attach="file"
    )
