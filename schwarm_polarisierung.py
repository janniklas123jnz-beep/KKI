"""
KKI Polarisierungs-Experiment: Konsensbildung und Lagerbildung im Schwarm
=========================================================================
Untersucht, wie sich Meinungen, Kooperation und Gruppenbildung in einem
Netzwerk-Schwarm gegenseitig beeinflussen.
"""

from __future__ import annotations

import os
import random
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import configure_simulation, save_and_maybe_show

DEFAULT_AGENT_COUNT = 60
DEFAULT_ROUNDS = 180
DEFAULT_CONNECTIONS_PER_AGENT = 6
DEFAULT_INTERACTIONS_PER_ROUND = 90
DEFAULT_RANDOM_EDGE_CHANCE = 0.1
VALID_SCENARIOS = {'polarization', 'consensus'}
DEFAULT_REWIRE_MIN_INTERACTIONS = 3
DEFAULT_REWIRE_REPUTATION_THRESHOLD = 0.35
DEFAULT_REWIRE_OPINION_DISTANCE_THRESHOLD = 0.55
DEFAULT_REWIRE_PROXIMITY_WEIGHT = 0.45
DEFAULT_REWIRE_REMOVAL_PROBABILITY = 0.35
DEFAULT_REWIRE_ADDITION_PROBABILITY = 0.75
DEFAULT_REWIRE_CROSS_GROUP_BONUS = 0.08
DEFAULT_CENTER_MIN = 0.35
DEFAULT_CENTER_MAX = 0.65
DEFAULT_GENERALIST_SHARE = 0.55
DEFAULT_CONNECTOR_SHARE = 0.25
DEFAULT_SENTINEL_SHARE = 0.20
DEFAULT_MEDIATOR_SHARE = 0.0
DEFAULT_ANALYZER_SHARE = 0.0
DEFAULT_CONNECTOR_BONUS = 0.10
DEFAULT_SENTINEL_REP_THRESHOLD = 0.45
DEFAULT_SENTINEL_COOPERATION_PENALTY = 0.06
DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING = 0.15
DEFAULT_SENTINEL_REPUTATION_LEARNING = 1.20
DEFAULT_MEDIATOR_BONUS = 0.06
DEFAULT_MEDIATOR_CONTACT_BIAS = 0.70
DEFAULT_MEDIATOR_OPINION_DISTANCE = 0.25
DEFAULT_ANALYZER_MEMORY_WINDOW = 15
DEFAULT_ANALYZER_LEARNING_MULTIPLIER = 1.10
DEFAULT_ROLE_SWITCH_INTERVAL = 20
DEFAULT_ROLE_SWITCH_MIN_TENURE = 20
DEFAULT_ROLE_SWITCH_REPUTATION_COST = 0.02
DEFAULT_MISSION_SWITCH_INTERVAL = 30
DEFAULT_MISSION_CONFLICT_THRESHOLD = 0.45
DEFAULT_MISSION_ARBITRATION_MARGIN = 0.08
DEFAULT_WORKFLOW_STAGE_MIN_TENURE = 2
DEFAULT_HANDOFF_PRIORITY_BONUS = 0.12
DEFAULT_RESOURCE_BUDGET = 1.0
DEFAULT_RESOURCE_SHARE_FACTOR = 0.20
DEFAULT_CLUSTER_BUDGET_SKEW = 0.35
DEFAULT_BOTTLENECK_THRESHOLD = 1.05
DEFAULT_BOTTLENECK_TRIAGE_INTENSITY = 0.55
DEFAULT_META_UPDATE_INTERVAL = 12
DEFAULT_META_PRIORITY_STRENGTH = 0.18
DEFAULT_INJECTION_ATTACK_ROUND = 90
DEFAULT_INJECTION_STRENGTH = 0.38
DEFAULT_INJECTION_SOURCE_COUNT = 6
DEFAULT_GROUP_LEARNING_RATE = 0.10
DEFAULT_SKILL_SPECIALIZATION_THRESHOLD = 0.62
DEFAULT_QUARANTINE_COMPROMISE_THRESHOLD = 0.28
DEFAULT_QUARANTINE_EXPOSURE_THRESHOLD = 0.34
DEFAULT_QUARANTINE_DURATION = 4
DEFAULT_TRUST_SHIELD_STRENGTH = 0.22
MISSION_CONSENSUS = 'consensus_building'
MISSION_KNOWLEDGE = 'knowledge_sharing'
MISSION_DEFENSE = 'reputation_defense'
MISSION_STABILITY = 'network_stability'
MISSION_SUPPORT = 'support'
MISSION_TYPES = (
    MISSION_CONSENSUS,
    MISSION_KNOWLEDGE,
    MISSION_DEFENSE,
    MISSION_STABILITY,
    MISSION_SUPPORT,
)
WORKFLOW_STAGES = (
    'task_queue',
    'discovery',
    'preparation',
    'execution',
    'consolidation',
    'recovery',
)
WORKFLOW_CELLS = (
    'interface_cell',
    'analysis_cell',
    'execution_cell',
    'stability_cell',
)
CAPABILITY_CLUSTERS = (
    'scout_cluster',
    'synthesis_cluster',
    'response_cluster',
    'resilience_cluster',
)


