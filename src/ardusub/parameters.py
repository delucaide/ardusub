"""Runtime parameters for the simplified ArduSub motor controller."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict


@dataclass
class Parameter:
    """Metadata container for a runtime tunable parameter."""

    name: str
    value: float
    minimum: float
    maximum: float
    on_change: Callable[[float], None]

    def set(self, new_value: float) -> None:
        """Update the parameter value and trigger callbacks."""

        clamped = min(max(new_value, self.minimum), self.maximum)
        self.value = clamped
        self.on_change(clamped)


class ParameterStore:
    """Registry for tunable parameters.

    Only the ``SLEW_LIMIT`` parameter is currently modelled but the class is
    flexible enough to be extended with additional parameters if needed.
    """

    def __init__(self) -> None:
        self._parameters: Dict[str, Parameter] = {}

    def register(self, parameter: Parameter) -> None:
        """Add a new parameter to the store."""

        self._parameters[parameter.name] = parameter

    def set_value(self, name: str, value: float) -> None:
        """Update a parameter by name."""

        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        self._parameters[name].set(value)

    def get_value(self, name: str) -> float:
        """Retrieve the current value of a parameter."""

        if name not in self._parameters:
            raise KeyError(f"Unknown parameter: {name}")
        return self._parameters[name].value

    def __contains__(self, name: str) -> bool:  # pragma: no cover - trivial
        return name in self._parameters

    def items(self):  # pragma: no cover - convenience wrapper
        return self._parameters.items()
