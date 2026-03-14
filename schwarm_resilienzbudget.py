"""
KKI Resilienzbudget-Studie
==========================
Vergleicht adaptive Schutzbudgets fuer operative Baugruppen und misst, wie viel
zusaetzliche Resilienz zugeschaltet werden sollte, damit Schutz staerker wird,
ohne den operativen Siegervorteil in Overhead und Steuerdruck zu verlieren.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_bauphasen_blueprint import blueprint_profiles
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
from schwarm_supervisor_eingriffe import intervention_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_RESILIENCE_BUDGET_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_RESILIENCE_BUDGET_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_RESILIENCE_BUDGET_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_RESILIENCE_BUDGET_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_RESILIENCE_BUDGET_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_RESILIENCE_BUDGET_FAILURE_FRACTION', '0.18')),
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
    }


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def normalize(value, minimum, maximum):
    if maximum <= minimum:
        return 0.0
    return clamp01((float(value) - minimum) / (maximum - minimum))


def kontexte():
    return [
        {'name': 'operations', 'label': 'Operation', 'scenario': 'consensus'},
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
        {
            'name': 'surge',
            'label': 'Schutzspitze',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
            'budget_surge': True,
        },
    ]


def budget_profiles(katalog, params):
    operative = get_named(blueprint_profiles(katalog, params), 'operativer-blueprint')['config']
    resilient = get_named(blueprint_profiles(katalog, params), 'resilienter-blueprint')['config']
    interventions = get_named(intervention_profiles(katalog, params), 'leitplanken-supervisor')

    runtime = {
        **operative,
        **interventions['base_config'],
    }

    return [
        {
            'name': 'starres-minimumbudget',
            'label': 'Starres Minimumbudget',
            'selected_tools': ['memory', 'analysis'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                'trust_shield_strength': 0.30,
                'resource_budget': 0.74,
                'resource_share_factor': 0.27,
                'failure_fraction': min(0.22, params['failure_fraction'] + 0.02),
                'resync_strength': 0.40,
            },
            'budget_level': 1,
            'adaptivity': 0,
            'surge_headroom': 1,
            'bias': {
                'protection': 0.28,
                'adaptivity': 0.18,
                'operability': 0.88,
                'recovery': 0.34,
                'efficiency': 0.84,
                'overhead': 0.08,
            },
        },
        {
            'name': 'operatives-budget',
            'label': 'Operatives Budget',
            'selected_tools': ['memory', 'analysis', 'bridge'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                'trust_shield_strength': 0.34,
                'resource_budget': 0.78,
                'resource_share_factor': 0.28,
                'failure_fraction': params['failure_fraction'],
                'resync_strength': 0.44,
            },
            'budget_level': 2,
            'adaptivity': 1,
            'surge_headroom': 2,
            'bias': {
                'protection': 0.56,
                'adaptivity': 0.46,
                'operability': 0.86,
                'recovery': 0.58,
                'efficiency': 0.82,
                'overhead': 0.16,
            },
        },
        {
            'name': 'adaptives-budget',
            'label': 'Adaptives Budget',
            'selected_tools': ['memory', 'analysis', 'bridge', 'shield'],
            'multiplier': 0.95,
            'base_config': {
                **runtime,
                'trust_shield_strength': 0.36,
                'resource_budget': 0.79,
                'resource_share_factor': 0.29,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.02),
                'resync_strength': 0.48,
                'enable_fault_isolation': True,
            },
            'budget_level': 3,
            'adaptivity': 3,
            'surge_headroom': 3,
            'bias': {
                'protection': 0.82,
                'adaptivity': 0.84,
                'operability': 0.84,
                'recovery': 0.82,
                'efficiency': 0.78,
                'overhead': 0.22,
            },
        },
        {
            'name': 'spitzenbudget',
            'label': 'Spitzenbudget',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                **resilient,
                'trust_shield_strength': 0.38,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
                'resync_strength': 0.52,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
            },
            'budget_level': 4,
            'adaptivity': 2,
            'surge_headroom': 4,
            'bias': {
                'protection': 0.92,
                'adaptivity': 0.66,
                'operability': 0.70,
                'recovery': 0.90,
                'efficiency': 0.68,
                'overhead': 0.30,
            },
        },
        {
            'name': 'dynamisches-resilienzbudget',
            'label': 'Dynamisches Resilienzbudget',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                'trust_shield_strength': 0.37,
                'resource_budget': 0.79,
                'resource_share_factor': 0.29,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.03),
                'resync_strength': 0.50,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.92,
                'bottleneck_triage_intensity': 0.94,
            },
            'budget_level': 3,
            'adaptivity': 4,
            'surge_headroom': 4,
            'bias': {
                'protection': 0.90,
                'adaptivity': 0.96,
                'operability': 0.86,
                'recovery': 0.90,
                'efficiency': 0.82,
                'overhead': 0.24,
            },
        },
        {
            'name': 'maximales-schutzbudget',
            'label': 'Maximales Schutzbudget',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **resilient,
                **runtime,
                'trust_shield_strength': 0.40,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.05),
                'resync_strength': 0.54,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.92,
                'bottleneck_triage_intensity': 0.96,
            },
            'budget_level': 5,
            'adaptivity': 1,
            'surge_headroom': 5,
            'bias': {
                'protection': 0.96,
                'adaptivity': 0.42,
                'operability': 0.60,
                'recovery': 0.96,
                'efficiency': 0.56,
                'overhead': 0.32,
            },
        },
    ]


def budget_metrics(config, result, params, profile, kontext):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    traceability = clamp01(mittelwert([catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]))
    exposure = clamp01(mittelwert([catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]))
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    protection_level = normalize(profile['budget_level'], 1.0, 5.0)
    adaptivity_level = normalize(profile['adaptivity'], 0.0, 4.0)
    surge_headroom = normalize(profile['surge_headroom'], 1.0, 5.0)
    bottleneck_rate = workflow.get('bottleneck_rate', 0.0)
    bottleneck_relief_rate = workflow.get('bottleneck_relief_rate', 0.0)
    surge_factor = 1.0 if not kontext.get('budget_surge') else 1.12

    protection_strength = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                protection_level,
                profile['bias']['protection'],
            ]
        )
        * surge_factor
    )
    adaptive_fit = clamp01(
        mittelwert(
            [
                adaptivity_level,
                surge_headroom,
                1.0 if config.get('enable_bottleneck_management', False) else 0.0,
                bottleneck_relief_rate,
                profile['bias']['adaptivity'],
            ]
        )
    )
    operational_retention = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                groups['functional_group_share'],
                workflow.get('handoff_rate', 0.0),
                profile['bias']['operability'],
            ]
        )
    )
    recovery_margin = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - bottleneck_rate,
                profile['bias']['recovery'],
            ]
        )
        * surge_factor
    )
    efficiency_value = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                traceability,
                1.0 - exposure,
                profile['bias']['efficiency'],
            ]
        )
    )
    budget_integrity = clamp01(
        mittelwert(
            [
                protection_strength,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                efficiency_value,
            ]
        )
    )
    protection_return = clamp01(
        mittelwert(
            [
                adaptive_fit,
                operational_retention,
                recovery_margin,
                efficiency_value,
                1.0 - budget_overhead if 'budget_overhead' in locals() else 0.0,
            ]
        )
    )
    budget_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_budget', 0.74), 0.74, 0.80),
                normalize(config.get('resource_share_factor', 0.27), 0.27, 0.30),
                protection_level,
                1.0 - adaptivity_level,
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
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
        'protection_strength': protection_strength,
        'adaptive_fit': adaptive_fit,
        'operational_retention': operational_retention,
        'recovery_margin': recovery_margin,
        'efficiency_value': efficiency_value,
        'budget_integrity': budget_integrity,
        'protection_return': protection_return,
        'budget_overhead': budget_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    budget_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(budget_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('enable_prompt_injection'):
        config['enable_prompt_injection'] = True
        config['injection_attack_round'] = params['attack_round']
        config['injection_strength'] = params['stress_strength'] * (1.15 if kontext.get('budget_surge') else 1.0)
        config['injection_source_count'] = params['stress_sources'] + (2 if kontext.get('budget_surge') else 0)
    else:
        config['enable_prompt_injection'] = False

    if kontext.get('enable_failures'):
        config['enable_cluster_failures'] = True
        config['enable_restart_recovery'] = True
        config['failure_round'] = params['failure_round']
        config['failure_duration'] = params['failure_duration']
        config['failure_fraction'] = min(0.28, params['failure_fraction'] + (0.03 if kontext.get('budget_surge') else 0.0))
        config.setdefault('resync_strength', params['resync_strength'])

    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    result['budget_metrics'] = budget_metrics(config, result, params, profile, kontext)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['budget_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['operational_retention']
            + 0.12 * metrics['efficiency_value']
            + 0.10 * metrics['adaptive_fit']
            - 0.12 * metrics['budget_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['budget_integrity']
            + 0.12 * metrics['adaptive_fit']
            + 0.08 * metrics['protection_return']
            - 0.10 * metrics['budget_overhead']
        )
    if kontext_name == 'recovery':
        return (
            base
            + 0.18 * metrics['protection_return']
            + 0.12 * metrics['adaptive_fit']
            + 0.08 * metrics['operational_retention']
            - 0.12 * failed_share
            - 0.08 * metrics['budget_overhead']
        )
    return (
        base
        + 0.22 * metrics['budget_integrity']
        + 0.16 * metrics['adaptive_fit']
        + 0.12 * metrics['protection_return']
        - 0.12 * metrics['budget_overhead']
        - 0.10 * failed_share
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'protection_strength': {},
        'adaptive_fit': {},
        'operational_retention': {},
        'recovery_margin': {},
        'efficiency_value': {},
        'budget_integrity': {},
        'protection_return': {},
        'budget_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['budget_metrics'][metric_name] for run in runs])

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
    profiles = budget_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI RESILIENZBUDGET-STUDIE')
    print('=' * 84)
    print('Vergleicht Schutzbudgets fuer operative Baugruppen, damit Resilienz')
    print('dynamisch staerker wird, ohne Operabilitaet und Effizienz zu verlieren.\n')

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
            f"{summary['label']:<29} Score={summary['combined_score']:+.3f} | "
            f"Integritaet={summary['budget_integrity']['stress']:.2f} | "
            f"Adaptiv={summary['adaptive_fit']['surge']:.2f} | "
            f"Rendite={summary['protection_return']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'operatives-budget')

    print('\nBestes Resilienzbudget:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum operativen Budget {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Integritaet {best['budget_integrity']['stress']:.2f}, "
        f"Adaptiv {best['adaptive_fit']['surge']:.2f}, "
        f"Rendite {best['protection_return']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Budget-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['budget_integrity']['stress'] for item in summaries],
        width,
        label='Budget-Integritaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['adaptive_fit']['surge'] for item in summaries],
        width,
        label='Adaptive Passung',
        color='#59a14f',
    )
    axes[0, 1].set_title('Integritaet und Adaptivitaet')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['operational_retention']['operations'] for item in summaries],
        width,
        label='Betrieb',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['efficiency_value']['operations'] for item in summaries],
        width,
        label='Effizienz',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Betrieb und Effizienz')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['protection_return']['recovery'] for item in summaries],
        width,
        label='Schutzrendite',
        color='#e15759',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['budget_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Schutzrendite gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['operations'] for item in summaries], color=colors)
    axes[1, 1].set_title('Operations-Score')
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
        [item['context_scores']['surge'] for item in summaries],
        width,
        label='Schutzspitze',
        color='#59a14f',
    )
    axes[1, 2].set_title('Stress- und Spitzenscore')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_resilienzbudget.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
