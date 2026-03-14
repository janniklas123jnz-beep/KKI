"""
KKI Wissensspeicher-Studie
==========================
Vergleicht operative Wissens- und Arbeitsgedaechtnisstrukturen fuer Baugruppen
und misst, welche Speicherarchitektur Lernen, Auditierbarkeit und Recovery am
besten verbindet, ohne den operativen Fluss zu stark zu belasten.
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
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import broker_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_MEMORY_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_MEMORY_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_MEMORY_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_MEMORY_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_MEMORY_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_MEMORY_FAILURE_FRACTION', '0.18')),
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
        {'name': 'operations', 'label': 'Operation', 'scenario': 'consensus'},
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def memory_profiles(katalog, params):
    broker = get_named(broker_profiles(katalog, params), 'resilienter-capability-broker')
    runtime = dict(broker['base_config'])

    return [
        {
            'name': 'fluechtiger-puffer',
            'label': 'Fluechtiger Puffer',
            'selected_tools': ['memory'],
            'multiplier': 0.82,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 8,
                'group_learning_rate': 0.10,
                'resource_share_factor': 0.24,
                'meta_update_interval': 6,
            },
            'audit_depth': 1,
            'replication_factor': 1,
            'bias': {
                'retention': 0.30,
                'consistency': 0.28,
                'audit': 0.20,
                'learning': 0.38,
                'recovery': 0.26,
                'overhead': 0.08,
            },
        },
        {
            'name': 'team-notizen',
            'label': 'Team-Notizen',
            'selected_tools': ['memory', 'bridge'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 16,
                'group_learning_rate': 0.11,
                'resource_share_factor': 0.26,
                'meta_update_interval': 5,
                'handoff_priority_bonus': 0.18,
            },
            'audit_depth': 2,
            'replication_factor': 2,
            'bias': {
                'retention': 0.52,
                'consistency': 0.50,
                'audit': 0.44,
                'learning': 0.58,
                'recovery': 0.42,
                'overhead': 0.14,
            },
        },
        {
            'name': 'arbeitsgedaechtnis',
            'label': 'Arbeitsgedaechtnis',
            'selected_tools': ['memory', 'analysis', 'bridge'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 24,
                'analyzer_learning_multiplier': 1.18,
                'group_learning_rate': 0.12,
                'resource_share_factor': 0.27,
                'meta_update_interval': 5,
                'handoff_priority_bonus': 0.20,
            },
            'audit_depth': 2,
            'replication_factor': 2,
            'bias': {
                'retention': 0.70,
                'consistency': 0.68,
                'audit': 0.60,
                'learning': 0.76,
                'recovery': 0.58,
                'overhead': 0.20,
            },
        },
        {
            'name': 'wissensspeicher',
            'label': 'Wissensspeicher',
            'selected_tools': ['memory', 'analysis', 'bridge', 'shield'],
            'multiplier': 0.95,
            'base_config': {
                **runtime,
                'analyzer_memory_window': 32,
                'analyzer_learning_multiplier': 1.22,
                'group_learning_rate': 0.13,
                'resource_share_factor': 0.28,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.22,
                'trust_shield_strength': 0.36,
            },
            'audit_depth': 3,
            'replication_factor': 3,
            'bias': {
                'retention': 0.82,
                'consistency': 0.80,
                'audit': 0.84,
                'learning': 0.84,
                'recovery': 0.76,
                'overhead': 0.24,
            },
        },
        {
            'name': 'foederierter-speicher',
            'label': 'Foederierter Speicher',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.97,
            'base_config': {
                **runtime,
                'analyzer_memory_window': params['memory_window'],
                'analyzer_learning_multiplier': 1.24,
                'group_learning_rate': 0.13,
                'resource_share_factor': 0.29,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.22,
                'trust_shield_strength': 0.36,
                'enable_fault_isolation': True,
            },
            'audit_depth': 3,
            'replication_factor': 4,
            'bias': {
                'retention': 0.86,
                'consistency': 0.84,
                'audit': 0.82,
                'learning': 0.88,
                'recovery': 0.86,
                'overhead': 0.28,
            },
        },
        {
            'name': 'resilienter-wissensspeicher',
            'label': 'Resilienter Wissensspeicher',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                'analyzer_memory_window': max(params['memory_window'], 40),
                'analyzer_learning_multiplier': 1.26,
                'group_learning_rate': 0.14,
                'resource_share_factor': 0.30,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.38,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
            },
            'audit_depth': 4,
            'replication_factor': 4,
            'bias': {
                'retention': 0.92,
                'consistency': 0.90,
                'audit': 0.94,
                'learning': 0.90,
                'recovery': 0.92,
                'overhead': 0.30,
            },
        },
    ]


def memory_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    relationships = beziehungsmetriken(result['agents'], params)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    memory_window_score = normalize(config.get('analyzer_memory_window', 8), 8.0, max(40.0, float(params['memory_window'])))
    audit_depth_score = normalize(profile['audit_depth'], 1.0, 4.0)
    replication_score = normalize(profile['replication_factor'], 1.0, 4.0)
    traceability = clamp01(mittelwert(trace_scores))
    exposure = clamp01(mittelwert(exposure_scores))

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
    memory_consistency = clamp01(
        mittelwert(
            [
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                relationships['cooperative_core_share'],
                groups['functional_group_share'],
                replication_score,
                profile['bias']['consistency'],
            ]
        )
    )
    auditability = clamp01(
        mittelwert(
            [
                traceability,
                1.0 - exposure,
                workflow.get('misinformation_detection_rate', 0.0),
                audit_depth_score,
                profile['bias']['audit'],
            ]
        )
    )
    learning_continuity = clamp01(
        mittelwert(
            [
                min(1.0, float(config.get('group_learning_rate', 0.1)) / 0.14),
                min(1.0, float(config.get('analyzer_learning_multiplier', 1.0)) / 1.26),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                profile['bias']['learning'],
            ]
        )
    )
    recovery_memory = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                relationships['cooperative_core_share'],
                replication_score,
                profile['bias']['recovery'],
            ]
        )
    )
    knowledge_integrity = clamp01(
        mittelwert(
            [
                auditability,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                memory_consistency,
            ]
        )
    )
    learning_resilience = clamp01(
        mittelwert(
            [
                learning_continuity,
                recovery_memory,
                workflow.get('resource_efficiency', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                retention_quality,
            ]
        )
    )
    memory_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 6.0),
                normalize(config.get('resource_share_factor', 0.24), 0.24, 0.30),
                audit_depth_score,
                replication_score,
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
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
        'memory_consistency': memory_consistency,
        'auditability': auditability,
        'learning_continuity': learning_continuity,
        'recovery_memory': recovery_memory,
        'knowledge_integrity': knowledge_integrity,
        'learning_resilience': learning_resilience,
        'memory_overhead': memory_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    memory_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(memory_config)
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
    result['memory_metrics'] = memory_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['memory_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['retention_quality']
            + 0.14 * metrics['memory_consistency']
            + 0.08 * metrics['learning_continuity']
            - 0.10 * metrics['memory_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['memory_consistency']
            + 0.14 * metrics['learning_continuity']
            + 0.10 * metrics['auditability']
            - 0.10 * metrics['memory_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['knowledge_integrity']
            + 0.12 * metrics['retention_quality']
            + 0.08 * metrics['learning_resilience']
            - 0.08 * metrics['memory_overhead']
        )
    return (
        base
        + 0.18 * metrics['learning_resilience']
        + 0.12 * metrics['memory_consistency']
        + 0.08 * metrics['auditability']
        - 0.12 * failed_share
        - 0.08 * metrics['memory_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'retention_quality': {},
        'memory_consistency': {},
        'auditability': {},
        'learning_continuity': {},
        'recovery_memory': {},
        'knowledge_integrity': {},
        'learning_resilience': {},
        'memory_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['memory_metrics'][metric_name] for run in runs])

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
    profiles = memory_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI WISSENSSPEICHER-STUDIE')
    print('=' * 84)
    print('Vergleicht Wissens- und Arbeitsgedaechtnisstrukturen fuer operative')
    print('Baugruppen, damit Lernen, Audit und Recovery gemeinsam tragfaehig bleiben.\n')

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
            f"Retention={summary['retention_quality']['startup']:.2f} | "
            f"Integritaet={summary['knowledge_integrity']['stress']:.2f} | "
            f"Lern-Resilienz={summary['learning_resilience']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'fluechtiger-puffer')

    print('\nBester Wissensspeicher:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum fluechtigen Puffer {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Retention {best['retention_quality']['startup']:.2f}, "
        f"Integritaet {best['knowledge_integrity']['stress']:.2f}, "
        f"Lern-Resilienz {best['learning_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Wissensspeicher-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['retention_quality']['startup'] for item in summaries],
        width,
        label='Retention',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['memory_consistency']['operations'] for item in summaries],
        width,
        label='Konsistenz',
        color='#59a14f',
    )
    axes[0, 1].set_title('Speicherqualitaet')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['knowledge_integrity']['stress'] for item in summaries],
        width,
        label='Wissens-Integritaet',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['learning_resilience']['recovery'] for item in summaries],
        width,
        label='Lern-Resilienz',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Integritaet und Lern-Resilienz')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['learning_continuity']['operations'] for item in summaries],
        width,
        label='Lernkontinuitaet',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['memory_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Lernen gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['startup'] for item in summaries], color=colors)
    axes[1, 1].set_title('Startup-Kontextscore')
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
        [item['context_scores']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#59a14f',
    )
    axes[1, 2].set_title('Stress- und Recovery-Score')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_wissensspeicher.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
