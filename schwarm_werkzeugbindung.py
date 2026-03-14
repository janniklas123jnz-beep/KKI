"""
KKI Werkzeugbindungs-Studie
===========================
Vergleicht, wie Gruppen spaeter Werkzeuge, Speicher und Umgebungen koppeln
koennen und misst, welche Bindungsform Nutzen, Nachvollziehbarkeit und
Sicherheit verbindet, ohne zu viel Kopplungsdruck zu erzeugen.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named, schema_metrics
from schwarm_governance_layer import governance_profiles
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_handoff_vertraege import contract_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_protokollstack import protocol_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_TOOL_BINDING_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_TOOL_BINDING_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_TOOL_BINDING_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_TOOL_BINDING_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_TOOL_BINDING_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_TOOL_BINDING_FAILURE_FRACTION', '0.18')),
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
        {'name': 'startup', 'label': 'Startup', 'scenario': 'consensus', 'startup_mode': True},
        {'name': 'integration', 'label': 'Integration', 'scenario': 'consensus'},
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


def tool_catalog():
    return {
        'memory': {
            'label': 'Speicher',
            'domains': ('memory', 'trace'),
            'config': {
                'group_learning_rate': 0.020,
                'resource_budget': 0.02,
                'resource_share_factor': 0.01,
            },
            'scores': {'coverage': 0.74, 'trace': 0.92, 'exposure': 0.18},
        },
        'analysis': {
            'label': 'Analyse',
            'domains': ('analysis', 'planning'),
            'config': {
                'meta_priority_strength': 0.02,
                'analyzer_learning_multiplier': 0.08,
                'resource_budget': 0.01,
            },
            'scores': {'coverage': 0.70, 'trace': 0.64, 'exposure': 0.20},
        },
        'execution': {
            'label': 'Ausfuehrung',
            'domains': ('execution', 'environment'),
            'config': {
                'resource_budget': 0.03,
                'resource_share_factor': 0.02,
                'mission_switch_interval': -1,
            },
            'scores': {'coverage': 0.92, 'trace': 0.42, 'exposure': 0.34},
        },
        'bridge': {
            'label': 'Bruecke',
            'domains': ('coordination', 'handoff'),
            'config': {
                'handoff_priority_bonus': 0.02,
                'resource_share_factor': 0.02,
                'connector_cross_group_learning_bonus': 0.04,
            },
            'scores': {'coverage': 0.68, 'trace': 0.62, 'exposure': 0.16},
        },
        'shield': {
            'label': 'Sicherheitsmodul',
            'domains': ('security', 'approval'),
            'config': {
                'trust_shield_strength': 0.05,
                'meta_priority_strength': 0.03,
                'quarantine_compromise_threshold': -0.02,
                'quarantine_exposure_threshold': -0.02,
            },
            'scores': {'coverage': 0.58, 'trace': 0.78, 'exposure': 0.06},
        },
    }


def add_delta(config, key, delta):
    current = config.get(key, 0)
    if isinstance(delta, int) and not isinstance(delta, bool):
        config[key] = int(round(int(current) + delta))
    else:
        config[key] = float(current) + float(delta)


def apply_tools(base_config, selected_tools, catalog, multiplier=1.0):
    config = dict(base_config)
    for tool_name in selected_tools:
        for key, delta in catalog[tool_name]['config'].items():
            add_delta(config, key, delta * multiplier)
    return config


def tool_binding_profiles(katalog, params):
    governance = get_named(governance_profiles(katalog, params), 'resilienter-governance-layer')['config']
    contract = get_named(contract_profiles(katalog, params), 'resilienter-handoff-vertrag')['config']
    protocol = get_named(protocol_profiles(katalog, params), 'resilienter-protokollstack')['config']
    catalog = tool_catalog()

    return [
        {
            'name': 'freie-werkzeuge',
            'label': 'Freie Werkzeuge',
            'selected_tools': ['execution', 'memory'],
            'base_config': {
                **contract,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'meta_update_interval': 8,
                'cluster_budget_skew': 0.32,
                'trust_shield_strength': 0.18,
            },
            'multiplier': 1.0,
            'bias': {
                'coverage': 0.46,
                'approval': 0.18,
                'trace': 0.24,
                'isolation': 0.16,
                'memory': 0.48,
                'flow': 0.78,
                'overhead': 0.08,
            },
        },
        {
            'name': 'gateway-bindung',
            'label': 'Gateway-Bindung',
            'selected_tools': ['execution', 'bridge', 'shield'],
            'base_config': {
                **contract,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'meta_update_interval': 6,
                'meta_priority_strength': 0.34,
                'cluster_budget_skew': 0.25,
                'trust_shield_strength': 0.28,
            },
            'multiplier': 0.9,
            'bias': {
                'coverage': 0.68,
                'approval': 0.46,
                'trace': 0.54,
                'isolation': 0.46,
                'memory': 0.42,
                'flow': 0.70,
                'overhead': 0.20,
            },
        },
        {
            'name': 'speicher-bruecke',
            'label': 'Speicher-Bruecke',
            'selected_tools': ['memory', 'analysis', 'bridge', 'shield'],
            'base_config': {
                **governance,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'meta_update_interval': 5,
                'cluster_budget_skew': 0.22,
                'trust_shield_strength': 0.32,
            },
            'multiplier': 0.85,
            'bias': {
                'coverage': 0.72,
                'approval': 0.70,
                'trace': 0.86,
                'isolation': 0.54,
                'memory': 0.88,
                'flow': 0.64,
                'overhead': 0.28,
            },
        },
        {
            'name': 'freigabe-kette',
            'label': 'Freigabe-Kette',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'base_config': {
                **protocol,
                **governance,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'cluster_budget_skew': 0.20,
                'trust_shield_strength': 0.36,
                'resource_share_factor': 0.28,
            },
            'multiplier': 0.82,
            'bias': {
                'coverage': 0.88,
                'approval': 0.84,
                'trace': 0.84,
                'isolation': 0.72,
                'memory': 0.84,
                'flow': 0.68,
                'overhead': 0.34,
            },
        },
        {
            'name': 'sandbox-stack',
            'label': 'Sandbox-Stack',
            'selected_tools': ['analysis', 'execution', 'bridge', 'shield'],
            'base_config': {
                **protocol,
                **governance,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'cluster_budget_skew': 0.18,
                'quarantine_compromise_threshold': 0.22,
                'quarantine_exposure_threshold': 0.28,
                'trust_shield_strength': 0.39,
                'resource_share_factor': 0.29,
            },
            'multiplier': 0.78,
            'bias': {
                'coverage': 0.86,
                'approval': 0.82,
                'trace': 0.76,
                'isolation': 0.90,
                'memory': 0.62,
                'flow': 0.66,
                'overhead': 0.36,
            },
        },
        {
            'name': 'resiliente-werkzeugfoederation',
            'label': 'Resiliente Werkzeugfoederation',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'base_config': {
                **protocol,
                **governance,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'meta_priority_strength': 0.42,
                'cluster_budget_skew': 0.16,
                'quarantine_compromise_threshold': 0.22,
                'quarantine_exposure_threshold': 0.28,
                'trust_shield_strength': 0.40,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'resync_strength': min(0.54, governance.get('resync_strength', params['resync_strength']) + 0.04),
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
            },
            'multiplier': 0.72,
            'bias': {
                'coverage': 0.92,
                'approval': 0.90,
                'trace': 0.90,
                'isolation': 0.92,
                'memory': 0.90,
                'flow': 0.74,
                'overhead': 0.30,
            },
        },
    ]


def binding_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']

    coverage_scores = [catalog[name]['scores']['coverage'] for name in selected_tools] or [0.0]
    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]
    domain_count = len({domain for name in selected_tools for domain in catalog[name]['domains']})
    tool_count = len(selected_tools)
    arbitration_activity = normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0)

    tool_coverage = clamp01(
        mittelwert(
            [
                mittelwert(coverage_scores),
                normalize(domain_count, 1.0, 8.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                profile['bias']['coverage'],
            ]
        )
    )
    approval_integrity = clamp01(
        mittelwert(
            [
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                mittelwert(list(result.get('mission_success_rates', {}).values())),
                1.0 if config.get('enable_meta_coordination', False) else 0.0,
                1.0 if config.get('mission_arbitration_enabled', False) else 0.0,
                profile['bias']['approval'],
            ]
        )
    )
    traceability = clamp01(
        mittelwert(
            [
                mittelwert(trace_scores),
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                profile['bias']['trace'],
            ]
        )
    )
    environment_isolation = clamp01(
        mittelwert(
            [
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                1.0 - normalize(config.get('cluster_budget_skew', 0.0), 0.16, 0.34),
                profile['bias']['isolation'],
            ]
        )
    )
    memory_safety = clamp01(
        mittelwert(
            [
                schema['extensibility'],
                schema['safety_margin'],
                mittelwert([1.0 - score for score in exposure_scores]),
                workflow.get('sync_strength_mean', 0.0),
                profile['bias']['memory'],
            ]
        )
    )
    misuse_exposure = clamp01(
        mittelwert(
            [
                mittelwert(exposure_scores),
                workflow.get('misinformation_corruption_mean', 0.0),
                workflow.get('cluster_compromise_mean', 0.0),
                1.0 - workflow.get('misinformation_detection_rate', 0.0),
                1.0 - workflow.get('trust_shield_mean', 0.0),
            ]
        )
    )
    tool_flow = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                groups['functional_group_share'],
                result['cross_group_cooperation_rate'],
                profile['bias']['flow'],
            ]
        )
    )
    binding_overhead = clamp01(
        mittelwert(
            [
                normalize(tool_count, 1.0, 5.0),
                arbitration_activity,
                1.0 - normalize(config.get('meta_update_interval', 4), 4.0, 8.0),
                normalize(config.get('resource_share_factor', 0.20), 0.20, 0.30),
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
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
        'functional_group_share': groups['functional_group_share'],
        'tool_coverage': tool_coverage,
        'approval_integrity': approval_integrity,
        'traceability': traceability,
        'environment_isolation': environment_isolation,
        'memory_safety': memory_safety,
        'misuse_exposure': misuse_exposure,
        'tool_flow': tool_flow,
        'binding_overhead': binding_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    tool_applied = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(tool_applied)
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
    result['binding_metrics'] = binding_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['binding_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['tool_coverage']
            + 0.14 * metrics['approval_integrity']
            + 0.12 * metrics['traceability']
            + 0.10 * metrics['memory_safety']
            - 0.12 * metrics['binding_overhead']
        )
    if kontext_name == 'integration':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['tool_flow']
            + 0.14 * metrics['tool_coverage']
            + 0.12 * metrics['approval_integrity']
            + 0.10 * metrics['traceability']
            + 0.08 * metrics['functional_group_share']
            - 0.10 * metrics['binding_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['environment_isolation']
            + 0.14 * metrics['detection_rate']
            + 0.10 * metrics['traceability']
            + 0.10 * metrics['approval_integrity']
            - 0.16 * metrics['misuse_exposure']
            - 0.08 * metrics['binding_overhead']
        )
    return (
        base
        + 0.18 * metrics['memory_safety']
        + 0.16 * metrics['environment_isolation']
        + 0.10 * recoveries
        + 0.08 * metrics['tool_flow']
        - 0.12 * failed_share
        - 0.10 * metrics['misuse_exposure']
        - 0.08 * metrics['binding_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'tool_coverage': {},
        'approval_integrity': {},
        'traceability': {},
        'environment_isolation': {},
        'memory_safety': {},
        'misuse_exposure': {},
        'tool_flow': {},
        'binding_overhead': {},
        'detection_rate': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['binding_metrics'][metric_name] for run in runs])

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
    profiles = tool_binding_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI WERKZEUGBINDUNGS-STUDIE')
    print('=' * 84)
    print('Vergleicht Werkzeug-, Speicher- und Umweltkopplungen fuer die Bauphase,')
    print('damit externe Bindungen kontrollierbar, nachvollziehbar und robust bleiben.\n')

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
            f"Coverage={summary['tool_coverage']['integration']:.2f} | "
            f"Trace={summary['traceability']['integration']:.2f} | "
            f"Exposure={summary['misuse_exposure']['stress']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'freie-werkzeuge')

    print('\nBeste Werkzeugbindung:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu freien Werkzeugen {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Coverage {best['tool_coverage']['integration']:.2f}, "
        f"Trace {best['traceability']['integration']:.2f}, "
        f"Isolation {best['environment_isolation']['stress']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Werkzeugbindungs-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['tool_coverage']['integration'] for item in summaries],
        width,
        label='Coverage',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['traceability']['integration'] for item in summaries],
        width,
        label='Trace',
        color='#59a14f',
    )
    axes[0, 1].set_title('Werkzeugnutzen und Nachvollziehbarkeit')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['environment_isolation']['stress'] for item in summaries],
        width,
        label='Isolation',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['misuse_exposure']['stress'] for item in summaries],
        width,
        label='Exposure',
        color='#e15759',
    )
    axes[0, 2].set_title('Isolation vs. Missbrauchsflaeche')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['startup'],
                item['context_scores']['integration'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['memory_safety']['recovery'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Bindungskontexte')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Start', 'Int', 'Stress', 'Rec', 'Mem'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['tool_flow']['integration'] for item in summaries],
        width,
        label='Tool-Flow',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['binding_overhead']['integration'] for item in summaries],
        width,
        label='Overhead',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Fluss und Kopplungsaufwand')
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
            f"- Delta zu freien Werkzeugen: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Coverage: {best['tool_coverage']['integration']:.2f}\n"
            f"- Freigabe: {best['approval_integrity']['integration']:.2f}\n"
            f"- Trace: {best['traceability']['integration']:.2f}\n"
            f"- Isolation: {best['environment_isolation']['stress']:.2f}\n"
            f"- Memory-Sicherheit: {best['memory_safety']['recovery']:.2f}\n"
            f"- Exposure: {best['misuse_exposure']['stress']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_werkzeugbindung.png', dpi=150)


if __name__ == '__main__':
    main()
