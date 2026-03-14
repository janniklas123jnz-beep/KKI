"""
KKI Beziehungsgedaechtnis-Studie
================================
Vergleicht, ob langfristige Beziehungshistorien stabilere kooperative Kerne
erzeugen als rein kurzfristige Vertrauenssignale.
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


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_RELATIONSHIP_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_RELATIONSHIP_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_RELATIONSHIP_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stable_min_history': int(os.getenv('KKI_RELATIONSHIP_STABLE_MIN_HISTORY', '18')),
        'stable_trust_threshold': float(os.getenv('KKI_RELATIONSHIP_STABLE_TRUST', '0.76')),
        'stress_strength': float(os.getenv('KKI_RELATIONSHIP_STRESS_STRENGTH', '0.40')),
        'stress_sources': int(os.getenv('KKI_RELATIONSHIP_STRESS_SOURCES', '6')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def modellkatalog(params):
    return {item['name']: item for item in interaction_profiles(params)}


def profile(params):
    basis = modellkatalog(params)
    return [
        {'name': 'homogen', 'label': 'Homogen', 'source_model': 'homogen'},
        {
            'name': 'short-trust',
            'label': 'Kurzzeit-Vertrauen',
            'source_model': 'trust-weighted',
            'overrides': {
                'analyzer_memory_window': 6,
                'mediator_partner_bias': 0.60,
                'mediator_partner_distance': 0.20,
                'rewire_min_interactions': 2,
                'rewire_removal_probability': 0.48,
            },
        },
        {
            'name': 'memory-enhanced',
            'label': 'Analytisches Gedaechtnis',
            'source_model': 'memory-enhanced',
            'overrides': {},
        },
        {
            'name': 'relationship-memory',
            'label': 'Beziehungsgedaechtnis',
            'source_model': 'memory-enhanced',
            'overrides': {
                'generalist_share': 0.14,
                'connector_share': 0.18,
                'sentinel_share': 0.14,
                'mediator_share': 0.26,
                'analyzer_share': 0.28,
                'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
                'analyzer_learning_multiplier': 1.28,
                'mediator_partner_bias': 0.90,
                'mediator_partner_distance': 0.38,
                'rewire_min_interactions': 5,
                'rewire_removal_probability': 0.18,
                'rewire_addition_probability': 0.74,
                'enable_role_switching': False,
                'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.01,
            },
        },
        {
            'name': 'relationship-hybrid',
            'label': 'Resilientes Beziehungsgedaechtnis',
            'source_model': 'adaptive-hybrid',
            'overrides': {
                'generalist_share': 0.12,
                'connector_share': 0.18,
                'sentinel_share': 0.22,
                'mediator_share': 0.24,
                'analyzer_share': 0.24,
                'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
                'analyzer_learning_multiplier': 1.24,
                'mediator_partner_bias': 0.88,
                'mediator_partner_distance': 0.36,
                'rewire_min_interactions': 5,
                'rewire_removal_probability': 0.16,
                'rewire_addition_probability': 0.76,
                'sentinel_rep_threshold': 0.39,
                'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.03,
                'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.06,
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


def build_overrides(katalog, eintrag):
    basis = dict(katalog[eintrag['source_model']])
    overrides = {key: value for key, value in basis.items() if key not in {'name', 'label'}}
    overrides.update(eintrag.get('overrides', {}))
    return overrides


def beziehungsmetriken(agenten, params):
    agenten_dict = {agent.id: agent for agent in agenten}
    stable_min_history = params['stable_min_history']
    stable_trust_threshold = params['stable_trust_threshold']

    pair_count = 0
    stable_bonds = 0
    stable_cross_group = 0
    depth_values = []
    trust_values = []
    stable_partner_counts = {agent.id: 0 for agent in agenten}

    for agent in agenten:
        for partner_id, history in agent.interaktions_history.items():
            if partner_id not in agenten_dict or agent.id >= partner_id:
                continue

            partner = agenten_dict[partner_id]
            partner_history = partner.interaktions_history.get(agent.id, [])
            combined_len = 0.5 * (len(history) + len(partner_history))
            mutual_trust = 0.5 * (
                agent.berechne_partner_reputation(partner_id)
                + partner.berechne_partner_reputation(agent.id)
            )
            pair_count += 1
            depth_values.append(combined_len)
            trust_values.append(mutual_trust)

            if combined_len >= stable_min_history and mutual_trust >= stable_trust_threshold:
                stable_bonds += 1
                stable_partner_counts[agent.id] += 1
                stable_partner_counts[partner.id] += 1
                if agent.gruppe != partner.gruppe:
                    stable_cross_group += 1

    cooperative_core_share = sum(1 for count in stable_partner_counts.values() if count >= 4) / max(1, len(agenten))
    return {
        'active_relationships': pair_count,
        'stable_bond_rate': stable_bonds / max(1, pair_count),
        'stable_cross_group_share': stable_cross_group / max(1, stable_bonds),
        'cooperative_core_share': cooperative_core_share,
        'relationship_depth_mean': mittelwert(depth_values),
        'remembered_trust_mean': mittelwert(trust_values),
    }


def run_context(seed, params, katalog, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(build_overrides(katalog, eintrag))
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
    result['relationship_metrics'] = beziehungsmetriken(result['agents'], params)
    return result


def context_score(kontext_name, result):
    workflow = result['workflow_metrics']
    relation = result['relationship_metrics']
    base = result['final_consensus_score'] - result['final_polarization_index']
    cooperation = result['cross_group_cooperation_rate']
    stable_bond = relation['stable_bond_rate']
    stable_cross = relation['stable_cross_group_share']
    cooperative_core = relation['cooperative_core_share']
    trust_mean = relation['remembered_trust_mean']
    depth_mean = min(1.0, relation['relationship_depth_mean'] / 20.0)
    detection = workflow.get('misinformation_detection_rate', 0.0)
    corruption = workflow.get('misinformation_corruption_mean', 0.0)
    skill = workflow.get('skill_alignment_rate', 0.0)

    if kontext_name == 'polarization':
        return base + 0.16 * cooperation + 0.18 * stable_bond + 0.16 * cooperative_core + 0.10 * stable_cross
    if kontext_name == 'consensus':
        return (
            result['final_consensus_score']
            + 0.14 * cooperation
            + 0.18 * stable_bond
            + 0.12 * trust_mean
            + 0.10 * depth_mean
        )
    return (
        base
        + 0.14 * stable_bond
        + 0.12 * cooperative_core
        + 0.10 * detection
        - 0.10 * corruption
        + 0.06 * skill
    )


def summarize_runs(runs, eintrag, context_list):
    context_scores = {}
    stable_bond_rates = {}
    cooperative_core_rates = {}
    remembered_trust = {}
    stable_cross_group = {}
    stress_detection = {}
    stress_corruption = {}

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name]) for run in runs])
        stable_bond_rates[name] = mittelwert([run[name]['relationship_metrics']['stable_bond_rate'] for run in runs])
        cooperative_core_rates[name] = mittelwert(
            [run[name]['relationship_metrics']['cooperative_core_share'] for run in runs]
        )
        remembered_trust[name] = mittelwert(
            [run[name]['relationship_metrics']['remembered_trust_mean'] for run in runs]
        )
        stable_cross_group[name] = mittelwert(
            [run[name]['relationship_metrics']['stable_cross_group_share'] for run in runs]
        )
        stress_detection[name] = mittelwert(
            [run[name]['workflow_metrics'].get('misinformation_detection_rate', 0.0) for run in runs]
        )
        stress_corruption[name] = mittelwert(
            [run[name]['workflow_metrics'].get('misinformation_corruption_mean', 0.0) for run in runs]
        )

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']]) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        'stable_bond_rates': stable_bond_rates,
        'cooperative_core_rates': cooperative_core_rates,
        'remembered_trust': remembered_trust,
        'stable_cross_group': stable_cross_group,
        'stress_detection': stress_detection,
        'stress_corruption': stress_corruption,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    eintraege = profile(params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI BEZIEHUNGSGEDAECHTNIS-STUDIE')
    print('=' * 84)
    print('Vergleicht kurzfristiges Vertrauen mit analytischem und langfristigem')
    print('Beziehungsgedaechtnis fuer stabile kooperative Kerne im Schwarm.\n')

    zusammenfassungen = []
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
        zusammenfassungen.append(summary)
        print(
            f"{summary['label']:<30} Score={summary['combined_score']:+.3f} | "
            f"Stabile Bindungen={summary['stable_bond_rates']['polarization']:.1%} | "
            f"Kerne={summary['cooperative_core_rates']['polarization']:.1%} | "
            f"Stress-Detektion={summary['stress_detection']['stress']:.1%}"
        )

    best = max(zusammenfassungen, key=lambda item: item['combined_score'])
    baseline = next(item for item in zusammenfassungen if item['name'] == 'homogen')

    print('\nBestes Beziehungsgedaechtnisprofil:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur Homogenitaet {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Stabile Bindungen {best['stable_bond_rates']['polarization']:.1%}, "
        f"kooperative Kerne {best['cooperative_core_rates']['polarization']:.1%}, "
        f"erinnerte Vertrauensqualitaet {best['remembered_trust']['consensus']:.2f}"
    )

    labels = [item['label'] for item in zusammenfassungen]
    x = np.arange(len(labels))
    colors = ['#9aa0a6', '#4e79a7', '#f28e2b', '#59a14f', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in zusammenfassungen], color=colors)
    axes[0, 0].set_title('Kombinierter Beziehungs-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    width = 0.35
    axes[0, 1].bar(
        x - width / 2,
        [item['stable_bond_rates']['polarization'] * 100.0 for item in zusammenfassungen],
        width,
        label='Stabile Bindungen (%)',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['cooperative_core_rates']['polarization'] * 100.0 for item in zusammenfassungen],
        width,
        label='Kooperative Kerne (%)',
        color='#59a14f',
    )
    axes[0, 1].set_title('Polarisierungs-Kontext')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['stress_detection']['stress'] * 100.0 for item in zusammenfassungen],
        width,
        label='Detektion (%)',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [(1.0 - item['stress_corruption']['stress']) * 100.0 for item in zusammenfassungen],
        width,
        label='Integritaet (%)',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Manipulationsstress')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['stable_bond_rates']['polarization'],
                item['cooperative_core_rates']['polarization'],
                item['remembered_trust']['consensus'],
                item['stable_cross_group']['consensus'],
            ]
            for item in zusammenfassungen
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='Blues', aspect='auto')
    axes[1, 0].set_title('Beziehungsmetriken')
    axes[1, 0].set_xticks([0, 1, 2, 3])
    axes[1, 0].set_xticklabels(['Bindung', 'Kern', 'Trust', 'Cross'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['context_scores']['consensus'] for item in zusammenfassungen],
        width,
        label='Konsens',
        color='#59a14f',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['context_scores']['stress'] for item in zusammenfassungen],
        width,
        label='Stress',
        color='#e15759',
    )
    axes[1, 1].set_title('Kontextvergleich')
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
            f"- Delta zur Homogenitaet: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Stabile Bindungen: {best['stable_bond_rates']['polarization']:.1%}\n"
            f"- Kooperative Kerne: {best['cooperative_core_rates']['polarization']:.1%}\n"
            f"- Erinnerter Trust: {best['remembered_trust']['consensus']:.2f}\n"
            f"- Cross-Group-Bindungen: {best['stable_cross_group']['consensus']:.1%}\n"
            f"- Stress-Detektion: {best['stress_detection']['stress']:.1%}\n"
            f"- Stress-Korruption: {best['stress_corruption']['stress']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_beziehungsgedaechtnis.png', dpi=150)


if __name__ == '__main__':
    main()
