"""This package contains Behave agent's code for the Report Portal."""

from six import MovedModule, add_move


add_move(MovedModule("mock", "mock", "unittest.mock"))
