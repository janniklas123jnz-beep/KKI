"""
KKI Gruppentalente-Studie
=========================
Vergleicht, welche gruppenspezifischen Zusatzfaehigkeiten auf gemeinsamer
Grund-DNA den groessten Systemvorteil bringen, ohne die Gesamtkoordination
zu verlieren.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_gruppenidentitaet import basis_dna, kontexte, modellkatalog, mittelwert
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
        repetitions = int(os.getenv('KKI_GROUP_TALENT_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_GROUP_TALENT_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_GROUP_TALENT_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_GROUP_TALENT_STRESS_STRENGTH', '0.42')),
        'stress_sources': int(os.getenv('KKI_GROUP_TALENT_STRESS_SOURCES', '6')),
    }


def talent_profile():
    shared = basis_dna()
    return [
        {'name': 'shared-dna', 'label': 'Gemeinsame DNA', 'base_model': 'adaptive-hybrid', 'overrides': {}},
        {
            'name': 'analyse-fokus',
            'label': 'Analyse-Fokus',
            'base_model': 'adaptive-hybrid',
            'overrides': {
                'analyzer_share': 0.28,
                'mediator_share': 0.20,
                'sentinel_share': 0.18,
                'connector_share': 0.16,
                'generalist_share': 0.18,
                'analyzer_learning_multiplier': shared['analyzer_learning_multiplier'] + 0.10,
                'analyzer_memory_window': shared['analyzer_memory_window'] + 10,
                'group_learning_rate': shared['group_learning_rate'] + 0.02,
                'meta_priority_strength': shared['meta_priority_strength'] + 0.04,
                'cluster_budget_skew': shared['cluster_budget_skew'] + 0.04,
            },
        },
        {
            'name': 'bruecken-fokus',
            'label': 'Bruecken-Fokus',
            'base_model': 'adaptive-hybrid',
            'overrides': {
                'connector_share': 0.24,
                'mediator_share': 0.24,
                'sentinel_share': 0.16,
                'analyzer_share': 0.18,
                'generalist_share': 0.18,
                'connector_bridge_bonus': shared['connector_bridge_bonus'] + 0.04,
                'connector_cross_group_learning_bonus': shared['connector_cross_group_learning_bonus'] + 0.08,
                'mediator_bridge_bonus': shared['mediator_bridge_bonus'] + 0.03,
                'rewire_cross_group_bonus': shared['rewire_cross_group_bonus'] + 0.08,
                'group_learning_rate': shared['group_learning_rate'] + 0.01,
            },
        },
        {
            'name': 'schutz-fokus',
            'label': 'Schutz-Fokus',
            'base_model': 'adaptive-hybrid',
            'overrides': {
                'sentinel_share': 0.26,
                'analyzer_share': 0.22,
                'connector_share': 0.14,
                'mediator_share': 0.20,
                'generalist_share': 0.18,
                'sentinel_rep_threshold': shared['sentinel_rep_threshold'] + 0.06,
                'sentinel_cooperation_penalty': shared['sentinel_cooperation_penalty'] + 0.02,
                'sentinel_reputation_learning_multiplier': shared['sentinel_reputation_learning_multiplier'] + 0.10,
                'meta_priority_strength': shared['meta_priority_strength'] + 0.02,
                'cluster_budget_skew': shared['cluster_budget_skew'] + 0.08,
            },
        },
        {
            'name': 'regeneration-fokus',
            'label': 'Regeneration-Fokus',
            'base_model': 'adaptive-hybrid',
            'overrides': {
                'mediator_share': 0.24,
                'connector_share': 0.18,
                'sentinel_share': 0.18,
                'analyzer_share': 0.18,
                'generalist_share': 0.22,
                'group_learning_rate': shared['group_learning_rate'] + 0.03,
                'meta_priority_strength': shared['meta_priority_strength'] + 0.03,
                'rewire_removal_probability': max(0.08, shared['rewire_removal_probability'] - 0.04),
                'rewire_addition_probability': shared['rewire_addition_probability'] + 0.04,
                'mediator_contact_bias': shared['mediator_contact_bias'] + 0.04,
            },
        },
        {
            'name': 'koordinations-fokus',
            'label': 'Koordinations-Fokus',
            'base_model': 'adaptive-hybrid',
            'overrides': {
                'connector_share': 0.20,
                'mediator_share': 0.26,
                'sentinel_share': 0.18,
                'analyzer_share': 0.20,
                'generalist_share': 0.16,
                'meta_priority_strength': shared['meta_priority_strength'] + 0.08,
                'group_learning_rate': shared['group_learning_rate'] + 0.02,
                'cluster_budget_skew': max(0.18, shared['cluster_budget_skew'] - 0.04),
                'mediator_bridge_bonus': shared['mediator_bridge_bonus'] + 0.04,
                'connector_cross_group_learning_bonus': shared['connector_cross_group_learning_bonus'] + 0.04,
            },
        },
    ]


def build_profile(katalog, eintrag):
    shared = basis_dna()
    adaptive_basis = {
        key: value for key, value in katalog[eintrag['base_model']].items() if key not in {'name', 'label'}
    }
    profile = {**adaptive_basis, **shared}
    profile.update(eintrag.get('overrides', {}))
    return profile


def talent_metrics(result):
    workflow = result['workflow_metrics']
    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'learning_gain_rate': workflow.get('group_learning_gain_rate', 0.0),
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
    }


def run_context(seed, params, katalog, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(build_profile(katalog, eintrag))
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
    result['talent_metrics'] = talent_metrics(result)
    return result


def context_score(kontext_name, result):
    metrics = result['talent_metrics']
    base = metrics['consensus'] - metrics['polarization']
    if kontext_name == 'polarization':
        return (
            base
            + 0.18 * metrics['cross_group_cooperation']
            + 0.12 * metrics['skill_alignment_rate']
            + 0.08 * metrics['meta_alignment_rate']
            + 0.08 * metrics['resource_efficiency']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.16 * metrics['completion_rate']
            + 0.10 * metrics['meta_alignment_rate']
            + 0.08 * metrics['learning_gain_rate']
            + 0.08 * metrics['cross_group_cooperation']
        )
    return (
        base
        + 0.14 * metrics['detection_rate']
        + 0.12 * metrics['completion_rate']
        + 0.10 * metrics['resource_efficiency']
        + 0.08 * metrics['learning_gain_rate']
        - 0.12 * metrics['corruption_mean']
    )


def summarize_runs(runs, eintrag, context_list):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'resource_efficiency': {},
        'meta_alignment_rate': {},
        'skill_alignment_rate': {},
        'learning_gain_rate': {},
        'detection_rate': {},
        'corruption_mean': {},
        'cross_group_cooperation': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name]) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['talent_metrics'][metric_name] for run in runs])

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
    eintraege = talent_profile()
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI GRUPPENTALENTE-STUDIE')
    print('=' * 84)
    print('Vergleicht gruppenspezifische Zusatzfaehigkeiten auf gemeinsamer DNA und')
    print('misst, welche Talentmischung den groessten Systemvorteil bringt.\n')

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
                    katalog,
                    eintrag,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, eintrag, context_list)
        summaries.append(summary)
        print(
            f"{summary['label']:<24} Score={summary['combined_score']:+.3f} | "
            f"Koop={summary['cross_group_cooperation']['polarization']:.1%} | "
            f"Skill={summary['skill_alignment_rate']['polarization']:.1%} | "
            f"Stress-Detektion={summary['detection_rate']['stress']:.1%}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'shared-dna')
    print('\nBestes Gruppentalentprofil:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur gemeinsamen DNA {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Kooperation {best['cross_group_cooperation']['polarization']:.1%}, "
        f"Meta-Ausrichtung {best['meta_alignment_rate']['consensus']:.1%}, "
        f"Stress-Detektion {best['detection_rate']['stress']:.1%}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#4e79a7', '#9c755f', '#59a14f', '#e15759', '#76b7b2', '#f28e2b']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Talent-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['cross_group_cooperation']['polarization'] * 100.0 for item in summaries],
        width,
        label='Cross-Group-Kooperation',
        color='#59a14f',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['skill_alignment_rate']['polarization'] * 100.0 for item in summaries],
        width,
        label='Skill-Ausrichtung',
        color='#4e79a7',
    )
    axes[0, 1].set_title('Polarisierungskontext')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['completion_rate']['consensus'] * 100.0 for item in summaries],
        width,
        label='Completion',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['meta_alignment_rate']['consensus'] * 100.0 for item in summaries],
        width,
        label='Meta-Ausrichtung',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Konsenskontext')
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
                item['resource_efficiency']['stress'],
                item['detection_rate']['stress'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Pol', 'Kon', 'Stress', 'Eff', 'Det'])
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
        label='Detektion',
        color='#e15759',
    )
    axes[1, 1].bar(
        x + width / 2,
        [(1.0 - item['corruption_mean']['stress']) * 100.0 for item in summaries],
        width,
        label='Integritaet',
        color='#59a14f',
    )
    axes[1, 1].set_title('Stressrobustheit')
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
            f"- Cross-Group-Kooperation: {best['cross_group_cooperation']['polarization']:.1%}\n"
            f"- Skill-Ausrichtung: {best['skill_alignment_rate']['polarization']:.1%}\n"
            f"- Completion im Konsens: {best['completion_rate']['consensus']:.1%}\n"
            f"- Stress-Detektion: {best['detection_rate']['stress']:.1%}\n"
            f"- Stress-Korruption: {best['corruption_mean']['stress']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_gruppentalente.png', dpi=150)


if __name__ == '__main__':
    main()
