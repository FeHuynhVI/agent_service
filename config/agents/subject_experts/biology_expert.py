"""
Alias module for the Biology expert agent.

This file exists to provide a more conventional module name for the
``BiologyExpertAgent`` class, which is defined in
``bology_expert.py`` (note the historical misspelling).  Importing
``BiologyExpertAgent`` from ``biology_expert`` simply re‑exports the
class from the original module.  This alias helps maintain backward
compatibility while allowing users to import from a correctly spelled
module name.
"""

from __future__ import annotations

# Re-export the BiologyExpertAgent from the original module
from biology_expert import BiologyExpertAgent  # noqa: F401

__all__ = ["BiologyExpertAgent"]