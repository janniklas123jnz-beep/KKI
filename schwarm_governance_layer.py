"""
KKI Governance-Layer-Studie
===========================
Vergleicht Governance-, Policy- und Freigabelayer fuer die Bauphase und misst,
welche Schicht Erweiterbarkeit absichert, Dominanz begrenzt und Manipulation
abwehrt, ohne den Gruppenfluss zu stark zu bremsen.
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
from schwarm_gruppenrobustheit import robustness_profiles
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
        repetitions = int(os.getenv('KKI_GOVERNANCE_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_GOVERNANCE_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_GOVERNANCE_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_GOVERNANCE_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_GOVERNANCE_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_GOVERNANCE_FAILURE_FRACTION', '0.18')),
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
        {'name': 'extension', 'label': 'Erweiterung', 'scenario': 'consensus'},
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


def governance_profiles(katalog, params):
    contract = get_named(contract_profiles(katalog, params), 'resilienter-handoff-vertrag')['config']
    protocol = get_named(protocol_profiles(katalog, params), 'resilienter-protokollstack')['config']
    robust = get_named(robustness_profiles(katalog), 'robuste-balance')['config']

    return [
        {
            'name': 'freier-ausbau',
            'label': 'Freier Ausbau',
            'config': {
                **contract,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'meta_update_interval': 8,
                'mission_switch_interval': 6,
                'resource_share_factor': 0.20,
                'cluster_budget_skew': 0.32,
                'trust_shield_strength': 0.18,
                'failure_fraction': min(0.24, params['failure_fraction'] + 0.03),
            },
            'bias': {
                'policy': 0.18,
                'approval': 0.24,
                'dominance': 0.16,
                'extension': 0.34,
                'resilience': 0.22,
                'friction': 0.10,
            },
        },
        {
            'name': 'policy-gates',
            'label': 'Policy-Gates',
            'config': {
                **contract,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'meta_update_interval': 6,
                'meta_priority_strength': 0.34,
                'resource_share_factor': 0.24,
                'cluster_budget_skew': 0.26,
                'trust_shield_strength': 0.26,
            },
            'bias': {
                'policy': 0.54,
                'approval': 0.48,
                'dominance': 0.42,
                'extension': 0.52,
                'resilience': 0.38,
                'friction': 0.20,
            },
        },
        {
            'name': 'freigabe-board',
            'label': 'Freigabe-Board',
            'config': {
                **contract,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'meta_update_interval': 5,
                'meta_priority_strength': 0.38,
                'handoff_priority_bonus': 0.19,
                'resource_share_factor': 0.27,
                'cluster_budget_skew': 0.22,
                'trust_shield_strength': 0.30,
            },
            'bias': {
                'policy': 0.72,
                'approval': 0.74,
                'dominance': 0.62,
                'extension': 0.66,
                'resilience': 0.56,
                'friction': 0.26,
            },
        },
        {
            'name': 'sicherheitsrat',
            'label': 'Sicherheitsrat',
            'config': {
                **protocol,
                **robust,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'meta_priority_strength': 0.40,
                'resource_share_factor': 0.28,
                'cluster_budget_skew': 0.20,
                'quarantine_compromise_threshold': 0.23,
                'quarantine_exposure_threshold': 0.29,
                'trust_shield_strength': 0.36,
            },
            'bias': {
                'policy': 0.84,
                'approval': 0.72,
                'dominance': 0.84,
                'extension': 0.68,
                'resilience': 0.78,
                'friction': 0.32,
            },
        },
        {
            'name': 'foederierte-governance',
            'label': 'Foederierte Governance',
            'config': {
                **protocol,
                **contract,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'meta_priority_strength': 0.40,
                'resource_budget': 0.79,
                'resource_share_factor': 0.29,
                'cluster_budget_skew': 0.18,
                'trust_shield_strength': 0.38,
                'resync_strength': min(0.54, contract.get('resync_strength', params['resync_strength']) + 0.04),
            },
            'bias': {
                'policy': 0.88,
                'approval': 0.86,
                'dominance': 0.82,
                'extension': 0.84,
                'resilience': 0.82,
                'friction': 0.30,
            },
        },
        {
            'name': 'resilienter-governance-layer',
            'label': 'Resilienter Governance-Layer',
            'config': {
                **protocol,
                **contract,
                **robust,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'meta_update_interval': 4,
                'meta_priority_strength': 0.42,
                'handoff_priority_bonus': 0.20,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'cluster_budget_skew': 0.16,
                'quarantine_compromise_threshold': 0.22,
                'quarantine_exposure_threshold': 0.28,
                'trust_shield_strength': 0.40,
                'resync_strength': min(0.54, contract.get('resync_strength', params['resync_strength']) + 0.06),
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.05),
            },
            'bias': {
                'policy': 0.94,
                'approval': 0.90,
                'dominance': 0.92,
                'extension': 0.90,
                'resilience': 0.92,
                'friction': 0.28,
            },
        },
    ]


def governance_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)

    arbitration_activity = normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0)
    failed_share = workflow.get('failed_agents_mean', 0.0) / max(1.0, params['agent_count'])
    recovery_share = normalize(workflow.get('recovery_events_total', 0.0), 0.0, params['agent_count'] * 0.16)
    quarantine_share = normalize(workflow.get('quarantined_agents_mean', 0.0), 0.0, params['agent_count'] * 0.14)

    policy_coverage = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                schema['safety_margin'],
                1.0 if config.get('enable_meta_coordination', False) else 0.0,
                1.0 if config.get('mission_arbitration_enabled', False) else 0.0,
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                normalize(config.get('trust_shield_strength', 0.0), 0.18, 0.42),
                bias['policy'],
            ]
        )
    )
    approval_quality = clamp01(
        mittelwert(
            [
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('completion_rate', 0.0),
                mittelwert(list(result.get('mission_success_rates', {}).values())),
                bias['approval'],
            ]
        )
    )
    dominance_control = clamp01(
        mittelwert(
            [
                1.0 - normalize(config.get('cluster_budget_skew', 0.0), 0.16, 0.34),
                1.0 - groups['largest_group_share'],
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                bias['dominance'],
            ]
        )
    )
    extension_safety = clamp01(
        mittelwert(
            [
                schema['extensibility'],
                schema['safety_margin'],
                workflow.get('resource_efficiency', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                groups['functional_group_share'],
                1.0 - groups['group_separation'],
                bias['extension'],
            ]
        )
    )
    governance_resilience = clamp01(
        mittelwert(
            [
                workflow.get('sync_strength_mean', 0.0),
                recovery_share,
                1.0 - failed_share,
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                bias['resilience'],
            ]
        )
    )
    governance_friction = clamp01(
        mittelwert(
            [
                1.0 - normalize(config.get('meta_update_interval', 4), 4.0, 8.0),
                1.0 - normalize(config.get('mission_switch_interval', 4), 4.0, 8.0),
                arbitration_activity,
                quarantine_share,
                bias['friction'],
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
        'quarantined_agents_mean': workflow.get('quarantined_agents_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'functional_group_share': groups['functional_group_share'],
        'policy_coverage': policy_coverage,
        'approval_quality': approval_quality,
        'dominance_control': dominance_control,
        'extension_safety': extension_safety,
        'governance_resilience': governance_resilience,
        'governance_friction': governance_friction,
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
    result['governance_metrics'] = governance_metrics(config, result, params, eintrag['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['governance_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['policy_coverage']
            + 0.14 * metrics['approval_quality']
            + 0.12 * metrics['extension_safety']
            + 0.10 * metrics['dominance_control']
            - 0.12 * metrics['governance_friction']
        )
    if kontext_name == 'extension':
        return (
            metrics['completion_rate']
            + 0.14 * metrics['resource_efficiency']
            + 0.16 * metrics['extension_safety']
            + 0.14 * metrics['approval_quality']
            + 0.12 * metrics['dominance_control']
            + 0.08 * metrics['functional_group_share']
            - 0.10 * metrics['governance_friction']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['detection_rate']
            + 0.16 * metrics['dominance_control']
            + 0.12 * metrics['policy_coverage']
            + 0.10 * metrics['governance_resilience']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['governance_friction']
        )
    return (
        base
        + 0.18 * metrics['governance_resilience']
        + 0.12 * recoveries
        + 0.12 * metrics['extension_safety']
        + 0.10 * metrics['approval_quality']
        + 0.08 * metrics['dominance_control']
        - 0.12 * failed_share
        - 0.08 * metrics['cluster_compromise_mean']
        - 0.08 * metrics['governance_friction']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'policy_coverage': {},
        'approval_quality': {},
        'dominance_control': {},
        'extension_safety': {},
        'governance_resilience': {},
        'governance_friction': {},
        'detection_rate': {},
        'quarantined_agents_mean': {},
        'trust_shield_mean': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['governance_metrics'][metric_name] for run in runs])

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
    eintraege = governance_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI GOVERNANCE-LAYER-STUDIE')
    print('=' * 84)
    print('Vergleicht Freigabe-, Policy- und Sicherheitslayer fuer die Bauphase,')
    print('damit Erweiterbarkeit nicht zur Angriffs- oder Dominanzflaeche wird.\n')

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
            f"Policy={summary['policy_coverage']['startup']:.2f} | "
            f"Dominanz={summary['dominance_control']['stress']:.2f} | "
            f"Friktion={summary['governance_friction']['startup']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'freier-ausbau')

    print('\nBester Governance-Layer:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum freien Ausbau {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Policy {best['policy_coverage']['startup']:.2f}, "
        f"Dominanzkontrolle {best['dominance_control']['stress']:.2f}, "
        f"Resilienz {best['governance_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Governance-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['policy_coverage']['startup'] for item in summaries],
        width,
        label='Policy',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['approval_quality']['extension'] for item in summaries],
        width,
        label='Freigabe',
        color='#59a14f',
    )
    axes[0, 1].set_title('Policy und Freigabe')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['dominance_control']['stress'] for item in summaries],
        width,
        label='Dominanzkontrolle',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['governance_friction']['startup'] for item in summaries],
        width,
        label='Friktion',
        color='#e15759',
    )
    axes[0, 2].set_title('Kontrolle vs. Friktion')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['startup'],
                item['context_scores']['extension'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['governance_resilience']['recovery'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Governance-Kontexte')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Start', 'Ext', 'Stress', 'Rec', 'Res'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['detection_rate']['stress'] * 100.0 for item in summaries],
        width,
        label='Detektion (%)',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['quarantined_agents_mean']['stress'] for item in summaries],
        width,
        label='Quarantaene',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Abwehrsignale')
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
            f"- Delta zum freien Ausbau: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Policy: {best['policy_coverage']['startup']:.2f}\n"
            f"- Freigabe: {best['approval_quality']['extension']:.2f}\n"
            f"- Dominanzkontrolle: {best['dominance_control']['stress']:.2f}\n"
            f"- Erweiterungssicherheit: {best['extension_safety']['extension']:.2f}\n"
            f"- Resilienz: {best['governance_resilience']['recovery']:.2f}\n"
            f"- Friktion: {best['governance_friction']['startup']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_governance_layer.png', dpi=150)


if __name__ == '__main__':
    main()
