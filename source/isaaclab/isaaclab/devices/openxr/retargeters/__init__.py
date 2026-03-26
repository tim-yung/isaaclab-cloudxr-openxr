# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
"""Retargeters for mapping input device data to robot commands."""

from __future__ import annotations

import importlib
from typing import Any, Final

from .manipulator.gripper_retargeter import GripperRetargeter, GripperRetargeterCfg
from .manipulator.se3_abs_retargeter import Se3AbsRetargeter, Se3AbsRetargeterCfg
from .manipulator.se3_rel_retargeter import Se3RelRetargeter, Se3RelRetargeterCfg

# Humanoid retargeters pull optional deps (e.g. pinocchio / dex_retargeting). Load them only when
# accessed so Franka OpenXR teleop does not require those stacks or NumPy 1.x-built wheels.
_LAZY_IMPORTS: Final[dict[str, tuple[str, str]]] = {
    "GR1T2Retargeter": ("isaaclab.devices.openxr.retargeters.humanoid.fourier.gr1t2_retargeter", "GR1T2Retargeter"),
    "GR1T2RetargeterCfg": ("isaaclab.devices.openxr.retargeters.humanoid.fourier.gr1t2_retargeter", "GR1T2RetargeterCfg"),
    "G1LowerBodyStandingRetargeter": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.g1_lower_body_standing",
        "G1LowerBodyStandingRetargeter",
    ),
    "G1LowerBodyStandingRetargeterCfg": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.g1_lower_body_standing",
        "G1LowerBodyStandingRetargeterCfg",
    ),
    "G1LowerBodyStandingMotionControllerRetargeter": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.g1_motion_controller_locomotion",
        "G1LowerBodyStandingMotionControllerRetargeter",
    ),
    "G1LowerBodyStandingMotionControllerRetargeterCfg": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.g1_motion_controller_locomotion",
        "G1LowerBodyStandingMotionControllerRetargeterCfg",
    ),
    "UnitreeG1Retargeter": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.inspire.g1_upper_body_retargeter",
        "UnitreeG1Retargeter",
    ),
    "UnitreeG1RetargeterCfg": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.inspire.g1_upper_body_retargeter",
        "UnitreeG1RetargeterCfg",
    ),
    "G1TriHandUpperBodyMotionControllerGripperRetargeter": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.trihand.g1_upper_body_motion_ctrl_gripper",
        "G1TriHandUpperBodyMotionControllerGripperRetargeter",
    ),
    "G1TriHandUpperBodyMotionControllerGripperRetargeterCfg": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.trihand.g1_upper_body_motion_ctrl_gripper",
        "G1TriHandUpperBodyMotionControllerGripperRetargeterCfg",
    ),
    "G1TriHandUpperBodyMotionControllerRetargeter": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.trihand.g1_upper_body_motion_ctrl_retargeter",
        "G1TriHandUpperBodyMotionControllerRetargeter",
    ),
    "G1TriHandUpperBodyMotionControllerRetargeterCfg": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.trihand.g1_upper_body_motion_ctrl_retargeter",
        "G1TriHandUpperBodyMotionControllerRetargeterCfg",
    ),
    "G1TriHandUpperBodyRetargeter": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.trihand.g1_upper_body_retargeter",
        "G1TriHandUpperBodyRetargeter",
    ),
    "G1TriHandUpperBodyRetargeterCfg": (
        "isaaclab.devices.openxr.retargeters.humanoid.unitree.trihand.g1_upper_body_retargeter",
        "G1TriHandUpperBodyRetargeterCfg",
    ),
}

__all__ = [
    "GripperRetargeter",
    "GripperRetargeterCfg",
    "Se3AbsRetargeter",
    "Se3AbsRetargeterCfg",
    "Se3RelRetargeter",
    "Se3RelRetargeterCfg",
    *_LAZY_IMPORTS.keys(),
]


def __getattr__(name: str) -> Any:
    spec = _LAZY_IMPORTS.get(name)
    if spec is None:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    module_name, attr_name = spec
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)
