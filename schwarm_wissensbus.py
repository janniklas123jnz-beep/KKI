"""
KKI Wissensbus-Studie
====================
Vergleicht Wissensbus-Architekturen fuer operative Baugruppen und misst, welche
Kopplung von Zellspeicher, Arbeitsgedaechtnis und Auditpfaden Wissen ueber
Instanziierung, Missionswechsel und Wiederanlauf hinweg konsistent haelt.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_beziehungsgedaechtnis import beziehungsmetriken
from schwarm_dna_schema import get_named, schema_metrics
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_instanziierungspipeline import pipeline_profiles
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
from schwarm_wissensspeicher import memory_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_KNOWLEDGE_BUS_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_KNOWLEDGE_BUS_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_KNOWLEDGE_BUS_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_KNOWLEDGE_BUS_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_KNOWLEDGE_BUS_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_KNOWLEDGE_BUS_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
        'stable_min_history': int(os.getenv('KKI_RELATIONSHIP_STABLE_MIN_HISTORY', '18')),
        'stable_trust_threshold': float(os.getenv('KKI_RELATIONSHIP_STABLE_TRUST', '0.76')),
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
        {'name': 'startup', 'label': 'Startup', 'scenario': 'consensus', 'startup_mode': True},
        {'name': 'sync', 'label': 'Sync', 'scenario': 'consensus', 'sync_mode': True},
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def knowledge_bus_profiles(katalog, params):
    pipeline = get_named(pipeline_profiles(katalog, params), 'foederierte-instanziierung')
    memory = get_named(memory_profiles(katalog, params), 'resilienter-wissensspeicher')
    storage = get_named(memory_profiles(katalog, params), 'foederierter-speicher')
    sandbox = get_named(sandbox_profiles(katalog, params), 'foederierte-sandbox-zellen')

    runtime = {
        **pipeline['base_config'],
        **memory['base_config'],
        **sandbox['base_config'],
    }

    return [
        {
            'name': 'zellnotizen',
            'label': 'Zellnotizen',
            'selected_tools': ['memory'],
            'multiplier': 0.86,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 16,
                'group_learning_rate': 0.11,
                'enable_fault_isolation': False,
                'meta_update_interval': 5,
                'resource_share_factor': 0.28,
            },
            'bus_depth': 1,
            'sync_layers': 1,
            'replication_depth': 1,
            'bias': {
                'retention': 0.46,
                'consistency': 0.40,
                'audit': 0.30,
                'sync': 0.36,
                'recovery': 0.34,
                'overhead': 0.08,
            },
        },
        {
            'name': 'handoff-bus',
            'label': 'Handoff-Bus',
            'selected_tools': ['memory', 'bridge'],
            'multiplier': 0.90,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 24,
                'group_learning_rate': 0.12,
                'meta_update_interval': 5,
                'handoff_priority_bonus': 0.20,
                'resource_share_factor': 0.28,
                'enable_fault_isolation': False,
            },
            'bus_depth': 2,
            'sync_layers': 2,
            'replication_depth': 2,
            'bias': {
                'retention': 0.62,
                'consistency': 0.60,
                'audit': 0.48,
                'sync': 0.62,
                'recovery': 0.48,
                'overhead': 0.14,
            },
        },
        {
            'name': 'arbeitsbus',
            'label': 'Arbeitsbus',
            'selected_tools': ['memory', 'analysis', 'bridge'],
            'multiplier': 0.94,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 30,
                'analyzer_learning_multiplier': 1.22,
                'group_learning_rate': 0.13,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.22,
                'resource_share_factor': 0.29,
                'enable_fault_isolation': True,
            },
            'bus_depth': 3,
            'sync_layers': 2,
            'replication_depth': 2,
            'bias': {
                'retention': 0.76,
                'consistency': 0.74,
                'audit': 0.68,
                'sync': 0.76,
                'recovery': 0.64,
                'overhead': 0.20,
            },
        },
        {
            'name': 'audit-bus',
            'label': 'Audit-Bus',
            'selected_tools': ['memory', 'analysis', 'bridge', 'shield'],
            'multiplier': 0.97,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 36,
                'analyzer_learning_multiplier': 1.24,
                'group_learning_rate': 0.13,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.22,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
                'enable_fault_isolation': True,
            },
            'bus_depth': 4,
            'sync_layers': 3,
            'replication_depth': 3,
            'bias': {
                'retention': 0.84,
                'consistency': 0.82,
                'audit': 0.90,
                'sync': 0.82,
                'recovery': 0.78,
                'overhead': 0.24,
            },
        },
        {
            'name': 'foederierter-wissensbus',
            'label': 'Foederierter Wissensbus',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **storage['base_config'],
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.38,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
            },
            'bus_depth': 4,
            'sync_layers': 4,
            'replication_depth': 4,
            'bias': {
                'retention': 0.90,
                'consistency': 0.90,
                'audit': 0.88,
                'sync': 0.90,
                'recovery': 0.88,
                'overhead': 0.26,
            },
        },
        {
            'name': 'resilienter-wissensbus',
            'label': 'Resilienter Wissensbus',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **runtime,
                **memory['base_config'],
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.30,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.40,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.03),
                'resync_strength': 0.48,
            },
            'bus_depth': 5,
            'sync_layers': 4,
            'replication_depth': 4,
            'bias': {
                'retention': 0.90,
                'consistency': 0.90,
                'audit': 0.92,
                'sync': 0.86,
                'recovery': 0.92,
                'overhead': 0.40,
            },
        },
    ]


def knowledge_bus_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    relationships = beziehungsmetriken(result['agents'], params)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    traceability = clamp01(mittelwert([catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]))
    exposure = clamp01(mittelwert([catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]))
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    bus_depth_score = normalize(profile['bus_depth'], 1.0, 5.0)
    sync_score = normalize(profile['sync_layers'], 1.0, 4.0)
    replication_score = normalize(profile['replication_depth'], 1.0, 4.0)
    memory_window_score = normalize(config.get('analyzer_memory_window', 16), 16.0, max(40.0, float(params['memory_window'])))

    retention_quality = clamp01(
        mittelwert(
            [
                memory_window_score,
                relationships['relationship_depth_mean'] / max(1.0, float(params['memory_window'])),
                relationships['stable_bond_rate'],
                profile['bias']['retention'],
            ]
        )
    )
    bus_consistency = clamp01(
        mittelwert(
            [
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                groups['functional_group_share'],
                replication_score,
                profile['bias']['consistency'],
            ]
        )
    )
    audit_signal = clamp01(
        mittelwert(
            [
                traceability,
                1.0 - exposure,
                workflow.get('misinformation_detection_rate', 0.0),
                sync_score,
                profile['bias']['audit'],
            ]
        )
    )
    sync_strength = clamp01(
        mittelwert(
            [
                workflow.get('resource_share_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                sync_score,
                profile['bias']['sync'],
            ]
        )
    )
    recovery_memory = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                profile['bias']['recovery'],
            ]
        )
    )
    bus_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_share_factor', 0.28), 0.28, 0.30),
                bus_depth_score,
                sync_score,
                replication_score,
                profile['bias']['overhead'],
            ]
        )
    )
    knowledge_integrity = clamp01(
        mittelwert(
            [
                retention_quality,
                bus_consistency,
                audit_signal,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                traceability,
            ]
        )
    )
    bus_resilience = clamp01(
        mittelwert(
            [
                sync_strength,
                recovery_memory,
                bus_consistency,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - bus_overhead,
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'retention_quality': retention_quality,
        'bus_consistency': bus_consistency,
        'audit_signal': audit_signal,
        'sync_strength': sync_strength,
        'recovery_memory': recovery_memory,
        'knowledge_integrity': knowledge_integrity,
        'bus_resilience': bus_resilience,
        'bus_overhead': bus_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    bus_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(bus_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('sync_mode'):
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
    result['knowledge_bus_metrics'] = knowledge_bus_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['knowledge_bus_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['retention_quality']
            + 0.18 * metrics['bus_consistency']
            + 0.12 * metrics['sync_strength']
            - 0.10 * metrics['bus_overhead']
        )
    if kontext_name == 'sync':
        return (
            metrics['bus_consistency']
            + 0.18 * metrics['sync_strength']
            + 0.12 * metrics['audit_signal']
            - 0.12 * metrics['bus_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['knowledge_integrity']
            + 0.12 * metrics['bus_resilience']
            + 0.10 * metrics['audit_signal']
            - 0.10 * metrics['bus_overhead']
        )
    return (
        base
        + 0.20 * metrics['bus_resilience']
        + 0.12 * metrics['knowledge_integrity']
        + 0.08 * metrics['audit_signal']
        - 0.12 * failed_share
        - 0.08 * metrics['bus_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'retention_quality': {},
        'bus_consistency': {},
        'audit_signal': {},
        'sync_strength': {},
        'recovery_memory': {},
        'knowledge_integrity': {},
        'bus_resilience': {},
        'bus_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['knowledge_bus_metrics'][metric_name] for run in runs])

    return {
        'name': profile['name'],
        'label': profile['label'],
        'combined_score': mittelwert([
            sum(context_score(kontext['name'], run[kontext['name']], agent_count) for kontext in context_list)
            for run in runs
        ]),
        'context_scores': context_scores,
        **metrics,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    profiles = knowledge_bus_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI WISSENSBUS-STUDIE')
    print('=' * 84)
    print('Vergleicht Bus-Architekturen fuer Zellspeicher, Auditpfade und Wissenssynchronisierung,')
    print('damit operative Baugruppen Wissen ueber Starts, Missionen und Recovery hinweg halten.\n')

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
            f"Integritaet={summary['knowledge_integrity']['stress']:.2f} | "
            f"Bus-Resilienz={summary['bus_resilience']['recovery']:.2f} | "
            f"Sync={summary['sync_strength']['sync']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'zellnotizen')

    print('\nBester Wissensbus:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Zellnotizen {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Integritaet {best['knowledge_integrity']['stress']:.2f}, "
        f"Sync {best['sync_strength']['sync']:.2f}, "
        f"Bus-Resilienz {best['bus_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Wissensbus-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['knowledge_integrity']['stress'] for item in summaries],
        width,
        label='Integritaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['bus_consistency']['sync'] for item in summaries],
        width,
        label='Konsistenz',
        color='#59a14f',
    )
    axes[0, 1].set_title('Wissens-Integritaet und Konsistenz')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['sync_strength']['sync'] for item in summaries],
        width,
        label='Sync',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['audit_signal']['stress'] for item in summaries],
        width,
        label='Audit',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Synchronisierung und Audit')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['bus_resilience']['recovery'] for item in summaries],
        width,
        label='Bus-Resilienz',
        color='#e15759',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['bus_overhead']['sync'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Bus-Resilienz gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['stress'] for item in summaries], color=colors)
    axes[1, 1].set_title('Stress-Score')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].bar(
        x - width / 2,
        [item['context_scores']['sync'] for item in summaries],
        width,
        label='Sync',
        color='#59a14f',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['recovery_memory']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#4e79a7',
    )
    axes[1, 2].set_title('Sync- und Recovery-Score')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_wissensbus.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
