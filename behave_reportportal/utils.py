"""Module contains utility functions."""
from time import time


class Singleton(type):
    """Implementation of Singleton pattern."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Redefine call method."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]


def timestamp():
    """Return current time."""
    return str(int(time() * 1000))
