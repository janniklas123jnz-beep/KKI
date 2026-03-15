"""Remediation campaigns derived from coordinated improvement waves."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .data_models import EvidenceRecord
from .improvement_orchestrator import (
    ImprovementExecutionMode,
    ImprovementOrchestrator,
    ImprovementWave,
    build_improvement_orchestrator,
)
from .module_boundaries import ModuleBoundaryName
from .telemetry import TelemetrySignal, TelemetrySnapshot, build_telemetry_snapshot


def _non_empty(value: str, *, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def _ordered_union(*groups: tuple[str, ...]) -> tuple[str, ...]:
    ordered: list[str] = []
    for group in groups:
        for item in group:
            if item not in ordered:
                ordered.append(item)
    return tuple(ordered)


class RemediationCampaignStatus(str, Enum):
    """Canonical remediation states over campaign stages."""

    READY = "ready"
    GUARDED = "guarded"
    RECOVERY_ONLY = "recovery-only"
    BLOCKED = "blocked"


class RemediationCampaignStageType(str, Enum):
    """Canonical stage types inside a remediation campaign."""

    EVIDENCE_PACK = "evidence-pack"
    GOVERNANCE_APPROVAL = "governance-approval"
    REMEDIATION_WAVE = "remediation-wave"
    RECOVERY_SAFEGUARD = "recovery-safeguard"
    CONTAINMENT = "containment"


@dataclass(frozen=True)
class RemediationCampaignStage:
    """Concrete remediation stage derived from one improvement wave."""

    stage_id: str
    wave_id: str
    case_id: str
    stage_type: RemediationCampaignStageType
    status: RemediationCampaignStatus
    owner: ModuleBoundaryName
    action_refs: tuple[str, ...]
    evidence_records: tuple[EvidenceRecord, ...]
    commitment_refs: tuple[str, ...]
    governance_refs: tuple[str, ...] = ()
    safeguard_refs: tuple[str, ...] = ()
    blocked_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_id", _non_empty(self.stage_id, field_name="stage_id"))
        object.__setattr__(self, "wave_id", _non_empty(self.wave_id, field_name="wave_id"))
        object.__setattr__(self, "case_id", _non_empty(self.case_id, field_name="case_id"))

    def to_dict(self) -> dict[str, object]:
        return {
            "stage_id": self.stage_id,
            "wave_id": self.wave_id,
            "case_id": self.case_id,
            "stage_type": self.stage_type.value,
            "status": self.status.value,
            "owner": self.owner.value,
            "action_refs": list(self.action_refs),
            "evidence_records": [record.to_dict() for record in self.evidence_records],
            "commitment_refs": list(self.commitment_refs),
            "governance_refs": list(self.governance_refs),
            "safeguard_refs": list(self.safeguard_refs),
            "blocked_refs": list(self.blocked_refs),
        }


@dataclass(frozen=True)
class RemediationCampaign:
    """Coordinated remediation campaign over one or more improvement waves."""

    campaign_id: str
    orchestrator: ImprovementOrchestrator
    stages: tuple[RemediationCampaignStage, ...]
    campaign_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "campaign_id", _non_empty(self.campaign_id, field_name="campaign_id"))

    @property
    def status(self) -> RemediationCampaignStatus:
        return RemediationCampaignStatus(self.campaign_signal.status)

    @property
    def commitment_refs(self) -> tuple[str, ...]:
        return _ordered_union(*(stage.commitment_refs for stage in self.stages))

    @property
    def evidence_records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(record for stage in self.stages for record in stage.evidence_records)

    @property
    def governance_case_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                stage.case_id for stage in self.stages if stage.stage_type is RemediationCampaignStageType.GOVERNANCE_APPROVAL
            )
        )

    @property
    def recovery_case_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                stage.case_id for stage in self.stages if stage.stage_type is RemediationCampaignStageType.RECOVERY_SAFEGUARD
            )
        )

    @property
    def blocked_case_ids(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(stage.case_id for stage in self.stages if stage.stage_type is RemediationCampaignStageType.CONTAINMENT)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "campaign_id": self.campaign_id,
            "orchestrator": self.orchestrator.to_dict(),
            "stages": [stage.to_dict() for stage in self.stages],
            "campaign_signal": self.campaign_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "status": self.status.value,
            "commitment_refs": list(self.commitment_refs),
            "evidence_records": [record.to_dict() for record in self.evidence_records],
            "governance_case_ids": list(self.governance_case_ids),
            "recovery_case_ids": list(self.recovery_case_ids),
            "blocked_case_ids": list(self.blocked_case_ids),
        }


def _commitment_ref(campaign_id: str, wave: ImprovementWave, suffix: str) -> str:
    return f"commit-{campaign_id}-{wave.case_id}-{suffix}"


def _evidence_for_stage(
    *,
    campaign_id: str,
    wave: ImprovementWave,
    stage_type: RemediationCampaignStageType,
    commitment_ref: str,
) -> EvidenceRecord:
    return EvidenceRecord(
        evidence_type="remediation-campaign-stage",
        subject=wave.case_id,
        correlation_id=campaign_id,
        audit_ref=f"audit-{campaign_id}-{wave.wave_id}-{stage_type.value}",
        commitment_ref=commitment_ref,
        payload={
            "campaign_id": campaign_id,
            "wave_id": wave.wave_id,
            "case_id": wave.case_id,
            "stage_type": stage_type.value,
            "execution_mode": wave.execution_mode.value,
            "target_status": wave.target_status,
            "budget_share": wave.budget_share,
        },
    )


def _stage_for_wave(
    *,
    campaign_id: str,
    wave: ImprovementWave,
    stage_type: RemediationCampaignStageType,
    status: RemediationCampaignStatus,
    governance_refs: tuple[str, ...] = (),
    safeguard_refs: tuple[str, ...] = (),
    blocked_refs: tuple[str, ...] = (),
) -> RemediationCampaignStage:
    commitment_ref = _commitment_ref(campaign_id, wave, stage_type.value)
    return RemediationCampaignStage(
        stage_id=f"{campaign_id}-{wave.wave_id}-{stage_type.value}",
        wave_id=wave.wave_id,
        case_id=wave.case_id,
        stage_type=stage_type,
        status=status,
        owner=wave.owner,
        action_refs=wave.action_refs,
        evidence_records=(_evidence_for_stage(campaign_id=campaign_id, wave=wave, stage_type=stage_type, commitment_ref=commitment_ref),),
        commitment_refs=(commitment_ref,),
        governance_refs=governance_refs,
        safeguard_refs=safeguard_refs,
        blocked_refs=blocked_refs,
    )


def _status_for_wave(wave: ImprovementWave) -> RemediationCampaignStatus:
    if wave.execution_mode is ImprovementExecutionMode.CONTAINED:
        return RemediationCampaignStatus.BLOCKED
    if wave.execution_mode is ImprovementExecutionMode.RECOVERY:
        return RemediationCampaignStatus.RECOVERY_ONLY
    if wave.execution_mode is ImprovementExecutionMode.GOVERNED:
        return RemediationCampaignStatus.GUARDED
    return RemediationCampaignStatus.READY


def _stages_for_wave(campaign_id: str, wave: ImprovementWave) -> tuple[RemediationCampaignStage, ...]:
    stages = [
        _stage_for_wave(
            campaign_id=campaign_id,
            wave=wave,
            stage_type=RemediationCampaignStageType.EVIDENCE_PACK,
            status=_status_for_wave(wave),
            blocked_refs=(wave.case_id,) if wave.blocked_release else (),
        )
    ]
    if wave.execution_mode is ImprovementExecutionMode.GOVERNED:
        stages.append(
            _stage_for_wave(
                campaign_id=campaign_id,
                wave=wave,
                stage_type=RemediationCampaignStageType.GOVERNANCE_APPROVAL,
                status=RemediationCampaignStatus.GUARDED,
                governance_refs=wave.guardrail_refs or wave.action_refs or (wave.case_id,),
            )
        )
    if wave.execution_mode is ImprovementExecutionMode.RECOVERY:
        stages.append(
            _stage_for_wave(
                campaign_id=campaign_id,
                wave=wave,
                stage_type=RemediationCampaignStageType.RECOVERY_SAFEGUARD,
                status=RemediationCampaignStatus.RECOVERY_ONLY,
                safeguard_refs=wave.guardrail_refs or wave.risk_refs or (wave.case_id,),
            )
        )
    if wave.execution_mode is ImprovementExecutionMode.CONTAINED:
        stages.append(
            _stage_for_wave(
                campaign_id=campaign_id,
                wave=wave,
                stage_type=RemediationCampaignStageType.CONTAINMENT,
                status=RemediationCampaignStatus.BLOCKED,
                blocked_refs=wave.guardrail_refs or wave.risk_refs or (wave.case_id,),
            )
        )
    stages.append(
        _stage_for_wave(
            campaign_id=campaign_id,
            wave=wave,
            stage_type=RemediationCampaignStageType.REMEDIATION_WAVE,
            status=_status_for_wave(wave),
            safeguard_refs=wave.guardrail_refs if wave.execution_mode in {ImprovementExecutionMode.RECOVERY, ImprovementExecutionMode.CONTAINED} else (),
        )
    )
    return tuple(stages)


def build_remediation_campaign(
    orchestrator: ImprovementOrchestrator | None = None,
    *,
    campaign_id: str = "remediation-campaign",
) -> RemediationCampaign:
    """Build a coordinated remediation campaign over improvement waves."""

    resolved_orchestrator = build_improvement_orchestrator(orchestrator_id=f"{campaign_id}-orchestrator") if orchestrator is None else orchestrator
    stages = tuple(stage for wave in resolved_orchestrator.waves for stage in _stages_for_wave(campaign_id, wave))
    if not stages:
        raise ValueError("remediation campaign requires at least one stage")

    severity = "info"
    status = RemediationCampaignStatus.READY.value
    if any(wave.execution_mode is ImprovementExecutionMode.CONTAINED for wave in resolved_orchestrator.waves):
        severity = "critical"
        status = RemediationCampaignStatus.BLOCKED.value
    elif any(wave.execution_mode is ImprovementExecutionMode.RECOVERY for wave in resolved_orchestrator.waves):
        severity = "warning"
        status = RemediationCampaignStatus.RECOVERY_ONLY.value
    elif any(wave.execution_mode is ImprovementExecutionMode.GOVERNED for wave in resolved_orchestrator.waves):
        severity = "warning"
        status = RemediationCampaignStatus.GUARDED.value

    campaign_signal = TelemetrySignal(
        signal_name="remediation-campaign",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=campaign_id,
        severity=severity,
        status=status,
        metrics={
            "wave_count": float(len(resolved_orchestrator.waves)),
            "stage_count": float(len(stages)),
            "commitment_count": float(len(_ordered_union(*(stage.commitment_refs for stage in stages)))),
            "governance_case_count": float(len([stage for stage in stages if stage.stage_type is RemediationCampaignStageType.GOVERNANCE_APPROVAL])),
            "recovery_case_count": float(len([stage for stage in stages if stage.stage_type is RemediationCampaignStageType.RECOVERY_SAFEGUARD])),
            "blocked_case_count": float(len([stage for stage in stages if stage.stage_type is RemediationCampaignStageType.CONTAINMENT])),
        },
        labels={"campaign_id": campaign_id},
    )
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=resolved_orchestrator.final_snapshot.runtime_stage,
        signals=(
            campaign_signal,
            resolved_orchestrator.orchestration_signal,
            *resolved_orchestrator.final_snapshot.signals,
        ),
        alerts=resolved_orchestrator.final_snapshot.alerts,
        audit_entries=resolved_orchestrator.final_snapshot.audit_entries,
        active_controls=resolved_orchestrator.final_snapshot.active_controls,
    )
    return RemediationCampaign(
        campaign_id=campaign_id,
        orchestrator=resolved_orchestrator,
        stages=stages,
        campaign_signal=campaign_signal,
        final_snapshot=final_snapshot,
    )
