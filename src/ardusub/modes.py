"""Operating modes for the simplified ArduSub model.

This is not a complete representation of the real firmware but provides
just enough structure to showcase how the new slew limiting parameter is
applied in every mode.
"""

from __future__ import annotations

from enum import Enum, auto


class Mode(Enum):
    """Minimal selection of vehicle modes.

    The real firmware contains many more modes, but the limiter applies to
    all of them so this small subset is sufficient for documentation and
    testing purposes.
    """

    STABILIZE = auto()
    DEPTH_HOLD = auto()
    MANUAL = auto()
    AUTO = auto()


ALL_MODES = tuple(Mode)
"""Convenience tuple for iterating over every available mode."""
