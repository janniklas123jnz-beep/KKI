"""
KKI Rollout-Protokolle-Studie
=============================
Vergleicht Update- und Rolloutarchitekturen fuer laufende Baugruppen und misst,
welche Patch- und Freigabelogik reale Adapter, Auditpfade und Recovery so koppelt,
dass Veraenderungen kontrolliert eingefuehrt werden koennen.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_missions_dry_run import mission_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_werkzeugadapter import adapter_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import (
    required_domain_coverage,
    required_domain_redundancy,
    route_specificity,
)
from schwarm_freigabe_workflow import approval_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_ROLLOUT_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_ROLLOUT_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_ROLLOUT_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_ROLLOUT_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_ROLLOUT_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_ROLLOUT_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
        'memory_window': int(os.getenv('KKI_MEMORY_WINDOW', '36')),
        'audit_depth': int(os.getenv('KKI_MEMORY_AUDIT_DEPTH', '4')),
        'approval_window': int(os.getenv('KKI_APPROVAL_WINDOW', '3')),
        'acceptance_cycles': int(os.getenv('KKI_MISSION_DRY_RUN_ACCEPTANCE_CYCLES', '3')),
    }


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def normalize(value, minimum, maximum):
    if maximum <= minimum:
        return 0.0
    return clamp01((float(value) - minimum) / (maximum - minimum))


def kontexte():
    return [
        {
            'name': 'patching',
            'label': 'Patchen',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('execution', 'trace'),
        },
        {
            'name': 'window',
            'label': 'Update-Fenster',
            'scenario': 'consensus',
            'window_mode': True,
            'required_domains': ('execution', 'approval', 'coordination'),
        },
        {
            'name': 'stress',
            'label': 'Stress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'required_domains': ('execution', 'security', 'approval', 'trace'),
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
            'required_domains': ('execution', 'memory', 'handoff', 'security'),
        },
    ]


def rollout_profiles(katalog, params):
    adapter = get_named(adapter_profiles(katalog, params), 'audit-gateway')
    approval = get_named(approval_profiles(katalog, params), 'resilienter-freigabe-workflow')
    mission = get_named(mission_profiles(katalog, params), 'resilienter-missions-dry-run')

    runtime = {
        **adapter['base_config'],
        **approval['base_config'],
        **mission['base_config'],
    }

    return [
        {
            'name': 'heisses-patchen',
            'label': 'Heisses Patchen',
            'selected_tools': ['execution'],
            'multiplier': 0.86,
            'base_config': {
                **runtime,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 6,
                'mission_switch_interval': 6,
                'resource_share_factor': 0.27,
                'trust_shield_strength': 0.26,
            },
            'window_depth': 0,
            'gate_layers': 0,
            'shadow_layers': 0,
            'rollback_depth': 1,
            'bias': {
                'readiness': 0.28,
                'safety': 0.20,
                'trace': 0.14,
                'continuity': 0.90,
                'recovery': 0.26,
                'overhead': 0.06,
            },
        },
        {
            'name': 'wartungsfenster',
            'label': 'Wartungsfenster',
            'selected_tools': ['memory', 'execution', 'bridge'],
            'multiplier': 0.90,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'handoff_priority_bonus': 0.22,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.30,
            },
            'window_depth': 2,
            'gate_layers': 1,
            'shadow_layers': 0,
            'rollback_depth': 2,
            'bias': {
                'readiness': 0.56,
                'safety': 0.48,
                'trace': 0.50,
                'continuity': 0.74,
                'recovery': 0.48,
                'overhead': 0.14,
            },
        },
        {
            'name': 'stage-gate-rollout',
            'label': 'Stage-Gate-Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.95,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.36,
            },
            'window_depth': 3,
            'gate_layers': 2,
            'shadow_layers': 1,
            'rollback_depth': 3,
            'bias': {
                'readiness': 0.78,
                'safety': 0.78,
                'trace': 0.82,
                'continuity': 0.72,
                'recovery': 0.70,
                'overhead': 0.22,
            },
        },
        {
            'name': 'foederierter-rollout',
            'label': 'Foederierter Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                **adapter['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.37,
            },
            'window_depth': 4,
            'gate_layers': 3,
            'shadow_layers': 1,
            'rollback_depth': 3,
            'bias': {
                'readiness': 0.88,
                'safety': 0.86,
                'trace': 0.90,
                'continuity': 0.84,
                'recovery': 0.82,
                'overhead': 0.26,
            },
        },
        {
            'name': 'shadow-rollout',
            'label': 'Shadow-Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.99,
            'base_config': {
                **runtime,
                **adapter['base_config'],
                **mission['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
            },
            'window_depth': 4,
            'gate_layers': 3,
            'shadow_layers': 3,
            'rollback_depth': 3,
            'bias': {
                'readiness': 0.92,
                'safety': 0.92,
                'trace': 0.92,
                'continuity': 0.76,
                'recovery': 0.86,
                'overhead': 0.30,
            },
        },
        {
            'name': 'resilientes-rollout-protokoll',
            'label': 'Resilientes Rollout-Protokoll',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **adapter['base_config'],
                **approval['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.03),
                'resync_strength': 0.48,
            },
            'window_depth': 5,
            'gate_layers': 4,
            'shadow_layers': 3,
            'rollback_depth': 4,
            'bias': {
                'readiness': 0.94,
                'safety': 0.96,
                'trace': 0.96,
                'continuity': 0.72,
                'recovery': 0.92,
                'overhead': 0.36,
            },
        },
    ]


def rollout_metrics(config, result, params, profile, kontext):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    required_domains = kontext['required_domains']
    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]

    coverage = required_domain_coverage(selected_tools, catalog, required_domains)
    redundancy = required_domain_redundancy(selected_tools, catalog, required_domains)
    specificity = route_specificity(selected_tools, required_domains)
    traceability = clamp01(mittelwert(trace_scores))
    exposure = clamp01(mittelwert(exposure_scores))
    window_depth_score = normalize(profile['window_depth'], 0.0, 5.0)
    gate_layers_score = normalize(profile['gate_layers'], 0.0, 4.0)
    shadow_layers_score = normalize(profile['shadow_layers'], 0.0, 3.0)
    rollback_depth_score = normalize(profile['rollback_depth'], 1.0, 4.0)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count

    rollout_readiness = clamp01(
        mittelwert(
            [
                coverage,
                redundancy,
                specificity,
                workflow.get('completion_rate', 0.0),
                profile['bias']['readiness'],
            ]
        )
    )
    rollout_safety = clamp01(
        mittelwert(
            [
                traceability,
                1.0 - exposure,
                workflow.get('misinformation_detection_rate', 0.0),
                gate_layers_score,
                profile['bias']['safety'],
            ]
        )
    )
    audit_rollout = clamp01(
        mittelwert(
            [
                traceability,
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                shadow_layers_score,
                profile['bias']['trace'],
            ]
        )
    )
    continuity_strength = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                result['cross_group_cooperation_rate'],
                groups['functional_group_share'],
                profile['bias']['continuity'],
            ]
        )
    )
    rollback_recovery = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                rollback_depth_score,
                profile['bias']['recovery'],
            ]
        )
    )
    recovery_readiness = clamp01(
        mittelwert(
            [
                rollback_recovery,
                audit_rollout,
                1.0 - exposure,
                workflow.get('sync_strength_mean', 0.0),
            ]
        )
    )
    rollout_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('workflow_stage_min_tenure', 1), 1.0, 3.0),
                window_depth_score,
                gate_layers_score,
                shadow_layers_score,
                profile['bias']['overhead'],
            ]
        )
    )
    rollout_integrity = clamp01(
        mittelwert(
            [
                rollout_readiness,
                rollout_safety,
                audit_rollout,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                traceability,
            ]
        )
    )
    protocol_resilience = clamp01(
        mittelwert(
            [
                continuity_strength,
                rollback_recovery,
                recovery_readiness,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - rollout_overhead,
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'rollout_readiness': rollout_readiness,
        'rollout_safety': rollout_safety,
        'audit_rollout': audit_rollout,
        'continuity_strength': continuity_strength,
        'rollback_recovery': rollback_recovery,
        'recovery_readiness': recovery_readiness,
        'rollout_integrity': rollout_integrity,
        'protocol_resilience': protocol_resilience,
        'rollout_overhead': rollout_overhead,
        'route_exposure': exposure,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    rollout_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(rollout_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('window_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 2)
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
    result['rollout_metrics'] = rollout_metrics(config, result, params, profile, kontext)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['rollout_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'patching':
        return (
            metrics['rollout_integrity']
            + 0.18 * metrics['protocol_resilience']
            + 0.14 * metrics['continuity_strength']
            + 0.08 * metrics['audit_rollout']
            - 0.10 * metrics['rollout_overhead']
        )
    if kontext_name == 'window':
        return (
            metrics['protocol_resilience']
            + 0.18 * metrics['rollout_integrity']
            + 0.14 * metrics['rollout_safety']
            + 0.10 * metrics['audit_rollout']
            - 0.10 * metrics['rollout_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['rollout_integrity']
            + 0.14 * metrics['protocol_resilience']
            + 0.10 * metrics['rollout_safety']
            - 0.10 * metrics['route_exposure']
            - 0.08 * metrics['rollout_overhead']
        )
    if kontext_name == 'recovery':
        return (
            base
            + 0.20 * metrics['protocol_resilience']
            + 0.14 * metrics['rollback_recovery']
            + 0.10 * metrics['recovery_readiness']
            - 0.12 * failed_share
            - 0.08 * metrics['rollout_overhead']
        )
    return (
        metrics['rollout_integrity']
        + 0.18 * metrics['continuity_strength']
        + 0.12 * metrics['audit_rollout']
        - 0.10 * metrics['rollout_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'rollout_readiness': {},
        'rollout_safety': {},
        'audit_rollout': {},
        'continuity_strength': {},
        'rollback_recovery': {},
        'recovery_readiness': {},
        'rollout_integrity': {},
        'protocol_resilience': {},
        'rollout_overhead': {},
        'route_exposure': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['rollout_metrics'][metric_name] for run in runs])

    return {
        'name': profile['name'],
        'label': profile['label'],
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
    profiles = rollout_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI ROLLOUT-PROTOKOLL-STUDIE')
    print('=' * 84)
    print('Vergleicht Update- und Rolloutarchitekturen fuer laufende Baugruppen,')
    print('damit Patchfenster, Freigaben und Recovery ueber reale Adapter kontrolliert bleiben.\n')

    summaries = []
    for profile_index, profile in enumerate(profiles):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + profile_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                run[kontext['name']] = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    profile,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, profile, context_list, params['agent_count'])
        summaries.append(summary)
        print(
            f"{summary['label']:<30} Score={summary['combined_score']:+.3f} | "
            f"Integritaet={summary['rollout_integrity']['stress']:.2f} | "
            f"Protokoll-Resilienz={summary['protocol_resilience']['recovery']:.2f} | "
            f"Audit={summary['audit_rollout']['window']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'heisses-patchen')

    print('\nBestes Rollout-Protokoll:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Heisses Patchen {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Integritaet {best['rollout_integrity']['stress']:.2f}, "
        f"Audit {best['audit_rollout']['window']:.2f}, "
        f"Protokoll-Resilienz {best['protocol_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Rollout-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['rollout_integrity']['stress'] for item in summaries],
        width,
        label='Rollout-Integritaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['continuity_strength']['window'] for item in summaries],
        width,
        label='Kontinuitaet',
        color='#59a14f',
    )
    axes[0, 1].set_title('Integritaet und Kontinuitaet')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['rollout_safety']['stress'] for item in summaries],
        width,
        label='Rollout-Sicherheit',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['route_exposure']['stress'] for item in summaries],
        width,
        label='Route-Exposition',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Sicherheit und Exposition')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['protocol_resilience']['recovery'] for item in summaries],
        width,
        label='Protokoll-Resilienz',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['rollout_overhead']['window'] for item in summaries],
        width,
        label='Rollout-Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Protokoll-Resilienz gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['window'] for item in summaries], color=colors)
    axes[1, 1].set_title('Updatefenster-Kontextscore')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].bar(
        x - width / 2,
        [item['context_scores']['stress'] for item in summaries],
        width,
        label='Stress',
        color='#e15759',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['recovery_readiness']['recovery'] for item in summaries],
        width,
        label='Recovery-Bereitschaft',
        color='#4e79a7',
    )
    axes[1, 2].set_title('Stress und Recovery-Bereitschaft')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_rollout_protokolle.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
