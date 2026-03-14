"""
KKI Bauphasen-Pilotarchitektur-Studie
=====================================
Verdichtet die Siegerbausteine der operativen Bauphase zu finalen Pilotarchitekturen
und misst, welche Synthese aus Runtime, Routing, Wissen, Dry-Run, Sandbox und
Leitplanken den besten Uebergang in eine spaetere reale Bauphase vorbereitet.
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
from schwarm_missions_dry_run import mission_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_runtime_dna import runtime_profiles
from schwarm_sandbox_zellen import sandbox_profiles
from schwarm_supervisor_eingriffe import intervention_profiles
from schwarm_wissensspeicher import memory_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import broker_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_PILOT_ARCH_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_PILOT_ARCH_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_PILOT_ARCH_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_PILOT_ARCH_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_PILOT_ARCH_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_PILOT_ARCH_FAILURE_FRACTION', '0.18')),
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
        {'name': 'blueprint', 'label': 'Blueprint', 'scenario': 'consensus', 'startup_mode': True},
        {'name': 'operations', 'label': 'Operation', 'scenario': 'consensus'},
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
        {'name': 'pilot', 'label': 'Pilot', 'scenario': 'consensus', 'pilot_mode': True},
    ]


def pilot_profiles(katalog, params):
    blueprint = get_named(blueprint_profiles(katalog, params), 'operativer-blueprint')
    runtime = get_named(runtime_profiles(katalog, params), 'operative-runtime-dna')
    runtime_resilient = get_named(runtime_profiles(katalog, params), 'resiliente-runtime-dna')
    broker = get_named(broker_profiles(katalog, params), 'resilienter-capability-broker')
    memory = get_named(memory_profiles(katalog, params), 'resilienter-wissensspeicher')
    supervisor = get_named(intervention_profiles(katalog, params), 'leitplanken-supervisor')
    supervisor_resilient = get_named(intervention_profiles(katalog, params), 'resilienter-eingriffs-supervisor')
    sandbox = get_named(sandbox_profiles(katalog, params), 'foederierte-sandbox-zellen')
    mission = get_named(mission_profiles(katalog, params), 'resilienter-missions-dry-run')

    return [
        {
            'name': 'minimaler-pilot',
            'label': 'Minimaler Pilot',
            'selected_tools': ['execution', 'memory'],
            'multiplier': 0.88,
            'base_config': {
                **runtime['config'],
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.28,
            },
            'integration_depth': 1,
            'pilot_readiness': 1,
            'safety_depth': 1,
            'bias': {
                'architecture': 0.34,
                'launch': 0.42,
                'coordination': 0.42,
                'safety': 0.28,
                'pilot': 0.46,
                'overhead': 0.08,
            },
        },
        {
            'name': 'operativer-pilot',
            'label': 'Operativer Pilot',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge'],
            'multiplier': 0.93,
            'base_config': {
                **blueprint['config'],
                **runtime['config'],
                'enable_fault_isolation': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'handoff_priority_bonus': 0.22,
            },
            'integration_depth': 2,
            'pilot_readiness': 2,
            'safety_depth': 2,
            'bias': {
                'architecture': 0.68,
                'launch': 0.70,
                'coordination': 0.72,
                'safety': 0.62,
                'pilot': 0.72,
                'overhead': 0.16,
            },
        },
        {
            'name': 'foederierter-pilot',
            'label': 'Foederierter Pilot',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.97,
            'base_config': {
                **runtime['config'],
                **broker['base_config'],
                **memory['base_config'],
                **sandbox['base_config'],
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
            },
            'integration_depth': 3,
            'pilot_readiness': 3,
            'safety_depth': 3,
            'bias': {
                'architecture': 0.84,
                'launch': 0.82,
                'coordination': 0.86,
                'safety': 0.82,
                'pilot': 0.84,
                'overhead': 0.24,
            },
        },
        {
            'name': 'leitplanken-pilot',
            'label': 'Leitplanken-Pilot',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime['config'],
                **broker['base_config'],
                **memory['base_config'],
                **sandbox['base_config'],
                **supervisor['base_config'],
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
            },
            'integration_depth': 4,
            'pilot_readiness': 3,
            'safety_depth': 4,
            'bias': {
                'architecture': 0.88,
                'launch': 0.84,
                'coordination': 0.88,
                'safety': 0.90,
                'pilot': 0.86,
                'overhead': 0.26,
            },
        },
        {
            'name': 'pilot-architektur',
            'label': 'Pilot-Architektur',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime_resilient['config'],
                **broker['base_config'],
                **memory['base_config'],
                **sandbox['base_config'],
                **supervisor['base_config'],
                **mission['base_config'],
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'bottleneck_triage_intensity': 0.94,
            },
            'integration_depth': 5,
            'pilot_readiness': 4,
            'safety_depth': 4,
            'bias': {
                'architecture': 0.94,
                'launch': 0.90,
                'coordination': 0.92,
                'safety': 0.92,
                'pilot': 0.94,
                'overhead': 0.30,
            },
        },
        {
            'name': 'maximaler-schutzpilot',
            'label': 'Maximaler Schutzpilot',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **runtime_resilient['config'],
                **broker['base_config'],
                **memory['base_config'],
                **sandbox['base_config'],
                **supervisor_resilient['base_config'],
                **mission['base_config'],
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.42,
                'bottleneck_triage_intensity': 0.96,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.05),
                'resync_strength': 0.54,
            },
            'integration_depth': 5,
            'pilot_readiness': 4,
            'safety_depth': 5,
            'bias': {
                'architecture': 0.92,
                'launch': 0.74,
                'coordination': 0.80,
                'safety': 0.94,
                'pilot': 0.80,
                'overhead': 0.48,
            },
        },
    ]


def pilot_metrics(config, result, params, profile):
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
    integration_score = normalize(profile['integration_depth'], 1.0, 5.0)
    readiness_score = normalize(profile['pilot_readiness'], 1.0, 4.0)
    safety_score = normalize(profile['safety_depth'], 1.0, 5.0)

    architecture_fit = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                workflow.get('meta_alignment_rate', 0.0),
                integration_score,
                profile['bias']['architecture'],
            ]
        )
    )
    launch_readiness = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('handoff_rate', 0.0),
                readiness_score,
                profile['bias']['launch'],
            ]
        )
    )
    coordination_quality = clamp01(
        mittelwert(
            [
                workflow.get('resource_share_rate', 0.0),
                groups['functional_group_share'],
                workflow.get('skill_alignment_rate', 0.0),
                traceability,
                profile['bias']['coordination'],
            ]
        )
    )
    safety_posture = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                1.0 - exposure,
                safety_score,
                profile['bias']['safety'],
            ]
        )
    )
    pilot_readiness = clamp01(
        mittelwert(
            [
                architecture_fit,
                launch_readiness,
                coordination_quality,
                safety_posture,
                recoveries,
                profile['bias']['pilot'],
            ]
        )
    )
    pilot_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_share_factor', 0.28), 0.28, 0.30),
                integration_score,
                safety_score,
                1.0 - readiness_score,
                profile['bias']['overhead'],
            ]
        )
    )
    recovery_strength = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - workflow.get('bottleneck_rate', 0.0),
                safety_score,
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
        'architecture_fit': architecture_fit,
        'launch_readiness': launch_readiness,
        'coordination_quality': coordination_quality,
        'safety_posture': safety_posture,
        'pilot_readiness': pilot_readiness,
        'pilot_overhead': pilot_overhead,
        'recovery_strength': recovery_strength,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    pilot_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(pilot_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('pilot_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), params['acceptance_cycles'])
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
    result['pilot_metrics'] = pilot_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['pilot_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'blueprint':
        return (
            metrics['architecture_fit']
            + 0.18 * metrics['coordination_quality']
            + 0.12 * metrics['launch_readiness']
            - 0.10 * metrics['pilot_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['launch_readiness']
            + 0.16 * metrics['coordination_quality']
            + 0.12 * metrics['pilot_readiness']
            - 0.10 * metrics['pilot_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['safety_posture']
            + 0.14 * metrics['pilot_readiness']
            + 0.08 * metrics['recovery_strength']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['pilot_overhead']
        )
    if kontext_name == 'recovery':
        return (
            base
            + 0.20 * metrics['recovery_strength']
            + 0.12 * metrics['safety_posture']
            + 0.08 * metrics['pilot_readiness']
            - 0.12 * failed_share
            - 0.08 * metrics['pilot_overhead']
        )
    return (
        metrics['pilot_readiness']
        + 0.18 * metrics['launch_readiness']
        + 0.12 * metrics['safety_posture']
        - 0.12 * metrics['pilot_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'architecture_fit': {},
        'launch_readiness': {},
        'coordination_quality': {},
        'safety_posture': {},
        'pilot_readiness': {},
        'pilot_overhead': {},
        'recovery_strength': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['pilot_metrics'][metric_name] for run in runs])

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
    profiles = pilot_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI BAUPHASEN-PILOTARCHITEKTUR-STUDIE')
    print('=' * 84)
    print('Verdichtet die Siegerbausteine der operativen Bauphase zu finalen Pilotarchitekturen,')
    print('damit der Uebergang in reale Bauaufgaben belastbar, koordiniert und abgesichert gelingt.\n')

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
            f"Pilot={summary['pilot_readiness']['pilot']:.2f} | "
            f"Safety={summary['safety_posture']['stress']:.2f} | "
            f"Launch={summary['launch_readiness']['operations']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'minimaler-pilot')

    print('\nBeste Bauphasen-Pilotarchitektur:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum minimalen Piloten {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Pilotreife {best['pilot_readiness']['pilot']:.2f}, "
        f"Safety {best['safety_posture']['stress']:.2f}, "
        f"Recovery {best['recovery_strength']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Pilot-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['pilot_readiness']['pilot'] for item in summaries],
        width,
        label='Pilotreife',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['launch_readiness']['operations'] for item in summaries],
        width,
        label='Launch',
        color='#59a14f',
    )
    axes[0, 1].set_title('Pilotreife und Launch')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['coordination_quality']['operations'] for item in summaries],
        width,
        label='Koordination',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['architecture_fit']['blueprint'] for item in summaries],
        width,
        label='Architekturfit',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Architektur und Koordination')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['safety_posture']['stress'] for item in summaries],
        width,
        label='Safety',
        color='#e15759',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['pilot_overhead']['pilot'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Safety gegen Overhead')
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
        [item['context_scores']['pilot'] for item in summaries],
        width,
        label='Pilot',
        color='#59a14f',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['recovery_strength']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#4e79a7',
    )
    axes[1, 2].set_title('Pilot- und Recovery-Score')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_bauphasen_pilot.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
