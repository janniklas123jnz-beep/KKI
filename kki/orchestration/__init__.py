"""Orchestration boundary for budget, state, and triage coordination."""

from kki.module_boundaries import ModuleBoundary, module_boundary

from .runtime_state import (
    GateReadiness,
    GateState,
    OperationalPressure,
    OrchestrationState,
    OrchestrationStatus,
    PressureLevel,
    advance_orchestration_state,
    orchestration_state_for_runtime,
)
from .work_units import (
    ClaimStatus,
    HandoffMode,
    WorkClaim,
    WorkCostProfile,
    WorkHandoff,
    WorkPriority,
    WorkStatus,
    WorkUnit,
    advance_work_unit,
    claim_for_work_unit,
    handoff_for_work_unit,
    work_unit_for_state,
)

BOUNDARY: ModuleBoundary = module_boundary("orchestration")

__all__ = [
    "BOUNDARY",
    "GateReadiness",
    "GateState",
    "OperationalPressure",
    "OrchestrationState",
    "OrchestrationStatus",
    "PressureLevel",
    "ClaimStatus",
    "HandoffMode",
    "WorkClaim",
    "WorkCostProfile",
    "WorkHandoff",
    "WorkPriority",
    "WorkStatus",
    "WorkUnit",
    "advance_orchestration_state",
    "advance_work_unit",
    "claim_for_work_unit",
    "handoff_for_work_unit",
    "orchestration_state_for_runtime",
    "work_unit_for_state",
]
