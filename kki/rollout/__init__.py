"""Rollout boundary for controlled promotion and activation paths."""

from kki.module_boundaries import ModuleBoundary, module_boundary
from kki.rollout.state_machine import RolloutPhase, RolloutState, advance_rollout_state, rollout_state_for_shadow

BOUNDARY: ModuleBoundary = module_boundary("rollout")

__all__ = [
    "BOUNDARY",
    "RolloutPhase",
    "RolloutState",
    "advance_rollout_state",
    "rollout_state_for_shadow",
]