class Agent:
    """Agent mit Meinung, Kooperationsneigung und Netzwerkbeziehungen."""

    def __init__(self, agent_id, gruppe, meinung, kooperations_neigung, hartnaeckigkeit=0.0):
        self.id = agent_id
        self.gruppe = gruppe
        self.name = f"G{gruppe + 1}-A{agent_id}"
        self.meinung = meinung
        self.kooperations_neigung = kooperations_neigung
        self.hartnaeckigkeit = hartnaeckigkeit
        self.intelligenz = 1.0
        self.reputation = 0.5
        self.nachbarn = set()
        self.interaktions_history = defaultdict(list)
        self.role = 'generalist'
        self.bridge_bonus = 0.0
        self.rewire_reputation_threshold = None
        self.cooperation_penalty_threshold = None
        self.cooperation_penalty = 0.0
        self.intelligence_learning_multiplier = 1.0
        self.cooperation_learning_multiplier = 1.0
        self.reputation_learning_multiplier = 1.0
        self.opinion_learning_multiplier = 1.0
        self.cross_group_learning_bonus = 0.0
        self.memory_window = 10
        self.partner_bias_probability = 0.0
        self.partner_bias_min_distance = 0.0
        self.role_tenure = 0
        self.initial_role = 'generalist'
        self.role_transition_history = []
        self.mission = MISSION_SUPPORT
        self.initial_mission = MISSION_SUPPORT
        self.mission_tenure = 0
        self.mission_transition_history = []
        self.mission_candidates = []
        self.mission_last_fitness = {}
        self.mission_arbitration_history = []
        self.workflow_stage = 'task_queue'
        self.initial_workflow_stage = 'task_queue'
        self.workflow_history = []
        self.task_priority = 0.5
        self.dependencies_met = True
        self.stage_tenure = 0
        self.workflow_cell = 'analysis_cell'
        self.initial_workflow_cell = 'analysis_cell'
        self.workflow_cell_history = []
        self.handoff_credit = 0.0
        self.handoff_received = 0
        self.handoff_given = 0
        self.handoff_history = []
        self.resource_credit = 0.0
        self.resource_received_total = 0.0
        self.resource_shared_total = 0.0
        self.capability_cluster = 'synthesis_cluster'
        self.initial_capability_cluster = 'synthesis_cluster'
        self.cluster_history = []
        self.cluster_budget_weight = 1.0
        self.cluster_demand_multiplier = 1.0
        self.cluster_output_multiplier = 1.0
        self.cluster_coordination_bonus = 0.0
        self.cluster_resilience_bonus = 0.0
        self.cluster_output_total = 0.0
        self.bottleneck_pressure = 0.0
        self.bottleneck_relief_total = 0.0
        self.resource_rerouted_total = 0.0
        self.meta_priority_score = 0.0
        self.meta_aligned_rounds = 0
        self.meta_focus_history = []
        self.ist_misinformation_source = False
        self.misinformation_intensity = 0.0
        self.cluster_compromise_level = 0.0
        self.meta_signal_corruption = 0.0
        self.misinformation_exposure = 0.0
        self.false_mission_signal = None
        self.false_cluster_signal = None
        self.misinformation_events = 0
        self.misinformation_detected = 0
        self.emergent_skill = 'adaptive_generalist'
        self.initial_emergent_skill = 'adaptive_generalist'
        self.emergent_skill_history = []
        self.bridge_skill = 0.25
        self.analysis_skill = 0.25
        self.defense_skill = 0.25
        self.recovery_skill = 0.25
        self.group_learning_gain_total = 0.0
        self.is_quarantined = False
        self.quarantine_rounds = 0
        self.quarantine_events = 0
        self.trust_shield_score = 0.0
        self.shielding_actions_total = 0
        self.isolation_relief_total = 0.0

        self.meinung_history = [meinung]
        self.kooperation_history = [kooperations_neigung]
        self.intelligenz_history = [1.0]

    def verbinde(self, anderer):
        self.nachbarn.add(anderer.id)
        anderer.nachbarn.add(self.id)

    def trenne(self, anderer):
        self.nachbarn.discard(anderer.id)
        anderer.nachbarn.discard(self.id)

    def berechne_partner_reputation(self, partner_id):
        history = self.interaktions_history.get(partner_id, [])
        if not history:
            return 0.5
        fenster = history[-self.memory_window :]
        return sum(1 for aktion in fenster if aktion == 'C') / len(fenster)

    def waehle_aktion(self, partner_reputation, partner_meinung, cooperation_bonus=0.0):
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        effektive_neigung = self.kooperations_neigung
        effektive_neigung *= 0.55 + 0.45 * partner_reputation
        effektive_neigung *= 0.35 + 0.65 * aehnlichkeit
        if (
            self.cooperation_penalty_threshold is not None
            and partner_reputation < self.cooperation_penalty_threshold
        ):
            effektive_neigung -= self.cooperation_penalty
        effektive_neigung += cooperation_bonus
        effektive_neigung = max(0.05, min(0.95, effektive_neigung))

        if random.random() < effektive_neigung:
            return 'C'
        return 'D'

    def lerne(
        self,
        meine_aktion,
        andere_aktion,
        partner_id,
        partner_intelligenz,
        partner_meinung,
        gleiche_gruppe,
        opinion_pull=0.0,
    ):
        self.interaktions_history[partner_id].append(andere_aktion)
        meinungs_distanz = abs(self.meinung - partner_meinung)
        aehnlichkeit = 1.0 - meinungs_distanz
        beweglichkeit = 1.0 - self.hartnaeckigkeit
        learning_factor = self.intelligence_learning_multiplier
        cooperation_factor = self.cooperation_learning_multiplier
        reputation_factor = self.reputation_learning_multiplier
        opinion_factor = self.opinion_learning_multiplier
        if not gleiche_gruppe:
            learning_factor *= 1.0 + self.cross_group_learning_bonus

        if meine_aktion == 'C' and andere_aktion == 'C':
            self.intelligenz *= 1.0 + (
                (1.002 + 0.002 * aehnlichkeit + 0.001 * min(partner_intelligenz, 4.0)) - 1.0
            ) * learning_factor
            self.kooperations_neigung += 0.006 * cooperation_factor * (0.5 + aehnlichkeit)
            self.reputation += 0.012 * reputation_factor
            zugkraft = 0.12 if gleiche_gruppe else 0.08
            zugkraft = (zugkraft + opinion_pull) * opinion_factor
            self.meinung += (partner_meinung - self.meinung) * zugkraft * beweglichkeit

        elif meine_aktion == 'C' and andere_aktion == 'D':
            self.kooperations_neigung -= 0.004 * cooperation_factor
            self.reputation += 0.004 * reputation_factor
            if meinungs_distanz > 0.3:
                self.meinung += (self.meinung - partner_meinung) * 0.03 * opinion_factor * beweglichkeit

        elif meine_aktion == 'D' and andere_aktion == 'C':
            self.intelligenz *= 1.0 - (1.0 - 0.997) * learning_factor
            self.reputation -= 0.02 * reputation_factor
            if meinungs_distanz > 0.25:
                self.meinung += (self.meinung - partner_meinung) * 0.025 * opinion_factor * beweglichkeit

        elif meine_aktion == 'D' and andere_aktion == 'D':
            self.intelligenz *= 1.0 - (1.0 - 0.991) * learning_factor
            self.reputation -= 0.01 * reputation_factor
            self.kooperations_neigung += 0.002 * cooperation_factor
            if meinungs_distanz > 0.2:
                self.meinung += (self.meinung - partner_meinung) * 0.02 * opinion_factor * beweglichkeit

        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(6.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
        self.meinung = max(0.0, min(1.0, self.meinung))

    def runde_beenden(self):
        self.meinung_history.append(self.meinung)
        self.kooperation_history.append(self.kooperations_neigung)
        self.intelligenz_history.append(self.intelligenz)


def resolve_scenario(name: str) -> str:
    scenario = name.strip().lower()
    if scenario not in VALID_SCENARIOS:
        raise ValueError(f"Unbekanntes Szenario '{name}'. Erlaubt: {', '.join(sorted(VALID_SCENARIOS))}")
    return scenario


def scenario_title(scenario: str) -> str:
    return 'KONSENS-SZENARIO' if scenario == 'consensus' else 'POLARISIERUNGS-SZENARIO'


def default_cross_group_chance(scenario: str) -> float:
    return 0.35 if scenario == 'consensus' else 0.08


def build_runtime_config() -> tuple[dict[str, float | int | str], int]:
    rounds_config, seed = configure_simulation(
        {
            'RUNDEN': DEFAULT_ROUNDS,
            'INTERAKTIONEN_PRO_RUNDE': DEFAULT_INTERACTIONS_PER_ROUND,
        },
        np_module=np,
        plt_module=plt,
    )

    scenario = resolve_scenario(os.getenv('KKI_POLARIZATION_SCENARIO', 'polarization'))
    rewiring_enabled = os.getenv('KKI_REWIRING_ENABLED', '').strip().lower() in {'1', 'true', 'yes', 'on'}
    target_degree = int(os.getenv('KKI_REWIRE_TARGET_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT)))
    config = {
        'scenario': scenario,
        'agent_count': int(os.getenv('KKI_POLARIZATION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'rounds': rounds_config['RUNDEN'],
        'interactions_per_round': rounds_config['INTERAKTIONEN_PRO_RUNDE'],
        'connections_per_agent': int(
            os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))
        ),
        'cross_group_chance': float(
            os.getenv('KKI_CROSS_GROUP_CHANCE', str(default_cross_group_chance(scenario)))
        ),
        'random_edge_chance': float(
            os.getenv('KKI_RANDOM_EDGE_CHANCE', str(DEFAULT_RANDOM_EDGE_CHANCE))
        ),
        'enable_dynamic_rewiring': rewiring_enabled,
        'rewire_min_interactions': int(
            os.getenv('KKI_REWIRE_MIN_INTERACTIONS', str(DEFAULT_REWIRE_MIN_INTERACTIONS))
        ),
        'rewire_reputation_threshold': float(
            os.getenv('KKI_REWIRE_REP_THRESHOLD', str(DEFAULT_REWIRE_REPUTATION_THRESHOLD))
        ),
        'rewire_opinion_distance_threshold': float(
            os.getenv('KKI_REWIRE_OPINION_THRESHOLD', str(DEFAULT_REWIRE_OPINION_DISTANCE_THRESHOLD))
        ),
        'rewire_proximity_weight': float(
            os.getenv('KKI_REWIRE_PROXIMITY_WEIGHT', str(DEFAULT_REWIRE_PROXIMITY_WEIGHT))
        ),
        'rewire_removal_probability': float(
            os.getenv('KKI_REWIRE_REMOVAL_PROB', str(DEFAULT_REWIRE_REMOVAL_PROBABILITY))
        ),
        'rewire_addition_probability': float(
            os.getenv('KKI_REWIRE_ADDITION_PROB', str(DEFAULT_REWIRE_ADDITION_PROBABILITY))
        ),
        'rewire_cross_group_bonus': float(
            os.getenv('KKI_REWIRE_CROSS_GROUP_BONUS', str(DEFAULT_REWIRE_CROSS_GROUP_BONUS))
        ),
        'rewire_target_degree': target_degree,
        'enable_bridge_mechanism': os.getenv('KKI_BRIDGE_MECHANISM', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'bridge_cooperation_bonus': float(os.getenv('KKI_BRIDGE_COOPERATION_BONUS', '0.08')),
        'enable_centrist_moderation': os.getenv('KKI_CENTRIST_MODERATION', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'centrist_pull_strength': float(os.getenv('KKI_CENTRIST_PULL', '0.08')),
        'enable_mediator_encouragement': os.getenv('KKI_MEDIATOR_MODE', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'mediator_contact_bias': float(os.getenv('KKI_MEDIATOR_CONTACT_BIAS', '0.60')),
        'center_zone_min': float(os.getenv('KKI_CENTER_ZONE_MIN', str(DEFAULT_CENTER_MIN))),
        'center_zone_max': float(os.getenv('KKI_CENTER_ZONE_MAX', str(DEFAULT_CENTER_MAX))),
        'roles_enabled': os.getenv('KKI_ROLES_ENABLED', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'generalist_share': float(os.getenv('KKI_GENERALIST_SHARE', str(DEFAULT_GENERALIST_SHARE))),
        'connector_share': float(os.getenv('KKI_CONNECTOR_SHARE', str(DEFAULT_CONNECTOR_SHARE))),
        'sentinel_share': float(os.getenv('KKI_SENTINEL_SHARE', str(DEFAULT_SENTINEL_SHARE))),
        'mediator_share': float(os.getenv('KKI_MEDIATOR_SHARE', str(DEFAULT_MEDIATOR_SHARE))),
        'analyzer_share': float(os.getenv('KKI_ANALYZER_SHARE', str(DEFAULT_ANALYZER_SHARE))),
        'connector_bridge_bonus': float(os.getenv('KKI_CONNECTOR_BRIDGE_BONUS', str(DEFAULT_CONNECTOR_BONUS))),
        'sentinel_rep_threshold': float(
            os.getenv('KKI_SENTINEL_REP_THRESHOLD', str(DEFAULT_SENTINEL_REP_THRESHOLD))
        ),
        'sentinel_cooperation_penalty': float(
            os.getenv(
                'KKI_SENTINEL_COOPERATION_PENALTY',
                str(DEFAULT_SENTINEL_COOPERATION_PENALTY),
            )
        ),
        'connector_cross_group_learning_bonus': float(
            os.getenv(
                'KKI_CONNECTOR_CROSS_GROUP_LEARNING',
                str(DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING),
            )
        ),
        'sentinel_reputation_learning_multiplier': float(
            os.getenv(
                'KKI_SENTINEL_REPUTATION_LEARNING',
                str(DEFAULT_SENTINEL_REPUTATION_LEARNING),
            )
        ),
        'mediator_bridge_bonus': float(
            os.getenv('KKI_MEDIATOR_BRIDGE_BONUS', str(DEFAULT_MEDIATOR_BONUS))
        ),
        'mediator_partner_bias': float(
            os.getenv('KKI_MEDIATOR_PARTNER_BIAS', str(DEFAULT_MEDIATOR_CONTACT_BIAS))
        ),
        'mediator_partner_distance': float(
            os.getenv('KKI_MEDIATOR_PARTNER_DISTANCE', str(DEFAULT_MEDIATOR_OPINION_DISTANCE))
        ),
        'analyzer_memory_window': int(
            os.getenv('KKI_ANALYZER_MEMORY_WINDOW', str(DEFAULT_ANALYZER_MEMORY_WINDOW))
        ),
        'analyzer_learning_multiplier': float(
            os.getenv(
                'KKI_ANALYZER_LEARNING_MULTIPLIER',
                str(DEFAULT_ANALYZER_LEARNING_MULTIPLIER),
            )
        ),
        'enable_role_switching': os.getenv('KKI_ENABLE_ROLE_SWITCHING', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'role_switch_interval': int(
            os.getenv('KKI_ROLE_SWITCH_INTERVAL', str(DEFAULT_ROLE_SWITCH_INTERVAL))
        ),
        'role_switch_min_tenure': int(
            os.getenv('KKI_ROLE_SWITCH_MIN_TENURE', str(DEFAULT_ROLE_SWITCH_MIN_TENURE))
        ),
        'role_switch_reputation_cost': float(
            os.getenv(
                'KKI_ROLE_SWITCH_REPUTATION_COST',
                str(DEFAULT_ROLE_SWITCH_REPUTATION_COST),
            )
        ),
        'enable_missions': os.getenv('KKI_MISSIONS_ENABLED', '').strip().lower() in {'1', 'true', 'yes', 'on'},
        'mission_assignment': os.getenv('KKI_MISSION_ASSIGNMENT', 'static').strip().lower(),
        'mission_switch_interval': int(
            os.getenv('KKI_MISSION_SWITCH_INTERVAL', str(DEFAULT_MISSION_SWITCH_INTERVAL))
        ),
        'mission_arbitration_enabled': os.getenv('KKI_MISSION_ARBITRATION_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'mission_conflict_threshold': float(
            os.getenv('KKI_MISSION_CONFLICT_THRESHOLD', str(DEFAULT_MISSION_CONFLICT_THRESHOLD))
        ),
        'mission_arbitration_margin': float(
            os.getenv('KKI_MISSION_ARBITRATION_MARGIN', str(DEFAULT_MISSION_ARBITRATION_MARGIN))
        ),
        'enable_workflow_stages': os.getenv('KKI_WORKFLOW_STAGES_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'workflow_stage_min_tenure': int(
            os.getenv('KKI_WORKFLOW_STAGE_MIN_TENURE', str(DEFAULT_WORKFLOW_STAGE_MIN_TENURE))
        ),
        'enable_workflow_cells': os.getenv('KKI_WORKFLOW_CELLS_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'enable_handoff_coordination': os.getenv('KKI_HANDOFF_COORDINATION_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'handoff_priority_bonus': float(
            os.getenv('KKI_HANDOFF_PRIORITY_BONUS', str(DEFAULT_HANDOFF_PRIORITY_BONUS))
        ),
        'enable_parallel_workflow_cells': os.getenv('KKI_PARALLEL_WORKFLOW_CELLS_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'enable_resource_coordination': os.getenv('KKI_RESOURCE_COORDINATION_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'resource_budget': float(os.getenv('KKI_RESOURCE_BUDGET', str(DEFAULT_RESOURCE_BUDGET))),
        'resource_share_factor': float(
            os.getenv('KKI_RESOURCE_SHARE_FACTOR', str(DEFAULT_RESOURCE_SHARE_FACTOR))
        ),
        'enable_capability_clusters': os.getenv('KKI_CAPABILITY_CLUSTERS_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'enable_asymmetric_cluster_budgets': os.getenv('KKI_ASYMMETRIC_CLUSTER_BUDGETS_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'cluster_budget_skew': float(
            os.getenv('KKI_CLUSTER_BUDGET_SKEW', str(DEFAULT_CLUSTER_BUDGET_SKEW))
        ),
        'enable_bottleneck_management': os.getenv('KKI_BOTTLENECK_MANAGEMENT_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'bottleneck_threshold': float(
            os.getenv('KKI_BOTTLENECK_THRESHOLD', str(DEFAULT_BOTTLENECK_THRESHOLD))
        ),
        'bottleneck_triage_intensity': float(
            os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', str(DEFAULT_BOTTLENECK_TRIAGE_INTENSITY))
        ),
        'enable_meta_coordination': os.getenv('KKI_META_COORDINATION_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'meta_update_interval': int(
            os.getenv('KKI_META_UPDATE_INTERVAL', str(DEFAULT_META_UPDATE_INTERVAL))
        ),
        'meta_priority_strength': float(
            os.getenv('KKI_META_PRIORITY_STRENGTH', str(DEFAULT_META_PRIORITY_STRENGTH))
        ),
        'enable_prompt_injection': os.getenv('KKI_PROMPT_INJECTION_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'injection_attack_round': int(
            os.getenv('KKI_INJECTION_ATTACK_ROUND', str(DEFAULT_INJECTION_ATTACK_ROUND))
        ),
        'injection_strength': float(
            os.getenv('KKI_INJECTION_STRENGTH', str(DEFAULT_INJECTION_STRENGTH))
        ),
        'injection_source_count': int(
            os.getenv('KKI_INJECTION_SOURCE_COUNT', str(DEFAULT_INJECTION_SOURCE_COUNT))
        ),
        'enable_emergent_skills': os.getenv('KKI_EMERGENT_SKILLS_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'group_learning_rate': float(
            os.getenv('KKI_GROUP_LEARNING_RATE', str(DEFAULT_GROUP_LEARNING_RATE))
        ),
        'skill_specialization_threshold': float(
            os.getenv(
                'KKI_SKILL_SPECIALIZATION_THRESHOLD',
                str(DEFAULT_SKILL_SPECIALIZATION_THRESHOLD),
            )
        ),
        'enable_fault_isolation': os.getenv('KKI_FAULT_ISOLATION_ENABLED', '').strip().lower()
        in {'1', 'true', 'yes', 'on'},
        'quarantine_compromise_threshold': float(
            os.getenv(
                'KKI_QUARANTINE_COMPROMISE_THRESHOLD',
                str(DEFAULT_QUARANTINE_COMPROMISE_THRESHOLD),
            )
        ),
        'quarantine_exposure_threshold': float(
            os.getenv(
                'KKI_QUARANTINE_EXPOSURE_THRESHOLD',
                str(DEFAULT_QUARANTINE_EXPOSURE_THRESHOLD),
            )
        ),
        'quarantine_duration': int(
            os.getenv('KKI_QUARANTINE_DURATION', str(DEFAULT_QUARANTINE_DURATION))
        ),
        'trust_shield_strength': float(
            os.getenv('KKI_TRUST_SHIELD_STRENGTH', str(DEFAULT_TRUST_SHIELD_STRENGTH))
        ),
    }
    return config, seed


def normalisiere_rollenanteile(config):
    generalist = max(0.0, float(config.get('generalist_share', DEFAULT_GENERALIST_SHARE)))
    connector = max(0.0, float(config.get('connector_share', DEFAULT_CONNECTOR_SHARE)))
    sentinel = max(0.0, float(config.get('sentinel_share', DEFAULT_SENTINEL_SHARE)))
    mediator = max(0.0, float(config.get('mediator_share', DEFAULT_MEDIATOR_SHARE)))
    analyzer = max(0.0, float(config.get('analyzer_share', DEFAULT_ANALYZER_SHARE)))
    total = generalist + connector + sentinel + mediator + analyzer
    if total <= 0.0:
        return {
            'generalist': 1.0,
            'connector': 0.0,
            'sentinel': 0.0,
            'mediator': 0.0,
            'analyzer': 0.0,
        }
    return {
        'generalist': generalist / total,
        'connector': connector / total,
        'sentinel': sentinel / total,
        'mediator': mediator / total,
        'analyzer': analyzer / total,
    }


def apply_role_profile(agent, role, config):
    agent.role = role
    agent.bridge_bonus = 0.0
    agent.rewire_reputation_threshold = None
    agent.cooperation_penalty_threshold = None
    agent.cooperation_penalty = 0.0
    agent.intelligence_learning_multiplier = 1.0
    agent.cooperation_learning_multiplier = 1.0
    agent.reputation_learning_multiplier = 1.0
    agent.opinion_learning_multiplier = 1.0
    agent.cross_group_learning_bonus = 0.0
    agent.memory_window = 10
    agent.partner_bias_probability = 0.0
    agent.partner_bias_min_distance = 0.0

    if role == 'connector':
        agent.bridge_bonus = float(config.get('connector_bridge_bonus', DEFAULT_CONNECTOR_BONUS))
        agent.opinion_learning_multiplier = 1.15
        agent.cross_group_learning_bonus = float(
            config.get(
                'connector_cross_group_learning_bonus',
                DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING,
            )
        )
    elif role == 'sentinel':
        agent.rewire_reputation_threshold = float(
            config.get('sentinel_rep_threshold', DEFAULT_SENTINEL_REP_THRESHOLD)
        )
        agent.cooperation_penalty_threshold = agent.rewire_reputation_threshold
        agent.cooperation_penalty = float(
            config.get('sentinel_cooperation_penalty', DEFAULT_SENTINEL_COOPERATION_PENALTY)
        )
        agent.reputation_learning_multiplier = float(
            config.get(
                'sentinel_reputation_learning_multiplier',
                DEFAULT_SENTINEL_REPUTATION_LEARNING,
            )
        )
        agent.opinion_learning_multiplier = 0.75
        agent.memory_window = 12
    elif role == 'mediator':
        agent.bridge_bonus = float(config.get('mediator_bridge_bonus', DEFAULT_MEDIATOR_BONUS))
        agent.partner_bias_probability = float(
            config.get('mediator_partner_bias', DEFAULT_MEDIATOR_CONTACT_BIAS)
        )
        agent.partner_bias_min_distance = float(
            config.get('mediator_partner_distance', DEFAULT_MEDIATOR_OPINION_DISTANCE)
        )
        agent.opinion_learning_multiplier = 1.30
        agent.cross_group_learning_bonus = 0.10
    elif role == 'analyzer':
        agent.memory_window = int(config.get('analyzer_memory_window', DEFAULT_ANALYZER_MEMORY_WINDOW))
        agent.intelligence_learning_multiplier = float(
            config.get(
                'analyzer_learning_multiplier',
                DEFAULT_ANALYZER_LEARNING_MULTIPLIER,
            )
        )
        agent.reputation_learning_multiplier = 1.10
        agent.opinion_learning_multiplier = 0.85


def mission_fuer_rolle(role):
    if role == 'connector':
        return MISSION_KNOWLEDGE
    if role == 'sentinel':
        return MISSION_DEFENSE
    if role == 'mediator':
        return MISSION_CONSENSUS
    if role == 'analyzer':
        return MISSION_STABILITY
    return MISSION_SUPPORT


def workflow_stufe_fuer_mission(mission):
    mapping = {
        MISSION_CONSENSUS: 'discovery',
        MISSION_KNOWLEDGE: 'preparation',
        MISSION_DEFENSE: 'execution',
        MISSION_STABILITY: 'consolidation',
        MISSION_SUPPORT: 'recovery',
    }
    return mapping.get(mission, 'task_queue')


def workflow_zelle_fuer_agent(agent):
    if agent.role in {'connector', 'mediator'} or agent.workflow_stage == 'discovery':
        return 'interface_cell'
    if agent.role == 'analyzer' or agent.workflow_stage == 'preparation':
        return 'analysis_cell'
    if agent.role == 'sentinel' or agent.workflow_stage == 'execution':
        return 'execution_cell'
    return 'stability_cell'


def setze_workflow_zelle(agent, cell, runde):
    cell = cell if cell in WORKFLOW_CELLS else 'analysis_cell'
    if agent.workflow_cell != cell:
        agent.workflow_cell_history.append((runde, agent.workflow_cell, cell))
    agent.workflow_cell = cell


def setze_workflow_stufe(agent, stage, runde):
    stage = stage if stage in WORKFLOW_STAGES else 'task_queue'
    if agent.workflow_stage != stage:
        agent.workflow_history.append((runde, agent.workflow_stage, stage))
        agent.stage_tenure = 0
    agent.workflow_stage = stage


def initialisiere_workflows(agenten):
    for agent in agenten:
        stage = workflow_stufe_fuer_mission(agent.mission)
        agent.workflow_stage = stage
        agent.initial_workflow_stage = stage
        agent.workflow_history = []
        agent.task_priority = 0.5
        agent.dependencies_met = True
        agent.stage_tenure = 0
        cell = workflow_zelle_fuer_agent(agent)
        agent.workflow_cell = cell
        agent.initial_workflow_cell = cell
        agent.workflow_cell_history = []
        agent.handoff_credit = 0.0
        agent.handoff_received = 0
        agent.handoff_given = 0
        agent.handoff_history = []


def faehigkeitscluster_fuer_agent(agent):
    mapping = {
        'interface_cell': 'scout_cluster',
        'analysis_cell': 'synthesis_cluster',
        'execution_cell': 'response_cluster',
        'stability_cell': 'resilience_cluster',
    }
    return mapping.get(agent.workflow_cell, 'synthesis_cluster')


def cluster_fuer_mission(mission):
    mapping = {
        MISSION_CONSENSUS: 'synthesis_cluster',
        MISSION_KNOWLEDGE: 'scout_cluster',
        MISSION_DEFENSE: 'response_cluster',
        MISSION_STABILITY: 'resilience_cluster',
        MISSION_SUPPORT: 'synthesis_cluster',
    }
    return mapping.get(mission, 'synthesis_cluster')


def skill_fokus_fuer_cluster(cluster):
    mapping = {
        'scout_cluster': 'bridge_specialist',
        'synthesis_cluster': 'analysis_specialist',
        'response_cluster': 'defense_specialist',
        'resilience_cluster': 'recovery_specialist',
    }
    return mapping.get(cluster, 'adaptive_generalist')


def skill_bonus_fuer_mission(agent, mission):
    bonuses = {
        'bridge_specialist': {MISSION_CONSENSUS: 0.06, MISSION_KNOWLEDGE: 0.04},
        'analysis_specialist': {MISSION_KNOWLEDGE: 0.07, MISSION_SUPPORT: 0.03},
        'defense_specialist': {MISSION_DEFENSE: 0.08, MISSION_STABILITY: 0.03},
        'recovery_specialist': {MISSION_STABILITY: 0.08, MISSION_SUPPORT: 0.04},
        'adaptive_generalist': {MISSION_SUPPORT: 0.02},
    }
    return bonuses.get(agent.emergent_skill, {}).get(mission, 0.0)


def cluster_profil(cluster, config):
    skew = max(0.0, float(config.get('cluster_budget_skew', DEFAULT_CLUSTER_BUDGET_SKEW)))
    profiles = {
        'scout_cluster': {
            'budget_weight': max(0.5, 1.0 - 0.35 * skew),
            'demand_multiplier': 0.92,
            'output_multiplier': 0.97,
            'coordination_bonus': 0.04,
            'resilience_bonus': 0.01,
        },
        'synthesis_cluster': {
            'budget_weight': 1.0,
            'demand_multiplier': 1.05,
            'output_multiplier': 1.05,
            'coordination_bonus': 0.03,
            'resilience_bonus': 0.02,
        },
        'response_cluster': {
            'budget_weight': 1.0 + 0.55 * skew,
            'demand_multiplier': 1.12,
            'output_multiplier': 1.12,
            'coordination_bonus': 0.02,
            'resilience_bonus': 0.01,
        },
        'resilience_cluster': {
            'budget_weight': max(0.65, 1.0 - 0.10 * skew),
            'demand_multiplier': 0.96,
            'output_multiplier': 1.00,
            'coordination_bonus': 0.01,
            'resilience_bonus': 0.05,
        },
    }
    return profiles.get(cluster, profiles['synthesis_cluster'])


def setze_faehigkeitscluster(agent, cluster, config, runde):
    cluster = cluster if cluster in CAPABILITY_CLUSTERS else 'synthesis_cluster'
    if agent.capability_cluster != cluster:
        agent.cluster_history.append((runde, agent.capability_cluster, cluster))
    profil = cluster_profil(cluster, config)
    if not config.get('enable_asymmetric_cluster_budgets'):
        profil = {**profil, 'budget_weight': 1.0}
    agent.capability_cluster = cluster
    agent.cluster_budget_weight = profil['budget_weight']
    agent.cluster_demand_multiplier = profil['demand_multiplier']
    agent.cluster_output_multiplier = profil['output_multiplier']
    agent.cluster_coordination_bonus = profil['coordination_bonus']
    agent.cluster_resilience_bonus = profil['resilience_bonus']


def initialisiere_faehigkeitscluster(agenten, config):
    for agent in agenten:
        cluster = faehigkeitscluster_fuer_agent(agent)
        agent.capability_cluster = cluster
        agent.initial_capability_cluster = cluster
        agent.cluster_history = []
        agent.cluster_output_total = 0.0
        agent.bottleneck_pressure = 0.0
        agent.bottleneck_relief_total = 0.0
        agent.resource_rerouted_total = 0.0
        agent.meta_priority_score = 0.0
        agent.meta_aligned_rounds = 0
        agent.meta_focus_history = []
        agent.ist_misinformation_source = False
        agent.misinformation_intensity = 0.0
        agent.cluster_compromise_level = 0.0
        agent.meta_signal_corruption = 0.0
        agent.misinformation_exposure = 0.0
        agent.false_mission_signal = None
        agent.false_cluster_signal = None
        agent.misinformation_events = 0
        agent.misinformation_detected = 0
        setze_faehigkeitscluster(agent, cluster, config, runde=0)


def initialisiere_emergente_faehigkeiten(agenten):
    for agent in agenten:
        fokus = skill_fokus_fuer_cluster(agent.capability_cluster)
        agent.bridge_skill = 0.25
        agent.analysis_skill = 0.25
        agent.defense_skill = 0.25
        agent.recovery_skill = 0.25
        if fokus == 'bridge_specialist':
            agent.bridge_skill += 0.08
        elif fokus == 'analysis_specialist':
            agent.analysis_skill += 0.08
        elif fokus == 'defense_specialist':
            agent.defense_skill += 0.08
        elif fokus == 'recovery_specialist':
            agent.recovery_skill += 0.08
        agent.emergent_skill = 'adaptive_generalist'
        agent.initial_emergent_skill = 'adaptive_generalist'
        agent.emergent_skill_history = []
        agent.group_learning_gain_total = 0.0


def initialisiere_fehlerisolation(agenten):
    for agent in agenten:
        agent.is_quarantined = False
        agent.quarantine_rounds = 0
        agent.quarantine_events = 0
        agent.trust_shield_score = 0.0
        agent.shielding_actions_total = 0
        agent.isolation_relief_total = 0.0


def skill_scores(agent):
    return {
        'bridge_specialist': agent.bridge_skill,
        'analysis_specialist': agent.analysis_skill,
        'defense_specialist': agent.defense_skill,
        'recovery_specialist': agent.recovery_skill,
    }


def setze_emergente_faehigkeit(agent, neue_faehigkeit, runde):
    if agent.emergent_skill != neue_faehigkeit:
        agent.emergent_skill_history.append((runde, agent.emergent_skill, neue_faehigkeit))
    agent.emergent_skill = neue_faehigkeit


def aktualisiere_gruppenlernen(agenten, agenten_dict, config, runde):
    if not config.get('enable_emergent_skills'):
        return {'switches': 0, 'alignment_rate': 0.0, 'learning_gain': 0.0}

    learning_rate = max(0.0, float(config.get('group_learning_rate', DEFAULT_GROUP_LEARNING_RATE)))
    threshold = float(
        config.get('skill_specialization_threshold', DEFAULT_SKILL_SPECIALIZATION_THRESHOLD)
    )
    switches = 0
    aligned = 0
    learning_gain = 0.0
    for agent in agenten:
        nachbarn = [agenten_dict[nid] for nid in agent.nachbarn if nid in agenten_dict]
        same_cluster_neighbors = [
            nachbar for nachbar in nachbarn if nachbar.capability_cluster == agent.capability_cluster
        ]
        coop_signal = agent.kooperations_neigung + 0.5 * agent.meta_priority_score
        rep_signal = agent.reputation + agent.cluster_resilience_bonus
        int_signal = min(1.0, agent.intelligenz / 4.0)
        cluster_focus = skill_fokus_fuer_cluster(agent.capability_cluster)
        bridge_delta = learning_rate * (
            0.30 * coop_signal
            + 0.25 * sum(1 for nachbar in nachbarn if nachbar.gruppe != agent.gruppe) / max(1, len(nachbarn))
            + (0.30 if cluster_focus == 'bridge_specialist' else 0.0)
        )
        analysis_delta = learning_rate * (
            0.28 * int_signal
            + 0.22 * len(same_cluster_neighbors) / max(1, len(nachbarn) or 1)
            + (0.30 if cluster_focus == 'analysis_specialist' else 0.0)
        )
        defense_delta = learning_rate * (
            0.26 * (1.0 - agent.misinformation_exposure)
            + 0.24 * rep_signal
            + (0.30 if cluster_focus == 'defense_specialist' else 0.0)
        )
        recovery_delta = learning_rate * (
            0.26 * rep_signal
            + 0.22 * (1.0 - agent.cluster_compromise_level)
            + (0.30 if cluster_focus == 'recovery_specialist' else 0.0)
        )
        if same_cluster_neighbors:
            bridge_delta += learning_rate * 0.08 * np.mean(
                [nachbar.bridge_skill for nachbar in same_cluster_neighbors]
            )
            analysis_delta += learning_rate * 0.08 * np.mean(
                [nachbar.analysis_skill for nachbar in same_cluster_neighbors]
            )
            defense_delta += learning_rate * 0.08 * np.mean(
                [nachbar.defense_skill for nachbar in same_cluster_neighbors]
            )
            recovery_delta += learning_rate * 0.08 * np.mean(
                [nachbar.recovery_skill for nachbar in same_cluster_neighbors]
            )

        agent.bridge_skill = min(1.0, agent.bridge_skill * (1.0 - learning_rate * 0.08) + bridge_delta)
        agent.analysis_skill = min(
            1.0, agent.analysis_skill * (1.0 - learning_rate * 0.08) + analysis_delta
        )
        agent.defense_skill = min(1.0, agent.defense_skill * (1.0 - learning_rate * 0.08) + defense_delta)
        agent.recovery_skill = min(
            1.0, agent.recovery_skill * (1.0 - learning_rate * 0.08) + recovery_delta
        )
        scores = skill_scores(agent)
        beste_faehigkeit, bester_score = max(scores.items(), key=lambda item: item[1])
        neue_faehigkeit = beste_faehigkeit if bester_score >= threshold else 'adaptive_generalist'
        if neue_faehigkeit == cluster_focus:
            aligned += 1
        if neue_faehigkeit != agent.emergent_skill:
            switches += 1
            setze_emergente_faehigkeit(agent, neue_faehigkeit, runde)
        gain = bridge_delta + analysis_delta + defense_delta + recovery_delta
        agent.group_learning_gain_total += gain
        learning_gain += gain

    return {
        'switches': switches,
        'alignment_rate': aligned / max(1, len(agenten)),
        'learning_gain': learning_gain,
    }


def aktualisiere_fehlerisolation(agenten, agenten_dict, config, runde):
    if not config.get('enable_fault_isolation'):
        for agent in agenten:
            agent.is_quarantined = False
            agent.quarantine_rounds = 0
            agent.trust_shield_score *= 0.85
        return {
            'events': 0,
            'quarantined_agents': 0,
            'quarantined_cells': 0,
            'shielding_actions': 0,
            'shield_mean': 0.0,
            'relief': 0.0,
        }

    compromise_threshold = float(
        config.get('quarantine_compromise_threshold', DEFAULT_QUARANTINE_COMPROMISE_THRESHOLD)
    )
    exposure_threshold = float(
        config.get('quarantine_exposure_threshold', DEFAULT_QUARANTINE_EXPOSURE_THRESHOLD)
    )
    quarantine_duration = max(1, int(config.get('quarantine_duration', DEFAULT_QUARANTINE_DURATION)))
    shield_strength = max(0.0, float(config.get('trust_shield_strength', DEFAULT_TRUST_SHIELD_STRENGTH)))

    cell_members = defaultdict(list)
    for agent in agenten:
        cell_members[agent.workflow_cell].append(agent)

    quarantined_cells = set()
    for cell, members in cell_members.items():
        compromise_mean = float(np.mean([agent.cluster_compromise_level for agent in members]))
        exposure_mean = float(np.mean([agent.misinformation_exposure for agent in members]))
        detection_mean = float(
            np.mean(
                [
                    agent.misinformation_detected / max(1, agent.misinformation_events)
                    if agent.misinformation_events
                    else 0.0
                    for agent in members
                ]
            )
        )
        if (
            compromise_mean >= compromise_threshold * 1.15
            or exposure_mean >= exposure_threshold * 1.15
            or (compromise_mean + exposure_mean) * 0.5 + detection_mean * 0.10
            >= compromise_threshold * 1.05
        ):
            quarantined_cells.add(cell)

    events = 0
    shielding_actions = 0
    relief_total = 0.0
    for agent in agenten:
        high_risk = (
            agent.cluster_compromise_level >= compromise_threshold
            or agent.misinformation_exposure >= exposure_threshold
            or agent.meta_signal_corruption >= compromise_threshold * 0.85
        )
        should_quarantine = high_risk or agent.workflow_cell in quarantined_cells
        if should_quarantine:
            if not agent.is_quarantined:
                events += 1
                agent.quarantine_events += 1
            agent.is_quarantined = True
            agent.quarantine_rounds = max(agent.quarantine_rounds, quarantine_duration)
            agent.task_priority = max(0.18, agent.task_priority * 0.82)
            agent.resource_credit *= 0.90
            agent.meta_priority_score *= 0.92
            if agent.workflow_stage != 'recovery':
                agent.workflow_history.append((runde, agent.workflow_stage, 'recovery'))
                agent.workflow_stage = 'recovery'
                agent.stage_tenure = 0
        elif agent.is_quarantined:
            agent.quarantine_rounds = max(0, agent.quarantine_rounds - 1)
            if (
                agent.quarantine_rounds == 0
                and agent.cluster_compromise_level < compromise_threshold * 0.70
                and agent.misinformation_exposure < exposure_threshold * 0.70
                and agent.meta_signal_corruption < compromise_threshold * 0.60
            ):
                agent.is_quarantined = False

    quarantined_agents = [agent for agent in agenten if agent.is_quarantined]
    for agent in agenten:
        if agent.is_quarantined:
            agent.trust_shield_score *= 0.65
            continue
        quarantined_neighbors = [
            agenten_dict[nid]
            for nid in agent.nachbarn
            if nid in agenten_dict and agenten_dict[nid].is_quarantined
        ]
        same_cell_quarantine = agent.workflow_cell in quarantined_cells
        if quarantined_neighbors or same_cell_quarantine:
            agent.trust_shield_score = min(
                1.0,
                agent.trust_shield_score * 0.85
                + shield_strength
                + 0.06 * agent.cluster_resilience_bonus
                + 0.08 * (agent.emergent_skill == 'defense_specialist'),
            )
            shielding_actions += 1
            agent.shielding_actions_total += 1
            before = (
                agent.cluster_compromise_level
                + agent.meta_signal_corruption
                + agent.misinformation_exposure
            )
            agent.cluster_compromise_level = max(
                0.0, agent.cluster_compromise_level - shield_strength * 0.22
            )
            agent.meta_signal_corruption = max(
                0.0, agent.meta_signal_corruption - shield_strength * 0.24
            )
            agent.misinformation_exposure = max(
                0.0, agent.misinformation_exposure - shield_strength * 0.20
            )
            after = (
                agent.cluster_compromise_level
                + agent.meta_signal_corruption
                + agent.misinformation_exposure
            )
            relief = max(0.0, before - after)
            relief_total += relief
            agent.isolation_relief_total += relief
        else:
            agent.trust_shield_score *= 0.92

    return {
        'events': events,
        'quarantined_agents': len(quarantined_agents),
        'quarantined_cells': len(quarantined_cells),
        'shielding_actions': shielding_actions,
        'shield_mean': float(np.mean([agent.trust_shield_score for agent in agenten])) if agenten else 0.0,
        'relief': relief_total,
    }


def weise_misinformation_quellen_zu(agenten, config):
    if not config.get('enable_prompt_injection'):
        return
    source_count = max(1, min(len(agenten), int(config.get('injection_source_count', DEFAULT_INJECTION_SOURCE_COUNT))))
    bevorzugte = [
        agent for agent in agenten if agent.capability_cluster in {'synthesis_cluster', 'response_cluster'}
    ]
    kandidaten = bevorzugte if len(bevorzugte) >= source_count else list(agenten)
    random.shuffle(kandidaten)
    for agent in kandidaten[:source_count]:
        agent.ist_misinformation_source = True
        agent.misinformation_intensity = float(config.get('injection_strength', DEFAULT_INJECTION_STRENGTH))
        agent.reputation = max(0.18, agent.reputation - 0.10)


def manipulations_zielmission(agent):
    if agent.capability_cluster == 'response_cluster':
        return MISSION_DEFENSE
    if agent.capability_cluster == 'resilience_cluster':
        return MISSION_STABILITY
    if agent.capability_cluster == 'scout_cluster':
        return MISSION_KNOWLEDGE
    return MISSION_SUPPORT


def manipulations_zielcluster(agent):
    mapping = {
        'synthesis_cluster': 'response_cluster',
        'response_cluster': 'resilience_cluster',
        'resilience_cluster': 'synthesis_cluster',
        'scout_cluster': 'response_cluster',
    }
    return mapping.get(agent.capability_cluster, 'response_cluster')


def wende_promptinjektion_an(agenten, agenten_dict, config, runde):
    if not config.get('enable_prompt_injection'):
        for agent in agenten:
            agent.cluster_compromise_level *= 0.90
            agent.meta_signal_corruption *= 0.85
            agent.misinformation_exposure *= 0.80
        return {'events': 0, 'detections': 0, 'corruption': 0.0, 'compromise': 0.0}

    attack_round = int(config.get('injection_attack_round', DEFAULT_INJECTION_ATTACK_ROUND))
    if runde < attack_round:
        return {'events': 0, 'detections': 0, 'corruption': 0.0, 'compromise': 0.0}

    attack_strength = max(0.0, float(config.get('injection_strength', DEFAULT_INJECTION_STRENGTH)))
    events = 0
    detections = 0
    for agent in agenten:
        if not agent.ist_misinformation_source:
            agent.cluster_compromise_level *= 0.90
            agent.meta_signal_corruption *= 0.85
            agent.misinformation_exposure *= 0.80
            continue
        if config.get('enable_fault_isolation') and agent.is_quarantined:
            agent.misinformation_intensity *= 0.92
            continue
        nachbarn = [agenten_dict[nid] for nid in agent.nachbarn if nid in agenten_dict]
        for ziel in nachbarn:
            effective_strength = attack_strength
            if config.get('enable_fault_isolation'):
                effective_strength *= max(0.15, 1.0 - 0.80 * ziel.trust_shield_score)
                if ziel.is_quarantined:
                    effective_strength *= 0.45
            if random.random() >= effective_strength:
                continue
            ziel.misinformation_exposure = min(1.0, ziel.misinformation_exposure + effective_strength * 0.8)
            ziel.cluster_compromise_level = min(1.0, ziel.cluster_compromise_level + effective_strength * 0.45)
            ziel.meta_signal_corruption = min(1.0, ziel.meta_signal_corruption + effective_strength * 0.40)
            ziel.false_mission_signal = manipulations_zielmission(agent)
            ziel.false_cluster_signal = manipulations_zielcluster(agent)
            ziel.misinformation_events += 1
            events += 1
            detection_score = (
                ziel.reputation
                + ziel.cluster_resilience_bonus
                + ziel.meta_priority_score
                + ziel.trust_shield_score * 0.45
                + (0.10 if ziel.emergent_skill == 'defense_specialist' else 0.0)
            )
            if detection_score >= 0.82:
                ziel.misinformation_detected += 1
                ziel.cluster_compromise_level = max(0.0, ziel.cluster_compromise_level - 0.18)
                ziel.meta_signal_corruption = max(0.0, ziel.meta_signal_corruption - 0.16)
                ziel.misinformation_exposure = max(0.0, ziel.misinformation_exposure - 0.14)
                detections += 1

    corruption = float(np.mean([agent.meta_signal_corruption for agent in agenten])) if agenten else 0.0
    compromise = float(np.mean([agent.cluster_compromise_level for agent in agenten])) if agenten else 0.0
    return {
        'events': events,
        'detections': detections,
        'corruption': corruption,
        'compromise': compromise,
    }


def aktualisiere_meta_koordination(agenten, config, runde, mission_success_counts, mission_contact_counts):
    if not config.get('enable_meta_coordination'):
        for agent in agenten:
            agent.meta_priority_score *= 0.7
        return {
            'switches': 0,
            'alignment_rate': 0.0,
            'priority_mission': None,
            'priority_cluster': None,
        }

    interval = max(1, int(config.get('meta_update_interval', DEFAULT_META_UPDATE_INTERVAL)))
    strength = max(0.0, float(config.get('meta_priority_strength', DEFAULT_META_PRIORITY_STRENGTH)))
    mission_scores = {
        mission: mission_success_counts[mission] / max(1, mission_contact_counts[mission])
        for mission in MISSION_TYPES
    }
    priority_mission = min(mission_scores, key=mission_scores.get)

    cluster_pressures = defaultdict(list)
    for agent in agenten:
        cluster_pressures[agent.capability_cluster].append(agent.bottleneck_pressure)
    if cluster_pressures:
        priority_cluster = max(
            cluster_pressures,
            key=lambda cluster: float(np.mean(cluster_pressures[cluster])) + (
                0.08 if cluster == cluster_fuer_mission(priority_mission) else 0.0
            ),
        )
    else:
        priority_cluster = cluster_fuer_mission(priority_mission)

    if config.get('enable_prompt_injection'):
        corrupt_agents = [agent for agent in agenten if agent.meta_signal_corruption > 0.0]
        if corrupt_agents:
            falsche_cluster = [agent.false_cluster_signal for agent in corrupt_agents if agent.false_cluster_signal]
            falsche_missionen = [agent.false_mission_signal for agent in corrupt_agents if agent.false_mission_signal]
            corruption_mean = float(np.mean([agent.meta_signal_corruption for agent in corrupt_agents]))
            if falsche_cluster and corruption_mean >= 0.22:
                priority_cluster = max(set(falsche_cluster), key=falsche_cluster.count)
            if falsche_missionen and corruption_mean >= 0.24:
                priority_mission = max(set(falsche_missionen), key=falsche_missionen.count)

    switches = 0
    aligned = 0
    if runde % interval == 0:
        for agent in agenten:
            aligned_now = (
                agent.capability_cluster == priority_cluster
                or agent.mission == priority_mission
                or cluster_fuer_mission(agent.mission) == priority_cluster
            )
            if aligned_now:
                aligned += 1
                agent.meta_aligned_rounds += 1
                neue_prioritaet = min(
                    1.0,
                    agent.meta_priority_score * 0.7 + strength + 0.10 * agent.cluster_coordination_bonus,
                )
            else:
                neue_prioritaet = max(0.0, agent.meta_priority_score * 0.65)
            if abs(neue_prioritaet - agent.meta_priority_score) > 1e-9:
                switches += 1
            agent.meta_priority_score = neue_prioritaet
            agent.meta_focus_history.append((runde, priority_mission, priority_cluster, aligned_now))
            if aligned_now:
                agent.task_priority = min(1.0, agent.task_priority + 0.16 + strength * 0.35)
                if agent.capability_cluster == priority_cluster:
                    agent.cluster_output_multiplier = min(1.45, agent.cluster_output_multiplier + 0.06)
            if agent.meta_signal_corruption > 0.0:
                agent.meta_priority_score = max(0.0, agent.meta_priority_score - 0.08 * agent.meta_signal_corruption)
        alignment_rate = aligned / max(1, len(agenten))
    else:
        for agent in agenten:
            agent.meta_priority_score *= 0.96
        alignment_rate = sum(1 for agent in agenten if agent.meta_priority_score >= strength * 0.5) / max(1, len(agenten))

    return {
        'switches': switches,
        'alignment_rate': alignment_rate,
        'priority_mission': priority_mission,
        'priority_cluster': priority_cluster,
    }


def workflow_voraussetzungen_erfuellt(agent, agenten_dict, config):
    if not config.get('enable_workflow_stages'):
        return True

    nachbarn = [agenten_dict[nid] for nid in agent.nachbarn if nid in agenten_dict]
    stage = agent.workflow_stage
    min_tenure = max(1, int(config.get('workflow_stage_min_tenure', DEFAULT_WORKFLOW_STAGE_MIN_TENURE)))

    if stage in {'task_queue', 'recovery'}:
        return True
    if stage == 'discovery':
        return sum(1 for nachbar in nachbarn if nachbar.gruppe != agent.gruppe) >= 1
    if stage == 'preparation':
        return agent.reputation >= 0.45
    if stage == 'execution':
        kooperative_partner = 0
        for partner_id, history in agent.interaktions_history.items():
            if history and history[-1] == 'C':
                kooperative_partner += 1
        return kooperative_partner >= 2
    if stage == 'consolidation':
        return agent.stage_tenure >= min_tenure and agent.reputation >= 0.5
    return True


def workflow_handoff_erlaubt(quelle, ziel):
    erlaubte_pfade = {
        ('interface_cell', 'analysis_cell'),
        ('analysis_cell', 'execution_cell'),
        ('execution_cell', 'stability_cell'),
        ('stability_cell', 'interface_cell'),
    }
    return (quelle, ziel) in erlaubte_pfade


def koordiniere_workflow_handoff(agent, partner, aktion_a, aktion_p, runde, config):
    if not (config.get('enable_workflow_cells') and config.get('enable_handoff_coordination')):
        return []
    if aktion_a != 'C' or aktion_p != 'C':
        return []

    handoffs = []
    bonus = float(config.get('handoff_priority_bonus', DEFAULT_HANDOFF_PRIORITY_BONUS))
    if workflow_handoff_erlaubt(agent.workflow_cell, partner.workflow_cell):
        partner.handoff_credit = min(1.0, partner.handoff_credit + bonus)
        partner.handoff_received += 1
        agent.handoff_given += 1
        agent.handoff_history.append((runde, agent.workflow_cell, partner.workflow_cell, partner.id))
        handoffs.append((agent.id, partner.id))
    if workflow_handoff_erlaubt(partner.workflow_cell, agent.workflow_cell):
        agent.handoff_credit = min(1.0, agent.handoff_credit + bonus)
        agent.handoff_received += 1
        partner.handoff_given += 1
        partner.handoff_history.append((runde, partner.workflow_cell, agent.workflow_cell, agent.id))
        handoffs.append((partner.id, agent.id))
    return handoffs


def koordiniere_ressourcen(agenten, config):
    if not (config.get('enable_workflow_cells') and config.get('enable_resource_coordination')):
        return {
            'shared': 0.0,
            'active_cells': 0,
            'effective_output': 0.0,
            'bottlenecks': 0,
            'relief': 0.0,
            'rerouted': 0.0,
        }

    budget = max(0.0, float(config.get('resource_budget', DEFAULT_RESOURCE_BUDGET)))
    share_factor = max(0.0, float(config.get('resource_share_factor', DEFAULT_RESOURCE_SHARE_FACTOR)))
    cell_members = defaultdict(list)
    cell_demand = defaultdict(float)

    for agent in agenten:
        cell_members[agent.workflow_cell].append(agent)
        skill_focus = skill_fokus_fuer_cluster(agent.capability_cluster)
        skill_alignment = 1.0 if agent.emergent_skill == skill_focus else 0.0
        quarantine_penalty = 0.70 if agent.is_quarantined else 1.0
        demand = (
            agent.task_priority
            + agent.handoff_credit * 0.5
            + agent.reputation * 0.1
            + agent.meta_priority_score * 0.35
            + skill_alignment * 0.12
            + agent.trust_shield_score * 0.08
        ) * agent.cluster_demand_multiplier * quarantine_penalty
        cell_demand[agent.workflow_cell] += demand
        agent.resource_credit *= 0.85
        agent.bottleneck_pressure *= 0.75

    total_demand = sum(cell_demand.values())
    active_cells = sum(1 for demand in cell_demand.values() if demand > 0.0)
    if total_demand <= 0.0 or budget <= 0.0:
        return {
            'shared': 0.0,
            'active_cells': active_cells,
            'effective_output': 0.0,
            'bottlenecks': 0,
            'relief': 0.0,
            'rerouted': 0.0,
        }

    cell_weighted_demand = {}
    for cell, members in cell_members.items():
        cluster_weight = 1.0
        if config.get('enable_capability_clusters') and members:
            cluster_weight = float(
                np.mean([agent.cluster_budget_weight * (1.0 + 0.25 * agent.meta_priority_score) for agent in members])
            )
        cell_weighted_demand[cell] = cell_demand[cell] * cluster_weight
    weighted_total = max(1e-9, sum(cell_weighted_demand.values()))

    base_allocations = {
        cell: budget * (weighted_demand / weighted_total)
        for cell, weighted_demand in cell_weighted_demand.items()
    }

    threshold = float(config.get('bottleneck_threshold', DEFAULT_BOTTLENECK_THRESHOLD))
    triage_intensity = max(0.0, min(1.0, float(
        config.get('bottleneck_triage_intensity', DEFAULT_BOTTLENECK_TRIAGE_INTENSITY)
    )))
    cell_pressure = {}
    for cell, demand in cell_demand.items():
        pressure = demand / max(1e-9, base_allocations.get(cell, 0.0))
        cell_pressure[cell] = pressure
    mean_pressure = float(np.mean(list(cell_pressure.values()))) if cell_pressure else 0.0
    bottleneck_limit = max(threshold, mean_pressure * 1.03)
    donor_limit = mean_pressure * 0.97 if mean_pressure > 0.0 else threshold
    bottleneck_cells = [cell for cell, pressure in cell_pressure.items() if pressure > bottleneck_limit]

    rerouted_budget = 0.0
    relief_total = 0.0
    allocations = dict(base_allocations)
    if config.get('enable_bottleneck_management') and bottleneck_cells:
        donors = [
            cell for cell, pressure in cell_pressure.items()
            if cell not in bottleneck_cells and pressure <= donor_limit and allocations.get(cell, 0.0) > 0.0
        ]
        if not donors:
            ordered_cells = sorted(cell_pressure.items(), key=lambda item: item[1])
            donors = [cell for cell, _ in ordered_cells[: max(1, len(ordered_cells) // 2)] if cell not in bottleneck_cells]
        donor_budget = sum(allocations.get(cell, 0.0) for cell in donors)
        donor_capacity = min(donor_budget * 0.55, budget * 0.35)
        triage_pool = donor_capacity * triage_intensity
        if triage_pool > 0.0:
            donor_total = sum(
                max(0.15, mean_pressure - cell_pressure.get(cell, mean_pressure) + 0.25)
                for cell in donors
            )
            for donor in donors:
                donor_share = max(0.15, mean_pressure - cell_pressure.get(donor, mean_pressure) + 0.25)
                transfer = triage_pool * (donor_share / max(1e-9, donor_total))
                allocations[donor] = max(0.0, allocations[donor] - transfer)
                rerouted_budget += transfer
            bottleneck_total = sum(max(0.0, cell_pressure[cell] - mean_pressure) for cell in bottleneck_cells)
            for cell in bottleneck_cells:
                severity = max(0.0, cell_pressure[cell] - mean_pressure)
                transfer = triage_pool * (severity / max(1e-9, bottleneck_total))
                allocations[cell] += transfer
                relief_total += transfer

    if not config.get('enable_parallel_workflow_cells'):
        dominant_cell = max(cell_demand, key=cell_demand.get)
        dominant_members = cell_members[dominant_cell]
        if not dominant_members:
            return {
                'shared': 0.0,
                'active_cells': 0,
                'effective_output': 0.0,
                'bottlenecks': len(bottleneck_cells),
                'relief': relief_total,
                'rerouted': rerouted_budget,
            }
        share_per_agent = budget / len(dominant_members)
        total_shared = 0.0
        total_output = 0.0
        for agent in dominant_members:
            resource_bonus = share_per_agent * share_factor
            if agent.is_quarantined:
                resource_bonus *= 0.75
            agent.resource_credit = min(1.0, agent.resource_credit + resource_bonus)
            agent.resource_received_total += resource_bonus
            agent.resource_shared_total += budget / len(agenten)
            output_gain = resource_bonus * agent.cluster_output_multiplier * (
                0.5
                + agent.task_priority
                + 0.25 * agent.meta_priority_score
                + (0.12 if agent.emergent_skill == skill_fokus_fuer_cluster(agent.capability_cluster) else 0.0)
            )
            agent.cluster_output_total += output_gain
            agent.bottleneck_pressure = max(agent.bottleneck_pressure, cell_pressure.get(dominant_cell, 0.0))
            total_shared += resource_bonus
            total_output += output_gain
        return {
            'shared': total_shared,
            'active_cells': 1,
            'effective_output': total_output,
            'bottlenecks': len(bottleneck_cells),
            'relief': relief_total,
            'rerouted': rerouted_budget,
        }

    total_shared = 0.0
    total_output = 0.0
    for cell, demand in cell_demand.items():
        members = cell_members[cell]
        if not members:
            continue
        allocation = allocations.get(cell, 0.0)
        share_per_agent = allocation / len(members)
        triage_bonus = 1.0
        if config.get('enable_bottleneck_management') and cell in bottleneck_cells and relief_total > 0.0:
            triage_bonus += 0.25 + 0.35 * min(1.0, relief_total / max(1e-9, budget))
        for agent in members:
            resource_bonus = share_per_agent * share_factor
            if agent.is_quarantined:
                resource_bonus *= 0.75
            agent.resource_credit = min(1.0, agent.resource_credit + resource_bonus)
            agent.resource_received_total += resource_bonus
            agent.resource_shared_total += allocation / len(agenten)
            output_gain = (
                resource_bonus
                * agent.cluster_output_multiplier
                * (
                    0.5
                    + agent.task_priority
                    + 0.25 * agent.meta_priority_score
                    + (0.12 if agent.emergent_skill == skill_fokus_fuer_cluster(agent.capability_cluster) else 0.0)
                )
                * triage_bonus
            )
            agent.cluster_output_total += output_gain
            agent.bottleneck_pressure = max(agent.bottleneck_pressure, cell_pressure.get(cell, 0.0))
            if cell in bottleneck_cells:
                relief_share = relief_total / len(members)
                agent.bottleneck_relief_total += relief_share
                agent.resource_rerouted_total += rerouted_budget / max(1, len(agenten))
            total_shared += resource_bonus
            total_output += output_gain

    return {
        'shared': total_shared,
        'active_cells': active_cells,
        'effective_output': total_output,
        'bottlenecks': len(bottleneck_cells),
        'relief': relief_total,
        'rerouted': rerouted_budget,
    }


def missionskonflikt(mission_a, mission_b):
    if mission_a == mission_b:
        return 0.0

    matrix = {
        frozenset({MISSION_CONSENSUS, MISSION_DEFENSE}): 0.75,
        frozenset({MISSION_CONSENSUS, MISSION_STABILITY}): 0.30,
        frozenset({MISSION_CONSENSUS, MISSION_KNOWLEDGE}): 0.12,
        frozenset({MISSION_KNOWLEDGE, MISSION_DEFENSE}): 0.45,
        frozenset({MISSION_KNOWLEDGE, MISSION_STABILITY}): 0.40,
        frozenset({MISSION_DEFENSE, MISSION_SUPPORT}): 0.35,
        frozenset({MISSION_STABILITY, MISSION_SUPPORT}): 0.18,
    }
    return matrix.get(frozenset({mission_a, mission_b}), 0.10)


def missions_rollenfit(role, mission):
    basis = {
        'generalist': {
            MISSION_SUPPORT: 0.08,
            MISSION_KNOWLEDGE: 0.05,
            MISSION_CONSENSUS: 0.04,
        },
        'connector': {
            MISSION_KNOWLEDGE: 0.12,
            MISSION_CONSENSUS: 0.05,
        },
        'sentinel': {
            MISSION_DEFENSE: 0.14,
            MISSION_STABILITY: 0.04,
        },
        'mediator': {
            MISSION_CONSENSUS: 0.14,
            MISSION_KNOWLEDGE: 0.04,
        },
        'analyzer': {
            MISSION_STABILITY: 0.12,
            MISSION_DEFENSE: 0.05,
        },
    }
    return basis.get(role, {}).get(mission, 0.0)


def berechne_missionsfitness(agent, agenten_dict):
    nachbarn = [agenten_dict[nachbar_id] for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict]
    if nachbarn:
        cross_group_share = sum(1 for nachbar in nachbarn if nachbar.gruppe != agent.gruppe) / len(nachbarn)
        mean_partner_reputation = float(
            np.mean([agent.berechne_partner_reputation(nachbar.id) for nachbar in nachbarn])
        )
        mean_neighbor_distance = float(np.mean([abs(agent.meinung - nachbar.meinung) for nachbar in nachbarn]))
    else:
        cross_group_share = 0.0
        mean_partner_reputation = 0.5
        mean_neighbor_distance = 0.0

    fitness = {
        MISSION_CONSENSUS: (
            missions_rollenfit(agent.role, MISSION_CONSENSUS)
            + 0.18 * cross_group_share
            + 0.08 * agent.kooperations_neigung
            + 0.06 * max(0.0, 1.0 - abs(agent.meinung - 0.5) * 2.0)
            + 0.05 * agent.handoff_credit
            + 0.06 * agent.resource_credit
            + 0.05 * agent.cluster_coordination_bonus
            + 0.05 * agent.meta_priority_score
            + skill_bonus_fuer_mission(agent, MISSION_CONSENSUS)
            + 0.04 * agent.trust_shield_score
            - (0.05 if agent.is_quarantined else 0.0)
            - 0.05 * agent.cluster_compromise_level
        ),
        MISSION_KNOWLEDGE: (
            missions_rollenfit(agent.role, MISSION_KNOWLEDGE)
            + 0.16 * cross_group_share
            + 0.05 * agent.intelligenz / 6.0
            + 0.04 * mean_neighbor_distance
            + 0.06 * agent.handoff_credit
            + 0.07 * agent.resource_credit
            + 0.04 * agent.cluster_output_multiplier
            + 0.06 * agent.meta_priority_score
            + skill_bonus_fuer_mission(agent, MISSION_KNOWLEDGE)
            + 0.05 * agent.trust_shield_score
            - (0.04 if agent.is_quarantined else 0.0)
            - 0.04 * agent.cluster_compromise_level
        ),
        MISSION_DEFENSE: (
            missions_rollenfit(agent.role, MISSION_DEFENSE)
            + 0.18 * max(0.0, 0.55 - mean_partner_reputation)
            + 0.08 * agent.reputation
            + 0.05 * (1.0 - agent.kooperations_neigung)
            + 0.05 * agent.handoff_credit
            + 0.05 * agent.resource_credit
            + 0.05 * agent.cluster_resilience_bonus
            + 0.05 * agent.meta_priority_score
            + 0.04 * agent.misinformation_exposure
            + skill_bonus_fuer_mission(agent, MISSION_DEFENSE)
            + 0.06 * agent.trust_shield_score
            - (0.01 if agent.is_quarantined else 0.0)
        ),
        MISSION_STABILITY: (
            missions_rollenfit(agent.role, MISSION_STABILITY)
            + 0.14 * max(0.0, 0.35 - mean_neighbor_distance)
            + 0.06 * agent.reputation
            + 0.04 * (1.0 - cross_group_share)
            + 0.04 * agent.handoff_credit
            + 0.05 * agent.resource_credit
            + 0.06 * agent.cluster_resilience_bonus
            + 0.05 * agent.meta_priority_score
            + 0.04 * agent.misinformation_exposure
            + skill_bonus_fuer_mission(agent, MISSION_STABILITY)
            + 0.06 * agent.trust_shield_score
            - (0.01 if agent.is_quarantined else 0.0)
        ),
        MISSION_SUPPORT: (
            missions_rollenfit(agent.role, MISSION_SUPPORT)
            + 0.05 * agent.kooperations_neigung
            + 0.04 * mean_partner_reputation
            + 0.03 * agent.handoff_credit
            + 0.04 * agent.resource_credit
            + 0.04 * agent.cluster_coordination_bonus
            + 0.04 * agent.meta_priority_score
            + skill_bonus_fuer_mission(agent, MISSION_SUPPORT)
            + 0.04 * agent.trust_shield_score
            - (0.03 if agent.is_quarantined else 0.0)
            - 0.05 * agent.meta_signal_corruption
        ),
    }

    if agent.mission in fitness:
        fitness[agent.mission] += 0.03
    if agent.false_mission_signal in fitness:
        fitness[agent.false_mission_signal] += 0.10 * agent.meta_signal_corruption
    return fitness


def erkenne_missionskonflikte(fitness, config):
    sortiert = sorted(fitness.items(), key=lambda item: item[1], reverse=True)
    if len(sortiert) < 2:
        return {'count': 0, 'top_conflict': 0.0, 'top_pair': None}

    top_conflict = missionskonflikt(sortiert[0][0], sortiert[1][0])
    threshold = float(config.get('mission_conflict_threshold', DEFAULT_MISSION_CONFLICT_THRESHOLD))
    konflikt_count = 0
    for index, (mission_a, score_a) in enumerate(sortiert):
        for mission_b, score_b in sortiert[index + 1 :]:
            if abs(score_a - score_b) <= 0.12 and missionskonflikt(mission_a, mission_b) >= threshold:
                konflikt_count += 1

    return {
        'count': konflikt_count,
        'top_conflict': top_conflict,
        'top_pair': (sortiert[0][0], sortiert[1][0]),
    }


def arbitriere_mission(agent, fitness, conflict_info, config):
    sortiert = sorted(fitness.items(), key=lambda item: item[1], reverse=True)
    beste_mission, bester_score = sortiert[0]
    if len(sortiert) == 1:
        return {
            'mission': beste_mission,
            'activated': False,
            'considered': False,
            'fitness_gain': 0.0,
            'conflicts': conflict_info['count'],
        }

    zweite_mission, zweiter_score = sortiert[1]
    margin = float(config.get('mission_arbitration_margin', DEFAULT_MISSION_ARBITRATION_MARGIN))
    role_default = mission_fuer_rolle(agent.role)
    chosen_mission = beste_mission
    activated = False
    considered = False

    if conflict_info['top_conflict'] >= float(
        config.get('mission_conflict_threshold', DEFAULT_MISSION_CONFLICT_THRESHOLD)
    ):
        considered = True
        if bester_score - zweiter_score <= margin:
            if agent.mission in {beste_mission, zweite_mission}:
                chosen_mission = agent.mission
            elif role_default in {beste_mission, zweite_mission}:
                chosen_mission = role_default
            elif zweite_mission == MISSION_STABILITY and agent.reputation >= 0.58:
                chosen_mission = zweite_mission
            elif zweite_mission == MISSION_DEFENSE and agent.reputation < 0.5:
                chosen_mission = zweite_mission
            activated = chosen_mission != beste_mission

    if (
        config.get('enable_prompt_injection')
        and agent.false_mission_signal in fitness
        and agent.meta_signal_corruption >= 0.18
        and agent.false_mission_signal != chosen_mission
    ):
        if fitness[agent.false_mission_signal] + margin * 0.5 >= fitness.get(chosen_mission, 0.0):
            chosen_mission = agent.false_mission_signal
            activated = True

    fitness_gain = fitness[chosen_mission] - fitness.get(role_default, 0.0)
    return {
        'mission': chosen_mission,
        'activated': activated,
        'considered': considered,
        'fitness_gain': fitness_gain,
        'conflicts': conflict_info['count'],
    }


def setze_mission(agent, mission, runde):
    if agent.mission != mission:
        agent.mission_transition_history.append((runde, agent.mission, mission))
        agent.mission_tenure = 0
    agent.mission = mission


def initialisiere_missionen(agenten, config=None):
    for agent in agenten:
        mission = mission_fuer_rolle(agent.role)
        agent.mission = mission
        agent.initial_mission = mission
        agent.mission_tenure = 0
        agent.mission_transition_history = []
        agent.mission_candidates = []
        agent.mission_last_fitness = {}
        agent.mission_arbitration_history = []
    initialisiere_workflows(agenten)
    if config and config.get('enable_capability_clusters'):
        initialisiere_faehigkeitscluster(agenten, config)
    if config and config.get('enable_emergent_skills'):
        initialisiere_emergente_faehigkeiten(agenten)
    if config and config.get('enable_fault_isolation'):
        initialisiere_fehlerisolation(agenten)


def aktualisiere_missionen(agenten, agenten_dict, config, runde):
    if not config.get('enable_missions'):
        return {'switches': 0, 'arbitrations': 0, 'conflicts': 0, 'fitness_gain': 0.0}

    assignment = str(config.get('mission_assignment', 'static'))
    if assignment not in {'adaptive', 'arbitrated'}:
        return {'switches': 0, 'arbitrations': 0, 'conflicts': 0, 'fitness_gain': 0.0}

    interval = max(1, int(config.get('mission_switch_interval', DEFAULT_MISSION_SWITCH_INTERVAL)))
    if runde % interval != 0:
        return {'switches': 0, 'arbitrations': 0, 'conflicts': 0, 'fitness_gain': 0.0}

    switches = 0
    arbitrations = 0
    conflicts = 0
    fitness_gain = 0.0
    for agent in agenten:
        if assignment == 'adaptive':
            neue_mission = mission_fuer_rolle(agent.role)
            if agent.role == 'generalist':
                if agent.reputation >= 0.62 and agent.kooperations_neigung >= 0.60:
                    neue_mission = MISSION_KNOWLEDGE
                elif agent.reputation < 0.45:
                    neue_mission = MISSION_DEFENSE
        else:
            fitness = berechne_missionsfitness(agent, agenten_dict)
            conflict_info = erkenne_missionskonflikte(fitness, config)
            arbitration = arbitriere_mission(agent, fitness, conflict_info, config)
            agent.mission_candidates = sorted(fitness.items(), key=lambda item: item[1], reverse=True)
            agent.mission_last_fitness = dict(fitness)
            agent.mission_arbitration_history.append(
                {
                    'round': runde,
                    'mission': arbitration['mission'],
                    'activated': arbitration['activated'],
                    'considered': arbitration['considered'],
                    'conflicts': conflict_info['count'],
                }
            )
            neue_mission = arbitration['mission']
            arbitrations += int(arbitration['considered'])
            conflicts += conflict_info['count']
            fitness_gain += arbitration['fitness_gain']
        if agent.mission != neue_mission:
            setze_mission(agent, neue_mission, runde)
            switches += 1
        if config.get('enable_workflow_stages'):
            agent.task_priority = max(0.0, min(1.0, agent.mission_last_fitness.get(neue_mission, 0.5)))
            zielstufe = workflow_stufe_fuer_mission(neue_mission)
            setze_workflow_stufe(agent, zielstufe, runde)
            agent.dependencies_met = workflow_voraussetzungen_erfuellt(agent, agenten_dict, config)
            if not agent.dependencies_met:
                setze_workflow_stufe(agent, 'task_queue', runde)
        if config.get('enable_workflow_cells'):
            setze_workflow_zelle(agent, workflow_zelle_fuer_agent(agent), runde)
            if config.get('enable_capability_clusters'):
                setze_faehigkeitscluster(agent, faehigkeitscluster_fuer_agent(agent), config, runde)
    return {
        'switches': switches,
        'arbitrations': arbitrations,
        'conflicts': conflicts,
        'fitness_gain': fitness_gain,
    }


def missions_bonus(agent, partner_reputation, partner, ist_cross_group):
    cooperation_bonus = 0.0
    opinion_pull = 0.0

    if agent.mission == MISSION_CONSENSUS and ist_cross_group:
        cooperation_bonus += 0.05
        opinion_pull += 0.04
    elif agent.mission == MISSION_KNOWLEDGE and ist_cross_group:
        cooperation_bonus += 0.06
    elif agent.mission == MISSION_DEFENSE and partner_reputation < DEFAULT_SENTINEL_REP_THRESHOLD:
        cooperation_bonus -= 0.08
    elif agent.mission == MISSION_STABILITY and not ist_cross_group and abs(agent.meinung - partner.meinung) < 0.2:
        cooperation_bonus += 0.03
    elif agent.mission == MISSION_SUPPORT and partner_reputation >= 0.5:
        cooperation_bonus += 0.01

    cooperation_bonus += agent.cluster_coordination_bonus * (0.6 if ist_cross_group else 0.3)
    opinion_pull += agent.cluster_resilience_bonus * 0.2
    cooperation_bonus += agent.meta_priority_score * (0.35 if ist_cross_group else 0.18)
    opinion_pull += agent.meta_priority_score * 0.08
    cooperation_bonus += agent.trust_shield_score * (0.14 if ist_cross_group else 0.06)
    if agent.is_quarantined:
        cooperation_bonus -= 0.06 if ist_cross_group else 0.02
        opinion_pull -= 0.02
    if agent.emergent_skill == 'bridge_specialist' and ist_cross_group:
        cooperation_bonus += 0.05
        opinion_pull += 0.03
    elif agent.emergent_skill == 'analysis_specialist' and ist_cross_group:
        cooperation_bonus += 0.03
    elif agent.emergent_skill == 'defense_specialist' and partner_reputation < 0.5:
        cooperation_bonus -= 0.04
    elif agent.emergent_skill == 'recovery_specialist':
        cooperation_bonus += 0.02
        opinion_pull += 0.02

    return cooperation_bonus, opinion_pull


def weise_rollen_zu(agenten, config):
    shares = normalisiere_rollenanteile(config)
    agent_count = len(agenten)
    connector_count = int(round(agent_count * shares['connector']))
    sentinel_count = int(round(agent_count * shares['sentinel']))
    mediator_count = int(round(agent_count * shares['mediator']))
    analyzer_count = int(round(agent_count * shares['analyzer']))
    connector_count = min(agent_count, connector_count)
    sentinel_count = min(agent_count - connector_count, sentinel_count)
    mediator_count = min(agent_count - connector_count - sentinel_count, mediator_count)
    analyzer_count = min(
        agent_count - connector_count - sentinel_count - mediator_count,
        analyzer_count,
    )

    shuffled = list(agenten)
    random.shuffle(shuffled)
    connector_ids = {agent.id for agent in shuffled[:connector_count]}
    offset = connector_count
    sentinel_ids = {agent.id for agent in shuffled[offset : offset + sentinel_count]}
    offset += sentinel_count
    mediator_ids = {agent.id for agent in shuffled[offset : offset + mediator_count]}
    offset += mediator_count
    analyzer_ids = {agent.id for agent in shuffled[offset : offset + analyzer_count]}

    for agent in agenten:
        zielrolle = 'generalist'
        if agent.id in connector_ids:
            zielrolle = 'connector'
            agent.hartnaeckigkeit = max(0.0, agent.hartnaeckigkeit * 0.6)
            agent.kooperations_neigung = min(0.95, agent.kooperations_neigung + 0.04)
        elif agent.id in sentinel_ids:
            zielrolle = 'sentinel'
            agent.reputation = min(1.0, agent.reputation + 0.04)
        elif agent.id in mediator_ids:
            zielrolle = 'mediator'
            agent.hartnaeckigkeit = max(0.0, agent.hartnaeckigkeit * 0.5)
        elif agent.id in analyzer_ids:
            zielrolle = 'analyzer'

        apply_role_profile(agent, zielrolle, config)
        agent.initial_role = zielrolle
        agent.role_tenure = 0
        agent.role_transition_history = []


def erstelle_agenten(config):
    agenten = []
    agent_count = int(config['agent_count'])
    scenario = str(config['scenario'])
    gruppengroesse = agent_count // 2

    for index in range(agent_count):
        gruppe = 0 if index < gruppengroesse else 1

        if scenario == 'consensus':
            basis_meinung = 0.45 if gruppe == 0 else 0.55
            streuung = 0.05
            hartnaeckigkeit = 0.15 if index % 7 == 0 else 0.05
            kooperation = 0.58 if gruppe == 0 else 0.56
        else:
            basis_meinung = 0.2 if gruppe == 0 else 0.8
            streuung = 0.08
            hartnaeckigkeit = 0.55 if index % 6 == 0 else 0.2
            kooperation = 0.5

        meinung = max(0.0, min(1.0, random.gauss(basis_meinung, streuung)))
        agenten.append(Agent(index, gruppe, meinung, kooperation, hartnaeckigkeit))

    if config.get('roles_enabled'):
        weise_rollen_zu(agenten, config)
    if config.get('enable_missions'):
        initialisiere_missionen(agenten, config)
    if config.get('enable_prompt_injection'):
        weise_misinformation_quellen_zu(agenten, config)

    return agenten


def erstelle_netzwerk(agenten, config):
    gruppen = {
        0: [agent for agent in agenten if agent.gruppe == 0],
        1: [agent for agent in agenten if agent.gruppe == 1],
    }
    connections_per_agent = int(config['connections_per_agent'])
    cross_group_chance = float(config['cross_group_chance'])
    random_edge_chance = float(config['random_edge_chance'])

    for gruppen_agenten in gruppen.values():
        n = len(gruppen_agenten)
        for i in range(n):
            for j in range(1, connections_per_agent // 2 + 1):
                gruppen_agenten[i].verbinde(gruppen_agenten[(i + j) % n])

    for agent in agenten:
        if random.random() < cross_group_chance:
            andere_gruppe = [ziel for ziel in agenten if ziel.gruppe != agent.gruppe and ziel.id != agent.id]
            ziel = random.choice(andere_gruppe)
            agent.verbinde(ziel)

        if random.random() < random_edge_chance:
            moegliche = [ziel for ziel in agenten if ziel.id != agent.id and ziel.id not in agent.nachbarn]
            if moegliche:
                agent.verbinde(random.choice(moegliche))


def waehle_partner(agent, agenten, agenten_dict, config=None):
    if config and config.get('enable_fault_isolation'):
        if agent.is_quarantined:
            kandidaten = [
                anderer
                for anderer in agenten
                if anderer.id != agent.id
                and (anderer.is_quarantined or anderer.workflow_cell == agent.workflow_cell)
            ]
            if kandidaten:
                return random.choice(kandidaten)
        else:
            unquarantined_neighbors = [
                agenten_dict[nid]
                for nid in agent.nachbarn
                if nid in agenten_dict and not agenten_dict[nid].is_quarantined
            ]
            if unquarantined_neighbors and random.random() < 0.9:
                return random.choice(unquarantined_neighbors)

    partner_bias_probability = getattr(agent, 'partner_bias_probability', 0.0)
    if partner_bias_probability > 0.0 and random.random() < partner_bias_probability:
        bias_distance = getattr(agent, 'partner_bias_min_distance', 0.0)
        kandidaten = [
            anderer
            for anderer in agenten
            if anderer.id != agent.id
            and abs(anderer.meinung - agent.meinung) >= bias_distance
            and (not config or not config.get('enable_fault_isolation') or not anderer.is_quarantined)
        ]
        if kandidaten:
            kandidaten.sort(key=lambda anderer: abs(anderer.meinung - agent.meinung), reverse=True)
            return kandidaten[0]
    if config and config.get('enable_mediator_encouragement') and ist_zentrist(agent.meinung, config):
        bias = float(config['mediator_contact_bias'])
        if random.random() < bias:
            kandidaten = [
                anderer
                for anderer in agenten
                if anderer.id != agent.id
                and abs(anderer.meinung - agent.meinung) > 0.30
                and (not config or not config.get('enable_fault_isolation') or not anderer.is_quarantined)
            ]
            if kandidaten:
                return random.choice(kandidaten)
    if agent.nachbarn and random.random() < 0.9:
        nachbar_ids = list(agent.nachbarn)
        if config and config.get('enable_fault_isolation'):
            sichere_ids = [nid for nid in nachbar_ids if nid in agenten_dict and not agenten_dict[nid].is_quarantined]
            if sichere_ids:
                return agenten_dict[random.choice(sichere_ids)]
        return agenten_dict[random.choice(nachbar_ids)]
    kandidaten = [
        anderer
        for anderer in agenten
        if anderer.id != agent.id
        and (not config or not config.get('enable_fault_isolation') or not anderer.is_quarantined)
    ]
    if not kandidaten:
        kandidaten = [anderer for anderer in agenten if anderer.id != agent.id]
    return random.choice(kandidaten)


def berechne_lager(agenten):
    links = sum(1 for agent in agenten if agent.meinung < 0.35)
    mitte = sum(1 for agent in agenten if 0.35 <= agent.meinung <= 0.65)
    rechts = sum(1 for agent in agenten if agent.meinung > 0.65)
    return links, mitte, rechts


def berechne_polarisierungs_index(agenten):
    return float(np.std([agent.meinung for agent in agenten]))


def berechne_konsens_score(agenten):
    meinungen = np.array([agent.meinung for agent in agenten])
    abweichung = np.mean(np.abs(meinungen - np.mean(meinungen)))
    return max(0.0, 1.0 - min(1.0, abweichung * 2.0))


def berechne_gruppenabstand(agenten):
    gruppe_links = [agent.meinung for agent in agenten if agent.gruppe == 0]
    gruppe_rechts = [agent.meinung for agent in agenten if agent.gruppe == 1]
    return abs(np.mean(gruppe_links) - np.mean(gruppe_rechts))


def ist_zentrist(meinung, config):
    center_min = float(config.get('center_zone_min', DEFAULT_CENTER_MIN))
    center_max = float(config.get('center_zone_max', DEFAULT_CENTER_MAX))
    return center_min <= meinung <= center_max


def berechne_brueckenagenten(agenten, agenten_dict):
    bridge_ids = set()
    for agent in agenten:
        gruppen = {agenten_dict[nachbar_id].gruppe for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict}
        if 0 in gruppen and 1 in gruppen:
            bridge_ids.add(agent.id)
    return bridge_ids


def berechne_netzwerkmetriken(agenten, agenten_dict):
    kanten = set()
    nachbarschaftsdistanzen = []
    gruppenuebergreifende_kanten = 0

    for agent in agenten:
        for nachbar_id in agent.nachbarn:
            kante = tuple(sorted((agent.id, nachbar_id)))
            if kante in kanten:
                continue
            kanten.add(kante)
            nachbar = agenten_dict[nachbar_id]
            nachbarschaftsdistanzen.append(abs(agent.meinung - nachbar.meinung))
            if agent.gruppe != nachbar.gruppe:
                gruppenuebergreifende_kanten += 1

    kantenanzahl = len(kanten)
    agentenzahl = len(agenten)
    moegliche_kanten = agentenzahl * (agentenzahl - 1) / 2

    return {
        'edge_count': kantenanzahl,
        'density': kantenanzahl / moegliche_kanten if moegliche_kanten else 0.0,
        'mean_degree': float(np.mean([len(agent.nachbarn) for agent in agenten])) if agenten else 0.0,
        'mean_neighbor_opinion_distance': (
            float(np.mean(nachbarschaftsdistanzen)) if nachbarschaftsdistanzen else 0.0
        ),
        'cross_group_edge_share': (
            gruppenuebergreifende_kanten / kantenanzahl if kantenanzahl else 0.0
        ),
    }


def finde_neuen_nachbarn(agent, agenten, config):
    proximity_weight = float(config['rewire_proximity_weight'])
    opinion_threshold = float(config['rewire_opinion_distance_threshold'])
    cross_group_bonus = float(config['rewire_cross_group_bonus'])

    bester_score = None
    beste_kandidaten = []

    for kandidat in agenten:
        if kandidat.id == agent.id or kandidat.id in agent.nachbarn:
            continue
        if config.get('enable_fault_isolation') and kandidat.is_quarantined:
            continue

        distanz = abs(agent.meinung - kandidat.meinung)
        if distanz > opinion_threshold + 0.25:
            continue

        aehnlichkeit = 1.0 - distanz
        score = (1.0 - proximity_weight) * kandidat.reputation + proximity_weight * aehnlichkeit
        if distanz > opinion_threshold:
            score -= (distanz - opinion_threshold) * 0.6
        if kandidat.gruppe != agent.gruppe:
            score += cross_group_bonus

        if bester_score is None or score > bester_score + 1e-9:
            bester_score = score
            beste_kandidaten = [kandidat]
        elif abs(score - bester_score) <= 1e-9:
            beste_kandidaten.append(kandidat)

    if not beste_kandidaten:
        return None
    return random.choice(beste_kandidaten)


def aktualisiere_adaptives_netzwerk(agenten, agenten_dict, config):
    if not config.get('enable_dynamic_rewiring'):
        return {
            'removed_edges': 0,
            'added_edges': 0,
            'rewired_edges': 0,
            'removed_for_reputation': 0,
            'removed_for_distance': 0,
        }

    min_interactions = int(config['rewire_min_interactions'])
    rep_threshold = float(config['rewire_reputation_threshold'])
    opinion_threshold = float(config['rewire_opinion_distance_threshold'])
    removal_probability = float(config['rewire_removal_probability'])
    addition_probability = float(config['rewire_addition_probability'])
    target_degree = max(1, int(config['rewire_target_degree']))

    removed_edges = 0
    added_edges = 0
    removed_for_reputation = 0
    removed_for_distance = 0

    for agent in agenten:
        zu_trennen = []
        agent_role_threshold = getattr(agent, 'rewire_reputation_threshold', None)
        lokaler_rep_threshold = (
            float(agent_role_threshold)
            if agent_role_threshold is not None
            else rep_threshold
        )
        for nachbar_id in list(agent.nachbarn):
            history = agent.interaktions_history.get(nachbar_id, [])
            if len(history) < min_interactions:
                continue

            nachbar = agenten_dict[nachbar_id]
            schwache_reputation = agent.berechne_partner_reputation(nachbar_id) < lokaler_rep_threshold
            grosse_distanz = abs(agent.meinung - nachbar.meinung) > opinion_threshold
            if (schwache_reputation or grosse_distanz) and random.random() < removal_probability:
                zu_trennen.append((nachbar, schwache_reputation, grosse_distanz))

        for nachbar, schwache_reputation, grosse_distanz in zu_trennen:
            if nachbar.id not in agent.nachbarn:
                continue
            agent.trenne(nachbar)
            removed_edges += 1
            if schwache_reputation:
                removed_for_reputation += 1
            else:
                removed_for_distance += 1

    for agent in agenten:
        additions_versucht = 0
        while len(agent.nachbarn) < target_degree and additions_versucht < 2:
            additions_versucht += 1
            if random.random() > addition_probability:
                break

            kandidat = finde_neuen_nachbarn(agent, agenten, config)
            if kandidat is None or kandidat.id in agent.nachbarn:
                break

            agent.verbinde(kandidat)
            added_edges += 1

    return {
        'removed_edges': removed_edges,
        'added_edges': added_edges,
        'rewired_edges': removed_edges + added_edges,
        'removed_for_reputation': removed_for_reputation,
        'removed_for_distance': removed_for_distance,
    }


def bestimme_rollenwechsel(agent, agenten_dict):
    if not agent.nachbarn:
        return None

    nachbarn = [agenten_dict[nachbar_id] for nachbar_id in agent.nachbarn if nachbar_id in agenten_dict]
    if not nachbarn:
        return None

    cross_group_neighbors = sum(1 for nachbar in nachbarn if nachbar.gruppe != agent.gruppe)
    cross_group_share = cross_group_neighbors / len(nachbarn)
    mean_partner_reputation = float(np.mean([agent.berechne_partner_reputation(nachbar.id) for nachbar in nachbarn]))
    mean_neighbor_distance = float(np.mean([abs(agent.meinung - nachbar.meinung) for nachbar in nachbarn]))

    if agent.role == 'generalist':
        if cross_group_share >= 0.35 and agent.kooperations_neigung >= 0.62:
            return 'connector'
        if agent.reputation >= 0.60 and mean_partner_reputation <= 0.45:
            return 'sentinel'
    elif agent.role == 'connector':
        if cross_group_share >= 0.45 and 0.30 <= agent.meinung <= 0.70:
            return 'mediator'
        if mean_partner_reputation <= 0.42 and agent.reputation >= 0.60:
            return 'sentinel'
    elif agent.role == 'sentinel':
        if agent.reputation >= 0.72 and mean_neighbor_distance <= 0.28:
            return 'analyzer'
        if cross_group_share >= 0.40 and agent.kooperations_neigung >= 0.60:
            return 'connector'
    elif agent.role == 'mediator':
        if mean_neighbor_distance <= 0.18 and agent.reputation >= 0.62:
            return 'analyzer'
        if mean_partner_reputation <= 0.40:
            return 'sentinel'
    elif agent.role == 'analyzer':
        if cross_group_share >= 0.40 and agent.reputation >= 0.65:
            return 'connector'
        if agent.kooperations_neigung <= 0.42:
            return 'generalist'

    if len(agent.nachbarn) <= 2 and agent.role != 'generalist':
        return 'generalist'
    return None


def aktualisiere_rollenwechsel(agenten, agenten_dict, config, runde):
    if not config.get('enable_role_switching') or not config.get('roles_enabled'):
        return {'switches': 0, 'transitions': []}

    interval = max(1, int(config.get('role_switch_interval', DEFAULT_ROLE_SWITCH_INTERVAL)))
    min_tenure = max(1, int(config.get('role_switch_min_tenure', DEFAULT_ROLE_SWITCH_MIN_TENURE)))
    if runde % interval != 0:
        return {'switches': 0, 'transitions': []}

    max_switches = int(config.get('max_role_switches_per_round', max(1, len(agenten) // 10)))
    switch_cost = float(config.get('role_switch_reputation_cost', DEFAULT_ROLE_SWITCH_REPUTATION_COST))
    transitions = []

    kandidaten = list(agenten)
    random.shuffle(kandidaten)
    for agent in kandidaten:
        if len(transitions) >= max_switches:
            break
        if agent.role_tenure < min_tenure:
            continue

        neue_rolle = bestimme_rollenwechsel(agent, agenten_dict)
        if neue_rolle is None or neue_rolle == agent.role:
            continue

        alte_rolle = agent.role
        apply_role_profile(agent, neue_rolle, config)
        agent.reputation = max(0.0, min(1.0, agent.reputation - switch_cost))
        agent.role_tenure = 0
        agent.role_transition_history.append((runde, alte_rolle, neue_rolle))
        transitions.append((alte_rolle, neue_rolle))

    return {'switches': len(transitions), 'transitions': transitions}


def run_polarization_experiment(
    config,
    *,
    make_plot=True,
    output_filename='kki_polarisierung.png',
    print_summary=True,
):
    config = dict(config)
    config.setdefault('center_zone_min', DEFAULT_CENTER_MIN)
    config.setdefault('center_zone_max', DEFAULT_CENTER_MAX)
    config.setdefault('enable_bridge_mechanism', False)
    config.setdefault('enable_centrist_moderation', False)
    config.setdefault('enable_mediator_encouragement', False)
    config.setdefault('bridge_cooperation_bonus', 0.08)
    config.setdefault('centrist_pull_strength', 0.08)
    config.setdefault('mediator_contact_bias', 0.60)
    config.setdefault('roles_enabled', False)
    config.setdefault('generalist_share', DEFAULT_GENERALIST_SHARE)
    config.setdefault('connector_share', DEFAULT_CONNECTOR_SHARE)
    config.setdefault('sentinel_share', DEFAULT_SENTINEL_SHARE)
    config.setdefault('mediator_share', DEFAULT_MEDIATOR_SHARE)
    config.setdefault('analyzer_share', DEFAULT_ANALYZER_SHARE)
    config.setdefault('connector_bridge_bonus', DEFAULT_CONNECTOR_BONUS)
    config.setdefault('sentinel_rep_threshold', DEFAULT_SENTINEL_REP_THRESHOLD)
    config.setdefault('sentinel_cooperation_penalty', DEFAULT_SENTINEL_COOPERATION_PENALTY)
    config.setdefault('connector_cross_group_learning_bonus', DEFAULT_CONNECTOR_CROSS_GROUP_LEARNING)
    config.setdefault('sentinel_reputation_learning_multiplier', DEFAULT_SENTINEL_REPUTATION_LEARNING)
    config.setdefault('mediator_bridge_bonus', DEFAULT_MEDIATOR_BONUS)
    config.setdefault('mediator_partner_bias', DEFAULT_MEDIATOR_CONTACT_BIAS)
    config.setdefault('mediator_partner_distance', DEFAULT_MEDIATOR_OPINION_DISTANCE)
    config.setdefault('analyzer_memory_window', DEFAULT_ANALYZER_MEMORY_WINDOW)
    config.setdefault('analyzer_learning_multiplier', DEFAULT_ANALYZER_LEARNING_MULTIPLIER)
    config.setdefault('enable_role_switching', False)
    config.setdefault('role_switch_interval', DEFAULT_ROLE_SWITCH_INTERVAL)
    config.setdefault('role_switch_min_tenure', DEFAULT_ROLE_SWITCH_MIN_TENURE)
    config.setdefault('role_switch_reputation_cost', DEFAULT_ROLE_SWITCH_REPUTATION_COST)
    config.setdefault('max_role_switches_per_round', max(1, int(config['agent_count']) // 10))
    config.setdefault('enable_missions', False)
    config.setdefault('mission_assignment', 'static')
    config.setdefault('mission_switch_interval', DEFAULT_MISSION_SWITCH_INTERVAL)
    config.setdefault('mission_arbitration_enabled', False)
    config.setdefault('mission_conflict_threshold', DEFAULT_MISSION_CONFLICT_THRESHOLD)
    config.setdefault('mission_arbitration_margin', DEFAULT_MISSION_ARBITRATION_MARGIN)
    config.setdefault('enable_workflow_stages', False)
    config.setdefault('workflow_stage_min_tenure', DEFAULT_WORKFLOW_STAGE_MIN_TENURE)
    config.setdefault('enable_workflow_cells', False)
    config.setdefault('enable_handoff_coordination', False)
    config.setdefault('handoff_priority_bonus', DEFAULT_HANDOFF_PRIORITY_BONUS)
    config.setdefault('enable_parallel_workflow_cells', False)
    config.setdefault('enable_resource_coordination', False)
    config.setdefault('resource_budget', DEFAULT_RESOURCE_BUDGET)
    config.setdefault('resource_share_factor', DEFAULT_RESOURCE_SHARE_FACTOR)
    config.setdefault('enable_capability_clusters', False)
    config.setdefault('enable_asymmetric_cluster_budgets', False)
    config.setdefault('cluster_budget_skew', DEFAULT_CLUSTER_BUDGET_SKEW)
    config.setdefault('enable_bottleneck_management', False)
    config.setdefault('bottleneck_threshold', DEFAULT_BOTTLENECK_THRESHOLD)
    config.setdefault('bottleneck_triage_intensity', DEFAULT_BOTTLENECK_TRIAGE_INTENSITY)
    config.setdefault('enable_meta_coordination', False)
    config.setdefault('meta_update_interval', DEFAULT_META_UPDATE_INTERVAL)
    config.setdefault('meta_priority_strength', DEFAULT_META_PRIORITY_STRENGTH)
    config.setdefault('enable_prompt_injection', False)
    config.setdefault('injection_attack_round', DEFAULT_INJECTION_ATTACK_ROUND)
    config.setdefault('injection_strength', DEFAULT_INJECTION_STRENGTH)
    config.setdefault('injection_source_count', DEFAULT_INJECTION_SOURCE_COUNT)
    scenario = str(config['scenario'])
    rounds = int(config['rounds'])
    interactions_per_round = int(config['interactions_per_round'])
    connections_per_agent = int(config['connections_per_agent'])

    agenten = erstelle_agenten(config)
    agenten_dict = {agent.id: agent for agent in agenten}
    erstelle_netzwerk(agenten, config)

    if print_summary:
        print("=" * 78)
        print(f"KKI POLARISIERUNGS-EXPERIMENT: {scenario_title(scenario)}")
        print("=" * 78)
        print(f"\nSzenario: {scenario}")
        print(
            f"Agenten: {config['agent_count']}, Runden: {rounds}, "
            f"Interaktionen/Runde: {interactions_per_round}"
        )
        print(
            "Netzwerk: "
            f"Grad={connections_per_agent}, "
            f"Cross-Group={float(config['cross_group_chance']):.2f}, "
            f"Shortcut={float(config['random_edge_chance']):.2f}"
        )
        if config.get('enable_dynamic_rewiring'):
            print(
                "Adaptives Rewiring: "
                f"aktiv | Rep-Schwelle={float(config['rewire_reputation_threshold']):.2f}, "
                f"Meinungs-Schwelle={float(config['rewire_opinion_distance_threshold']):.2f}, "
                f"Zielgrad={int(config['rewire_target_degree'])}"
            )
        if config.get('roles_enabled'):
            shares = normalisiere_rollenanteile(config)
            print(
                "Rollen: "
                f"Generalisten={shares['generalist']:.0%}, "
                f"Brueckenbauer={shares['connector']:.0%}, "
                f"Waechter={shares['sentinel']:.0%}, "
                f"Vermittler={shares['mediator']:.0%}, "
                f"Analytiker={shares['analyzer']:.0%}"
            )
            if config.get('enable_role_switching'):
                print(
                    "Rollenwechsel: "
                    f"aktiv | Intervall={int(config['role_switch_interval'])}, "
                    f"Mindestdauer={int(config['role_switch_min_tenure'])}, "
                    f"Kosten={float(config['role_switch_reputation_cost']):.2f}"
                )
        if config.get('enable_missions'):
            print(
                "Missionen: "
                f"aktiv | Zuweisung={config['mission_assignment']}, "
                f"Intervall={int(config['mission_switch_interval'])}"
            )
            if config.get('mission_arbitration_enabled') or config.get('mission_assignment') == 'arbitrated':
                print(
                    "Missions-Arbitration: "
                    f"aktiv | Konflikt-Schwelle={float(config['mission_conflict_threshold']):.2f}, "
                    f"Margin={float(config['mission_arbitration_margin']):.2f}"
                )
            if config.get('enable_workflow_stages'):
                print(
                    "Workflow-Stufen: "
                    f"aktiv | Mindestdauer={int(config['workflow_stage_min_tenure'])}"
                )
            if config.get('enable_workflow_cells'):
                print(
                    "Workflow-Zellen: "
                    f"aktiv | Handoffs={'an' if config.get('enable_handoff_coordination') else 'aus'}"
                )
                if config.get('enable_parallel_workflow_cells') or config.get('enable_resource_coordination'):
                    print(
                        "Ressourcenkoordination: "
                        f"Zellen={'parallel' if config.get('enable_parallel_workflow_cells') else 'normal'}, "
                        f"Sharing={'an' if config.get('enable_resource_coordination') else 'aus'}"
                    )
                if config.get('enable_capability_clusters'):
                    print(
                        "Faehigkeitscluster: "
                        f"aktiv | asymmetrische Budgets={'an' if config.get('enable_asymmetric_cluster_budgets') else 'aus'}"
                    )
                if config.get('enable_bottleneck_management'):
                    print(
                        "Bottleneck-Management: "
                        f"aktiv | Schwelle={float(config.get('bottleneck_threshold', DEFAULT_BOTTLENECK_THRESHOLD)):.2f}"
                    )
                if config.get('enable_meta_coordination'):
                    print(
                        "Meta-Koordination: "
                        f"aktiv | Intervall={int(config.get('meta_update_interval', DEFAULT_META_UPDATE_INTERVAL))}"
                    )
                if config.get('enable_prompt_injection'):
                    print(
                        "Promptinjektion: "
                        f"aktiv | Start={int(config.get('injection_attack_round', DEFAULT_INJECTION_ATTACK_ROUND))}, "
                        f"Staerke={float(config.get('injection_strength', DEFAULT_INJECTION_STRENGTH)):.2f}"
                    )
        print("Ziel: Beobachte, ob der Schwarm in Richtung Konsens oder in stabile Lager driftet.")
        print("\nSimulation läuft...\n")

    polarisierungs_history = []
    konsens_history = []
    gruppenabstand_history = []
    links_history = []
    mitte_history = []
    rechts_history = []
    gruppe_a_intelligenz = []
    gruppe_b_intelligenz = []
    cross_group_history = []
    cross_group_cooperation_history = []
    bridge_count_history = []
    center_zone_history = []
    role_cross_group_contacts = defaultdict(int)
    role_cross_group_cooperations = defaultdict(int)
    role_switch_history = []
    role_transition_counts = defaultdict(int)
    removed_edges_history = []
    added_edges_history = []
    rewired_edges_history = []
    removed_reputation_history = []
    removed_distance_history = []
    density_history = []
    mean_degree_history = []
    neighbor_distance_history = []
    cross_group_edge_share_history = []
    mission_switch_history = []
    mission_contact_counts = defaultdict(int)
    mission_success_counts = defaultdict(int)
    mission_arbitration_history = []
    mission_conflict_history = []
    mission_fitness_gain_history = []
    workflow_completion_history = []
    workflow_prerequisite_failures_history = []
    workflow_stage_counts = defaultdict(int)
    handoff_history = []
    workflow_cell_counts = defaultdict(int)
    resource_sharing_history = []
    active_cell_history = []
    cluster_output_history = []
    capability_cluster_counts = defaultdict(int)
    bottleneck_history = []
    bottleneck_relief_history = []
    rerouted_budget_history = []
    meta_switch_history = []
    meta_alignment_history = []
    meta_mission_focus_counts = defaultdict(int)
    meta_cluster_focus_counts = defaultdict(int)
    misinformation_events_history = []
    misinformation_detection_history = []
    misinformation_corruption_history = []
    misinformation_compromise_history = []
    skill_switch_history = []
    skill_alignment_history = []
    learning_gain_history = []
    emergent_skill_counts = defaultdict(int)
    quarantine_event_history = []
    quarantined_agents_history = []
    quarantined_cells_history = []
    shielding_action_history = []
    shield_strength_history = []
    isolation_relief_history = []

    for runde in range(1, rounds + 1):
        gruppenuebergreifende_interaktionen = 0
        gruppenuebergreifende_kooperationen = 0
        bridge_ids = berechne_brueckenagenten(agenten, agenten_dict)
        manipulation_stats = wende_promptinjektion_an(agenten, agenten_dict, config, runde)
        isolation_stats = aktualisiere_fehlerisolation(agenten, agenten_dict, config, runde)

        for _ in range(interactions_per_round):
            agent = random.choice(agenten)
            partner = waehle_partner(agent, agenten, agenten_dict, config)

            if agent.gruppe != partner.gruppe:
                gruppenuebergreifende_interaktionen += 1
                role_cross_group_contacts[agent.role] += 1
                role_cross_group_contacts[partner.role] += 1

            partner_rep_aus_agent_sicht = agent.berechne_partner_reputation(partner.id)
            agent_rep_aus_partner_sicht = partner.berechne_partner_reputation(agent.id)

            cooperation_bonus_a = 0.0
            cooperation_bonus_p = 0.0
            if agent.gruppe != partner.gruppe and config.get('enable_bridge_mechanism'):
                if agent.id in bridge_ids:
                    cooperation_bonus_a += float(config['bridge_cooperation_bonus'])
                if partner.id in bridge_ids:
                    cooperation_bonus_p += float(config['bridge_cooperation_bonus'])
            if agent.gruppe != partner.gruppe:
                cooperation_bonus_a += agent.bridge_bonus
                cooperation_bonus_p += partner.bridge_bonus
            if agent.gruppe != partner.gruppe and config.get('enable_centrist_moderation'):
                if ist_zentrist(agent.meinung, config):
                    cooperation_bonus_a += 0.04
                if ist_zentrist(partner.meinung, config):
                    cooperation_bonus_p += 0.04
            mission_bonus_a, mission_pull_a = missions_bonus(
                agent, partner_rep_aus_agent_sicht, partner, agent.gruppe != partner.gruppe
            )
            mission_bonus_p, mission_pull_p = missions_bonus(
                partner, agent_rep_aus_partner_sicht, agent, agent.gruppe != partner.gruppe
            )
            cooperation_bonus_a += mission_bonus_a
            cooperation_bonus_p += mission_bonus_p

            aktion_a = agent.waehle_aktion(partner_rep_aus_agent_sicht, partner.meinung, cooperation_bonus_a)
            aktion_p = partner.waehle_aktion(agent_rep_aus_partner_sicht, agent.meinung, cooperation_bonus_p)
            if agent.gruppe != partner.gruppe and aktion_a == 'C' and aktion_p == 'C':
                gruppenuebergreifende_kooperationen += 1
                role_cross_group_cooperations[agent.role] += 1
                role_cross_group_cooperations[partner.role] += 1

            opinion_pull_a = 0.0
            opinion_pull_p = 0.0
            if config.get('enable_centrist_moderation') and agent.gruppe != partner.gruppe:
                if ist_zentrist(agent.meinung, config) or ist_zentrist(partner.meinung, config):
                    opinion_pull_a += float(config['centrist_pull_strength'])
                    opinion_pull_p += float(config['centrist_pull_strength'])
            opinion_pull_a += mission_pull_a
            opinion_pull_p += mission_pull_p

            if config.get('enable_missions'):
                mission_contact_counts[agent.mission] += 1
                mission_contact_counts[partner.mission] += 1
                if agent.mission in {MISSION_CONSENSUS, MISSION_KNOWLEDGE}:
                    if agent.gruppe != partner.gruppe and aktion_a == 'C' and aktion_p == 'C':
                        mission_success_counts[agent.mission] += 1
                elif agent.mission == MISSION_DEFENSE:
                    if partner_rep_aus_agent_sicht < DEFAULT_SENTINEL_REP_THRESHOLD and aktion_a == 'D':
                        mission_success_counts[agent.mission] += 1
                elif agent.mission == MISSION_STABILITY:
                    if agent.gruppe == partner.gruppe and aktion_a == 'C' and aktion_p == 'C':
                        mission_success_counts[agent.mission] += 1
                elif agent.mission == MISSION_SUPPORT and aktion_a == 'C':
                    mission_success_counts[agent.mission] += 1

                if partner.mission in {MISSION_CONSENSUS, MISSION_KNOWLEDGE}:
                    if agent.gruppe != partner.gruppe and aktion_a == 'C' and aktion_p == 'C':
                        mission_success_counts[partner.mission] += 1
                elif partner.mission == MISSION_DEFENSE:
                    if agent_rep_aus_partner_sicht < DEFAULT_SENTINEL_REP_THRESHOLD and aktion_p == 'D':
                        mission_success_counts[partner.mission] += 1
                elif partner.mission == MISSION_STABILITY:
                    if agent.gruppe == partner.gruppe and aktion_a == 'C' and aktion_p == 'C':
                        mission_success_counts[partner.mission] += 1
                elif partner.mission == MISSION_SUPPORT and aktion_p == 'C':
                    mission_success_counts[partner.mission] += 1

            if config.get('enable_workflow_cells'):
                handoffs = koordiniere_workflow_handoff(agent, partner, aktion_a, aktion_p, runde, config)
                handoff_history.append(len(handoffs))

            agent.lerne(
                aktion_a,
                aktion_p,
                partner.id,
                partner.intelligenz,
                partner.meinung,
                agent.gruppe == partner.gruppe,
                opinion_pull=opinion_pull_a,
            )
            partner.lerne(
                aktion_p,
                aktion_a,
                agent.id,
                agent.intelligenz,
                agent.meinung,
                agent.gruppe == partner.gruppe,
                opinion_pull=opinion_pull_p,
            )

        switch_stats = aktualisiere_rollenwechsel(agenten, agenten_dict, config, runde)
        mission_stats = aktualisiere_missionen(agenten, agenten_dict, config, runde)
        meta_stats = aktualisiere_meta_koordination(
            agenten,
            config,
            runde,
            mission_success_counts,
            mission_contact_counts,
        )
        learning_stats = aktualisiere_gruppenlernen(agenten, agenten_dict, config, runde)
        resource_stats = koordiniere_ressourcen(agenten, config)
        rewiring_stats = aktualisiere_adaptives_netzwerk(agenten, agenten_dict, config)
        for agent in agenten:
            agent.role_tenure += 1
            agent.mission_tenure += 1
            agent.stage_tenure += 1
            agent.runde_beenden()

        polarisierungs_index = berechne_polarisierungs_index(agenten)
        konsens_score = berechne_konsens_score(agenten)
        gruppenabstand = berechne_gruppenabstand(agenten)
        netzwerkmetriken = berechne_netzwerkmetriken(agenten, agenten_dict)
        links, mitte, rechts = berechne_lager(agenten)

        polarisierungs_history.append(polarisierungs_index)
        konsens_history.append(konsens_score)
        gruppenabstand_history.append(gruppenabstand)
        links_history.append(links)
        mitte_history.append(mitte)
        rechts_history.append(rechts)
        gruppe_a_intelligenz.append(np.mean([agent.intelligenz for agent in agenten if agent.gruppe == 0]))
        gruppe_b_intelligenz.append(np.mean([agent.intelligenz for agent in agenten if agent.gruppe == 1]))
        cross_group_history.append(gruppenuebergreifende_interaktionen / interactions_per_round)
        cross_group_cooperation_history.append(
            gruppenuebergreifende_kooperationen / max(1, gruppenuebergreifende_interaktionen)
        )
        bridge_count_history.append(len(bridge_ids))
        center_zone_history.append(sum(1 for agent in agenten if ist_zentrist(agent.meinung, config)))
        role_switch_history.append(switch_stats['switches'])
        mission_switch_history.append(mission_stats['switches'])
        mission_arbitration_history.append(mission_stats['arbitrations'])
        mission_conflict_history.append(mission_stats['conflicts'])
        mission_fitness_gain_history.append(mission_stats['fitness_gain'])
        if config.get('enable_workflow_stages'):
            workflow_completion_history.append(
                sum(1 for agent in agenten if agent.workflow_stage == 'recovery') / len(agenten)
            )
            workflow_prerequisite_failures_history.append(
                sum(1 for agent in agenten if not agent.dependencies_met)
            )
            for agent in agenten:
                workflow_stage_counts[agent.workflow_stage] += 1
        if config.get('enable_workflow_cells'):
            for agent in agenten:
                workflow_cell_counts[agent.workflow_cell] += 1
                if config.get('enable_capability_clusters'):
                    capability_cluster_counts[agent.capability_cluster] += 1
                if config.get('enable_emergent_skills'):
                    emergent_skill_counts[agent.emergent_skill] += 1
            resource_sharing_history.append(resource_stats['shared'])
            active_cell_history.append(resource_stats['active_cells'])
            cluster_output_history.append(resource_stats['effective_output'])
            bottleneck_history.append(resource_stats['bottlenecks'])
            bottleneck_relief_history.append(resource_stats['relief'])
            rerouted_budget_history.append(resource_stats['rerouted'])
            meta_switch_history.append(meta_stats['switches'])
            meta_alignment_history.append(meta_stats['alignment_rate'])
            misinformation_events_history.append(manipulation_stats['events'])
            misinformation_detection_history.append(manipulation_stats['detections'])
            misinformation_corruption_history.append(manipulation_stats['corruption'])
            misinformation_compromise_history.append(manipulation_stats['compromise'])
            skill_switch_history.append(learning_stats['switches'])
            skill_alignment_history.append(learning_stats['alignment_rate'])
            learning_gain_history.append(learning_stats['learning_gain'])
            quarantine_event_history.append(isolation_stats['events'])
            quarantined_agents_history.append(isolation_stats['quarantined_agents'])
            quarantined_cells_history.append(isolation_stats['quarantined_cells'])
            shielding_action_history.append(isolation_stats['shielding_actions'])
            shield_strength_history.append(isolation_stats['shield_mean'])
            isolation_relief_history.append(isolation_stats['relief'])
            if meta_stats['priority_mission'] is not None:
                meta_mission_focus_counts[meta_stats['priority_mission']] += 1
            if meta_stats['priority_cluster'] is not None:
                meta_cluster_focus_counts[meta_stats['priority_cluster']] += 1
        for alte_rolle, neue_rolle in switch_stats['transitions']:
            role_transition_counts[f'{alte_rolle}->{neue_rolle}'] += 1
        removed_edges_history.append(rewiring_stats['removed_edges'])
        added_edges_history.append(rewiring_stats['added_edges'])
        rewired_edges_history.append(rewiring_stats['rewired_edges'])
        removed_reputation_history.append(rewiring_stats['removed_for_reputation'])
        removed_distance_history.append(rewiring_stats['removed_for_distance'])
        density_history.append(netzwerkmetriken['density'])
        mean_degree_history.append(netzwerkmetriken['mean_degree'])
        neighbor_distance_history.append(netzwerkmetriken['mean_neighbor_opinion_distance'])
        cross_group_edge_share_history.append(netzwerkmetriken['cross_group_edge_share'])

        if print_summary and runde % 30 == 0:
            status = (
                f"Runde {runde:3d}: PI={polarisierungs_index:.3f}, "
                f"Konsens={konsens_score:.3f}, Gruppenabstand={gruppenabstand:.3f}, "
                f"Links/Mitte/Rechts={links}/{mitte}/{rechts}"
            )
            if config.get('enable_bridge_mechanism') or config.get('enable_centrist_moderation'):
                status += f", Brücken={len(bridge_ids)}, Mitte={center_zone_history[-1]}"
            if config.get('enable_role_switching'):
                status += f", Wechsel={switch_stats['switches']}"
            if config.get('enable_missions'):
                status += f", Missionen={mission_stats['switches']}"
                if config.get('mission_arbitration_enabled') or config.get('mission_assignment') == 'arbitrated':
                    status += (
                        f", Konflikte={mission_stats['conflicts']}, "
                        f"Arb={mission_stats['arbitrations']}"
                    )
            if config.get('enable_dynamic_rewiring'):
                status += f", Rewiring={rewiring_stats['rewired_edges']}"
            if config.get('enable_resource_coordination'):
                status += f", Ressourcen={resource_stats['shared']:.2f}"
            if config.get('enable_capability_clusters'):
                status += f", Cluster-Output={resource_stats['effective_output']:.2f}"
            if config.get('enable_bottleneck_management'):
                status += f", Bottlenecks={resource_stats['bottlenecks']}"
            if config.get('enable_meta_coordination'):
                status += f", Meta={meta_stats['alignment_rate']:.2f}"
            if config.get('enable_prompt_injection'):
                status += f", Angriff={manipulation_stats['events']}, Det={manipulation_stats['detections']}"
            if config.get('enable_emergent_skills'):
                status += f", Skills={learning_stats['alignment_rate']:.2f}"
            if config.get('enable_fault_isolation'):
                status += f", Quar={isolation_stats['quarantined_agents']}"
            print(status)

    finale_pi = polarisierungs_history[-1]
    finaler_konsens = konsens_history[-1]
    finaler_abstand = gruppenabstand_history[-1]
    links, mitte, rechts = berechne_lager(agenten)
    cross_group_rate = float(np.mean(cross_group_history))
    cross_group_cooperation_rate = float(np.mean(cross_group_cooperation_history))
    mean_group_a = float(np.mean([agent.meinung for agent in agenten if agent.gruppe == 0]))
    mean_group_b = float(np.mean([agent.meinung for agent in agenten if agent.gruppe == 1]))
    finale_netzwerkmetriken = berechne_netzwerkmetriken(agenten, agenten_dict)
    durchschnitt_rewiring = float(np.mean(rewired_edges_history)) if rewired_edges_history else 0.0
    bekannte_rollen = ('generalist', 'connector', 'sentinel', 'mediator', 'analyzer')
    initial_role_counts = {role: sum(1 for agent in agenten if agent.initial_role == role) for role in bekannte_rollen}
    role_counts = {role: sum(1 for agent in agenten if agent.role == role) for role in bekannte_rollen}
    role_mean_intelligence = {
        role: float(np.mean([agent.intelligenz for agent in agenten if agent.role == role]))
        if role_counts[role]
        else 0.0
        for role in role_counts
    }
    role_mean_reputation = {
        role: float(np.mean([agent.reputation for agent in agenten if agent.role == role]))
        if role_counts[role]
        else 0.0
        for role in role_counts
    }
    role_mean_opinion_shift = {
        role: float(
            np.mean(
                [
                    abs(agent.meinung_history[-1] - agent.meinung_history[0])
                    for agent in agenten
                    if agent.role == role
                ]
            )
        )
        if role_counts[role]
        else 0.0
        for role in role_counts
    }
    role_cross_group_cooperation_rate = {
        role: role_cross_group_cooperations[role] / max(1, role_cross_group_contacts[role])
        for role in role_counts
    }
    bekannte_missionen = MISSION_TYPES
    initial_mission_counts = {
        mission: sum(1 for agent in agenten if agent.initial_mission == mission) for mission in bekannte_missionen
    }
    mission_counts = {mission: sum(1 for agent in agenten if agent.mission == mission) for mission in bekannte_missionen}
    mission_success_rates = {
        mission: mission_success_counts[mission] / max(1, mission_contact_counts[mission])
        for mission in bekannte_missionen
    }
    mission_conflict_total = int(sum(mission_conflict_history))
    mission_arbitration_total = int(sum(mission_arbitration_history))
    mission_arbitration_mean_gain = float(np.mean(mission_fitness_gain_history))
    mission_switch_stability = float(np.std(mission_switch_history) / max(1.0, np.mean(mission_switch_history)))
    workflow_metrics = {
        'stage_distribution': {stage: sum(1 for agent in agenten if agent.workflow_stage == stage) for stage in WORKFLOW_STAGES},
        'completion_rate': float(np.mean(workflow_completion_history)) if workflow_completion_history else 0.0,
        'prerequisite_failures': int(sum(workflow_prerequisite_failures_history)),
        'observed_stage_counts': dict(workflow_stage_counts),
        'cell_distribution': {cell: sum(1 for agent in agenten if agent.workflow_cell == cell) for cell in WORKFLOW_CELLS},
        'observed_cell_counts': dict(workflow_cell_counts),
        'handoff_total': int(sum(handoff_history)),
        'handoff_rate': float(np.mean(handoff_history)) if handoff_history else 0.0,
        'resource_shared_total': float(sum(resource_sharing_history)),
        'resource_share_rate': float(np.mean(resource_sharing_history)) if resource_sharing_history else 0.0,
        'active_cells_mean': float(np.mean(active_cell_history)) if active_cell_history else 0.0,
        'capability_cluster_distribution': {
            cluster: sum(1 for agent in agenten if agent.capability_cluster == cluster)
            for cluster in CAPABILITY_CLUSTERS
        },
        'observed_capability_clusters': dict(capability_cluster_counts),
        'cluster_output_total': float(sum(cluster_output_history)),
        'cluster_output_rate': float(np.mean(cluster_output_history)) if cluster_output_history else 0.0,
        'resource_efficiency': float(sum(cluster_output_history) / max(1e-9, sum(resource_sharing_history)))
        if resource_sharing_history
        else 0.0,
        'bottleneck_total': int(sum(bottleneck_history)),
        'bottleneck_rate': float(np.mean(bottleneck_history)) if bottleneck_history else 0.0,
        'bottleneck_relief_total': float(sum(bottleneck_relief_history)),
        'bottleneck_relief_rate': float(np.mean(bottleneck_relief_history)) if bottleneck_relief_history else 0.0,
        'rerouted_budget_total': float(sum(rerouted_budget_history)),
        'meta_switch_total': int(sum(meta_switch_history)),
        'meta_alignment_rate': float(np.mean(meta_alignment_history)) if meta_alignment_history else 0.0,
        'meta_mission_focus_counts': dict(meta_mission_focus_counts),
        'meta_cluster_focus_counts': dict(meta_cluster_focus_counts),
        'misinformation_events_total': int(sum(misinformation_events_history)),
        'misinformation_detection_rate': float(sum(misinformation_detection_history) / max(1, sum(misinformation_events_history))),
        'misinformation_corruption_mean': float(np.mean(misinformation_corruption_history))
        if misinformation_corruption_history
        else 0.0,
        'cluster_compromise_mean': float(np.mean(misinformation_compromise_history))
        if misinformation_compromise_history
        else 0.0,
        'quarantine_events_total': int(sum(quarantine_event_history)),
        'quarantine_rate': float(np.mean(quarantine_event_history)) if quarantine_event_history else 0.0,
        'quarantined_agents_mean': float(np.mean(quarantined_agents_history))
        if quarantined_agents_history
        else 0.0,
        'quarantined_cells_mean': float(np.mean(quarantined_cells_history))
        if quarantined_cells_history
        else 0.0,
        'shielding_actions_total': int(sum(shielding_action_history)),
        'trust_shield_mean': float(np.mean(shield_strength_history)) if shield_strength_history else 0.0,
        'isolation_relief_total': float(sum(isolation_relief_history)),
        'isolation_relief_rate': float(np.mean(isolation_relief_history)) if isolation_relief_history else 0.0,
        'emergent_skill_distribution': {
            skill: sum(1 for agent in agenten if agent.emergent_skill == skill)
            for skill in (
                'adaptive_generalist',
                'bridge_specialist',
                'analysis_specialist',
                'defense_specialist',
                'recovery_specialist',
            )
        },
        'observed_emergent_skills': dict(emergent_skill_counts),
        'skill_switch_total': int(sum(skill_switch_history)),
        'skill_alignment_rate': float(np.mean(skill_alignment_history)) if skill_alignment_history else 0.0,
        'group_learning_gain_total': float(sum(learning_gain_history)),
        'group_learning_gain_rate': float(np.mean(learning_gain_history)) if learning_gain_history else 0.0,
    }

    interpretation = "hybrid"
    if finale_pi > 0.22 and finaler_abstand > 0.35:
        interpretation = "polarized"
    elif finaler_konsens > 0.72 and mitte > links and mitte > rechts:
        interpretation = "consensus"

    if print_summary:
        print("\n" + "=" * 78)
        print("ERGEBNISSE")
        print("=" * 78)
        print(f"\nFinaler Polarisierungs-Index: {finale_pi:.3f}")
        print(f"Finaler Konsens-Score:       {finaler_konsens:.3f}")
        print(f"Finaler Gruppenabstand:      {finaler_abstand:.3f}")
        print(f"Lagerverteilung:             Links={links}, Mitte={mitte}, Rechts={rechts}")
        print(f"Ø gruppenübergreifende Interaktionen: {cross_group_rate:.1%}")
        print(f"Ø gruppenübergreifende Kooperation:   {cross_group_cooperation_rate:.1%}")
        if config.get('enable_bridge_mechanism') or config.get('enable_centrist_moderation'):
            print(f"Ø Brückenagenten:            {float(np.mean(bridge_count_history)):.2f}")
            print(f"Ø Agenten in Mittelzone:     {float(np.mean(center_zone_history)):.2f}")
        if config.get('roles_enabled'):
            print(
                "Rollen-Kooperation:          "
                f"Generalisten={role_cross_group_cooperation_rate['generalist']:.1%}, "
                f"Brueckenbauer={role_cross_group_cooperation_rate['connector']:.1%}, "
                f"Waechter={role_cross_group_cooperation_rate['sentinel']:.1%}, "
                f"Vermittler={role_cross_group_cooperation_rate['mediator']:.1%}, "
                f"Analytiker={role_cross_group_cooperation_rate['analyzer']:.1%}"
            )
            if config.get('enable_role_switching'):
                print(f"Ø Rollenwechsel/Runde:       {float(np.mean(role_switch_history)):.2f}")
        if config.get('enable_missions'):
            print(
                "Missionserfolg:             "
                f"Konsens={mission_success_rates[MISSION_CONSENSUS]:.1%}, "
                f"Wissen={mission_success_rates[MISSION_KNOWLEDGE]:.1%}, "
                f"Abwehr={mission_success_rates[MISSION_DEFENSE]:.1%}, "
                f"Stabilitaet={mission_success_rates[MISSION_STABILITY]:.1%}, "
                f"Support={mission_success_rates[MISSION_SUPPORT]:.1%}"
            )
            print(f"Ø Missionswechsel/Runde:     {float(np.mean(mission_switch_history)):.2f}")
            if config.get('mission_arbitration_enabled') or config.get('mission_assignment') == 'arbitrated':
                print(f"Ø Konflikte/Runde:           {float(np.mean(mission_conflict_history)):.2f}")
                print(f"Ø Arbitrierungen/Runde:      {float(np.mean(mission_arbitration_history)):.2f}")
                print(f"Ø Fitnessgewinn/Arbitration: {mission_arbitration_mean_gain:.3f}")
            if config.get('enable_workflow_stages'):
                print(f"Workflow-Abschlussrate:      {workflow_metrics['completion_rate']:.1%}")
                print(f"Workflow-Blockaden gesamt:   {workflow_metrics['prerequisite_failures']}")
            if config.get('enable_workflow_cells'):
                print(f"Handoffs gesamt:            {workflow_metrics['handoff_total']}")
                print(f"Ø Handoffs/Runde:           {workflow_metrics['handoff_rate']:.2f}")
            if config.get('enable_resource_coordination'):
                print(f"Ressourcen gesamt:         {workflow_metrics['resource_shared_total']:.2f}")
                print(f"Ø aktive Zellen/Runde:     {workflow_metrics['active_cells_mean']:.2f}")
            if config.get('enable_capability_clusters'):
                print(f"Cluster-Output gesamt:    {workflow_metrics['cluster_output_total']:.2f}")
                print(f"Ressourcen-Effizienz:     {workflow_metrics['resource_efficiency']:.2f}")
            if config.get('enable_bottleneck_management'):
                print(f"Bottlenecks gesamt:       {workflow_metrics['bottleneck_total']}")
                print(f"Entlastung gesamt:        {workflow_metrics['bottleneck_relief_total']:.2f}")
            if config.get('enable_meta_coordination'):
                print(f"Meta-Wechsel gesamt:      {workflow_metrics['meta_switch_total']}")
                print(f"Meta-Ausrichtung:         {workflow_metrics['meta_alignment_rate']:.1%}")
            if config.get('enable_prompt_injection'):
                print(f"Manipulationsereignisse:  {workflow_metrics['misinformation_events_total']}")
                print(f"Detektionsrate:           {workflow_metrics['misinformation_detection_rate']:.1%}")
                print(f"Korruptionsniveau:        {workflow_metrics['misinformation_corruption_mean']:.2f}")
            if config.get('enable_fault_isolation'):
                print(f"Quarantaenen gesamt:      {workflow_metrics['quarantine_events_total']}")
                print(f"Ø quarant. Agenten:       {workflow_metrics['quarantined_agents_mean']:.2f}")
                print(f"Abschirmaktionen gesamt:  {workflow_metrics['shielding_actions_total']}")
                print(f"Abschirmniveau:           {workflow_metrics['trust_shield_mean']:.2f}")
            if config.get('enable_emergent_skills'):
                print(f"Skill-Wechsel gesamt:     {workflow_metrics['skill_switch_total']}")
                print(f"Skill-Ausrichtung:        {workflow_metrics['skill_alignment_rate']:.1%}")
                print(f"Lerngewinn gesamt:        {workflow_metrics['group_learning_gain_total']:.2f}")
        if config.get('enable_dynamic_rewiring'):
            print(f"Ø Rewiring-Operationen/Runde: {durchschnitt_rewiring:.2f}")
            print(f"Finale Netzwerkdichte:       {finale_netzwerkmetriken['density']:.3f}")
            print(f"Finaler mittlerer Grad:      {finale_netzwerkmetriken['mean_degree']:.2f}")
            print(f"Anteil gruppenübergreifender Kanten: {finale_netzwerkmetriken['cross_group_edge_share']:.1%}")
        print(f"\nØ Meinung Gruppe 1: {mean_group_a:.3f}")
        print(f"Ø Meinung Gruppe 2: {mean_group_b:.3f}")

        if interpretation == "polarized":
            print("\n⚡ Der Schwarm ist in stabile Lager polarisiert.")
        elif interpretation == "consensus":
            print("\n🤝 Der Schwarm hat eine robuste Konsenszone ausgebildet.")
        else:
            print("\n🔄 Der Schwarm bleibt in einer hybriden Zwischenphase aus Konsens und Lagerbildung.")

    results = {
        'scenario': scenario,
        'config': dict(config),
        'final_polarization_index': finale_pi,
        'final_consensus_score': finaler_konsens,
        'final_group_distance': finaler_abstand,
        'left_count': links,
        'center_count': mitte,
        'right_count': rechts,
        'cross_group_interaction_rate': cross_group_rate,
        'cross_group_cooperation_rate': cross_group_cooperation_rate,
        'role_switch_enabled': bool(config.get('enable_role_switching')),
        'missions_enabled': bool(config.get('enable_missions')),
        'mission_assignment': str(config.get('mission_assignment', 'static')),
        'mission_arbitration_enabled': bool(
            config.get('mission_arbitration_enabled') or config.get('mission_assignment') == 'arbitrated'
        ),
        'initial_role_counts': initial_role_counts,
        'role_counts': role_counts,
        'role_mean_intelligence': role_mean_intelligence,
        'role_mean_reputation': role_mean_reputation,
        'role_mean_opinion_shift': role_mean_opinion_shift,
        'role_cross_group_cooperation_rate': role_cross_group_cooperation_rate,
        'role_switch_history': role_switch_history,
        'role_switch_total': int(sum(role_switch_history)),
        'role_transition_counts': dict(role_transition_counts),
        'initial_mission_counts': initial_mission_counts,
        'mission_counts': mission_counts,
        'mission_success_rates': mission_success_rates,
        'mission_switch_history': mission_switch_history,
        'mission_switch_total': int(sum(mission_switch_history)),
        'mission_conflict_history': mission_conflict_history,
        'mission_conflict_total': mission_conflict_total,
        'mission_arbitration_history': mission_arbitration_history,
        'mission_arbitration_total': mission_arbitration_total,
        'mission_arbitration_mean_gain': mission_arbitration_mean_gain,
        'mission_switch_stability': mission_switch_stability,
        'workflow_metrics': workflow_metrics,
        'group_1_mean_opinion': mean_group_a,
        'group_2_mean_opinion': mean_group_b,
        'interpretation': interpretation,
        'rewiring_enabled': bool(config.get('enable_dynamic_rewiring')),
        'polarization_history': polarisierungs_history,
        'consensus_history': konsens_history,
        'group_distance_history': gruppenabstand_history,
        'left_history': links_history,
        'center_history': mitte_history,
        'right_history': rechts_history,
        'group_a_intelligence_history': gruppe_a_intelligenz,
        'group_b_intelligence_history': gruppe_b_intelligenz,
        'cross_group_history': cross_group_history,
        'cross_group_cooperation_history': cross_group_cooperation_history,
        'bridge_count_history': bridge_count_history,
        'center_zone_history': center_zone_history,
        'removed_edges_history': removed_edges_history,
        'added_edges_history': added_edges_history,
        'rewired_edges_history': rewired_edges_history,
        'removed_reputation_history': removed_reputation_history,
        'removed_distance_history': removed_distance_history,
        'network_density_history': density_history,
        'mean_degree_history': mean_degree_history,
        'neighbor_opinion_distance_history': neighbor_distance_history,
        'cross_group_edge_share_history': cross_group_edge_share_history,
        'average_rewired_edges_per_round': durchschnitt_rewiring,
        'final_network_density': finale_netzwerkmetriken['density'],
        'final_mean_degree': finale_netzwerkmetriken['mean_degree'],
        'final_cross_group_edge_share': finale_netzwerkmetriken['cross_group_edge_share'],
        'final_neighbor_opinion_distance': finale_netzwerkmetriken['mean_neighbor_opinion_distance'],
        'agents': agenten,
    }

    if make_plot:
        if config.get('enable_dynamic_rewiring'):
            fig = plt.figure(figsize=(18, 16))
            axes = [fig.add_subplot(3, 3, index + 1) for index in range(9)]
            ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9 = axes
        else:
            fig = plt.figure(figsize=(18, 12))
            axes = [fig.add_subplot(2, 3, index + 1) for index in range(6)]
            ax1, ax2, ax3, ax4, ax5, ax6 = axes

        fig.suptitle(
            f'KKI Polarisierungs-Experiment: {scenario_title(scenario)}',
            fontsize=14,
            fontweight='bold',
        )

        runden_x = list(range(rounds + 1))

        ax1.set_title('Meinungsdynamik aller Agenten')
        ax1.set_ylabel('Meinung (0 = links, 1 = rechts)')
        ax1.set_xlabel('Runde')
        for agent in agenten:
            color = '#3498DB' if agent.gruppe == 0 else '#E74C3C'
            alpha = 0.6 if agent.hartnaeckigkeit > 0.4 else 0.25
            linewidth = 1.4 if agent.hartnaeckigkeit > 0.4 else 0.7
            ax1.plot(runden_x, agent.meinung_history, color=color, alpha=alpha, linewidth=linewidth)
        ax1.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5)
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)

        ax2.set_title('Polarisierung vs. Konsens')
        ax2.set_xlabel('Runde')
        ax2.set_ylabel('Index')
        ax2.plot(range(1, rounds + 1), polarisierungs_history, color='#8E44AD', linewidth=2, label='Polarisierungs-Index')
        ax2.plot(range(1, rounds + 1), konsens_history, color='#27AE60', linewidth=2, label='Konsens-Score')
        ax2.plot(range(1, rounds + 1), gruppenabstand_history, color='#F39C12', linewidth=2, label='Gruppenabstand')
        ax2.set_ylim(0, 1)
        ax2.legend(loc='best', fontsize=8)
        ax2.grid(True, alpha=0.3)

        ax3.set_title('Lagerbildung über Zeit')
        ax3.set_xlabel('Runde')
        ax3.set_ylabel('Anzahl Agenten')
        ax3.fill_between(range(1, rounds + 1), links_history, alpha=0.5, color='#3498DB', label='Links')
        ax3.fill_between(range(1, rounds + 1), mitte_history, alpha=0.5, color='#95A5A6', label='Mitte')
        ax3.fill_between(range(1, rounds + 1), rechts_history, alpha=0.5, color='#E74C3C', label='Rechts')
        ax3.set_ylim(0, int(config['agent_count']))
        ax3.legend(loc='upper right', fontsize=8)
        ax3.grid(True, alpha=0.3)

        ax4.set_title('Intelligenz nach Gruppen')
        ax4.set_xlabel('Runde')
        ax4.set_ylabel('Ø Intelligenz')
        ax4.plot(range(1, rounds + 1), gruppe_a_intelligenz, color='#3498DB', linewidth=2, label='Gruppe 1')
        ax4.plot(range(1, rounds + 1), gruppe_b_intelligenz, color='#E74C3C', linewidth=2, label='Gruppe 2')
        ax4.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
        ax4.legend(loc='best', fontsize=8)
        ax4.grid(True, alpha=0.3)

        ax5.set_title('Finale Position: Meinung vs. Kooperation')
        ax5.set_xlabel('Meinung')
        ax5.set_ylabel('Kooperationsneigung')
        for agent in agenten:
            color = '#3498DB' if agent.gruppe == 0 else '#E74C3C'
            ax5.scatter(
                agent.meinung,
                agent.kooperations_neigung,
                c=color,
                s=40 + agent.intelligenz * 12,
                alpha=0.7,
            )
        ax5.axvline(x=0.5, color='gray', linestyle=':', alpha=0.4)
        ax5.set_xlim(0, 1)
        ax5.set_ylim(0, 1)
        ax5.grid(True, alpha=0.3)

        ax6.set_title('Finale Meinungsverteilung')
        ax6.set_xlabel('Meinung')
        ax6.set_ylabel('Anzahl Agenten')
        agenten_g1 = [agent.meinung for agent in agenten if agent.gruppe == 0]
        agenten_g2 = [agent.meinung for agent in agenten if agent.gruppe == 1]
        ax6.hist(agenten_g1, bins=12, alpha=0.6, color='#3498DB', edgecolor='black', label='Gruppe 1')
        ax6.hist(agenten_g2, bins=12, alpha=0.6, color='#E74C3C', edgecolor='black', label='Gruppe 2')
        ax6.axvline(x=np.mean(agenten_g1), color='#1F618D', linestyle='--', linewidth=2)
        ax6.axvline(x=np.mean(agenten_g2), color='#922B21', linestyle='--', linewidth=2)
        ax6.legend(loc='best', fontsize=8)
        ax6.grid(True, alpha=0.3)

        if config.get('enable_dynamic_rewiring'):
            runden = range(1, rounds + 1)

            ax7.set_title('Adaptive Kanten pro Runde')
            ax7.set_xlabel('Runde')
            ax7.set_ylabel('Kantenänderungen')
            ax7.plot(runden, added_edges_history, color='#27AE60', linewidth=2, label='Hinzugefügt')
            ax7.plot(runden, removed_edges_history, color='#C0392B', linewidth=2, label='Entfernt')
            ax7.plot(runden, rewired_edges_history, color='#8E44AD', linewidth=2, label='Gesamt')
            ax7.legend(loc='best', fontsize=8)
            ax7.grid(True, alpha=0.3)

            ax8.set_title('Netzwerkdichte und mittlerer Grad')
            ax8.set_xlabel('Runde')
            ax8.set_ylabel('Dichte')
            linie_dichte = ax8.plot(runden, density_history, color='#1F618D', linewidth=2, label='Dichte')[0]
            ax8.set_ylim(0, max(0.05, max(density_history) * 1.2))
            ax8.grid(True, alpha=0.3)
            ax8_rechts = ax8.twinx()
            linie_grad = ax8_rechts.plot(
                runden,
                mean_degree_history,
                color='#F39C12',
                linewidth=2,
                label='Ø Grad',
            )[0]
            ax8_rechts.set_ylabel('Ø Grad')
            ax8.legend([linie_dichte, linie_grad], ['Dichte', 'Ø Grad'], loc='best', fontsize=8)

            ax9.set_title('Brücken und Nachbarschaftsabstand')
            ax9.set_xlabel('Runde')
            ax9.set_ylabel('Anteil / Distanz')
            ax9.plot(
                runden,
                cross_group_edge_share_history,
                color='#16A085',
                linewidth=2,
                label='Cross-Group-Kantenanteil',
            )
            ax9.plot(
                runden,
                neighbor_distance_history,
                color='#7F8C8D',
                linewidth=2,
                label='Ø Nachbarschaftsdistanz',
            )
            ax9.set_ylim(0, 1)
            ax9.legend(loc='best', fontsize=8)
            ax9.grid(True, alpha=0.3)

        plt.tight_layout()
        save_and_maybe_show(plt, output_filename, dpi=150)

    return results


def main():
    config, _ = build_runtime_config()
    run_polarization_experiment(config)


if __name__ == '__main__':
    main()
