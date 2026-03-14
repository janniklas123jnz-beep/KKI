"""
KKI DNA-Schema-Studie
=====================
Vergleicht explizite Bauvertraege fuer eine gemeinsame Agenten-Grund-DNA und
misst, welche Pflichtkomponenten, Invarianten und Startkonfigurationen die
spaetere Bauphase am stabilsten vorbereiten.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_gruppenidentitaet import (
    build_profile as build_identity_profile,
    modellkatalog,
    mittelwert,
    overlay_profiles,
)
from schwarm_gruppenrobustheit import robustness_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_DNA_SCHEMA_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_DNA_SCHEMA_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))
        failure_round = int(os.getenv('KKI_FAILURE_ROUND', '110'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'failure_round': min(rounds - 1, max(attack_round + 1, failure_round)),
        'agent_count': int(os.getenv('KKI_DNA_SCHEMA_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_DNA_SCHEMA_STRESS_STRENGTH', '0.44')),
        'stress_sources': int(os.getenv('KKI_DNA_SCHEMA_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_DNA_SCHEMA_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
    }


def get_named(items, name):
    return next(item for item in items if item['name'] == name)


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def normalize(value, minimum, maximum):
    if maximum <= minimum:
        return 0.0
    return clamp01((float(value) - minimum) / (maximum - minimum))


def kontexte():
    return [
        {'name': 'bootstrap', 'label': 'Bootstrap', 'scenario': 'consensus', 'bootstrap_mode': True},
        {'name': 'consensus', 'label': 'Konsens', 'scenario': 'consensus'},
        {
            'name': 'stress',
            'label': 'Manipulationsstress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def schema_profiles(katalog):
    shared_identity = build_identity_profile(katalog, get_named(overlay_profiles(), 'shared-dna'))
    robust_balance = get_named(robustness_profiles(katalog), 'robuste-balance')['config']

    base_contract = {
        **robust_balance,
        'roles_enabled': True,
        'analyzer_memory_window': max(
            int(robust_balance.get('analyzer_memory_window', 24)),
            int(shared_identity.get('analyzer_memory_window', 24)),
        ),
        'analyzer_learning_multiplier': max(
            float(robust_balance.get('analyzer_learning_multiplier', 1.18)),
            float(shared_identity.get('analyzer_learning_multiplier', 1.18)),
        ),
        'connector_cross_group_learning_bonus': max(
            float(robust_balance.get('connector_cross_group_learning_bonus', 0.12)),
            float(shared_identity.get('connector_cross_group_learning_bonus', 0.12)),
        ),
        'rewire_cross_group_bonus': max(
            float(robust_balance.get('rewire_cross_group_bonus', 0.10)),
            float(shared_identity.get('rewire_cross_group_bonus', 0.10)),
        ),
        'generalist_share': max(
            float(robust_balance.get('generalist_share', 0.14)),
            float(shared_identity.get('generalist_share', 0.18)),
        ),
    }

    underdefined = {
        **base_contract,
        'enable_missions': False,
        'mission_arbitration_enabled': False,
        'enable_workflow_stages': False,
        'enable_workflow_cells': False,
        'enable_handoff_coordination': False,
        'enable_parallel_workflow_cells': False,
        'enable_resource_coordination': False,
        'enable_capability_clusters': False,
        'enable_asymmetric_cluster_budgets': False,
        'enable_bottleneck_management': False,
        'enable_meta_coordination': False,
        'enable_fault_isolation': False,
        'enable_role_switching': False,
        'resource_budget': 0.54,
        'resource_share_factor': 0.16,
        'cluster_budget_skew': 0.38,
        'group_learning_rate': 0.10,
        'meta_priority_strength': 0.24,
        'trust_shield_strength': 0.14,
        'rewire_cross_group_bonus': 0.06,
        'connector_cross_group_learning_bonus': 0.10,
        'analyzer_memory_window': 18,
        'analyzer_learning_multiplier': 1.12,
    }
    underdefined['generalist_share'] = max(
        0.08,
        1.0
        - underdefined.get('connector_share', 0.0)
        - underdefined.get('sentinel_share', 0.0)
        - underdefined.get('mediator_share', 0.0)
        - underdefined.get('analyzer_share', 0.0),
    )

    minimal_contract = {
        **base_contract,
        'enable_role_switching': False,
        'resource_budget': 0.60,
        'resource_share_factor': 0.20,
        'cluster_budget_skew': 0.28,
        'group_learning_rate': 0.12,
        'meta_priority_strength': 0.30,
        'trust_shield_strength': 0.22,
        'rewire_cross_group_bonus': max(0.10, float(base_contract.get('rewire_cross_group_bonus', 0.10))),
        'connector_cross_group_learning_bonus': max(
            0.14,
            float(base_contract.get('connector_cross_group_learning_bonus', 0.14)),
        ),
        'analyzer_memory_window': max(24, int(base_contract.get('analyzer_memory_window', 24)) - 8),
        'analyzer_learning_multiplier': max(
            1.18, float(base_contract.get('analyzer_learning_multiplier', 1.18)) - 0.04
        ),
        'quarantine_compromise_threshold': 0.24,
        'quarantine_exposure_threshold': 0.30,
    }

    learning_contract = {
        **minimal_contract,
        'enable_role_switching': True,
        'group_learning_rate': max(0.16, float(base_contract.get('group_learning_rate', 0.14)) + 0.02),
        'analyzer_memory_window': max(54, int(base_contract.get('analyzer_memory_window', 36)) + 8),
        'analyzer_learning_multiplier': max(
            1.30, float(base_contract.get('analyzer_learning_multiplier', 1.24)) + 0.04
        ),
        'connector_cross_group_learning_bonus': max(
            0.20,
            float(base_contract.get('connector_cross_group_learning_bonus', 0.16)) + 0.02,
        ),
        'rewire_cross_group_bonus': max(0.16, float(base_contract.get('rewire_cross_group_bonus', 0.12)) + 0.02),
        'resource_budget': 0.64,
        'resource_share_factor': 0.24,
        'trust_shield_strength': 0.26,
        'meta_priority_strength': 0.34,
        'quarantine_compromise_threshold': 0.23,
        'quarantine_exposure_threshold': 0.29,
    }

    security_contract = {
        **minimal_contract,
        'enable_role_switching': True,
        'group_learning_rate': 0.14,
        'resource_budget': 0.64,
        'resource_share_factor': 0.22,
        'cluster_budget_skew': 0.24,
        'trust_shield_strength': 0.40,
        'meta_priority_strength': 0.36,
        'quarantine_compromise_threshold': 0.20,
        'quarantine_exposure_threshold': 0.26,
        'rewire_cross_group_bonus': 0.12,
        'connector_cross_group_learning_bonus': 0.16,
    }

    balanced_contract = {
        **base_contract,
        'enable_role_switching': True,
        'resource_budget': max(0.68, float(base_contract.get('resource_budget', 0.66))),
        'resource_share_factor': max(0.26, float(base_contract.get('resource_share_factor', 0.24))),
        'cluster_budget_skew': max(0.16, float(base_contract.get('cluster_budget_skew', 0.24)) - 0.02),
        'group_learning_rate': max(0.17, float(base_contract.get('group_learning_rate', 0.14))),
        'meta_priority_strength': max(0.38, float(base_contract.get('meta_priority_strength', 0.34))),
        'trust_shield_strength': max(0.38, float(base_contract.get('trust_shield_strength', 0.34))),
        'rewire_cross_group_bonus': max(0.16, float(base_contract.get('rewire_cross_group_bonus', 0.12))),
        'connector_cross_group_learning_bonus': max(
            0.20,
            float(base_contract.get('connector_cross_group_learning_bonus', 0.16)),
        ),
        'analyzer_memory_window': max(48, int(base_contract.get('analyzer_memory_window', 36))),
        'analyzer_learning_multiplier': max(
            1.28, float(base_contract.get('analyzer_learning_multiplier', 1.24))
        ),
        'quarantine_compromise_threshold': 0.21,
        'quarantine_exposure_threshold': 0.28,
        'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')) + 0.06,
    }

    overloaded_contract = {
        **balanced_contract,
        'generalist_share': 0.08,
        'connector_share': min(0.26, float(balanced_contract.get('connector_share', 0.18)) + 0.04),
        'sentinel_share': min(0.28, float(balanced_contract.get('sentinel_share', 0.18)) + 0.05),
        'mediator_share': max(0.16, float(balanced_contract.get('mediator_share', 0.20)) - 0.02),
        'analyzer_share': min(0.26, float(balanced_contract.get('analyzer_share', 0.20)) + 0.04),
        'resource_budget': 0.86,
        'resource_share_factor': 0.34,
        'cluster_budget_skew': 0.44,
        'group_learning_rate': 0.24,
        'meta_priority_strength': 0.48,
        'trust_shield_strength': 0.48,
        'rewire_cross_group_bonus': 0.24,
        'connector_cross_group_learning_bonus': 0.28,
        'analyzer_memory_window': 90,
        'analyzer_learning_multiplier': 1.44,
        'quarantine_compromise_threshold': 0.17,
        'quarantine_exposure_threshold': 0.22,
        'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')) + 0.14,
    }

    return [
        {'name': 'homogen', 'label': 'Homogen', 'config': {}},
        {'name': 'underdefined-contract', 'label': 'Unterdefinierte DNA', 'config': underdefined},
        {'name': 'minimal-contract', 'label': 'Minimaler Bauvertrag', 'config': minimal_contract},
        {'name': 'learning-contract', 'label': 'Lernfokussierter Vertrag', 'config': learning_contract},
        {'name': 'security-contract', 'label': 'Sicherheitsvertrag', 'config': security_contract},
        {'name': 'balanced-contract', 'label': 'Balancierter Bauvertrag', 'config': balanced_contract},
        {'name': 'overloaded-contract', 'label': 'Ueberfrachteter Vertrag', 'config': overloaded_contract},
    ]


def schema_metrics(config):
    required_flags = [
        'roles_enabled',
        'enable_missions',
        'mission_arbitration_enabled',
        'enable_workflow_stages',
        'enable_workflow_cells',
        'enable_handoff_coordination',
        'enable_resource_coordination',
        'enable_capability_clusters',
        'enable_meta_coordination',
        'enable_fault_isolation',
    ]
    mandatory_coverage = mittelwert([1.0 if config.get(flag, False) else 0.0 for flag in required_flags])

    generalist_share = float(config.get('generalist_share', 0.0))
    group_learning = float(config.get('group_learning_rate', 0.0))
    meta_priority = float(config.get('meta_priority_strength', 0.0))
    resource_budget = float(config.get('resource_budget', 0.0))
    resource_share = float(config.get('resource_share_factor', 0.0))
    cluster_skew = float(config.get('cluster_budget_skew', 0.0))
    trust_shield = float(config.get('trust_shield_strength', 0.0))
    memory_window = float(config.get('analyzer_memory_window', 0.0))
    learning_multiplier = float(config.get('analyzer_learning_multiplier', 1.0))
    cross_group_bonus = float(config.get('rewire_cross_group_bonus', 0.0))
    connector_learning_bonus = float(config.get('connector_cross_group_learning_bonus', 0.0))
    compromise_threshold = float(config.get('quarantine_compromise_threshold', 0.34))
    exposure_threshold = float(config.get('quarantine_exposure_threshold', 0.38))
    role_switch_interval = int(config.get('role_switch_interval', 0))
    role_switch_tenure = int(config.get('role_switch_min_tenure', 0))

    invariants = [
        not config.get('mission_arbitration_enabled', False) or config.get('enable_missions', False),
        not config.get('enable_handoff_coordination', False) or config.get('enable_workflow_cells', False),
        not config.get('enable_handoff_coordination', False) or config.get('enable_workflow_stages', False),
        not config.get('enable_meta_coordination', False) or config.get('enable_capability_clusters', False),
        not config.get('enable_meta_coordination', False) or config.get('enable_resource_coordination', False),
        0.10 <= generalist_share <= 0.30,
        0.12 <= group_learning <= 0.22,
        0.28 <= meta_priority <= 0.42,
        0.60 <= resource_budget <= 0.78,
        0.18 <= resource_share <= 0.30,
        0.16 <= cluster_skew <= 0.34,
        24.0 <= memory_window <= 72.0,
        1.18 <= learning_multiplier <= 1.40,
        0.10 <= cross_group_bonus <= 0.22,
        0.12 <= connector_learning_bonus <= 0.24,
        0.22 <= trust_shield <= 0.42,
        0.18 <= compromise_threshold <= exposure_threshold <= 0.32,
        not config.get('enable_role_switching', False) or 3 <= role_switch_interval <= 20,
        not config.get('enable_role_switching', False) or 1 <= role_switch_tenure <= max(1, role_switch_interval),
    ]
    invariant_compliance = mittelwert([1.0 if item else 0.0 for item in invariants])

    learning_capacity = mittelwert(
        [
            normalize(group_learning, 0.10, 0.20),
            normalize(memory_window, 18.0, 60.0),
            normalize(learning_multiplier, 1.10, 1.36),
            normalize(connector_learning_bonus, 0.08, 0.22),
            normalize(cross_group_bonus, 0.08, 0.18),
        ]
    )
    startup_readiness = mittelwert(
        [
            1.0 if config.get('roles_enabled', False) else 0.0,
            1.0 if config.get('enable_missions', False) else 0.0,
            1.0 if config.get('enable_workflow_stages', False) else 0.0,
            1.0 if config.get('enable_workflow_cells', False) else 0.0,
            1.0 if config.get('enable_handoff_coordination', False) else 0.0,
            1.0 if config.get('enable_meta_coordination', False) else 0.0,
            1.0 if config.get('enable_role_switching', False) else 0.0,
            normalize(resource_budget, 0.56, 0.72),
            normalize(generalist_share, 0.10, 0.22),
        ]
    )
    safety_margin = mittelwert(
        [
            normalize(trust_shield, 0.18, 0.40),
            1.0 - normalize(cluster_skew, 0.16, 0.40),
            1.0 if config.get('enable_fault_isolation', False) else 0.0,
            normalize(exposure_threshold - compromise_threshold, 0.04, 0.10),
            normalize(resource_share, 0.18, 0.28),
        ]
    )

    enabled_features = [
        'enable_missions',
        'mission_arbitration_enabled',
        'enable_role_switching',
        'enable_workflow_stages',
        'enable_workflow_cells',
        'enable_handoff_coordination',
        'enable_parallel_workflow_cells',
        'enable_resource_coordination',
        'enable_capability_clusters',
        'enable_asymmetric_cluster_budgets',
        'enable_bottleneck_management',
        'enable_meta_coordination',
        'enable_fault_isolation',
    ]
    feature_density = mittelwert([1.0 if config.get(flag, False) else 0.0 for flag in enabled_features])
    scalar_pressure = mittelwert(
        [
            normalize(resource_budget, 0.55, 0.90),
            normalize(cluster_skew, 0.16, 0.48),
            normalize(meta_priority, 0.26, 0.50),
            normalize(group_learning, 0.10, 0.24),
            normalize(trust_shield, 0.18, 0.50),
            normalize(memory_window, 18.0, 90.0),
        ]
    )
    overload_risk = clamp01(max(0.0, feature_density - 0.78) / 0.22 + max(0.0, scalar_pressure - 0.72) / 0.28)
    extensibility = mittelwert(
        [
            mandatory_coverage,
            invariant_compliance,
            learning_capacity,
            safety_margin,
            1.0 - overload_risk,
            normalize(generalist_share, 0.12, 0.24),
            normalize(cross_group_bonus, 0.08, 0.18),
        ]
    )
    contract_risk = clamp01((1.0 - mandatory_coverage) * 0.40 + (1.0 - invariant_compliance) * 0.35 + overload_risk * 0.25)

    return {
        'mandatory_coverage': mandatory_coverage,
        'invariant_compliance': invariant_compliance,
        'learning_capacity': learning_capacity,
        'startup_readiness': startup_readiness,
        'safety_margin': safety_margin,
        'overload_risk': overload_risk,
        'extensibility': extensibility,
        'contract_risk': contract_risk,
    }


def dna_schema_metrics(result):
    workflow = result['workflow_metrics']
    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'bottleneck_relief_rate': workflow.get('bottleneck_relief_rate', 0.0),
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'reconfiguration_switch_total': workflow.get('reconfiguration_switch_total', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
    }


def run_context(seed, params, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(eintrag['config'])
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('bootstrap_mode'):
        config['mission_switch_interval'] = 4
        config['role_switch_interval'] = max(4, int(config.get('role_switch_interval', 4)))
        config['role_switch_min_tenure'] = min(
            max(2, int(config.get('role_switch_min_tenure', 2))),
            int(config['role_switch_interval']),
        )
        config['workflow_stage_min_tenure'] = 1
        config['resource_budget'] = min(0.80, float(config.get('resource_budget', 0.60)) + 0.02)
        config['enable_prompt_injection'] = False
    elif kontext.get('enable_prompt_injection'):
        config['enable_prompt_injection'] = True
        config['injection_attack_round'] = params['attack_round']
        config['injection_strength'] = params['stress_strength']
        config['injection_source_count'] = params['stress_sources']
    else:
        config['enable_prompt_injection'] = False

    if kontext.get('enable_failures'):
        config['enable_cluster_failures'] = True
        config['enable_restart_recovery'] = True
        config['failure_round'] = params['failure_round']
        config['failure_duration'] = params['failure_duration']
        config.setdefault('failure_fraction', params['failure_fraction'])
        config.setdefault('resync_strength', params['resync_strength'])

    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    result['dna_schema_metrics'] = dna_schema_metrics(result)
    result['schema_metrics'] = schema_metrics(config)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['dna_schema_metrics']
    schema = result['schema_metrics']
    base = metrics['consensus'] - metrics['polarization']
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'bootstrap':
        return (
            metrics['completion_rate']
            + 0.14 * metrics['cross_group_cooperation']
            + 0.10 * metrics['skill_alignment_rate']
            + 0.10 * metrics['meta_alignment_rate']
            + 0.16 * schema['startup_readiness']
            + 0.12 * schema['mandatory_coverage']
            + 0.12 * schema['invariant_compliance']
            + 0.10 * schema['learning_capacity']
            - 0.12 * schema['overload_risk']
            - 0.08 * metrics['polarization']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.10 * metrics['resource_efficiency']
            + 0.10 * metrics['handoff_rate']
            + 0.12 * schema['extensibility']
            + 0.10 * schema['learning_capacity']
            - 0.08 * schema['overload_risk']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['detection_rate']
            + 0.12 * metrics['trust_shield_mean']
            + 0.12 * schema['safety_margin']
            + 0.10 * schema['invariant_compliance']
            + 0.08 * metrics['mission_success']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.10 * schema['overload_risk']
        )
    return (
        base
        + 0.18 * metrics['sync_strength_mean']
        + 0.16 * recoveries
        + 0.12 * schema['startup_readiness']
        + 0.10 * schema['extensibility']
        + 0.10 * schema['safety_margin']
        - 0.12 * failed_share
        - 0.10 * metrics['cluster_compromise_mean']
        - 0.08 * schema['overload_risk']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'resource_efficiency': {},
        'meta_alignment_rate': {},
        'skill_alignment_rate': {},
        'handoff_rate': {},
        'detection_rate': {},
        'corruption_mean': {},
        'cluster_compromise_mean': {},
        'trust_shield_mean': {},
        'recovery_events_total': {},
        'sync_strength_mean': {},
        'failed_agents_mean': {},
        'mandatory_coverage': {},
        'invariant_compliance': {},
        'learning_capacity': {},
        'startup_readiness': {},
        'safety_margin': {},
        'overload_risk': {},
        'extensibility': {},
        'contract_risk': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        metrics['completion_rate'][name] = mittelwert([run[name]['dna_schema_metrics']['completion_rate'] for run in runs])
        metrics['resource_efficiency'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['resource_efficiency'] for run in runs]
        )
        metrics['meta_alignment_rate'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['meta_alignment_rate'] for run in runs]
        )
        metrics['skill_alignment_rate'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['skill_alignment_rate'] for run in runs]
        )
        metrics['handoff_rate'][name] = mittelwert([run[name]['dna_schema_metrics']['handoff_rate'] for run in runs])
        metrics['detection_rate'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['detection_rate'] for run in runs]
        )
        metrics['corruption_mean'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['corruption_mean'] for run in runs]
        )
        metrics['cluster_compromise_mean'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['cluster_compromise_mean'] for run in runs]
        )
        metrics['trust_shield_mean'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['trust_shield_mean'] for run in runs]
        )
        metrics['recovery_events_total'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['recovery_events_total'] for run in runs]
        )
        metrics['sync_strength_mean'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['sync_strength_mean'] for run in runs]
        )
        metrics['failed_agents_mean'][name] = mittelwert(
            [run[name]['dna_schema_metrics']['failed_agents_mean'] for run in runs]
        )
        metrics['mandatory_coverage'][name] = mittelwert(
            [run[name]['schema_metrics']['mandatory_coverage'] for run in runs]
        )
        metrics['invariant_compliance'][name] = mittelwert(
            [run[name]['schema_metrics']['invariant_compliance'] for run in runs]
        )
        metrics['learning_capacity'][name] = mittelwert(
            [run[name]['schema_metrics']['learning_capacity'] for run in runs]
        )
        metrics['startup_readiness'][name] = mittelwert(
            [run[name]['schema_metrics']['startup_readiness'] for run in runs]
        )
        metrics['safety_margin'][name] = mittelwert([run[name]['schema_metrics']['safety_margin'] for run in runs])
        metrics['overload_risk'][name] = mittelwert([run[name]['schema_metrics']['overload_risk'] for run in runs])
        metrics['extensibility'][name] = mittelwert([run[name]['schema_metrics']['extensibility'] for run in runs])
        metrics['contract_risk'][name] = mittelwert([run[name]['schema_metrics']['contract_risk'] for run in runs])

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']], agent_count) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        **metrics,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    eintraege = schema_profiles(katalog)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI DNA-SCHEMA-STUDIE')
    print('=' * 84)
    print('Vergleicht explizite Bauvertraege fuer die gemeinsame Grund-DNA und misst,')
    print('welche Pflichtkomponenten die spaetere Bauphase stabil, lernfaehig und sicher machen.\n')

    summaries = []
    for profil_index, eintrag in enumerate(eintraege):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + profil_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                run[kontext['name']] = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    eintrag,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, eintrag, context_list, params['agent_count'])
        summaries.append(summary)
        print(
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"Coverage={summary['mandatory_coverage']['bootstrap']:.2f} | "
            f"Vertragsrisiko={summary['contract_risk']['bootstrap']:.2f} | "
            f"Sicherheitsreserve={summary['safety_margin']['stress']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'homogen')

    print('\nBeste DNA-Schema-Architektur:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur Homogenitaet {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Coverage {best['mandatory_coverage']['bootstrap']:.2f}, "
        f"Vertragsrisiko {best['contract_risk']['bootstrap']:.2f}, "
        f"Sicherheitsreserve {best['safety_margin']['stress']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#e15759', '#76b7b2', '#b07aa1']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter DNA-Schema-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['mandatory_coverage']['bootstrap'] for item in summaries],
        width,
        label='Pflichtabdeckung',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['invariant_compliance']['bootstrap'] for item in summaries],
        width,
        label='Invarianten',
        color='#59a14f',
    )
    axes[0, 1].set_title('Bauvertrag und Regelkonsistenz')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['learning_capacity']['bootstrap'] for item in summaries],
        width,
        label='Lernkapazitaet',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['startup_readiness']['bootstrap'] for item in summaries],
        width,
        label='Startbereitschaft',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Bootstrap-Faehigkeit')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['bootstrap'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['extensibility']['bootstrap'],
                item['contract_risk']['bootstrap'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4, 5])
    axes[1, 0].set_xticklabels(['Boot', 'Kon', 'Stress', 'Rec', 'Ext', 'Risk'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['safety_margin']['stress'] * 100.0 for item in summaries],
        width,
        label='Sicherheitsreserve (%)',
        color='#e15759',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['contract_risk']['bootstrap'] * 100.0 for item in summaries],
        width,
        label='Vertragsrisiko (%)',
        color='#edc948',
    )
    axes[1, 1].set_title('Vertragsrisiko und Schutz')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].axis('off')
    axes[1, 2].text(
        0.0,
        0.98,
        (
            "Zusammenfassung\n"
            f"- Bestes Profil: {best['label']}\n"
            f"- Delta zur Homogenitaet: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Pflichtabdeckung: {best['mandatory_coverage']['bootstrap']:.2f}\n"
            f"- Invarianten: {best['invariant_compliance']['bootstrap']:.2f}\n"
            f"- Vertragsrisiko: {best['contract_risk']['bootstrap']:.2f}\n"
            f"- Lernkapazitaet: {best['learning_capacity']['bootstrap']:.2f}\n"
            f"- Startbereitschaft: {best['startup_readiness']['bootstrap']:.2f}\n"
            f"- Erweiterbarkeit: {best['extensibility']['bootstrap']:.2f}\n"
            f"- Sicherheitsreserve: {best['safety_margin']['stress']:.2f}\n"
            f"- Recovery-Sync: {best['sync_strength_mean']['recovery']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_dna_schema.png', dpi=150)


if __name__ == '__main__':
    main()
