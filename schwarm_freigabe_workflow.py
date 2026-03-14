"""
KKI Freigabe-Workflow-Studie
============================
Vergleicht Freigabe- und Eingriffsschleifen fuer operative Baugruppen und misst,
welche Kombination aus Gates, Review, Eskalation und Handlungsfreiheit Governance
staerkt, ohne den operativen Blueprint zu blockieren.
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
from schwarm_rollenassembler import normalize_role_shares
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import broker_profiles
from schwarm_wissensspeicher import memory_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_APPROVAL_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_APPROVAL_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_APPROVAL_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_APPROVAL_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_APPROVAL_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_APPROVAL_FAILURE_FRACTION', '0.18')),
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


def approval_profiles(katalog, params):
    governance = get_named(governance_profiles(katalog, params), 'resilienter-governance-layer')['config']
    contract = get_named(contract_profiles(katalog, params), 'resilienter-handoff-vertrag')['config']
    broker = get_named(broker_profiles(katalog, params), 'resilienter-capability-broker')
    memory = get_named(memory_profiles(katalog, params), 'resilienter-wissensspeicher')

    runtime = {
        **governance,
        **contract,
        **broker['base_config'],
        **memory['base_config'],
    }

    return [
        {
            'name': 'offener-durchlauf',
            'label': 'Offener Durchlauf',
            'selected_tools': ['memory', 'execution'],
            'multiplier': 0.86,
            'base_config': {
                **runtime,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'meta_update_interval': 6,
                'mission_switch_interval': 6,
                'workflow_stage_min_tenure': 1,
                'trust_shield_strength': 0.22,
            },
            'approval_levels': 0,
            'reviewers': 1,
            'escalation_depth': 0,
            'bias': {
                'gate': 0.18,
                'trace': 0.24,
                'intervention': 0.16,
                'flow': 0.88,
                'recovery': 0.28,
                'overhead': 0.08,
            },
        },
        {
            'name': 'checkpoint-gates',
            'label': 'Checkpoint-Gates',
            'selected_tools': ['memory', 'analysis', 'bridge'],
            'multiplier': 0.90,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'workflow_stage_min_tenure': 2,
                'handoff_priority_bonus': 0.20,
            },
            'approval_levels': 1,
            'reviewers': 2,
            'escalation_depth': 1,
            'bias': {
                'gate': 0.50,
                'trace': 0.52,
                'intervention': 0.42,
                'flow': 0.76,
                'recovery': 0.46,
                'overhead': 0.16,
            },
        },
        {
            'name': 'review-board',
            'label': 'Review-Board',
            'selected_tools': ['memory', 'analysis', 'bridge', 'shield'],
            'multiplier': 0.94,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'meta_update_interval': 4,
                'mission_switch_interval': 5,
                'workflow_stage_min_tenure': 2,
                'handoff_priority_bonus': 0.22,
                'trust_shield_strength': 0.34,
            },
            'approval_levels': 2,
            'reviewers': 3,
            'escalation_depth': 2,
            'bias': {
                'gate': 0.74,
                'trace': 0.72,
                'intervention': 0.66,
                'flow': 0.68,
                'recovery': 0.62,
                'overhead': 0.22,
            },
        },
        {
            'name': 'foederierte-freigabe',
            'label': 'Foederierte Freigabe',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.97,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'workflow_stage_min_tenure': 2,
                'handoff_priority_bonus': 0.22,
                'trust_shield_strength': 0.36,
                'resource_share_factor': 0.29,
            },
            'approval_levels': 2,
            'reviewers': 4,
            'escalation_depth': 3,
            'bias': {
                'gate': 0.86,
                'trace': 0.84,
                'intervention': 0.82,
                'flow': 0.78,
                'recovery': 0.80,
                'overhead': 0.26,
            },
        },
        {
            'name': 'human-loop',
            'label': 'Human-in-the-Loop',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'workflow_stage_min_tenure': 2,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.38,
                'resource_share_factor': 0.29,
            },
            'approval_levels': 3,
            'reviewers': 4,
            'escalation_depth': 3,
            'bias': {
                'gate': 0.92,
                'trace': 0.92,
                'intervention': 0.90,
                'flow': 0.66,
                'recovery': 0.84,
                'overhead': 0.30,
            },
        },
        {
            'name': 'resilienter-freigabe-workflow',
            'label': 'Resilienter Freigabe-Workflow',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'workflow_stage_min_tenure': 2,
                'handoff_priority_bonus': 0.24,
                'trust_shield_strength': 0.40,
                'resource_share_factor': 0.30,
                'bottleneck_threshold': 0.94,
                'bottleneck_triage_intensity': 0.92,
            },
            'approval_levels': 3,
            'reviewers': 5,
            'escalation_depth': 4,
            'bias': {
                'gate': 0.96,
                'trace': 0.94,
                'intervention': 0.94,
                'flow': 0.78,
                'recovery': 0.94,
                'overhead': 0.30,
            },
        },
    ]


def approval_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]
    traceability = clamp01(mittelwert(trace_scores))
    exposure = clamp01(mittelwert(exposure_scores))
    approval_level_score = normalize(profile['approval_levels'], 0.0, 3.0)
    reviewer_score = normalize(profile['reviewers'], 1.0, 5.0)
    escalation_score = normalize(profile['escalation_depth'], 0.0, 4.0)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count

    gate_quality = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                workflow.get('misinformation_detection_rate', 0.0),
                approval_level_score,
                profile['bias']['gate'],
            ]
        )
    )
    trace_quality = clamp01(
        mittelwert(
            [
                traceability,
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                reviewer_score,
                profile['bias']['trace'],
            ]
        )
    )
    intervention_quality = clamp01(
        mittelwert(
            [
                1.0 if config.get('mission_arbitration_enabled', False) else 0.0,
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                escalation_score,
                workflow.get('trust_shield_mean', 0.0),
                profile['bias']['intervention'],
            ]
        )
    )
    workflow_flow = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('handoff_rate', 0.0),
                groups['functional_group_share'],
                profile['bias']['flow'],
            ]
        )
    )
    recovery_safety = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - exposure,
                profile['bias']['recovery'],
            ]
        )
    )
    approval_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 6.0),
                normalize(config.get('mission_switch_interval', 4), 4.0, 6.0),
                approval_level_score,
                reviewer_score,
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
        'gate_quality': gate_quality,
        'trace_quality': trace_quality,
        'intervention_quality': intervention_quality,
        'workflow_flow': workflow_flow,
        'recovery_safety': recovery_safety,
        'approval_overhead': approval_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    workflow_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(workflow_config)
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
    result['approval_metrics'] = approval_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['approval_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['gate_quality']
            + 0.12 * metrics['trace_quality']
            + 0.10 * metrics['workflow_flow']
            - 0.10 * metrics['approval_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['workflow_flow']
            + 0.14 * metrics['trace_quality']
            + 0.10 * metrics['intervention_quality']
            - 0.10 * metrics['approval_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['gate_quality']
            + 0.14 * metrics['intervention_quality']
            + 0.08 * metrics['trace_quality']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['approval_overhead']
        )
    return (
        base
        + 0.18 * metrics['recovery_safety']
        + 0.12 * metrics['intervention_quality']
        + 0.08 * metrics['workflow_flow']
        - 0.12 * failed_share
        - 0.08 * metrics['approval_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'gate_quality': {},
        'trace_quality': {},
        'intervention_quality': {},
        'workflow_flow': {},
        'recovery_safety': {},
        'approval_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['approval_metrics'][metric_name] for run in runs])

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
    profiles = approval_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI FREIGABE-WORKFLOW-STUDIE')
    print('=' * 84)
    print('Vergleicht Freigabe- und Eingriffsschleifen fuer operative Baugruppen,')
    print('damit Governance, Audit und Handlungsfaehigkeit gemeinsam tragfaehig bleiben.\n')

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
            f"Gate={summary['gate_quality']['startup']:.2f} | "
            f"Trace={summary['trace_quality']['operations']:.2f} | "
            f"Recovery={summary['recovery_safety']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'offener-durchlauf')

    print('\nBester Freigabe-Workflow:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum offenen Durchlauf {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Gate {best['gate_quality']['startup']:.2f}, "
        f"Trace {best['trace_quality']['operations']:.2f}, "
        f"Recovery {best['recovery_safety']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Freigabe-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['gate_quality']['startup'] for item in summaries],
        width,
        label='Gate-Qualitaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['trace_quality']['operations'] for item in summaries],
        width,
        label='Trace-Qualitaet',
        color='#59a14f',
    )
    axes[0, 1].set_title('Freigabe und Nachvollziehbarkeit')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['intervention_quality']['stress'] for item in summaries],
        width,
        label='Intervention',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['recovery_safety']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Eingriffe und Recovery')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['workflow_flow']['operations'] for item in summaries],
        width,
        label='Flow',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['approval_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Flow gegen Overhead')
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
    output = save_and_maybe_show(plt, 'kki_freigabe_workflow.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
