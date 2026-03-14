"""
KKI Faehigkeitsarbitrations-Studie
==================================
Vergleicht, wie konkurrierende Talentgruppen mit unterschiedlichen Missionen,
Budgets und Prioritaeten gemeinsam koordiniert werden koennen, ohne in
Konflikte oder Dominanz einzelner Spezialgruppen abzugleiten.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_gruppenidentitaet import kontexte, modellkatalog, mittelwert
from schwarm_gruppentalente import build_profile as build_talent_profile
from schwarm_gruppentalente import talent_profile
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
        repetitions = int(os.getenv('KKI_CAPABILITY_ARBITRATION_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_CAPABILITY_ARBITRATION_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_CAPABILITY_ARBITRATION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_CAPABILITY_ARBITRATION_STRESS_STRENGTH', '0.44')),
        'stress_sources': int(os.getenv('KKI_CAPABILITY_ARBITRATION_STRESS_SOURCES', '6')),
    }


def talent_lookup():
    return {item['name']: item for item in talent_profile()}


def arbitration_profiles(katalog):
    talents = talent_lookup()
    shared = build_talent_profile(katalog, talents['shared-dna'])
    protection = build_talent_profile(katalog, talents['schutz-fokus'])
    coordination = build_talent_profile(katalog, talents['koordinations-fokus'])
    regeneration = build_talent_profile(katalog, talents['regeneration-fokus'])

    common = {
        'enable_missions': True,
        'mission_switch_interval': int(os.getenv('KKI_MISSION_SWITCH_INTERVAL', '20')),
        'enable_role_switching': True,
        'role_switch_interval': int(os.getenv('KKI_ROLE_SWITCH_INTERVAL', '20')),
        'role_switch_min_tenure': int(os.getenv('KKI_ROLE_SWITCH_MIN_TENURE', '20')),
        'role_switch_reputation_cost': float(os.getenv('KKI_ROLE_SWITCH_REPUTATION_COST', '0.02')),
        'enable_workflow_stages': True,
        'workflow_stage_min_tenure': int(os.getenv('KKI_WORKFLOW_STAGE_MIN_TENURE', '2')),
        'enable_workflow_cells': True,
        'enable_handoff_coordination': True,
        'handoff_priority_bonus': float(os.getenv('KKI_HANDOFF_PRIORITY_BONUS', '0.16')),
        'enable_parallel_workflow_cells': True,
        'enable_resource_coordination': True,
        'resource_budget': float(os.getenv('KKI_CAPABILITY_ARBITRATION_RESOURCE_BUDGET', '0.62')),
        'resource_share_factor': float(os.getenv('KKI_RESOURCE_SHARE_FACTOR', '0.24')),
        'enable_capability_clusters': True,
        'enable_asymmetric_cluster_budgets': True,
        'enable_bottleneck_management': True,
    }

    return [
        {
            'name': 'shared-dna',
            'label': 'Gemeinsame DNA',
            'config': {
                **shared,
                'enable_missions': False,
                'enable_workflow_cells': False,
                'enable_handoff_coordination': False,
                'enable_parallel_workflow_cells': False,
                'enable_resource_coordination': False,
                'enable_capability_clusters': False,
                'enable_asymmetric_cluster_budgets': False,
                'enable_bottleneck_management': False,
                'enable_meta_coordination': False,
            },
        },
        {
            'name': 'talent-konflikte',
            'label': 'Talent-Konflikte',
            'config': {
                **protection,
                **common,
                'mission_assignment': 'adaptive',
                'mission_arbitration_enabled': False,
                'mission_conflict_threshold': 0.42,
                'enable_meta_coordination': False,
                'cluster_budget_skew': protection.get('cluster_budget_skew', 0.0) + 0.12,
            },
        },
        {
            'name': 'missions-arbitration',
            'label': 'Missions-Arbitration',
            'config': {
                **protection,
                **common,
                'mission_assignment': 'arbitrated',
                'mission_arbitration_enabled': True,
                'mission_conflict_threshold': 0.46,
                'mission_arbitration_margin': float(os.getenv('KKI_MISSION_ARBITRATION_MARGIN', '0.08')),
                'enable_meta_coordination': False,
                'cluster_budget_skew': protection.get('cluster_budget_skew', 0.0) + 0.08,
            },
        },
        {
            'name': 'budget-arbitration',
            'label': 'Budget-Arbitration',
            'config': {
                **regeneration,
                **common,
                'mission_assignment': 'arbitrated',
                'mission_arbitration_enabled': True,
                'mission_conflict_threshold': 0.45,
                'mission_arbitration_margin': float(os.getenv('KKI_MISSION_ARBITRATION_MARGIN', '0.08')) + 0.02,
                'enable_meta_coordination': False,
                'cluster_budget_skew': regeneration.get('cluster_budget_skew', 0.0) + 0.10,
                'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')) + 0.06,
            },
        },
        {
            'name': 'meta-arbitration',
            'label': 'Meta-Arbitration',
            'config': {
                **coordination,
                **common,
                'mission_assignment': 'arbitrated',
                'mission_arbitration_enabled': True,
                'mission_conflict_threshold': 0.44,
                'mission_arbitration_margin': float(os.getenv('KKI_MISSION_ARBITRATION_MARGIN', '0.08')) + 0.03,
                'enable_meta_coordination': True,
                'meta_update_interval': int(os.getenv('KKI_META_UPDATE_INTERVAL', '6')),
                'meta_priority_strength': coordination.get('meta_priority_strength', 0.0) + 0.08,
                'resource_budget': float(os.getenv('KKI_CAPABILITY_ARBITRATION_RESOURCE_BUDGET', '0.62')) + 0.02,
                'cluster_budget_skew': max(0.18, coordination.get('cluster_budget_skew', 0.55) - 0.06),
            },
        },
        {
            'name': 'gekoppelte-arbitration',
            'label': 'Gekoppelte Arbitration',
            'config': {
                **coordination,
                **common,
                'mission_assignment': 'arbitrated',
                'mission_arbitration_enabled': True,
                'mission_conflict_threshold': 0.43,
                'mission_arbitration_margin': float(os.getenv('KKI_MISSION_ARBITRATION_MARGIN', '0.08')) + 0.04,
                'enable_meta_coordination': True,
                'meta_update_interval': int(os.getenv('KKI_META_UPDATE_INTERVAL', '6')),
                'meta_priority_strength': coordination.get('meta_priority_strength', 0.0) + 0.10,
                'group_learning_rate': coordination.get('group_learning_rate', 0.0) + 0.02,
                'resource_budget': float(os.getenv('KKI_CAPABILITY_ARBITRATION_RESOURCE_BUDGET', '0.62')) + 0.04,
                'resource_share_factor': float(os.getenv('KKI_RESOURCE_SHARE_FACTOR', '0.24')) + 0.03,
                'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')) + 0.08,
                'cluster_budget_skew': max(0.16, coordination.get('cluster_budget_skew', 0.55) - 0.08),
            },
        },
    ]


def arbitration_metrics(result):
    workflow = result['workflow_metrics']
    mission_conflicts = float(result.get('mission_conflict_total', 0.0))
    mission_arbitrations = float(result.get('mission_arbitration_total', 0.0))
    arbitration_activity = min(1.0, mission_arbitrations / 60.0)
    conflict_pressure = min(1.0, mission_conflicts / 60.0)
    resolution_balance = (
        max(0.0, 1.0 - abs(arbitration_activity - conflict_pressure))
        if mission_conflicts > 0.0 or mission_arbitrations > 0.0
        else 0.0
    )
    coordination_reserve = mittelwert(
        [
            min(1.0, workflow.get('resource_efficiency', 0.0)),
            min(1.0, workflow.get('bottleneck_relief_rate', 0.0)),
            min(1.0, workflow.get('meta_alignment_rate', 0.0)),
            min(1.0, float(result.get('mission_switch_stability', 0.0))),
        ]
    )
    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'bottleneck_relief_rate': workflow.get('bottleneck_relief_rate', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'stress_integrity': max(0.0, 1.0 - workflow.get('misinformation_corruption_mean', 0.0)),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'mission_conflicts': mission_conflicts,
        'mission_arbitrations': mission_arbitrations,
        'arbitration_gain': float(result.get('mission_arbitration_mean_gain', 0.0)),
        'switch_stability': float(result.get('mission_switch_stability', 0.0)),
        'resolution_balance': resolution_balance,
        'coordination_reserve': coordination_reserve,
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
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

    if kontext['enable_prompt_injection']:
        config['enable_prompt_injection'] = True
        config['injection_attack_round'] = params['attack_round']
        config['injection_strength'] = params['stress_strength']
        config['injection_source_count'] = params['stress_sources']
    else:
        config['enable_prompt_injection'] = False

    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    result['arbitration_metrics'] = arbitration_metrics(result)
    return result


def context_score(kontext_name, result):
    metrics = result['arbitration_metrics']
    base = metrics['consensus'] - metrics['polarization']
    arbitration_activity = min(1.0, metrics['mission_arbitrations'] / 40.0)
    conflict_pressure = min(1.0, metrics['mission_conflicts'] / 60.0)
    if kontext_name == 'polarization':
        return (
            base
            + 0.16 * metrics['mission_success']
            + 0.12 * metrics['cross_group_cooperation']
            + 0.10 * metrics['skill_alignment_rate']
            + 0.10 * metrics['switch_stability']
            + 0.10 * arbitration_activity
            + 0.08 * metrics['arbitration_gain']
            - 0.06 * conflict_pressure
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.12 * metrics['meta_alignment_rate']
            + 0.12 * arbitration_activity
            + 0.12 * metrics['arbitration_gain']
            + 0.08 * metrics['resource_efficiency']
        )
    return (
        base
        + 0.14 * metrics['detection_rate']
        + 0.10 * metrics['resource_share_rate']
        + 0.10 * metrics['bottleneck_relief_rate']
        + 0.08 * metrics['meta_alignment_rate']
        + 0.08 * arbitration_activity
        - 0.12 * metrics['corruption_mean']
    )


def summarize_runs(runs, eintrag, context_list):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'resource_efficiency': {},
        'bottleneck_relief_rate': {},
        'meta_alignment_rate': {},
        'handoff_rate': {},
        'resource_share_rate': {},
        'skill_alignment_rate': {},
        'detection_rate': {},
        'corruption_mean': {},
        'cross_group_cooperation': {},
        'mission_success': {},
        'mission_conflicts': {},
        'mission_arbitrations': {},
        'arbitration_gain': {},
        'switch_stability': {},
        'stress_integrity': {},
        'resolution_balance': {},
        'coordination_reserve': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name]) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['arbitration_metrics'][metric_name] for run in runs])

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']]) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        **metrics,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    eintraege = arbitration_profiles(katalog)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI FAEHIGKEITSARBITRATIONS-STUDIE')
    print('=' * 84)
    print('Vergleicht konkurrierende Talentgruppen unter Missionen, Budgets und')
    print('Meta-Prioritaeten und misst, welche Arbitration Konflikte am besten befriedet.\n')

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

        summary = summarize_runs(runs, eintrag, context_list)
        summaries.append(summary)
        print(
            f"{summary['label']:<26} Score={summary['combined_score']:+.3f} | "
            f"Mission={summary['mission_success']['polarization']:.1%} | "
            f"Arb={summary['mission_arbitrations']['consensus']:.1f} | "
            f"Balance={summary['resolution_balance']['consensus']:.1%} | "
            f"Reserve={summary['coordination_reserve']['stress']:.1%}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'shared-dna')
    print('\nBeste Faehigkeitsarbitration:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur gemeinsamen DNA {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Missionserfolg {best['mission_success']['polarization']:.1%}, "
        f"Balance {best['resolution_balance']['consensus']:.1%}, "
        f"Reserve {best['coordination_reserve']['stress']:.1%}, "
        f"Arbitrationsgewinn {best['arbitration_gain']['consensus']:.3f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#4e79a7', '#9c755f', '#e15759', '#f28e2b', '#76b7b2', '#59a14f']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Arbitration-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['mission_success']['polarization'] * 100.0 for item in summaries],
        width,
        label='Missionserfolg',
        color='#59a14f',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['mission_conflicts']['polarization'] for item in summaries],
        width,
        label='Konflikte',
        color='#e15759',
    )
    axes[0, 1].set_title('Konfliktlage')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['mission_arbitrations']['consensus'] for item in summaries],
        width,
        label='Arbitrierungen',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['arbitration_gain']['consensus'] for item in summaries],
        width,
        label='Gewinn',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Arbitrationseffekt')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['polarization'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
                item['resolution_balance']['consensus'],
                item['coordination_reserve']['stress'],
                item['stress_integrity']['stress'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4, 5])
    axes[1, 0].set_xticklabels(['Pol', 'Kon', 'Stress', 'Balance', 'Reserve', 'Int'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['resolution_balance']['consensus'] * 100.0 for item in summaries],
        width,
        label='Balance (%)',
        color='#4e79a7',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['coordination_reserve']['stress'] * 100.0 for item in summaries],
        width,
        label='Reserve (%)',
        color='#9c755f',
    )
    axes[1, 1].set_title('Arbitrationsstabilitaet')
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
            f"- Delta zur gemeinsamen DNA: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Missionserfolg: {best['mission_success']['polarization']:.1%}\n"
            f"- Konflikte: {best['mission_conflicts']['polarization']:.1f}\n"
            f"- Arbitrierungen: {best['mission_arbitrations']['consensus']:.1f}\n"
            f"- Arbitrationsgewinn: {best['arbitration_gain']['consensus']:.3f}\n"
            f"- Balance: {best['resolution_balance']['consensus']:.1%}\n"
            f"- Reserve: {best['coordination_reserve']['stress']:.1%}\n"
            f"- Stress-Integritaet: {best['stress_integrity']['stress']:.1%}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_faehigkeitsarbitration.png', dpi=150)


if __name__ == '__main__':
    main()
