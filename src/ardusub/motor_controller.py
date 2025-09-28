"""Motor controller with configurable slew limiting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

from .modes import Mode
from .parameters import Parameter, ParameterStore

DEFAULT_SLEW_LIMIT = 0.5
"""Default slew limit in normalised thrust units per second."""

MIN_SLEW_LIMIT = 0.01
MAX_SLEW_LIMIT = 5.0


@dataclass
class MotorController:
    """Simplified representation of ArduSub motor mixing with slew limiting.

    The controller keeps track of the most recent motor outputs and ensures
    that updates transition toward the requested targets at a rate limited by
    the ``SLEW_LIMIT`` parameter.  This mimics the firmware behaviour where a
    slew-limited ramp helps avoid overshoot and abrupt torque changes.
    """

    motor_count: int
    parameters: ParameterStore = field(default_factory=ParameterStore)
    _outputs: List[float] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        if self.motor_count <= 0:
            raise ValueError("motor_count must be positive")
        self._outputs = [0.0] * self.motor_count
        self.parameters.register(
            Parameter(
                name="SLEW_LIMIT",
                value=DEFAULT_SLEW_LIMIT,
                minimum=MIN_SLEW_LIMIT,
                maximum=MAX_SLEW_LIMIT,
                on_change=self._on_slew_limit_change,
            )
        )
        self._slew_limit = DEFAULT_SLEW_LIMIT

    # ------------------------------------------------------------------
    # Parameter handling
    # ------------------------------------------------------------------
    def _on_slew_limit_change(self, value: float) -> None:
        self._slew_limit = value

    @property
    def slew_limit(self) -> float:
        return self._slew_limit

    def set_slew_limit(self, value: float) -> None:
        """Public helper to update the slew limit."""

        self.parameters.set_value("SLEW_LIMIT", value)

    # ------------------------------------------------------------------
    # Motor command processing
    # ------------------------------------------------------------------
    def outputs(self) -> Sequence[float]:
        """Return the current motor outputs."""

        return tuple(self._outputs)

    def reset(self) -> None:
        """Reset motor outputs to zero."""

        for i in range(self.motor_count):
            self._outputs[i] = 0.0

    def run_mode(self, mode: Mode, targets: Iterable[float], dt: float) -> Sequence[float]:
        """Apply the slew limited ramp for the provided mode.

        The real firmware performs mode-specific control mixing before the
        slew limiting stage.  Here we only model the smoothing behaviour to
        demonstrate that the ramp is applied consistently across all modes.
        """

        del mode  # In this simplified model the mode does not alter the ramp.
        return self._apply_slew(targets, dt)

    def _apply_slew(self, targets: Iterable[float], dt: float) -> Sequence[float]:
        """Internal helper performing slew limiting."""

        target_list = list(targets)
        if len(target_list) != self.motor_count:
            raise ValueError("target count must match motor_count")
        if dt <= 0:
            raise ValueError("dt must be positive")

        max_delta = self._slew_limit * dt
        for i, target in enumerate(target_list):
            target = _saturate(target)
            current = self._outputs[i]
            delta = target - current
            if delta > max_delta:
                delta = max_delta
            elif delta < -max_delta:
                delta = -max_delta
            self._outputs[i] = _saturate(current + delta)
        return self.outputs()


def _saturate(value: float) -> float:
    """Clamp motor outputs to the valid [-1, 1] range."""

    return max(-1.0, min(1.0, value))
