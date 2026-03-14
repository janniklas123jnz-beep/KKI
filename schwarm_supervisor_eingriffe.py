"""
KKI Supervisor-Eingriffs-Studie
===============================
Vergleicht konkrete Supervisor-Aktionen und Leitplanken fuer operative
Baugruppen und misst, welche Eingriffsmuster Stabilitaet, Recovery und
Handlungsfaehigkeit verbinden, ohne in Uebersteuerung zu kippen.
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
from schwarm_laufzeitsupervision import supervision_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_freigabe_workflow import approval_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_SUPERVISOR_ACTION_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_SUPERVISOR_ACTION_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_SUPERVISOR_ACTION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_SUPERVISOR_ACTION_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_SUPERVISOR_ACTION_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_SUPERVISOR_ACTION_FAILURE_FRACTION', '0.18')),
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


def intervention_profiles(katalog, params):
    supervision = get_named(supervision_profiles(katalog, params), 'resiliente-supervisor-foederation')['config']
    approval = get_named(approval_profiles(katalog, params), 'resilienter-freigabe-workflow')
    runtime = {
        **supervision,
        **approval['base_config'],
    }

    return [
        {
            'name': 'hinweis-supervisor',
            'label': 'Hinweis-Supervisor',
            'selected_tools': ['analysis', 'memory'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                'enable_fault_isolation': False,
                'mission_arbitration_enabled': False,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'trust_shield_strength': 0.30,
                'bottleneck_triage_intensity': 0.84,
            },
            'intervention_depth': 1,
            'autonomy_floor': 4,
            'recovery_depth': 1,
            'bias': {
                'detection': 0.54,
                'precision': 0.42,
                'stabilization': 0.40,
                'autonomy': 0.88,
                'recovery': 0.42,
                'overhead': 0.12,
            },
        },
        {
            'name': 'soft-triage',
            'label': 'Soft-Triage',
            'selected_tools': ['analysis', 'memory', 'bridge'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                'enable_fault_isolation': False,
                'mission_arbitration_enabled': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 5,
                'handoff_priority_bonus': 0.22,
                'trust_shield_strength': 0.34,
                'bottleneck_triage_intensity': 0.88,
            },
            'intervention_depth': 2,
            'autonomy_floor': 3,
            'recovery_depth': 2,
            'bias': {
                'detection': 0.72,
                'precision': 0.66,
                'stabilization': 0.62,
                'autonomy': 0.80,
                'recovery': 0.60,
                'overhead': 0.18,
            },
        },
        {
            'name': 'leitplanken-supervisor',
            'label': 'Leitplanken-Supervisor',
            'selected_tools': ['analysis', 'memory', 'bridge', 'shield'],
            'multiplier': 0.95,
            'base_config': {
                **runtime,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.22,
                'trust_shield_strength': 0.36,
                'bottleneck_triage_intensity': 0.90,
            },
            'intervention_depth': 3,
            'autonomy_floor': 3,
            'recovery_depth': 2,
            'bias': {
                'detection': 0.84,
                'precision': 0.80,
                'stabilization': 0.78,
                'autonomy': 0.72,
                'recovery': 0.72,
                'overhead': 0.22,
            },
        },
        {
            'name': 'quarantaene-leitplanken',
            'label': 'Quarantaene-Leitplanken',
            'selected_tools': ['analysis', 'memory', 'bridge', 'shield'],
            'multiplier': 0.97,
            'base_config': {
                **runtime,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.38,
                'quarantine_compromise_threshold': 0.22,
                'quarantine_exposure_threshold': 0.28,
                'bottleneck_triage_intensity': 0.92,
            },
            'intervention_depth': 4,
            'autonomy_floor': 2,
            'recovery_depth': 3,
            'bias': {
                'detection': 0.90,
                'precision': 0.88,
                'stabilization': 0.84,
                'autonomy': 0.62,
                'recovery': 0.82,
                'overhead': 0.28,
            },
        },
        {
            'name': 'recovery-orchestrator',
            'label': 'Recovery-Orchestrator',
            'selected_tools': ['analysis', 'memory', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.38,
                'resync_strength': 0.52,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
                'bottleneck_triage_intensity': 0.92,
            },
            'intervention_depth': 4,
            'autonomy_floor': 2,
            'recovery_depth': 4,
            'bias': {
                'detection': 0.86,
                'precision': 0.84,
                'stabilization': 0.86,
                'autonomy': 0.64,
                'recovery': 0.94,
                'overhead': 0.28,
            },
        },
        {
            'name': 'resilienter-eingriffs-supervisor',
            'label': 'Resilienter Eingriffs-Supervisor',
            'selected_tools': ['analysis', 'memory', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'enable_bottleneck_management': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.40,
                'resync_strength': 0.54,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.05),
                'bottleneck_threshold': 0.92,
                'bottleneck_triage_intensity': 0.96,
            },
            'intervention_depth': 5,
            'autonomy_floor': 3,
            'recovery_depth': 4,
            'bias': {
                'detection': 0.94,
                'precision': 0.92,
                'stabilization': 0.92,
                'autonomy': 0.76,
                'recovery': 0.96,
                'overhead': 0.30,
            },
        },
    ]


def intervention_metrics(config, result, params, profile):
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
    intervention_depth_score = normalize(profile['intervention_depth'], 1.0, 5.0)
    autonomy_score = normalize(profile['autonomy_floor'], 2.0, 4.0)
    recovery_depth_score = normalize(profile['recovery_depth'], 1.0, 4.0)
    arbitration_activity = normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0)
    bottleneck_rate = workflow.get('bottleneck_rate', 0.0)
    bottleneck_relief_rate = workflow.get('bottleneck_relief_rate', 0.0)

    detection_strength = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                intervention_depth_score,
                profile['bias']['detection'],
            ]
        )
    )
    precision_quality = clamp01(
        mittelwert(
            [
                traceability,
                schema['invariant_compliance'],
                arbitration_activity,
                1.0 - exposure,
                profile['bias']['precision'],
            ]
        )
    )
    stabilization_gain = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                1.0 - bottleneck_rate,
                bottleneck_relief_rate,
                profile['bias']['stabilization'],
            ]
        )
    )
    autonomy_preservation = clamp01(
        mittelwert(
            [
                groups['functional_group_share'],
                workflow.get('handoff_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                autonomy_score,
                profile['bias']['autonomy'],
            ]
        )
    )
    recovery_strength = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                recovery_depth_score,
                profile['bias']['recovery'],
            ]
        )
    )
    intervention_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 5.0),
                normalize(config.get('mission_switch_interval', 4), 4.0, 5.0),
                intervention_depth_score,
                recovery_depth_score,
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
        'detection_strength': detection_strength,
        'precision_quality': precision_quality,
        'stabilization_gain': stabilization_gain,
        'autonomy_preservation': autonomy_preservation,
        'recovery_strength': recovery_strength,
        'intervention_overhead': intervention_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    intervention_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(intervention_config)
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
    result['intervention_metrics'] = intervention_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['intervention_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['detection_strength']
            + 0.12 * metrics['precision_quality']
            + 0.12 * metrics['autonomy_preservation']
            - 0.10 * metrics['intervention_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['stabilization_gain']
            + 0.14 * metrics['autonomy_preservation']
            + 0.10 * metrics['precision_quality']
            - 0.10 * metrics['intervention_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['detection_strength']
            + 0.14 * metrics['precision_quality']
            + 0.10 * metrics['stabilization_gain']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['intervention_overhead']
        )
    return (
        base
        + 0.18 * metrics['recovery_strength']
        + 0.12 * metrics['stabilization_gain']
        + 0.08 * metrics['autonomy_preservation']
        - 0.12 * failed_share
        - 0.08 * metrics['intervention_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'detection_strength': {},
        'precision_quality': {},
        'stabilization_gain': {},
        'autonomy_preservation': {},
        'recovery_strength': {},
        'intervention_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['intervention_metrics'][metric_name] for run in runs])

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
    profiles = intervention_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI SUPERVISOR-EINGRIFFS-STUDIE')
    print('=' * 84)
    print('Vergleicht konkrete Supervisor-Aktionen fuer operative Baugruppen,')
    print('damit Stabilisierung, Recovery und Autonomie im Gleichgewicht bleiben.\n')

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
            f"Detect={summary['detection_strength']['stress']:.2f} | "
            f"Autonomie={summary['autonomy_preservation']['operations']:.2f} | "
            f"Recovery={summary['recovery_strength']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'hinweis-supervisor')

    print('\nBester Supervisor-Eingriff:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum Hinweis-Supervisor {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Detection {best['detection_strength']['stress']:.2f}, "
        f"Autonomie {best['autonomy_preservation']['operations']:.2f}, "
        f"Recovery {best['recovery_strength']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Eingriffs-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['detection_strength']['stress'] for item in summaries],
        width,
        label='Detection',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['precision_quality']['stress'] for item in summaries],
        width,
        label='Praezision',
        color='#59a14f',
    )
    axes[0, 1].set_title('Erkennung und Praezision')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['stabilization_gain']['operations'] for item in summaries],
        width,
        label='Stabilisierung',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['autonomy_preservation']['operations'] for item in summaries],
        width,
        label='Autonomie',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Eingriff und Freiheit')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['recovery_strength']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['intervention_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Recovery gegen Overhead')
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
    output = save_and_maybe_show(plt, 'kki_supervisor_eingriffe.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
