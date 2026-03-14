"""
KKI Protokollstack-Studie
=========================
Vergleicht mehrstufige Kommunikations- und Entscheidungsprotokolle zwischen
Gruppen und misst, welche Schichtung Handoffs, Arbitration, Validierung und
Eskalation robust zusammensetzt, ohne zu viel Koordinations-Overhead zu
erzeugen.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named, schema_metrics
from schwarm_faehigkeitsarbitration import arbitration_profiles
from schwarm_gruppenbootstrap import bootstrap_profiles
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenhandoff import handoff_profiles
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_PROTOCOL_STACK_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_PROTOCOL_STACK_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_PROTOCOL_STACK_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_PROTOCOL_STACK_STRESS_STRENGTH', '0.46')),
        'stress_sources': int(os.getenv('KKI_PROTOCOL_STACK_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_PROTOCOL_STACK_FAILURE_FRACTION', '0.18')),
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
        {'name': 'consensus', 'label': 'Konsens', 'scenario': 'consensus'},
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


def protocol_profiles(katalog, params):
    bootstrap = get_named(bootstrap_profiles(katalog, params), 'resilienter-bootstrap')['config']
    handoff = get_named(handoff_profiles(katalog), 'parallele-resiliente-handoffs')['config']
    arbitration = get_named(arbitration_profiles(katalog), 'meta-arbitration')['config']
    coupled = get_named(arbitration_profiles(katalog), 'gekoppelte-arbitration')['config']

    return [
        {
            'name': 'direktprotokoll',
            'label': 'Direktprotokoll',
            'config': {
                **bootstrap,
                'enable_handoff_coordination': False,
                'enable_parallel_workflow_cells': False,
                'enable_resource_coordination': False,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'workflow_stage_min_tenure': 2,
                'mission_switch_interval': 8,
            },
            'bias': {'validation': 0.28, 'trace': 0.20, 'escalation': 0.12, 'overhead': 0.08},
        },
        {
            'name': 'handoff-protokoll',
            'label': 'Handoff-Protokoll',
            'config': {
                **handoff,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'workflow_stage_min_tenure': 2,
            },
            'bias': {'validation': 0.40, 'trace': 0.44, 'escalation': 0.26, 'overhead': 0.14},
        },
        {
            'name': 'validierungs-stack',
            'label': 'Validierungs-Stack',
            'config': {
                **bootstrap,
                'enable_handoff_coordination': True,
                'enable_parallel_workflow_cells': True,
                'enable_resource_coordination': True,
                'handoff_priority_bonus': 0.18,
                'enable_meta_coordination': True,
                'meta_update_interval': 5,
                'mission_arbitration_enabled': True,
                'mission_assignment': 'arbitrated',
                'enable_fault_isolation': True,
                'trust_shield_strength': min(0.42, bootstrap.get('trust_shield_strength', 0.38) + 0.02),
                'resource_share_factor': min(0.30, bootstrap.get('resource_share_factor', 0.30)),
            },
            'bias': {'validation': 0.82, 'trace': 0.72, 'escalation': 0.68, 'overhead': 0.22},
        },
        {
            'name': 'mehrschicht-stack',
            'label': 'Mehrschicht-Stack',
            'config': {
                **handoff,
                **arbitration,
                'enable_fault_isolation': True,
                'trust_shield_strength': 0.34,
                'workflow_stage_min_tenure': 1,
                'mission_switch_interval': 5,
                'meta_update_interval': 4,
                'resource_budget': max(handoff.get('resource_budget', 0.62), arbitration.get('resource_budget', 0.64)),
                'resource_share_factor': max(
                    handoff.get('resource_share_factor', 0.24),
                    arbitration.get('resource_share_factor', 0.24),
                ),
            },
            'bias': {'validation': 0.86, 'trace': 0.84, 'escalation': 0.76, 'overhead': 0.28},
        },
        {
            'name': 'meta-protokollstack',
            'label': 'Meta-Protokollstack',
            'config': {
                **arbitration,
                'enable_handoff_coordination': True,
                'enable_parallel_workflow_cells': True,
                'enable_resource_coordination': True,
                'handoff_priority_bonus': 0.18,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'meta_priority_strength': min(0.42, arbitration.get('meta_priority_strength', 0.38) + 0.02),
                'resource_share_factor': min(0.30, arbitration.get('resource_share_factor', 0.24) + 0.02),
            },
            'bias': {'validation': 0.88, 'trace': 0.90, 'escalation': 0.86, 'overhead': 0.32},
        },
        {
            'name': 'resilienter-protokollstack',
            'label': 'Resilienter Protokollstack',
            'config': {
                **bootstrap,
                **coupled,
                'enable_handoff_coordination': True,
                'enable_parallel_workflow_cells': True,
                'enable_resource_coordination': True,
                'enable_meta_coordination': True,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'mission_assignment': 'arbitrated',
                'workflow_stage_min_tenure': 1,
                'mission_switch_interval': 4,
                'meta_update_interval': 4,
                'handoff_priority_bonus': 0.20,
                'trust_shield_strength': min(0.42, coupled.get('trust_shield_strength', 0.36) + 0.02),
                'resource_budget': min(0.78, coupled.get('resource_budget', 0.66) + 0.02),
                'resource_share_factor': min(0.30, coupled.get('resource_share_factor', 0.27) + 0.01),
                'resync_strength': min(0.54, bootstrap.get('resync_strength', params['resync_strength']) + 0.06),
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
            },
            'bias': {'validation': 0.92, 'trace': 0.92, 'escalation': 0.92, 'overhead': 0.30},
        },
    ]


def protocol_stack_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)

    protocol_layers = [
        config.get('enable_workflow_stages', False),
        config.get('enable_workflow_cells', False),
        config.get('enable_handoff_coordination', False),
        config.get('enable_parallel_workflow_cells', False),
        config.get('enable_resource_coordination', False),
        config.get('mission_arbitration_enabled', False),
        config.get('enable_meta_coordination', False),
        config.get('enable_fault_isolation', False),
    ]
    layer_depth = sum(1 for item in protocol_layers if item)
    normalized_depth = min(1.0, layer_depth / 8.0)

    proto_share = groups['proto_group_share']
    functional_share = groups['functional_group_share']
    anti_monolith = 1.0 - groups['largest_group_share']

    validation_coverage = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                schema['startup_readiness'],
                schema['safety_margin'],
                bias['validation'],
            ]
        )
    )
    traceability = clamp01(
        mittelwert(
            [
                normalized_depth,
                workflow.get('handoff_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                normalize(workflow.get('active_cells_mean', 0.0), 1.0, 4.0),
                normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0),
                bias['trace'],
            ]
        )
    )
    escalation_readiness = clamp01(
        mittelwert(
            [
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                1.0 if config.get('mission_arbitration_enabled', False) else 0.0,
                1.0 if config.get('enable_meta_coordination', False) else 0.0,
                normalize(config.get('trust_shield_strength', 0.0), 0.22, 0.42),
                normalize(config.get('resync_strength', params['resync_strength']), 0.24, 0.54),
                bias['escalation'],
            ]
        )
    )
    stack_cohesion = clamp01(
        mittelwert(
            [
                result['cross_group_cooperation_rate'],
                workflow.get('resource_share_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                functional_share,
                anti_monolith,
                1.0 - groups['group_separation'],
            ]
        )
    )
    protocol_overhead = clamp01(
        mittelwert(
            [
                normalized_depth,
                normalize(config.get('cluster_budget_skew', 0.0), 0.16, 0.34),
                1.0 - normalize(config.get('mission_switch_interval', 4), 4.0, 10.0),
                1.0 - normalize(config.get('workflow_stage_min_tenure', 1), 1.0, 4.0),
                bias['overhead'],
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
        'active_cells_mean': workflow.get('active_cells_mean', 0.0),
        'bottleneck_relief_rate': workflow.get('bottleneck_relief_rate', 0.0),
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'mission_arbitrations': float(result.get('mission_arbitration_total', 0.0)),
        'arbitration_gain': float(result.get('mission_arbitration_mean_gain', 0.0)),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'proto_group_share': proto_share,
        'functional_group_share': functional_share,
        'validation_coverage': validation_coverage,
        'traceability': traceability,
        'escalation_readiness': escalation_readiness,
        'stack_cohesion': stack_cohesion,
        'protocol_overhead': protocol_overhead,
        'layer_depth': normalized_depth,
    }


def run_context(seed, params, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(eintrag['config'])
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
        config['mission_switch_interval'] = min(4, int(config.get('mission_switch_interval', 4)))
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
    result['protocol_metrics'] = protocol_stack_metrics(config, result, params, eintrag['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['protocol_metrics']
    base = metrics['consensus'] - metrics['polarization']
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['validation_coverage']
            + 0.14 * metrics['traceability']
            + 0.12 * metrics['stack_cohesion']
            + 0.10 * metrics['functional_group_share']
            + 0.10 * metrics['escalation_readiness']
            - 0.12 * metrics['protocol_overhead']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.12 * metrics['traceability']
            + 0.12 * metrics['stack_cohesion']
            + 0.10 * metrics['resource_efficiency']
            + 0.08 * metrics['handoff_rate']
            - 0.08 * metrics['protocol_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['detection_rate']
            + 0.12 * metrics['escalation_readiness']
            + 0.10 * metrics['validation_coverage']
            + 0.08 * metrics['traceability']
            + 0.08 * metrics['mission_success']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['protocol_overhead']
        )
    return (
        base
        + 0.18 * metrics['sync_strength_mean']
        + 0.16 * recoveries
        + 0.12 * metrics['escalation_readiness']
        + 0.10 * metrics['traceability']
        + 0.08 * metrics['stack_cohesion']
        - 0.12 * failed_share
        - 0.10 * metrics['cluster_compromise_mean']
        - 0.08 * metrics['protocol_overhead']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'traceability': {},
        'validation_coverage': {},
        'escalation_readiness': {},
        'stack_cohesion': {},
        'protocol_overhead': {},
        'handoff_rate': {},
        'detection_rate': {},
        'sync_strength_mean': {},
        'functional_group_share': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['protocol_metrics'][metric_name] for run in runs])

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
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
    eintraege = protocol_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI PROTOKOLLSTACK-STUDIE')
    print('=' * 84)
    print('Vergleicht Kommunikations- und Entscheidungsprotokolle zwischen Gruppen')
    print('und misst, welche Schichtung Robustheit, Nachvollziehbarkeit und Skalierung vereint.\n')

    summaries = []
    for profil_index, eintrag in enumerate(eintraege):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + profil_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                run[kontext['name']] = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    eintrag,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, eintrag, context_list, params['agent_count'])
        summaries.append(summary)
        print(
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"Trace={summary['traceability']['startup']:.2f} | "
            f"Validierung={summary['validation_coverage']['startup']:.2f} | "
            f"Overhead={summary['protocol_overhead']['startup']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'direktprotokoll')

    print('\nBester Protokollstack:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum Direktprotokoll {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Traceability {best['traceability']['startup']:.2f}, "
        f"Validierung {best['validation_coverage']['startup']:.2f}, "
        f"Overhead {best['protocol_overhead']['startup']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Protokollstack-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['traceability']['startup'] for item in summaries],
        width,
        label='Traceability',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['validation_coverage']['startup'] for item in summaries],
        width,
        label='Validierung',
        color='#59a14f',
    )
    axes[0, 1].set_title('Protokollklarheit')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['stack_cohesion']['consensus'] for item in summaries],
        width,
        label='Stack-Kohäsion',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['protocol_overhead']['startup'] for item in summaries],
        width,
        label='Overhead',
        color='#e15759',
    )
    axes[0, 2].set_title('Nutzen vs. Overhead')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['startup'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['escalation_readiness']['recovery'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Start', 'Kon', 'Stress', 'Rec', 'Esc'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['handoff_rate']['consensus'] * 100.0 for item in summaries],
        width,
        label='Handoffs (%)',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['detection_rate']['stress'] * 100.0 for item in summaries],
        width,
        label='Detektion (%)',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Kommunikation und Abwehr')
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
            f"- Delta zum Direktprotokoll: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Traceability: {best['traceability']['startup']:.2f}\n"
            f"- Validierung: {best['validation_coverage']['startup']:.2f}\n"
            f"- Eskalation: {best['escalation_readiness']['recovery']:.2f}\n"
            f"- Stack-Kohäsion: {best['stack_cohesion']['consensus']:.2f}\n"
            f"- Recovery-Sync: {best['sync_strength_mean']['recovery']:.2f}\n"
            f"- Overhead: {best['protocol_overhead']['startup']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_protokollstack.png', dpi=150)


if __name__ == '__main__':
    main()
