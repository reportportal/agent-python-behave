from behave_reportportal.utils import timestamp


try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


@patch("behave_reportportal.utils.time")
def test_timestamp(mock_time):
    mock_time.return_value = 123
    actual = timestamp()
    assert (
        actual == "123000"
    ), "Incorrect timestamp returned:\nActual: {}\nExpected: {}".format(
        actual, "123000"
    )
