"""Module contains utility functions."""
from time import time

from pkg_resources import DistributionNotFound, get_distribution


def timestamp():
    """Return current time."""
    return str(int(time() * 1000))


def get_package_version(package_name):
    """Get version of the given package.

    :param package_name: Name of the package
    :return:             Version of the package
    """
    try:
        package_version = get_distribution(package_name).version
    except DistributionNotFound:
        package_version = "not found"
    return package_version
