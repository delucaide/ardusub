import math

import pytest

from ardusub import Mode, MotorController


def test_slew_limit_applies_uniformly_across_modes():
    controller = MotorController(motor_count=4)
    dt = 0.1
    target = [1.0, -1.0, 0.5, -0.5]

    # Run through all modes to confirm the ramp behaviour is identical.
    outputs = {}
    for mode in Mode:
        controller.reset()
        outputs[mode] = controller.run_mode(mode, target, dt)

    first = next(iter(outputs.values()))
    for other in outputs.values():
        assert other == pytest.approx(first)


def test_slew_limit_bounds_motor_delta():
    controller = MotorController(motor_count=2)
    controller.reset()
    dt = 0.05
    max_step = controller.slew_limit * dt

    out = controller.run_mode(Mode.MANUAL, [1.0, -1.0], dt)
    assert out[0] == pytest.approx(max_step)
    assert out[1] == pytest.approx(-max_step)


def test_runtime_slew_limit_update():
    controller = MotorController(motor_count=1)
    controller.reset()
    dt = 0.1

    controller.set_slew_limit(2.0)
    assert math.isclose(controller.slew_limit, 2.0)
    max_step = controller.slew_limit * dt
    out = controller.run_mode(Mode.AUTO, [1.0], dt)
    assert out[0] == pytest.approx(max_step)

    controller.set_slew_limit(0.2)
    max_step = controller.slew_limit * dt
    previous = controller.outputs()[0]
    out = controller.run_mode(Mode.AUTO, [1.0], dt)
    assert out[0] == pytest.approx(previous + max_step)
