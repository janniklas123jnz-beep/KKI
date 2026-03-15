"""Release-campaign coordination over change windows."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .change_windows import ChangeWindow, ChangeWindowStatus
from .data_models import EvidenceRecord
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


class ReleaseCampaignStatus(str, Enum):
    """Canonical readiness states for release campaigns."""

    READY = "ready"
    GUARDED = "guarded"
    RECOVERY_ONLY = "recovery-only"
    BLOCKED = "blocked"


class ReleaseCampaignStageType(str, Enum):
    """Canonical stage types inside a release campaign."""

    EVIDENCE_PACK = "evidence-pack"
    GOVERNANCE_REVIEW = "governance-review"
    PROMOTION_WAVE = "promotion-wave"
    RECOVERY_WAVE = "recovery-wave"
    CONTAINMENT = "containment"


@dataclass(frozen=True)
class ReleaseCampaignStage:
    """A concrete campaign stage derived from a change window."""

    stage_id: str
    window_id: str
    stage_type: ReleaseCampaignStageType
    status: ReleaseCampaignStatus
    mission_refs: tuple[str, ...]
    evidence_records: tuple[EvidenceRecord, ...]
    commitment_refs: tuple[str, ...]
    governance_refs: tuple[str, ...] = ()
    blocked_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "stage_id", _non_empty(self.stage_id, field_name="stage_id"))
        object.__setattr__(self, "window_id", _non_empty(self.window_id, field_name="window_id"))
        if not self.mission_refs:
            raise ValueError("mission_refs must not be empty")
        if len(self.evidence_records) != len(self.mission_refs):
            raise ValueError("evidence_records must match mission_refs length")
        if len(self.commitment_refs) != len(self.mission_refs):
            raise ValueError("commitment_refs must match mission_refs length")

    def to_dict(self) -> dict[str, object]:
        return {
            "stage_id": self.stage_id,
            "window_id": self.window_id,
            "stage_type": self.stage_type.value,
            "status": self.status.value,
            "mission_refs": list(self.mission_refs),
            "evidence_records": [record.to_dict() for record in self.evidence_records],
            "commitment_refs": list(self.commitment_refs),
            "governance_refs": list(self.governance_refs),
            "blocked_refs": list(self.blocked_refs),
        }


@dataclass(frozen=True)
class ReleaseCampaign:
    """Coordinated multi-stage release campaign over one or more change windows."""

    campaign_id: str
    windows: tuple[ChangeWindow, ...]
    stages: tuple[ReleaseCampaignStage, ...]
    campaign_signal: TelemetrySignal
    final_snapshot: TelemetrySnapshot

    def __post_init__(self) -> None:
        object.__setattr__(self, "campaign_id", _non_empty(self.campaign_id, field_name="campaign_id"))

    @property
    def status(self) -> ReleaseCampaignStatus:
        return ReleaseCampaignStatus(self.campaign_signal.status)

    @property
    def promotion_refs(self) -> tuple[str, ...]:
        return _ordered_union(*(window.allowed_promotions for window in self.windows))

    @property
    def governance_review_refs(self) -> tuple[str, ...]:
        governance_stages = tuple(stage.governance_refs for stage in self.stages if stage.governance_refs)
        return _ordered_union(*governance_stages)

    @property
    def recovery_only_refs(self) -> tuple[str, ...]:
        return _ordered_union(*(window.recovery_only_refs for window in self.windows))

    @property
    def blocked_refs(self) -> tuple[str, ...]:
        return _ordered_union(*(window.blocked_refs for window in self.windows))

    @property
    def commitment_refs(self) -> tuple[str, ...]:
        return _ordered_union(*(stage.commitment_refs for stage in self.stages))

    @property
    def evidence_records(self) -> tuple[EvidenceRecord, ...]:
        return tuple(record for stage in self.stages for record in stage.evidence_records)

    def to_dict(self) -> dict[str, object]:
        return {
            "campaign_id": self.campaign_id,
            "windows": [window.to_dict() for window in self.windows],
            "stages": [stage.to_dict() for stage in self.stages],
            "campaign_signal": self.campaign_signal.to_dict(),
            "final_snapshot": self.final_snapshot.to_dict(),
            "status": self.status.value,
            "promotion_refs": list(self.promotion_refs),
            "governance_review_refs": list(self.governance_review_refs),
            "recovery_only_refs": list(self.recovery_only_refs),
            "blocked_refs": list(self.blocked_refs),
            "commitment_refs": list(self.commitment_refs),
            "evidence_records": [record.to_dict() for record in self.evidence_records],
        }


def _commitment_ref(campaign_id: str, mission_ref: str) -> str:
    return f"commit-{campaign_id}-{mission_ref}"


def _evidence_records_for_stage(
    *,
    campaign_id: str,
    window: ChangeWindow,
    stage_type: ReleaseCampaignStageType,
    mission_refs: tuple[str, ...],
) -> tuple[EvidenceRecord, ...]:
    return tuple(
        EvidenceRecord(
            evidence_type="release-campaign-stage",
            subject=mission_ref,
            correlation_id=campaign_id,
            audit_ref=f"audit-{campaign_id}-{window.window_id}-{stage_type.value}-{mission_ref}",
            commitment_ref=_commitment_ref(campaign_id, mission_ref),
            payload={
                "campaign_id": campaign_id,
                "window_id": window.window_id,
                "stage_type": stage_type.value,
                "window_status": window.status.value,
                "mission_ref": mission_ref,
            },
        )
        for mission_ref in mission_refs
    )


def _stage_for_window(
    *,
    campaign_id: str,
    window: ChangeWindow,
    stage_type: ReleaseCampaignStageType,
    mission_refs: tuple[str, ...],
    status: ReleaseCampaignStatus,
    governance_refs: tuple[str, ...] = (),
    blocked_refs: tuple[str, ...] = (),
) -> ReleaseCampaignStage:
    evidence_records = _evidence_records_for_stage(
        campaign_id=campaign_id,
        window=window,
        stage_type=stage_type,
        mission_refs=mission_refs,
    )
    commitment_refs = tuple(_commitment_ref(campaign_id, mission_ref) for mission_ref in mission_refs)
    return ReleaseCampaignStage(
        stage_id=f"{campaign_id}-{window.window_id}-{stage_type.value}",
        window_id=window.window_id,
        stage_type=stage_type,
        status=status,
        mission_refs=mission_refs,
        evidence_records=evidence_records,
        commitment_refs=commitment_refs,
        governance_refs=governance_refs,
        blocked_refs=blocked_refs,
    )


def _stages_for_window(campaign_id: str, window: ChangeWindow) -> tuple[ReleaseCampaignStage, ...]:
    stages: list[ReleaseCampaignStage] = []
    scope_refs = _ordered_union(window.allowed_promotions, window.recovery_only_refs, window.blocked_refs)
    if scope_refs:
        stages.append(
            _stage_for_window(
                campaign_id=campaign_id,
                window=window,
                stage_type=ReleaseCampaignStageType.EVIDENCE_PACK,
                mission_refs=scope_refs,
                status=ReleaseCampaignStatus.READY if window.status is ChangeWindowStatus.OPEN else ReleaseCampaignStatus(window.status.value),
                governance_refs=window.blocked_refs if window.status is ChangeWindowStatus.GUARDED else (),
                blocked_refs=window.blocked_refs if window.status is ChangeWindowStatus.BLOCKED else (),
            )
        )
    if window.allowed_promotions:
        stages.append(
            _stage_for_window(
                campaign_id=campaign_id,
                window=window,
                stage_type=ReleaseCampaignStageType.PROMOTION_WAVE,
                mission_refs=window.allowed_promotions,
                status=ReleaseCampaignStatus.READY,
            )
        )
    if window.status is ChangeWindowStatus.GUARDED:
        stages.append(
            _stage_for_window(
                campaign_id=campaign_id,
                window=window,
                stage_type=ReleaseCampaignStageType.GOVERNANCE_REVIEW,
                mission_refs=window.blocked_refs,
                status=ReleaseCampaignStatus.GUARDED,
                governance_refs=window.blocked_refs,
            )
        )
    if window.status is ChangeWindowStatus.RECOVERY_ONLY:
        stages.append(
            _stage_for_window(
                campaign_id=campaign_id,
                window=window,
                stage_type=ReleaseCampaignStageType.RECOVERY_WAVE,
                mission_refs=window.recovery_only_refs,
                status=ReleaseCampaignStatus.RECOVERY_ONLY,
            )
        )
    if window.status is ChangeWindowStatus.BLOCKED:
        stages.append(
            _stage_for_window(
                campaign_id=campaign_id,
                window=window,
                stage_type=ReleaseCampaignStageType.CONTAINMENT,
                mission_refs=window.blocked_refs,
                status=ReleaseCampaignStatus.BLOCKED,
                blocked_refs=window.blocked_refs,
            )
        )
    return tuple(stages)


def build_release_campaign(
    windows: tuple[ChangeWindow, ...] | list[ChangeWindow],
    *,
    campaign_id: str = "release-campaign",
) -> ReleaseCampaign:
    """Build a coordinated release campaign over one or more change windows."""

    resolved_windows = tuple(windows)
    if not resolved_windows:
        raise ValueError("windows must not be empty")

    stages = tuple(stage for window in resolved_windows for stage in _stages_for_window(campaign_id, window))
    if not stages:
        raise ValueError("release campaign requires at least one stage")

    severity = "info"
    status = ReleaseCampaignStatus.READY.value
    if any(window.status is ChangeWindowStatus.BLOCKED for window in resolved_windows):
        severity = "critical"
        status = ReleaseCampaignStatus.BLOCKED.value
    elif any(window.status is ChangeWindowStatus.RECOVERY_ONLY for window in resolved_windows):
        severity = "warning"
        status = ReleaseCampaignStatus.RECOVERY_ONLY.value
    elif any(window.status is ChangeWindowStatus.GUARDED for window in resolved_windows):
        severity = "warning"
        status = ReleaseCampaignStatus.GUARDED.value

    campaign_signal = TelemetrySignal(
        signal_name="release-campaign",
        boundary=ModuleBoundaryName.GOVERNANCE,
        correlation_id=campaign_id,
        severity=severity,
        status=status,
        metrics={
            "window_count": float(len(resolved_windows)),
            "stage_count": float(len(stages)),
            "promotion_count": float(sum(len(window.allowed_promotions) for window in resolved_windows)),
            "governance_review_count": float(
                sum(len(stage.governance_refs) for stage in stages if stage.stage_type is ReleaseCampaignStageType.GOVERNANCE_REVIEW)
            ),
            "recovery_count": float(sum(len(window.recovery_only_refs) for window in resolved_windows)),
            "blocked_count": float(sum(len(window.blocked_refs) for window in resolved_windows)),
        },
        labels={"campaign_id": campaign_id},
    )
    first_stage = resolved_windows[0].final_snapshot.runtime_stage
    final_snapshot = build_telemetry_snapshot(
        runtime_stage=first_stage,
        signals=(campaign_signal, *(window.window_signal for window in resolved_windows), *(signal for window in resolved_windows for signal in window.final_snapshot.signals)),
        alerts=tuple(alert for window in resolved_windows for alert in window.final_snapshot.alerts),
        audit_entries=tuple(record for window in resolved_windows for record in window.final_snapshot.audit_entries),
        active_controls=tuple(dict.fromkeys(control for window in resolved_windows for control in window.final_snapshot.active_controls)),
    )
    return ReleaseCampaign(
        campaign_id=campaign_id,
        windows=resolved_windows,
        stages=stages,
        campaign_signal=campaign_signal,
        final_snapshot=final_snapshot,
    )
