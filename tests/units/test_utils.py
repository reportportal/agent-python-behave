from pkg_resources import DistributionNotFound

from behave_reportportal.utils import get_package_version, timestamp


try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


@patch("behave_reportportal.utils.time")
def test_timestamp(mock_time):
    mock_time.return_value = 123
    actual = timestamp()
    assert (
        actual == "123000"
    ), "Incorrect timestamp returned:\nActual: {}\nExpected: {}".format(
        actual, "123000"
    )


@patch("behave_reportportal.utils.get_distribution")
def test_get_package_version(mock_get_distribution):
    mock_dist = Mock()
    mock_dist.version = "123"
    mock_get_distribution.return_value = mock_dist
    actual = get_package_version("package_name")
    assert (
        actual == "123"
    ), "Incorrect version\nActual: {}\nExpected:{}".format(actual, "123")


@patch("behave_reportportal.utils.get_distribution")
def test_get_package_version_unknown_version(mock_get_distribution):
    mock_get_distribution.side_effect = DistributionNotFound
    actual = get_package_version("package_name")
    assert (
        actual == "not found"
    ), "Incorrect version\nActual: {}\nExpected:{}".format(actual, "123")
