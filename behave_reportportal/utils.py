"""Module contains utility functions."""
from time import time


def timestamp():
    """Return current time."""
    return str(int(time() * 1000))
