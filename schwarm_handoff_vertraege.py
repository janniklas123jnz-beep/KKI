"""
KKI Handoff-Vertrags-Studie
===========================
Vergleicht formalisierte Uebergabevertraege zwischen Gruppen und misst, welche
Kombination aus Validierung, Quittierung, Eskalation und Recovery Handoffs
sicher macht, ohne die Arbeitsfluesse zu blockieren.
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
from schwarm_gruppenhandoff import handoff_profiles
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
        repetitions = int(os.getenv('KKI_HANDOFF_CONTRACT_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_HANDOFF_CONTRACT_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_HANDOFF_CONTRACT_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_HANDOFF_CONTRACT_STRESS_STRENGTH', '0.46')),
        'stress_sources': int(os.getenv('KKI_HANDOFF_CONTRACT_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_HANDOFF_CONTRACT_FAILURE_FRACTION', '0.18')),
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


def contract_profiles(katalog, params):
    protocol = get_named(protocol_profiles(katalog, params), 'resilienter-protokollstack')['config']
    handoff = get_named(handoff_profiles(katalog), 'parallele-resiliente-handoffs')['config']

    return [
        {
            'name': 'offene-uebergabe',
            'label': 'Offene Uebergabe',
            'config': {
                **handoff,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'workflow_stage_min_tenure': 1,
                'mission_switch_interval': 6,
            },
            'bias': {'validation': 0.18, 'receipt': 0.14, 'escalation': 0.10, 'rollback': 0.16, 'overhead': 0.08},
        },
        {
            'name': 'quittierte-uebergabe',
            'label': 'Quittierte Uebergabe',
            'config': {
                **handoff,
                'enable_meta_coordination': True,
                'meta_update_interval': 5,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'handoff_priority_bonus': 0.18,
                'resource_share_factor': min(0.30, handoff.get('resource_share_factor', 0.24) + 0.02),
            },
            'bias': {'validation': 0.44, 'receipt': 0.70, 'escalation': 0.28, 'rollback': 0.36, 'overhead': 0.18},
        },
        {
            'name': 'validierter-vertrag',
            'label': 'Validierter Vertrag',
            'config': {
                **protocol,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'trust_shield_strength': min(0.42, protocol.get('trust_shield_strength', 0.38) + 0.01),
                'handoff_priority_bonus': 0.19,
            },
            'bias': {'validation': 0.86, 'receipt': 0.84, 'escalation': 0.62, 'rollback': 0.58, 'overhead': 0.26},
        },
        {
            'name': 'eskalationsvertrag',
            'label': 'Eskalationsvertrag',
            'config': {
                **protocol,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'meta_update_interval': 4,
                'trust_shield_strength': min(0.42, protocol.get('trust_shield_strength', 0.38) + 0.03),
                'resync_strength': min(0.54, protocol.get('resync_strength', params['resync_strength']) + 0.04),
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.02),
            },
            'bias': {'validation': 0.88, 'receipt': 0.82, 'escalation': 0.90, 'rollback': 0.74, 'overhead': 0.30},
        },
        {
            'name': 'vertragskette',
            'label': 'Vertragskette',
            'config': {
                **protocol,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'enable_meta_coordination': True,
                'meta_update_interval': 4,
                'resource_share_factor': min(0.30, protocol.get('resource_share_factor', 0.28) + 0.01),
                'mission_switch_interval': 4,
                'workflow_stage_min_tenure': 1,
                'trust_shield_strength': min(0.42, protocol.get('trust_shield_strength', 0.38) + 0.02),
            },
            'bias': {'validation': 0.90, 'receipt': 0.90, 'escalation': 0.84, 'rollback': 0.70, 'overhead': 0.34},
        },
        {
            'name': 'resilienter-handoff-vertrag',
            'label': 'Resilienter Handoff-Vertrag',
            'config': {
                **protocol,
                'enable_fault_isolation': True,
                'mission_arbitration_enabled': True,
                'enable_meta_coordination': True,
                'meta_update_interval': 4,
                'resource_budget': min(0.80, protocol.get('resource_budget', 0.78) + 0.01),
                'resource_share_factor': min(0.30, protocol.get('resource_share_factor', 0.28) + 0.01),
                'handoff_priority_bonus': 0.20,
                'trust_shield_strength': min(0.42, protocol.get('trust_shield_strength', 0.40) + 0.02),
                'resync_strength': min(0.54, protocol.get('resync_strength', params['resync_strength']) + 0.06),
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
            },
            'bias': {'validation': 0.94, 'receipt': 0.92, 'escalation': 0.94, 'rollback': 0.88, 'overhead': 0.30},
        },
    ]


def contract_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)

    handoff_rate = workflow.get('handoff_rate', 0.0)
    handoff_total = float(workflow.get('handoff_total', 0.0))
    arbitration_activity = normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0)

    validation_strength = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                schema['safety_margin'],
                normalize(config.get('trust_shield_strength', 0.0), 0.22, 0.42),
                bias['validation'],
            ]
        )
    )
    receipt_reliability = clamp01(
        mittelwert(
            [
                handoff_rate,
                normalize(handoff_total, 0.0, 60.0),
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                bias['receipt'],
            ]
        )
    )
    escalation_strength = clamp01(
        mittelwert(
            [
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                1.0 if config.get('mission_arbitration_enabled', False) else 0.0,
                1.0 if config.get('enable_meta_coordination', False) else 0.0,
                arbitration_activity,
                normalize(config.get('resync_strength', params['resync_strength']), 0.24, 0.54),
                bias['escalation'],
            ]
        )
    )
    rollback_safety = clamp01(
        mittelwert(
            [
                normalize(config.get('resync_strength', params['resync_strength']), 0.24, 0.54),
                1.0 - normalize(config.get('failure_fraction', params['failure_fraction']), 0.10, 0.26),
                workflow.get('sync_strength_mean', 0.0),
                schema['safety_margin'],
                bias['rollback'],
            ]
        )
    )
    contract_flow = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                groups['functional_group_share'],
                1.0 - groups['group_separation'],
            ]
        )
    )
    contract_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('mission_switch_interval', 4), 4.0, 8.0),
                normalize(config.get('workflow_stage_min_tenure', 1), 1.0, 3.0),
                normalize(config.get('cluster_budget_skew', 0.0), 0.16, 0.34),
                arbitration_activity,
                bias['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'handoff_rate': handoff_rate,
        'handoff_total': handoff_total,
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
        'validation_strength': validation_strength,
        'receipt_reliability': receipt_reliability,
        'escalation_strength': escalation_strength,
        'rollback_safety': rollback_safety,
        'contract_flow': contract_flow,
        'contract_overhead': contract_overhead,
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
    result['contract_metrics'] = contract_metrics(config, result, params, eintrag['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['contract_metrics']
    base = metrics['consensus'] - metrics['polarization']
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['validation_strength']
            + 0.14 * metrics['receipt_reliability']
            + 0.12 * metrics['contract_flow']
            + 0.10 * metrics['functional_group_share']
            + 0.10 * metrics['rollback_safety']
            - 0.10 * metrics['contract_overhead']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.12 * metrics['contract_flow']
            + 0.10 * metrics['receipt_reliability']
            + 0.10 * metrics['handoff_rate']
            + 0.08 * metrics['validation_strength']
            - 0.08 * metrics['contract_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['detection_rate']
            + 0.12 * metrics['escalation_strength']
            + 0.10 * metrics['validation_strength']
            + 0.08 * metrics['rollback_safety']
            + 0.08 * metrics['receipt_reliability']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['contract_overhead']
        )
    return (
        base
        + 0.18 * metrics['sync_strength_mean']
        + 0.16 * recoveries
        + 0.12 * metrics['rollback_safety']
        + 0.10 * metrics['escalation_strength']
        + 0.08 * metrics['receipt_reliability']
        - 0.12 * failed_share
        - 0.10 * metrics['cluster_compromise_mean']
        - 0.08 * metrics['contract_overhead']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'validation_strength': {},
        'receipt_reliability': {},
        'escalation_strength': {},
        'rollback_safety': {},
        'contract_flow': {},
        'contract_overhead': {},
        'handoff_rate': {},
        'detection_rate': {},
        'sync_strength_mean': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['contract_metrics'][metric_name] for run in runs])

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
    eintraege = contract_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI HANDOFF-VERTRAGS-STUDIE')
    print('=' * 84)
    print('Vergleicht Handoff-Vertraege mit Validierung, Quittierung, Eskalation')
    print('und Recovery, um sichere Gruppenuebergaben in der Bauphase vorzubereiten.\n')

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
            f"Validierung={summary['validation_strength']['startup']:.2f} | "
            f"Quittung={summary['receipt_reliability']['startup']:.2f} | "
            f"Overhead={summary['contract_overhead']['startup']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'offene-uebergabe')

    print('\nBester Handoff-Vertrag:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur offenen Uebergabe {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Validierung {best['validation_strength']['startup']:.2f}, "
        f"Quittung {best['receipt_reliability']['startup']:.2f}, "
        f"Rollback {best['rollback_safety']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Handoff-Vertrags-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['validation_strength']['startup'] for item in summaries],
        width,
        label='Validierung',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['receipt_reliability']['startup'] for item in summaries],
        width,
        label='Quittierung',
        color='#59a14f',
    )
    axes[0, 1].set_title('Vertragskonsistenz')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['rollback_safety']['recovery'] for item in summaries],
        width,
        label='Rollback',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['contract_overhead']['startup'] for item in summaries],
        width,
        label='Overhead',
        color='#e15759',
    )
    axes[0, 2].set_title('Sicherheit vs. Aufwand')
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
                item['escalation_strength']['recovery'],
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
    axes[1, 1].set_title('Uebergabe und Abwehr')
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
            f"- Delta zur offenen Uebergabe: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Validierung: {best['validation_strength']['startup']:.2f}\n"
            f"- Quittierung: {best['receipt_reliability']['startup']:.2f}\n"
            f"- Eskalation: {best['escalation_strength']['recovery']:.2f}\n"
            f"- Rollback: {best['rollback_safety']['recovery']:.2f}\n"
            f"- Vertragsfluss: {best['contract_flow']['consensus']:.2f}\n"
            f"- Overhead: {best['contract_overhead']['startup']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_handoff_vertraege.png', dpi=150)


if __name__ == '__main__':
    main()
