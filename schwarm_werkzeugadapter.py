"""
KKI Werkzeug-Adapter-Studie
===========================
Vergleicht Adapter- und IO-Schleusenarchitekturen fuer spaetere reale Schnittstellen
und misst, welche Kopplung von Wissensbus, Routing, Audit und Abschirmung reale
Werkzeugkontakte robust integriert, ohne den operativen Fluss zu blockieren.
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
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_sandbox_zellen import sandbox_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import (
    broker_profiles,
    required_domain_coverage,
    required_domain_redundancy,
    route_specificity,
)
from schwarm_wissensbus import knowledge_bus_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_TOOL_ADAPTER_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_TOOL_ADAPTER_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_TOOL_ADAPTER_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_TOOL_ADAPTER_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_TOOL_ADAPTER_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_TOOL_ADAPTER_FAILURE_FRACTION', '0.18')),
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
            'name': 'integration',
            'label': 'Integration',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('execution', 'memory'),
        },
        {
            'name': 'operations',
            'label': 'Operation',
            'scenario': 'consensus',
            'required_domains': ('execution', 'handoff', 'coordination'),
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


def adapter_profiles(katalog, params):
    broker = get_named(broker_profiles(katalog, params), 'resilienter-capability-broker')
    bus = get_named(knowledge_bus_profiles(katalog, params), 'resilienter-wissensbus')
    sandbox = get_named(sandbox_profiles(katalog, params), 'foederierte-sandbox-zellen')

    runtime = {
        **broker['base_config'],
        **bus['base_config'],
        **sandbox['base_config'],
    }

    return [
        {
            'name': 'direkter-io-zugriff',
            'label': 'Direkter IO-Zugriff',
            'selected_tools': ['execution'],
            'multiplier': 0.84,
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
                'trust_shield_strength': 0.24,
            },
            'gate_depth': 1,
            'audit_layers': 0,
            'isolation_depth': 0,
            'fallback_depth': 1,
            'bias': {
                'fit': 0.32,
                'safety': 0.18,
                'audit': 0.12,
                'flow': 0.88,
                'recovery': 0.26,
                'overhead': 0.06,
            },
        },
        {
            'name': 'read-only-schleuse',
            'label': 'Read-Only-Schleuse',
            'selected_tools': ['memory', 'execution'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.26,
            },
            'gate_depth': 2,
            'audit_layers': 1,
            'isolation_depth': 1,
            'fallback_depth': 1,
            'bias': {
                'fit': 0.54,
                'safety': 0.42,
                'audit': 0.44,
                'flow': 0.76,
                'recovery': 0.42,
                'overhead': 0.12,
            },
        },
        {
            'name': 'queue-adapter',
            'label': 'Queue-Adapter',
            'selected_tools': ['memory', 'execution', 'bridge'],
            'multiplier': 0.92,
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
            'gate_depth': 3,
            'audit_layers': 1,
            'isolation_depth': 1,
            'fallback_depth': 2,
            'bias': {
                'fit': 0.72,
                'safety': 0.54,
                'audit': 0.58,
                'flow': 0.80,
                'recovery': 0.60,
                'overhead': 0.18,
            },
        },
        {
            'name': 'audit-gateway',
            'label': 'Audit-Gateway',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.96,
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
            'gate_depth': 4,
            'audit_layers': 3,
            'isolation_depth': 2,
            'fallback_depth': 3,
            'bias': {
                'fit': 0.86,
                'safety': 0.86,
                'audit': 0.92,
                'flow': 0.72,
                'recovery': 0.78,
                'overhead': 0.24,
            },
        },
        {
            'name': 'foederierte-io-schleuse',
            'label': 'Foederierte IO-Schleuse',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **broker['base_config'],
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
            'gate_depth': 4,
            'audit_layers': 3,
            'isolation_depth': 3,
            'fallback_depth': 3,
            'bias': {
                'fit': 0.92,
                'safety': 0.90,
                'audit': 0.90,
                'flow': 0.84,
                'recovery': 0.86,
                'overhead': 0.26,
            },
        },
        {
            'name': 'resiliente-adapterkette',
            'label': 'Resiliente Adapterkette',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **runtime,
                **broker['base_config'],
                **bus['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.03),
                'resync_strength': 0.48,
            },
            'gate_depth': 5,
            'audit_layers': 4,
            'isolation_depth': 4,
            'fallback_depth': 4,
            'bias': {
                'fit': 0.92,
                'safety': 0.94,
                'audit': 0.94,
                'flow': 0.74,
                'recovery': 0.90,
                'overhead': 0.40,
            },
        },
    ]


def adapter_metrics(config, result, params, profile, kontext):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    required_domains = kontext['required_domains']
    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]

    adapter_coverage = required_domain_coverage(selected_tools, catalog, required_domains)
    adapter_redundancy = required_domain_redundancy(selected_tools, catalog, required_domains)
    adapter_specificity = route_specificity(selected_tools, required_domains)
    route_traceability = clamp01(mittelwert(trace_scores))
    route_exposure = clamp01(mittelwert(exposure_scores))
    gate_depth_score = normalize(profile['gate_depth'], 1.0, 5.0)
    audit_layers_score = normalize(profile['audit_layers'], 0.0, 4.0)
    isolation_depth_score = normalize(profile['isolation_depth'], 0.0, 4.0)
    fallback_depth_score = normalize(profile['fallback_depth'], 1.0, 4.0)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count

    adapter_fit = clamp01(
        mittelwert(
            [
                adapter_coverage,
                adapter_redundancy,
                adapter_specificity,
                workflow.get('completion_rate', 0.0),
                profile['bias']['fit'],
            ]
        )
    )
    gateway_safety = clamp01(
        mittelwert(
            [
                route_traceability,
                1.0 - route_exposure,
                workflow.get('trust_shield_mean', 0.0),
                workflow.get('misinformation_detection_rate', 0.0),
                isolation_depth_score,
                profile['bias']['safety'],
            ]
        )
    )
    audit_continuity = clamp01(
        mittelwert(
            [
                route_traceability,
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                audit_layers_score,
                profile['bias']['audit'],
            ]
        )
    )
    io_flow = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                result['cross_group_cooperation_rate'],
                groups['functional_group_share'],
                profile['bias']['flow'],
            ]
        )
    )
    recovery_bridge = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                fallback_depth_score,
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                profile['bias']['recovery'],
            ]
        )
    )
    recovery_readiness = clamp01(
        mittelwert(
            [
                recovery_bridge,
                route_traceability,
                1.0 - route_exposure,
                workflow.get('sync_strength_mean', 0.0),
            ]
        )
    )
    adapter_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 6.0),
                gate_depth_score,
                audit_layers_score,
                isolation_depth_score,
                profile['bias']['overhead'],
            ]
        )
    )
    adapter_integrity = clamp01(
        mittelwert(
            [
                adapter_fit,
                gateway_safety,
                audit_continuity,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                route_traceability,
            ]
        )
    )
    operational_resilience = clamp01(
        mittelwert(
            [
                io_flow,
                recovery_bridge,
                recovery_readiness,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - adapter_overhead,
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
        'adapter_fit': adapter_fit,
        'gateway_safety': gateway_safety,
        'audit_continuity': audit_continuity,
        'io_flow': io_flow,
        'recovery_bridge': recovery_bridge,
        'recovery_readiness': recovery_readiness,
        'adapter_integrity': adapter_integrity,
        'operational_resilience': operational_resilience,
        'adapter_overhead': adapter_overhead,
        'route_exposure': route_exposure,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    adapter_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(adapter_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
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
    result['adapter_metrics'] = adapter_metrics(config, result, params, profile, kontext)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['adapter_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'integration':
        return (
            metrics['adapter_integrity']
            + 0.18 * metrics['operational_resilience']
            + 0.14 * metrics['io_flow']
            + 0.08 * metrics['audit_continuity']
            - 0.10 * metrics['adapter_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['operational_resilience']
            + 0.18 * metrics['io_flow']
            + 0.14 * metrics['adapter_integrity']
            + 0.10 * metrics['audit_continuity']
            - 0.10 * metrics['adapter_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['adapter_integrity']
            + 0.14 * metrics['operational_resilience']
            + 0.10 * metrics['gateway_safety']
            - 0.10 * metrics['route_exposure']
            - 0.08 * metrics['adapter_overhead']
        )
    if kontext_name == 'recovery':
        return (
            base
            + 0.20 * metrics['operational_resilience']
            + 0.14 * metrics['recovery_bridge']
            + 0.10 * metrics['recovery_readiness']
            - 0.12 * failed_share
            - 0.08 * metrics['adapter_overhead']
        )
    return (
        metrics['adapter_integrity']
        + 0.18 * metrics['io_flow']
        + 0.12 * metrics['audit_continuity']
        - 0.10 * metrics['adapter_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'adapter_fit': {},
        'gateway_safety': {},
        'audit_continuity': {},
        'io_flow': {},
        'recovery_bridge': {},
        'recovery_readiness': {},
        'adapter_integrity': {},
        'operational_resilience': {},
        'adapter_overhead': {},
        'route_exposure': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['adapter_metrics'][metric_name] for run in runs])

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
    profiles = adapter_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI WERKZEUG-ADAPTER-STUDIE')
    print('=' * 84)
    print('Vergleicht Adapter- und IO-Schleusenarchitekturen fuer spaetere reale Schnittstellen,')
    print('damit operative Baugruppen Werkzeugkontakte mit Audit, Abschirmung und Recovery koppeln.\n')

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
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"Integritaet={summary['adapter_integrity']['stress']:.2f} | "
            f"Betriebs-Resilienz={summary['operational_resilience']['recovery']:.2f} | "
            f"Flow={summary['io_flow']['operations']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'direkter-io-zugriff')

    print('\nBester Werkzeug-Adapter:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Direkter IO-Zugriff {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Integritaet {best['adapter_integrity']['stress']:.2f}, "
        f"Audit {best['audit_continuity']['stress']:.2f}, "
        f"Betriebs-Resilienz {best['operational_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Adapter-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['adapter_integrity']['stress'] for item in summaries],
        width,
        label='Adapter-Integritaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['io_flow']['operations'] for item in summaries],
        width,
        label='IO-Flow',
        color='#59a14f',
    )
    axes[0, 1].set_title('Integritaet und Fluss')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['gateway_safety']['stress'] for item in summaries],
        width,
        label='Gateway-Sicherheit',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['route_exposure']['stress'] for item in summaries],
        width,
        label='Route-Exposition',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Sicherheit und Exposition')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['operational_resilience']['recovery'] for item in summaries],
        width,
        label='Betriebs-Resilienz',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['adapter_overhead']['operations'] for item in summaries],
        width,
        label='Adapter-Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Betriebs-Resilienz gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(
        x - width / 2,
        [item['context_scores']['integration'] for item in summaries],
        width,
        label='Integration',
        color='#4e79a7',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['context_scores']['operations'] for item in summaries],
        width,
        label='Operation',
        color='#59a14f',
    )
    axes[1, 1].set_title('Integrations- und Operations-Score')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].legend()
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
    output = save_and_maybe_show(plt, 'kki_werkzeugadapter.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
