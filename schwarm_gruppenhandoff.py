"""
KKI Gruppenhandoff-Studie
=========================
Vergleicht gruppenuebergreifende Uebergabeprotokolle zwischen Talentgruppen
und misst, wie Informationen, Prioritaeten und Ressourcen uebergeben werden
muessen, damit Spezialisierung skalierbar bleibt.
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
        repetitions = int(os.getenv('KKI_GROUP_HANDOFF_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_GROUP_HANDOFF_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_GROUP_HANDOFF_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_GROUP_HANDOFF_STRESS_STRENGTH', '0.42')),
        'stress_sources': int(os.getenv('KKI_GROUP_HANDOFF_STRESS_SOURCES', '6')),
    }


def talent_lookup():
    return {item['name']: item for item in talent_profile()}


def handoff_profiles(katalog):
    talents = talent_lookup()
    shared = build_talent_profile(katalog, talents['shared-dna'])
    regeneration = build_talent_profile(katalog, talents['regeneration-fokus'])
    bridge = build_talent_profile(katalog, talents['bruecken-fokus'])
    coordination = build_talent_profile(katalog, talents['koordinations-fokus'])

    return [
        {
            'name': 'shared-dna',
            'label': 'Gemeinsame DNA',
            'config': {
                **shared,
                'enable_workflow_cells': False,
                'enable_handoff_coordination': False,
                'enable_parallel_workflow_cells': False,
                'enable_resource_coordination': False,
            },
        },
        {
            'name': 'talent-inseln',
            'label': 'Talent-Inseln',
            'config': {
                **regeneration,
                'enable_workflow_cells': True,
                'enable_handoff_coordination': False,
                'enable_parallel_workflow_cells': False,
                'enable_resource_coordination': False,
            },
        },
        {
            'name': 'sequenzielle-handoffs',
            'label': 'Sequenzielle Handoffs',
            'config': {
                **regeneration,
                'enable_workflow_cells': True,
                'enable_handoff_coordination': True,
                'handoff_priority_bonus': 0.16,
                'enable_parallel_workflow_cells': False,
                'enable_resource_coordination': False,
            },
        },
        {
            'name': 'vertrauens-handoffs',
            'label': 'Vertrauens-Handoffs',
            'config': {
                **bridge,
                'enable_workflow_cells': True,
                'enable_handoff_coordination': True,
                'handoff_priority_bonus': 0.18,
                'enable_parallel_workflow_cells': False,
                'enable_resource_coordination': False,
                'meta_priority_strength': bridge.get('meta_priority_strength', 0.0) + 0.03,
                'rewire_cross_group_bonus': bridge.get('rewire_cross_group_bonus', 0.0) + 0.05,
                'analyzer_memory_window': bridge.get('analyzer_memory_window', 18) + 6,
            },
        },
        {
            'name': 'parallele-resiliente-handoffs',
            'label': 'Resiliente Parallel-Handoffs',
            'config': {
                **coordination,
                'enable_workflow_cells': True,
                'enable_handoff_coordination': True,
                'handoff_priority_bonus': 0.18,
                'enable_parallel_workflow_cells': True,
                'enable_resource_coordination': True,
                'resource_budget': 0.62,
                'resource_share_factor': 0.24,
                'meta_priority_strength': coordination.get('meta_priority_strength', 0.0) + 0.04,
                'group_learning_rate': coordination.get('group_learning_rate', 0.0) + 0.02,
                'rewire_cross_group_bonus': coordination.get('rewire_cross_group_bonus', 0.0) + 0.04,
            },
        },
    ]


def handoff_metrics(result):
    workflow = result['workflow_metrics']
    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'handoff_total': workflow.get('handoff_total', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'active_cells_mean': workflow.get('active_cells_mean', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
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
    result['handoff_metrics'] = handoff_metrics(result)
    return result


def context_score(kontext_name, result):
    metrics = result['handoff_metrics']
    base = metrics['consensus'] - metrics['polarization']
    if kontext_name == 'polarization':
        return (
            base
            + 0.16 * metrics['cross_group_cooperation']
            + 0.14 * metrics['handoff_rate']
            + 0.08 * metrics['skill_alignment_rate']
            + 0.06 * metrics['meta_alignment_rate']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.12 * metrics['handoff_rate']
            + 0.10 * metrics['meta_alignment_rate']
            + 0.06 * metrics['active_cells_mean'] / 4.0
        )
    return (
        base
        + 0.14 * metrics['detection_rate']
        + 0.10 * metrics['resource_efficiency']
        + 0.10 * metrics['resource_share_rate']
        + 0.08 * metrics['handoff_rate']
        - 0.12 * metrics['corruption_mean']
    )


def summarize_runs(runs, eintrag, context_list):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'handoff_rate': {},
        'handoff_total': {},
        'resource_share_rate': {},
        'active_cells_mean': {},
        'resource_efficiency': {},
        'meta_alignment_rate': {},
        'skill_alignment_rate': {},
        'detection_rate': {},
        'corruption_mean': {},
        'cross_group_cooperation': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name]) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['handoff_metrics'][metric_name] for run in runs])

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
    eintraege = handoff_profiles(katalog)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI GRUPPENHANDOFF-STUDIE')
    print('=' * 84)
    print('Vergleicht Uebergabeprotokolle zwischen Talentgruppen und misst,')
    print('welche Handoff-Architektur Spezialisierung am besten skaliert.\n')

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
            f"{summary['label']:<30} Score={summary['combined_score']:+.3f} | "
            f"Handoffs={summary['handoff_rate']['consensus']:.2f} | "
            f"Completion={summary['completion_rate']['consensus']:.1%} | "
            f"Stress-Detektion={summary['detection_rate']['stress']:.1%}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'shared-dna')
    print('\nBestes Gruppenhandoff-Profil:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur gemeinsamen DNA {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Handoffs/Konsensrunde {best['handoff_rate']['consensus']:.2f}, "
        f"Completion {best['completion_rate']['consensus']:.1%}, "
        f"Stress-Detektion {best['detection_rate']['stress']:.1%}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#4e79a7', '#9c755f', '#59a14f', '#e15759', '#76b7b2']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Handoff-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['handoff_rate']['consensus'] for item in summaries],
        width,
        label='Handoffs/Runde',
        color='#59a14f',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['completion_rate']['consensus'] * 100.0 for item in summaries],
        width,
        label='Completion (%)',
        color='#4e79a7',
    )
    axes[0, 1].set_title('Konsens-Uebergaben')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['resource_share_rate']['stress'] for item in summaries],
        width,
        label='Ressourcen/Runde',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['resource_efficiency']['stress'] for item in summaries],
        width,
        label='Effizienz',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Stress und Ressourcen')
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
                item['meta_alignment_rate']['consensus'],
                item['detection_rate']['stress'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Pol', 'Kon', 'Stress', 'Meta', 'Det'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['cross_group_cooperation']['polarization'] * 100.0 for item in summaries],
        width,
        label='Kooperation',
        color='#59a14f',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['active_cells_mean']['consensus'] for item in summaries],
        width,
        label='Aktive Zellen',
        color='#9c755f',
    )
    axes[1, 1].set_title('Gruppenkopplung')
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
            f"- Handoffs/Runde (Konsens): {best['handoff_rate']['consensus']:.2f}\n"
            f"- Completion: {best['completion_rate']['consensus']:.1%}\n"
            f"- Meta-Ausrichtung: {best['meta_alignment_rate']['consensus']:.1%}\n"
            f"- Ressourcen/Runde: {best['resource_share_rate']['stress']:.2f}\n"
            f"- Stress-Detektion: {best['detection_rate']['stress']:.1%}\n"
            f"- Stress-Korruption: {best['corruption_mean']['stress']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_gruppentalente.png'.replace('talente', 'handoff'), dpi=150)


if __name__ == '__main__':
    main()
