"""
KKI Modellwechsel-Studie
========================
Vergleicht feste Interaktionsmodelle mit einem situativen Modellwechsel,
der je nach Kontext zwischen mehreren Interaktionsregeln umschaltet.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_interaktionsmodelle import profile as interaction_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


MODEL_SHORT_LABELS = {
    'homogen': 'HOM',
    'bounded-confidence': 'BC',
    'trust-weighted': 'TR',
    'memory-enhanced': 'MEM',
    'adaptive-hybrid': 'HYB',
}


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_MODEL_SWITCH_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_MODEL_SWITCH_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_MODEL_SWITCH_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_MODEL_SWITCH_STRESS_STRENGTH', '0.42')),
        'stress_sources': int(os.getenv('KKI_MODEL_SWITCH_STRESS_SOURCES', '6')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def modellkatalog(params):
    return {item['name']: item for item in interaction_profiles(params)}


def wechselprofile():
    return [
        {'name': 'homogen', 'label': 'Homogen', 'static_model': 'homogen'},
        {
            'name': 'bounded-static',
            'label': 'Bounded Confidence',
            'static_model': 'bounded-confidence',
        },
        {
            'name': 'trust-static',
            'label': 'Vertrauensgewichtet',
            'static_model': 'trust-weighted',
        },
        {
            'name': 'memory-static',
            'label': 'Gedaechtnisbasiert',
            'static_model': 'memory-enhanced',
        },
        {
            'name': 'hybrid-static',
            'label': 'Adaptiver Hybrid',
            'static_model': 'adaptive-hybrid',
        },
        {
            'name': 'situativ',
            'label': 'Situativer Wechsel',
            'context_models': {
                'polarization': 'trust-weighted',
                'consensus': 'adaptive-hybrid',
                'stress': 'trust-weighted',
            },
        },
    ]


def kontexte():
    return [
        {
            'name': 'polarization',
            'label': 'Polarisierung',
            'scenario': 'polarization',
            'enable_prompt_injection': False,
        },
        {
            'name': 'consensus',
            'label': 'Konsens',
            'scenario': 'consensus',
            'enable_prompt_injection': False,
        },
        {
            'name': 'stress',
            'label': 'Manipulationsstress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
        },
    ]


def modell_fuer_kontext(architektur, kontext_name):
    if 'context_models' in architektur:
        return architektur['context_models'][kontext_name]
    return architektur['static_model']


def run_context(seed, params, katalog, architektur, kontext):
    modellname = modell_fuer_kontext(architektur, kontext['name'])
    profil = katalog[modellname]
    overrides = {key: value for key, value in profil.items() if key not in {'name', 'label'}}

    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(overrides)
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
    return modellname, result


def score_context(kontext_name, result):
    workflow = result['workflow_metrics']
    base = result['final_consensus_score'] - result['final_polarization_index']
    cooperation = result['cross_group_cooperation_rate']
    resource = workflow.get('resource_efficiency', 0.0)
    completion = workflow.get('completion_rate', 0.0)
    meta = workflow.get('meta_alignment_rate', 0.0)
    detection = workflow.get('misinformation_detection_rate', 0.0)
    corruption = workflow.get('misinformation_corruption_mean', 0.0)
    skill = workflow.get('skill_alignment_rate', 0.0)

    if kontext_name == 'polarization':
        return base + 0.24 * cooperation + 0.08 * meta + 0.08 * skill + 0.04 * resource
    if kontext_name == 'consensus':
        return result['final_consensus_score'] + 0.20 * cooperation + 0.08 * skill + 0.06 * resource + 0.04 * completion
    return base + 0.18 * cooperation + 0.10 * meta + 0.12 * detection - 0.10 * corruption + 0.06 * skill


def summarize_runs(runs, architektur, context_list):
    context_scores = {}
    context_consensus = {}
    context_polarization = {}
    context_detection = {}
    context_corruption = {}
    context_skill = {}

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([score_context(name, run[name]['result']) for run in runs])
        context_consensus[name] = mittelwert([run[name]['result']['final_consensus_score'] for run in runs])
        context_polarization[name] = mittelwert([run[name]['result']['final_polarization_index'] for run in runs])
        context_detection[name] = mittelwert(
            [run[name]['result']['workflow_metrics'].get('misinformation_detection_rate', 0.0) for run in runs]
        )
        context_corruption[name] = mittelwert(
            [run[name]['result']['workflow_metrics'].get('misinformation_corruption_mean', 0.0) for run in runs]
        )
        context_skill[name] = mittelwert(
            [run[name]['result']['workflow_metrics'].get('skill_alignment_rate', 0.0) for run in runs]
        )

    return {
        'name': architektur['name'],
        'label': architektur['label'],
        'combined_score': mittelwert(
            [sum(score_context(kontext['name'], run[kontext['name']]['result']) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        'context_consensus': context_consensus,
        'context_polarization': context_polarization,
        'context_detection': context_detection,
        'context_corruption': context_corruption,
        'context_skill': context_skill,
        'context_models': {
            kontext['name']: MODEL_SHORT_LABELS[modell_fuer_kontext(architektur, kontext['name'])]
            for kontext in context_list
        },
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    architekturen = wechselprofile()
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI MODELLWECHSEL-STUDIE')
    print('=' * 84)
    print('Vergleicht feste Interaktionsmodelle mit situativem Modellwechsel zwischen')
    print('Bounded Confidence, Vertrauensgewichtung, Gedaechtnis und Hybrid-Abwehr.\n')

    zusammenfassungen = []
    for architektur_index, architektur in enumerate(architekturen):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + architektur_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                model_name, result = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    katalog,
                    architektur,
                    kontext,
                )
                run[kontext['name']] = {'model_name': model_name, 'result': result}
            runs.append(run)

        summary = summarize_runs(runs, architektur, context_list)
        zusammenfassungen.append(summary)
        print(
            f"{summary['label']:<22} Score={summary['combined_score']:+.3f} | "
            f"Pol={summary['context_scores']['polarization']:+.3f} | "
            f"Kon={summary['context_scores']['consensus']:+.3f} | "
            f"Stress={summary['context_scores']['stress']:+.3f}"
        )

    best = max(zusammenfassungen, key=lambda item: item['combined_score'])
    static_best = max(
        [item for item in zusammenfassungen if item['name'] != 'situativ'],
        key=lambda item: item['combined_score'],
    )

    print('\nBestes Modellwechselprofil:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum besten statischen Profil {best['combined_score'] - static_best['combined_score']:+.3f}"
    )
    print(
        'Kontextwahl: '
        f"Pol={best['context_models']['polarization']}, "
        f"Kon={best['context_models']['consensus']}, "
        f"Stress={best['context_models']['stress']}"
    )

    labels = [item['label'] for item in zusammenfassungen]
    x = np.arange(len(labels))
    width = 0.24

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    combined_scores = [item['combined_score'] for item in zusammenfassungen]
    axes[0, 0].bar(x, combined_scores, color=['#9aa0a6', '#4e79a7', '#f28e2b', '#59a14f', '#b07aa1', '#e15759'])
    axes[0, 0].set_title('Kombinierter Kontext-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width,
        [item['context_scores']['polarization'] for item in zusammenfassungen],
        width,
        label='Polarisierung',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x,
        [item['context_scores']['consensus'] for item in zusammenfassungen],
        width,
        label='Konsens',
        color='#59a14f',
    )
    axes[0, 1].bar(
        x + width,
        [item['context_scores']['stress'] for item in zusammenfassungen],
        width,
        label='Stress',
        color='#e15759',
    )
    axes[0, 1].set_title('Kontextbeitraege')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['context_detection']['stress'] * 100.0 for item in zusammenfassungen],
        width,
        label='Detektion (%)',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [(1.0 - item['context_corruption']['stress']) * 100.0 for item in zusammenfassungen],
        width,
        label='Integritaet (%)',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Stress-Abwehr')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    score_matrix = np.array(
        [
            [
                item['context_scores']['polarization'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
            ]
            for item in zusammenfassungen
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(score_matrix, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontext-Heatmap')
    axes[1, 0].set_xticks([0, 1, 2])
    axes[1, 0].set_xticklabels(['Pol', 'Kon', 'Stress'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(score_matrix.shape[0]):
        for col in range(score_matrix.shape[1]):
            axes[1, 0].text(col, row, f'{score_matrix[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    model_order = ['homogen', 'bounded-confidence', 'trust-weighted', 'memory-enhanced', 'adaptive-hybrid']
    switch_matrix = np.array(
        [
            [
                model_order.index(modell_fuer_kontext(architektur, 'polarization')),
                model_order.index(modell_fuer_kontext(architektur, 'consensus')),
                model_order.index(modell_fuer_kontext(architektur, 'stress')),
            ]
            for architektur in architekturen
        ],
        dtype=float,
    )
    switch_map = axes[1, 1].imshow(switch_matrix, cmap='tab20', aspect='auto')
    axes[1, 1].set_title('Modellwahl pro Kontext')
    axes[1, 1].set_xticks([0, 1, 2])
    axes[1, 1].set_xticklabels(['Pol', 'Kon', 'Stress'])
    axes[1, 1].set_yticks(range(len(labels)))
    axes[1, 1].set_yticklabels(labels)
    for row, summary in enumerate(zusammenfassungen):
        for col, context_name in enumerate(['polarization', 'consensus', 'stress']):
            axes[1, 1].text(
                col,
                row,
                summary['context_models'][context_name],
                ha='center',
                va='center',
                fontsize=8,
                color='black',
            )
    fig.colorbar(switch_map, ax=axes[1, 1], fraction=0.046, pad=0.04)

    axes[1, 2].axis('off')
    axes[1, 2].text(
        0.0,
        0.98,
        (
            "Zusammenfassung\n"
            f"- Bestes Profil: {best['label']}\n"
            f"- Bester statischer Vergleich: {static_best['label']}\n"
            f"- Delta: {best['combined_score'] - static_best['combined_score']:+.3f}\n"
            f"- Pol-Modell: {best['context_models']['polarization']}\n"
            f"- Konsens-Modell: {best['context_models']['consensus']}\n"
            f"- Stress-Modell: {best['context_models']['stress']}\n"
            f"- Stress-Detektion: {best['context_detection']['stress']:.1%}\n"
            f"- Stress-Korruption: {best['context_corruption']['stress']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_modellwechsel.png', dpi=150)


if __name__ == '__main__':
    main()
