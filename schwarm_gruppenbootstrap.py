"""
KKI Gruppen-Bootstrap-Studie
============================
Vergleicht Initialisierungsstrategien fuer Rollen, Gruppen und Overlay-Pakete
und misst, welche Startlogik Spezialisierung frueh koordinierbar macht, ohne
den Schwarm bereits beim Hochfahren zu fragmentieren.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named, schema_metrics, schema_profiles
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_overlay_module import build_profile as build_overlay_profile
from schwarm_overlay_module import overlay_profiles as overlay_module_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


ROLE_KEYS = ['connector_share', 'sentinel_share', 'mediator_share', 'analyzer_share']


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_GROUP_BOOTSTRAP_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_GROUP_BOOTSTRAP_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_GROUP_BOOTSTRAP_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_GROUP_BOOTSTRAP_STRESS_STRENGTH', '0.45')),
        'stress_sources': int(os.getenv('KKI_GROUP_BOOTSTRAP_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_GROUP_BOOTSTRAP_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
    }


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


def role_balance_score(config):
    targets = {
        'generalist_share': 0.16,
        'connector_share': 0.20,
        'sentinel_share': 0.20,
        'mediator_share': 0.22,
        'analyzer_share': 0.22,
    }
    deviations = []
    for key, target in targets.items():
        deviations.append(abs(float(config.get(key, target)) - target) / max(0.05, target))
    return clamp01(1.0 - mittelwert(deviations))


def bootstrap_profiles(katalog, params):
    balanced_contract = get_named(schema_profiles(katalog), 'balanced-contract')['config']
    compatible_overlay, _ = build_overlay_profile(
        katalog, params, get_named(overlay_module_profiles(), 'kompatible-overlays')
    )
    adaptive_overlay, _ = build_overlay_profile(
        katalog, params, get_named(overlay_module_profiles(), 'adaptiver-stack')
    )
    isolated_overlay, _ = build_overlay_profile(
        katalog, params, get_named(overlay_module_profiles(), 'isolierte-module')
    )

    return [
        {
            'name': 'unvorbereiteter-start',
            'label': 'Unvorbereiteter Start',
            'config': {
                **balanced_contract,
                'enable_role_switching': False,
                'workflow_stage_min_tenure': 4,
                'mission_switch_interval': 10,
                'resource_share_factor': max(0.18, balanced_contract.get('resource_share_factor', 0.26) - 0.06),
                'meta_priority_strength': max(0.28, balanced_contract.get('meta_priority_strength', 0.38) - 0.08),
                'group_learning_rate': max(0.12, balanced_contract.get('group_learning_rate', 0.17) - 0.04),
                'rewire_cross_group_bonus': max(
                    0.10, balanced_contract.get('rewire_cross_group_bonus', 0.16) - 0.04
                ),
            },
            'bias': {'randomness': 0.92, 'validation': 0.16, 'staging': 0.10, 'recovery': 0.18, 'alignment': 0.28},
        },
        {
            'name': 'zufalls-bootstrap',
            'label': 'Zufalls-Bootstrap',
            'config': {
                **compatible_overlay,
                'generalist_share': 0.22,
                'connector_share': 0.18,
                'sentinel_share': 0.18,
                'mediator_share': 0.22,
                'analyzer_share': 0.20,
                'enable_role_switching': True,
                'role_switch_interval': 8,
                'role_switch_min_tenure': 4,
                'resource_share_factor': max(0.20, compatible_overlay.get('resource_share_factor', 0.26) - 0.03),
                'meta_priority_strength': max(0.30, compatible_overlay.get('meta_priority_strength', 0.38) - 0.04),
            },
            'bias': {'randomness': 0.84, 'validation': 0.26, 'staging': 0.18, 'recovery': 0.28, 'alignment': 0.44},
        },
        {
            'name': 'cluster-bootstrap',
            'label': 'Cluster-Bootstrap',
            'config': {
                **isolated_overlay,
                'enable_role_switching': True,
                'role_switch_interval': 6,
                'role_switch_min_tenure': 3,
                'workflow_stage_min_tenure': 2,
                'cluster_budget_skew': min(0.30, isolated_overlay.get('cluster_budget_skew', 0.22) + 0.02),
                'resource_share_factor': max(0.20, isolated_overlay.get('resource_share_factor', 0.22) - 0.01),
                'rewire_cross_group_bonus': max(0.10, isolated_overlay.get('rewire_cross_group_bonus', 0.12) - 0.02),
            },
            'bias': {'randomness': 0.34, 'validation': 0.50, 'staging': 0.42, 'recovery': 0.34, 'alignment': 0.72},
        },
        {
            'name': 'rollen-bootstrap',
            'label': 'Rollen-Bootstrap',
            'config': {
                **compatible_overlay,
                'generalist_share': 0.14,
                'connector_share': 0.22,
                'sentinel_share': 0.20,
                'mediator_share': 0.24,
                'analyzer_share': 0.20,
                'enable_role_switching': True,
                'role_switch_interval': 6,
                'role_switch_min_tenure': 3,
                'workflow_stage_min_tenure': 2,
                'handoff_priority_bonus': 0.18,
                'resource_share_factor': min(0.30, compatible_overlay.get('resource_share_factor', 0.26) + 0.01),
            },
            'bias': {'randomness': 0.22, 'validation': 0.62, 'staging': 0.58, 'recovery': 0.38, 'alignment': 0.82},
        },
        {
            'name': 'phasen-bootstrap',
            'label': 'Phasen-Bootstrap',
            'config': {
                **adaptive_overlay,
                'enable_role_switching': True,
                'role_switch_interval': 5,
                'role_switch_min_tenure': 2,
                'workflow_stage_min_tenure': 1,
                'mission_switch_interval': 4,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.20,
                'resource_share_factor': min(0.30, adaptive_overlay.get('resource_share_factor', 0.29) + 0.01),
                'rewire_cross_group_bonus': min(0.18, adaptive_overlay.get('rewire_cross_group_bonus', 0.18) + 0.01),
            },
            'bias': {'randomness': 0.16, 'validation': 0.78, 'staging': 0.90, 'recovery': 0.52, 'alignment': 0.88},
        },
        {
            'name': 'resilienter-bootstrap',
            'label': 'Resilienter Bootstrap',
            'config': {
                **adaptive_overlay,
                'generalist_share': 0.18,
                'connector_share': 0.22,
                'sentinel_share': 0.18,
                'mediator_share': 0.24,
                'analyzer_share': 0.18,
                'enable_role_switching': True,
                'role_switch_interval': 5,
                'role_switch_min_tenure': 2,
                'workflow_stage_min_tenure': 1,
                'mission_switch_interval': 4,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.20,
                'resource_budget': min(0.76, adaptive_overlay.get('resource_budget', 0.71) + 0.02),
                'resource_share_factor': min(0.30, adaptive_overlay.get('resource_share_factor', 0.29) + 0.01),
                'meta_priority_strength': min(
                    0.40, adaptive_overlay.get('meta_priority_strength', 0.40) + 0.01
                ),
                'trust_shield_strength': min(
                    0.42, adaptive_overlay.get('trust_shield_strength', 0.38) + 0.03
                ),
                'rewire_cross_group_bonus': min(
                    0.18, adaptive_overlay.get('rewire_cross_group_bonus', 0.17) + 0.02
                ),
                'connector_cross_group_learning_bonus': min(
                    0.24, adaptive_overlay.get('connector_cross_group_learning_bonus', 0.20) + 0.02
                ),
                'cluster_budget_skew': max(0.16, adaptive_overlay.get('cluster_budget_skew', 0.22) - 0.02),
                'resync_strength': min(0.54, adaptive_overlay.get('resync_strength', params['resync_strength']) + 0.08),
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
            },
            'bias': {'randomness': 0.10, 'validation': 0.90, 'staging': 0.88, 'recovery': 0.86, 'alignment': 0.90},
        },
    ]


def bootstrap_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)

    proto_share = groups['proto_group_share']
    functional_share = groups['functional_group_share']
    anti_monolith = 1.0 - groups['largest_group_share']
    cluster_diversity = min(1.0, groups['dominant_cluster_diversity'] / 3.0)
    skill_diversity = min(1.0, groups['dominant_skill_diversity'] / 3.0)
    separation = groups['group_separation']

    assignment_balance = clamp01(
        mittelwert(
            [
                role_balance_score(config),
                normalize(config.get('resource_share_factor', 0.0), 0.18, 0.30),
                normalize(config.get('meta_priority_strength', 0.0), 0.28, 0.40),
                normalize(config.get('rewire_cross_group_bonus', 0.0), 0.10, 0.18),
                1.0 - bias['randomness'],
            ]
        )
    )
    startup_cohesion = clamp01(
        mittelwert(
            [
                proto_share,
                functional_share,
                groups['strong_edge_rate'],
                result['cross_group_cooperation_rate'],
                anti_monolith,
                cluster_diversity,
                skill_diversity,
            ]
        )
        - 0.12 * max(0.0, separation - 0.12)
    )
    overlay_fit = clamp01(
        mittelwert(
            [
                workflow.get('skill_alignment_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('group_learning_gain_rate', 0.0),
                normalize(config.get('group_learning_rate', 0.0), 0.12, 0.20),
                bias['alignment'],
            ]
        )
    )
    handoff_readiness = clamp01(
        mittelwert(
            [
                workflow.get('handoff_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                workflow.get('active_cells_mean', 0.0) / 4.0,
                workflow.get('resource_efficiency', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                schema['startup_readiness'],
            ]
        )
    )
    startup_validation = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                schema['safety_margin'],
                schema['extensibility'],
                bias['validation'],
                1.0 - bias['randomness'],
            ]
        )
    )
    recovery_margin = clamp01(
        mittelwert(
            [
                normalize(config.get('trust_shield_strength', 0.0), 0.22, 0.42),
                normalize(config.get('resync_strength', params['resync_strength']), 0.24, 0.52),
                1.0 - normalize(config.get('failure_fraction', params['failure_fraction']), 0.10, 0.26),
                schema['safety_margin'],
                bias['recovery'],
            ]
        )
    )
    staging_quality = clamp01(
        mittelwert(
            [
                1.0 - normalize(config.get('workflow_stage_min_tenure', 2), 1.0, 5.0),
                1.0 - normalize(config.get('mission_switch_interval', 8), 4.0, 12.0),
                normalize(config.get('handoff_priority_bonus', 0.0), 0.12, 0.20),
                bias['staging'],
            ]
        )
    )
    fragmentation_risk = clamp01(
        0.22 * bias['randomness']
        + 0.20 * max(0.0, groups['largest_group_share'] - 0.46) / 0.28
        + 0.16 * max(0.0, separation - 0.14) / 0.20
        + 0.14 * (1.0 - result['cross_group_cooperation_rate'])
        + 0.14 * schema['contract_risk']
        + 0.14 * max(0.0, 0.16 - proto_share) / 0.16
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'learning_gain_rate': workflow.get('group_learning_gain_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'active_cells_mean': workflow.get('active_cells_mean', 0.0),
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'proto_group_share': proto_share,
        'functional_group_share': functional_share,
        'group_separation': separation,
        'largest_group_share': groups['largest_group_share'],
        'cluster_diversity': cluster_diversity,
        'skill_diversity': skill_diversity,
        'assignment_balance': assignment_balance,
        'startup_cohesion': startup_cohesion,
        'overlay_fit': overlay_fit,
        'handoff_readiness': handoff_readiness,
        'startup_validation': startup_validation,
        'recovery_margin': recovery_margin,
        'staging_quality': staging_quality,
        'fragmentation_risk': fragmentation_risk,
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
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
        config['mission_switch_interval'] = min(4, int(config.get('mission_switch_interval', 4)))
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
    result['bootstrap_metrics'] = bootstrap_metrics(config, result, params, eintrag['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['bootstrap_metrics']
    base = metrics['consensus'] - metrics['polarization']
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'bootstrap':
        return (
            metrics['completion_rate']
            + 0.14 * metrics['assignment_balance']
            + 0.14 * metrics['startup_validation']
            + 0.12 * metrics['startup_cohesion']
            + 0.12 * metrics['overlay_fit']
            + 0.10 * metrics['handoff_readiness']
            + 0.10 * metrics['staging_quality']
            - 0.20 * metrics['fragmentation_risk']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.12 * metrics['handoff_readiness']
            + 0.10 * metrics['overlay_fit']
            + 0.10 * metrics['functional_group_share']
            + 0.08 * metrics['startup_cohesion']
            - 0.12 * metrics['fragmentation_risk']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.14 * metrics['detection_rate']
            + 0.12 * metrics['recovery_margin']
            + 0.10 * metrics['startup_validation']
            + 0.10 * metrics['functional_group_share']
            + 0.08 * metrics['handoff_readiness']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.16 * metrics['fragmentation_risk']
        )
    return (
        base
        + 0.18 * metrics['sync_strength_mean']
        + 0.14 * recoveries
        + 0.14 * metrics['recovery_margin']
        + 0.10 * metrics['startup_validation']
        + 0.08 * metrics['handoff_readiness']
        - 0.12 * failed_share
        - 0.10 * metrics['cluster_compromise_mean']
        - 0.14 * metrics['fragmentation_risk']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'handoff_readiness': {},
        'startup_validation': {},
        'startup_cohesion': {},
        'assignment_balance': {},
        'overlay_fit': {},
        'fragmentation_risk': {},
        'functional_group_share': {},
        'detection_rate': {},
        'recovery_margin': {},
        'sync_strength_mean': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['bootstrap_metrics'][metric_name] for run in runs])

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
    eintraege = bootstrap_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI GRUPPEN-BOOTSTRAP-STUDIE')
    print('=' * 84)
    print('Vergleicht, wie Rollen, Gruppen und Overlay-Pakete beim Start verteilt')
    print('werden muessen, damit Spezialisierung frueh koordinierbar statt fragmentiert beginnt.\n')

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
            f"{summary['label']:<26} Score={summary['combined_score']:+.3f} | "
            f"Validierung={summary['startup_validation']['bootstrap']:.2f} | "
            f"Kohäsion={summary['startup_cohesion']['bootstrap']:.2f} | "
            f"Fragmentierung={summary['fragmentation_risk']['bootstrap']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'unvorbereiteter-start')

    print('\nBestes Bootstrap-Profil:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum unvorbereiteten Start {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Validierung {best['startup_validation']['bootstrap']:.2f}, "
        f"Handoff-Reife {best['handoff_readiness']['bootstrap']:.2f}, "
        f"Fragmentierung {best['fragmentation_risk']['bootstrap']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Bootstrap-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['startup_validation']['bootstrap'] for item in summaries],
        width,
        label='Validierung',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['assignment_balance']['bootstrap'] for item in summaries],
        width,
        label='Zuteilungsbalance',
        color='#59a14f',
    )
    axes[0, 1].set_title('Startlogik')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['startup_cohesion']['bootstrap'] for item in summaries],
        width,
        label='Start-Kohäsion',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['fragmentation_risk']['bootstrap'] for item in summaries],
        width,
        label='Fragmentierung',
        color='#e15759',
    )
    axes[0, 2].set_title('Gruppenbildung beim Start')
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
                item['handoff_readiness']['bootstrap'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Boot', 'Kon', 'Stress', 'Rec', 'Handoff'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['functional_group_share']['consensus'] * 100.0 for item in summaries],
        width,
        label='Funktionsgruppen (%)',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['detection_rate']['stress'] * 100.0 for item in summaries],
        width,
        label='Detektion (%)',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Gruppenfitness')
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
            f"- Delta zum unvorbereiteten Start: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Validierung: {best['startup_validation']['bootstrap']:.2f}\n"
            f"- Start-Kohäsion: {best['startup_cohesion']['bootstrap']:.2f}\n"
            f"- Handoff-Reife: {best['handoff_readiness']['bootstrap']:.2f}\n"
            f"- Recovery-Marge: {best['recovery_margin']['recovery']:.2f}\n"
            f"- Funktionsgruppen: {best['functional_group_share']['consensus']:.1%}\n"
            f"- Fragmentierung: {best['fragmentation_risk']['bootstrap']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_gruppenbootstrap.png', dpi=150)


if __name__ == '__main__':
    main()
