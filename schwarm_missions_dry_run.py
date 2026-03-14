"""
KKI Missions-Dry-Run-Studie
===========================
Vergleicht Vorabnahme- und Missionsproben fuer operative Baugruppen und misst,
welche Dry-Run-Architektur Freigabe, Supervisorik, Routing und Sandboxen so
zusammenfuehrt, dass reale Bauaufgaben belastbar vorbereitet werden.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
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
from schwarm_sandbox_zellen import sandbox_profiles
from schwarm_supervisor_eingriffe import intervention_profiles
from schwarm_freigabe_workflow import approval_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import broker_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_MISSION_DRY_RUN_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_MISSION_DRY_RUN_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_MISSION_DRY_RUN_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_MISSION_DRY_RUN_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_MISSION_DRY_RUN_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_MISSION_DRY_RUN_FAILURE_FRACTION', '0.18')),
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
        {'name': 'briefing', 'label': 'Briefing', 'scenario': 'consensus', 'startup_mode': True},
        {'name': 'acceptance', 'label': 'Vorabnahme', 'scenario': 'consensus', 'acceptance_mode': True},
        {'name': 'stress', 'label': 'Stressprobe', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def mission_profiles(katalog, params):
    broker = get_named(broker_profiles(katalog, params), 'resilienter-capability-broker')
    approval = get_named(approval_profiles(katalog, params), 'resilienter-freigabe-workflow')
    supervisor = get_named(intervention_profiles(katalog, params), 'leitplanken-supervisor')
    sandbox = get_named(sandbox_profiles(katalog, params), 'foederierte-sandbox-zellen')

    runtime = {
        **broker['base_config'],
        **approval['base_config'],
        **supervisor['base_config'],
        **sandbox['base_config'],
    }

    return [
        {
            'name': 'direkter-missionsstart',
            'label': 'Direkter Missionsstart',
            'selected_tools': ['execution', 'memory'],
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
                'trust_shield_strength': 0.28,
                'handoff_priority_bonus': 0.18,
            },
            'rehearsal_depth': 1,
            'acceptance_layers': 0,
            'launch_buffer': 1,
            'bias': {
                'brief': 0.28,
                'fidelity': 0.48,
                'approval': 0.22,
                'launch': 0.56,
                'recovery': 0.34,
                'overhead': 0.08,
            },
        },
        {
            'name': 'checklisten-dry-run',
            'label': 'Checklisten-Dry-Run',
            'selected_tools': ['memory', 'analysis', 'execution'],
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
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.32,
                'handoff_priority_bonus': 0.20,
            },
            'rehearsal_depth': 2,
            'acceptance_layers': 1,
            'launch_buffer': 2,
            'bias': {
                'brief': 0.56,
                'fidelity': 0.64,
                'approval': 0.46,
                'launch': 0.66,
                'recovery': 0.48,
                'overhead': 0.14,
            },
        },
        {
            'name': 'stage-gate-dry-run',
            'label': 'Stage-Gate-Dry-Run',
            'selected_tools': ['memory', 'analysis', 'bridge', 'shield'],
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
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.36,
                'handoff_priority_bonus': 0.22,
            },
            'rehearsal_depth': 3,
            'acceptance_layers': 2,
            'launch_buffer': 2,
            'bias': {
                'brief': 0.78,
                'fidelity': 0.70,
                'approval': 0.78,
                'launch': 0.72,
                'recovery': 0.62,
                'overhead': 0.20,
            },
        },
        {
            'name': 'foederierter-missions-dry-run',
            'label': 'Foederierter Missions-Dry-Run',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
                'handoff_priority_bonus': 0.24,
                'bottleneck_triage_intensity': 0.92,
            },
            'rehearsal_depth': 4,
            'acceptance_layers': 3,
            'launch_buffer': 3,
            'bias': {
                'brief': 0.88,
                'fidelity': 0.86,
                'approval': 0.88,
                'launch': 0.86,
                'recovery': 0.80,
                'overhead': 0.24,
            },
        },
        {
            'name': 'abnahmeboard',
            'label': 'Abnahmeboard',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.99,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.40,
                'handoff_priority_bonus': 0.24,
                'bottleneck_triage_intensity': 0.94,
            },
            'rehearsal_depth': 4,
            'acceptance_layers': 4,
            'launch_buffer': 3,
            'bias': {
                'brief': 0.90,
                'fidelity': 0.78,
                'approval': 0.94,
                'launch': 0.74,
                'recovery': 0.82,
                'overhead': 0.30,
            },
        },
        {
            'name': 'resilienter-missions-dry-run',
            'label': 'Resilienter Missions-Dry-Run',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'handoff_priority_bonus': 0.24,
                'bottleneck_triage_intensity': 0.94,
                'resync_strength': 0.48,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.03),
            },
            'rehearsal_depth': 5,
            'acceptance_layers': 4,
            'launch_buffer': 4,
            'bias': {
                'brief': 0.90,
                'fidelity': 0.76,
                'approval': 0.90,
                'launch': 0.72,
                'recovery': 0.90,
                'overhead': 0.36,
            },
        },
    ]


def mission_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    traces = [catalog[name]['scores']['trace'] for name in selected_tools]
    exposures = [catalog[name]['scores']['exposure'] for name in selected_tools]
    traceability = clamp01(mittelwert(traces or [0.0]))
    exposure = clamp01(mittelwert(exposures or [0.0]))
    agent_count = max(1.0, params['agent_count'])
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    rehearsal_depth_score = normalize(profile['rehearsal_depth'], 1.0, 5.0)
    acceptance_score = normalize(profile['acceptance_layers'], 0.0, 4.0)
    launch_buffer_score = normalize(profile['launch_buffer'], 1.0, 4.0)

    briefing_reliability = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                workflow.get('meta_alignment_rate', 0.0),
                groups['functional_group_share'],
                rehearsal_depth_score,
                profile['bias']['brief'],
            ]
        )
    )
    rehearsal_fidelity = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                launch_buffer_score,
                profile['bias']['fidelity'],
            ]
        )
    )
    approval_readiness = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                traceability,
                1.0 - exposure,
                acceptance_score,
                profile['bias']['approval'],
            ]
        )
    )
    launch_confidence = clamp01(
        mittelwert(
            [
                briefing_reliability,
                rehearsal_fidelity,
                approval_readiness,
                1.0 - workflow.get('bottleneck_rate', 0.0),
                profile['bias']['launch'],
            ]
        )
    )
    recovery_assurance = clamp01(
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
    dry_run_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_share_factor', 0.28), 0.28, 0.30),
                rehearsal_depth_score,
                acceptance_score,
                1.0 - launch_buffer_score,
                profile['bias']['overhead'],
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
        'briefing_reliability': briefing_reliability,
        'rehearsal_fidelity': rehearsal_fidelity,
        'approval_readiness': approval_readiness,
        'launch_confidence': launch_confidence,
        'recovery_assurance': recovery_assurance,
        'dry_run_overhead': dry_run_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    dry_run_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(dry_run_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('acceptance_mode'):
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
    result['mission_metrics'] = mission_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['mission_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'briefing':
        return (
            metrics['briefing_reliability']
            + 0.18 * metrics['rehearsal_fidelity']
            + 0.12 * metrics['launch_confidence']
            - 0.10 * metrics['dry_run_overhead']
        )
    if kontext_name == 'acceptance':
        return (
            metrics['launch_confidence']
            + 0.18 * metrics['approval_readiness']
            + 0.12 * metrics['rehearsal_fidelity']
            - 0.12 * metrics['dry_run_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['approval_readiness']
            + 0.14 * metrics['launch_confidence']
            + 0.10 * metrics['recovery_assurance']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['dry_run_overhead']
        )
    return (
        base
        + 0.20 * metrics['recovery_assurance']
        + 0.12 * metrics['approval_readiness']
        + 0.08 * metrics['launch_confidence']
        - 0.12 * failed_share
        - 0.08 * metrics['dry_run_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'briefing_reliability': {},
        'rehearsal_fidelity': {},
        'approval_readiness': {},
        'launch_confidence': {},
        'recovery_assurance': {},
        'dry_run_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['mission_metrics'][metric_name] for run in runs])

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
    profiles = mission_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI MISSIONS-DRY-RUN-STUDIE')
    print('=' * 84)
    print('Vergleicht Missionsproben und Vorabnahme-Architekturen fuer operative Baugruppen,')
    print('damit reale Bauaufgaben mit Routing, Freigabe und Supervisorik belastbar starten.\n')

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
            f"{summary['label']:<31} Score={summary['combined_score']:+.3f} | "
            f"Start={summary['briefing_reliability']['briefing']:.2f} | "
            f"Freigabe={summary['approval_readiness']['acceptance']:.2f} | "
            f"Recovery={summary['recovery_assurance']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'direkter-missionsstart')

    print('\nBester Missions-Dry-Run:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum direkten Missionsstart {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Freigabe {best['approval_readiness']['acceptance']:.2f}, "
        f"Launch {best['launch_confidence']['acceptance']:.2f}, "
        f"Recovery {best['recovery_assurance']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Dry-Run-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['briefing_reliability']['briefing'] for item in summaries],
        width,
        label='Briefing',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['launch_confidence']['acceptance'] for item in summaries],
        width,
        label='Launch',
        color='#59a14f',
    )
    axes[0, 1].set_title('Start- und Launch-Reife')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['approval_readiness']['acceptance'] for item in summaries],
        width,
        label='Freigabe',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['rehearsal_fidelity']['acceptance'] for item in summaries],
        width,
        label='Fidelity',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Vorabnahme und Probenqualitaet')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['recovery_assurance']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#e15759',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['dry_run_overhead']['acceptance'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Recovery gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['stress'] for item in summaries], color=colors)
    axes[1, 1].set_title('Stressprobe-Score')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].bar(
        x - width / 2,
        [item['context_scores']['acceptance'] for item in summaries],
        width,
        label='Vorabnahme',
        color='#59a14f',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['context_scores']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#4e79a7',
    )
    axes[1, 2].set_title('Vorabnahme- und Recovery-Score')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_missions_dry_run.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
