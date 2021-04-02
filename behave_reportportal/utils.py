"""Module contains utility functions."""


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
