"""Minimal models for the ``autogen_core`` stub package."""

from enum import Enum


class ModelFamily(str, Enum):
    """Enumeration of model families.

    Only the members required by the tests are implemented.
    """

    UNKNOWN = "unknown"


__all__ = ["ModelFamily"]

