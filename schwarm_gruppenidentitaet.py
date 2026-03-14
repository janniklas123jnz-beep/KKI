"""
KKI Gruppenidentitaets-Studie
=============================
Vergleicht, wie viel gemeinsame Grund-DNA erhalten bleiben muss, damit
gruppenspezifische Overlay-Profile Spezialisierung bringen, ohne den
Schwarm in Fragmentierung kippen zu lassen.
"""

from __future__ import annotations

import os
import random
from collections import Counter

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
        repetitions = int(os.getenv('KKI_GROUP_IDENTITY_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_GROUP_IDENTITY_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_GROUP_IDENTITY_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'dna_similarity_weight': float(os.getenv('KKI_DNA_SIMILARITY_WEIGHT', '0.55')),
        'overlay_fragmentation_threshold': float(os.getenv('KKI_OVERLAY_FRAGMENTATION_THRESHOLD', '0.24')),
        'stress_strength': float(os.getenv('KKI_GROUP_IDENTITY_STRESS_STRENGTH', '0.40')),
        'stress_sources': int(os.getenv('KKI_GROUP_IDENTITY_STRESS_SOURCES', '6')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def modellkatalog(params):
    return {item['name']: item for item in interaction_profiles(params)}


def basis_dna():
    return {
        'roles_enabled': True,
        'generalist_share': 0.22,
        'connector_share': 0.18,
        'sentinel_share': 0.18,
        'mediator_share': 0.22,
        'analyzer_share': 0.20,
        'connector_bridge_bonus': 0.10,
        'connector_cross_group_learning_bonus': 0.18,
        'sentinel_rep_threshold': 0.40,
        'sentinel_cooperation_penalty': 0.07,
        'sentinel_reputation_learning_multiplier': 1.40,
        'mediator_bridge_bonus': 0.08,
        'mediator_partner_bias': 0.82,
        'mediator_partner_distance': 0.34,
        'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
        'analyzer_learning_multiplier': 1.24,
        'enable_bridge_mechanism': True,
        'enable_centrist_moderation': True,
        'enable_mediator_encouragement': True,
        'mediator_contact_bias': 0.68,
        'centrist_pull_strength': 0.08,
        'enable_dynamic_rewiring': True,
        'rewire_min_interactions': 5,
        'rewire_reputation_threshold': 0.40,
        'rewire_opinion_distance_threshold': 0.50,
        'rewire_proximity_weight': 0.62,
        'rewire_removal_probability': 0.18,
        'rewire_addition_probability': 0.80,
        'rewire_cross_group_bonus': 0.10,
        'enable_missions': True,
        'mission_assignment': 'arbitrated',
        'mission_arbitration_enabled': True,
        'enable_role_switching': False,
        'enable_workflow_stages': True,
        'enable_workflow_cells': True,
        'enable_handoff_coordination': True,
        'enable_parallel_workflow_cells': True,
        'enable_resource_coordination': True,
        'enable_capability_clusters': True,
        'enable_asymmetric_cluster_budgets': True,
        'enable_bottleneck_management': True,
        'enable_meta_coordination': True,
        'enable_prompt_injection': True,
        'enable_emergent_skills': True,
        'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.03,
        'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.05,
        'cluster_budget_skew': max(0.20, float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')) - 0.08),
    }


def overlay_profiles():
    return [
        {'name': 'homogen', 'label': 'Homogen', 'base_model': 'homogen', 'identity_mode': 'none'},
        {'name': 'shared-dna', 'label': 'Gemeinsame DNA', 'base_model': 'adaptive-hybrid', 'identity_mode': 'shared'},
        {
            'name': 'soft-overlay',
            'label': 'Sanftes Overlay',
            'base_model': 'adaptive-hybrid',
            'identity_mode': 'soft',
            'overlay_delta': 0.08,
        },
        {
            'name': 'balanced-overlay',
            'label': 'Balanciertes Overlay',
            'base_model': 'adaptive-hybrid',
            'identity_mode': 'balanced',
            'overlay_delta': 0.16,
        },
        {
            'name': 'hard-overlay',
            'label': 'Hartes Overlay',
            'base_model': 'adaptive-hybrid',
            'identity_mode': 'hard',
            'overlay_delta': 0.28,
        },
    ]


def kontexte():
    return [
        {'name': 'polarization', 'label': 'Polarisierung', 'scenario': 'polarization', 'enable_prompt_injection': False},
        {'name': 'consensus', 'label': 'Konsens', 'scenario': 'consensus', 'enable_prompt_injection': False},
        {'name': 'stress', 'label': 'Manipulationsstress', 'scenario': 'polarization', 'enable_prompt_injection': True},
    ]


def build_profile(katalog, eintrag):
    if eintrag['base_model'] == 'homogen':
        return {}

    basis = basis_dna()
    adaptive_basis = {
        key: value for key, value in katalog[eintrag['base_model']].items() if key not in {'name', 'label'}
    }
    profile = {**adaptive_basis, **basis}
    if eintrag['identity_mode'] == 'shared':
        return profile

    delta = float(eintrag.get('overlay_delta', 0.0))
    overlay = {
        'soft': {
            'connector_share': profile['connector_share'] + delta * 0.35,
            'sentinel_share': profile['sentinel_share'] + delta * 0.15,
            'mediator_share': profile['mediator_share'] + delta * 0.10,
            'analyzer_share': profile['analyzer_share'] + delta * 0.20,
            'rewire_cross_group_bonus': profile['rewire_cross_group_bonus'] + delta * 0.20,
            'group_learning_rate': profile['group_learning_rate'] + delta * 0.10,
        },
        'balanced': {
            'connector_share': profile['connector_share'] + delta * 0.20,
            'sentinel_share': profile['sentinel_share'] + delta * 0.20,
            'mediator_share': profile['mediator_share'] + delta * 0.10,
            'analyzer_share': profile['analyzer_share'] + delta * 0.20,
            'rewire_cross_group_bonus': profile['rewire_cross_group_bonus'] - delta * 0.05,
            'group_learning_rate': profile['group_learning_rate'] + delta * 0.16,
            'meta_priority_strength': profile['meta_priority_strength'] + delta * 0.12,
            'cluster_budget_skew': profile['cluster_budget_skew'] + delta * 0.30,
        },
        'hard': {
            'connector_share': profile['connector_share'] - delta * 0.06,
            'sentinel_share': profile['sentinel_share'] + delta * 0.24,
            'mediator_share': profile['mediator_share'] - delta * 0.10,
            'analyzer_share': profile['analyzer_share'] + delta * 0.26,
            'rewire_cross_group_bonus': max(0.0, profile['rewire_cross_group_bonus'] - delta * 0.20),
            'group_learning_rate': profile['group_learning_rate'] + delta * 0.20,
            'meta_priority_strength': profile['meta_priority_strength'] + delta * 0.20,
            'cluster_budget_skew': profile['cluster_budget_skew'] + delta * 0.60,
            'sentinel_rep_threshold': profile['sentinel_rep_threshold'] + delta * 0.15,
        },
    }[eintrag['identity_mode']]

    profile.update(overlay)
    profile['generalist_share'] = max(
        0.05,
        1.0
        - profile.get('connector_share', 0.0)
        - profile.get('sentinel_share', 0.0)
        - profile.get('mediator_share', 0.0)
        - profile.get('analyzer_share', 0.0),
    )
    return profile


def dna_overlay_metrics(config, params):
    dna_keys = [
        'connector_share',
        'sentinel_share',
        'mediator_share',
        'analyzer_share',
        'group_learning_rate',
        'meta_priority_strength',
        'cluster_budget_skew',
        'rewire_cross_group_bonus',
    ]
    basis = basis_dna()
    deviations = []
    for key in dna_keys:
        baseline = float(basis[key])
        current = float(config.get(key, baseline))
        deviations.append(abs(current - baseline) / max(0.05, abs(baseline)))

    overlay_intensity = mittelwert(deviations)
    dna_cohesion = max(0.0, 1.0 - overlay_intensity * params['dna_similarity_weight'])
    fragmentation_risk = max(0.0, overlay_intensity - params['overlay_fragmentation_threshold'])
    return {
        'overlay_intensity': overlay_intensity,
        'dna_cohesion': dna_cohesion,
        'fragmentation_risk': fragmentation_risk,
    }


def run_context(seed, params, katalog, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    profile = build_profile(katalog, eintrag)
    config.update(profile)
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
    result['identity_metrics'] = dna_overlay_metrics(config, params)
    return result


def context_score(kontext_name, result):
    workflow = result['workflow_metrics']
    identity = result['identity_metrics']
    base = result['final_consensus_score'] - result['final_polarization_index']
    cooperation = result['cross_group_cooperation_rate']
    dna_cohesion = identity['dna_cohesion']
    fragmentation_risk = identity['fragmentation_risk']
    overlay_intensity = identity['overlay_intensity']
    detection = workflow.get('misinformation_detection_rate', 0.0)
    corruption = workflow.get('misinformation_corruption_mean', 0.0)
    skill = workflow.get('skill_alignment_rate', 0.0)
    meta = workflow.get('meta_alignment_rate', 0.0)

    if kontext_name == 'polarization':
        return base + 0.16 * cooperation + 0.18 * dna_cohesion - 0.20 * fragmentation_risk + 0.06 * skill
    if kontext_name == 'consensus':
        return (
            result['final_consensus_score']
            + 0.12 * dna_cohesion
            + 0.08 * meta
            + 0.06 * skill
            - 0.12 * fragmentation_risk
        )
    return (
        base
        + 0.10 * detection
        + 0.10 * dna_cohesion
        + 0.06 * overlay_intensity
        - 0.14 * fragmentation_risk
        - 0.08 * corruption
    )


def summarize_runs(runs, eintrag, context_list):
    context_scores = {}
    dna_cohesion = {}
    overlay_intensity = {}
    fragmentation = {}
    detection = {}
    corruption = {}

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name]) for run in runs])
        dna_cohesion[name] = mittelwert([run[name]['identity_metrics']['dna_cohesion'] for run in runs])
        overlay_intensity[name] = mittelwert([run[name]['identity_metrics']['overlay_intensity'] for run in runs])
        fragmentation[name] = mittelwert([run[name]['identity_metrics']['fragmentation_risk'] for run in runs])
        detection[name] = mittelwert(
            [run[name]['workflow_metrics'].get('misinformation_detection_rate', 0.0) for run in runs]
        )
        corruption[name] = mittelwert(
            [run[name]['workflow_metrics'].get('misinformation_corruption_mean', 0.0) for run in runs]
        )

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']]) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        'dna_cohesion': dna_cohesion,
        'overlay_intensity': overlay_intensity,
        'fragmentation': fragmentation,
        'detection': detection,
        'corruption': corruption,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    eintraege = overlay_profiles()
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI GRUPPENIDENTITAETS-STUDIE')
    print('=' * 84)
    print('Vergleicht gemeinsame Grund-DNA mit unterschiedlich starken Overlay-Profilen')
    print('und misst, wann Spezialisierung in Fragmentierung umschlaegt.\n')

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
            f"{summary['label']:<24} Score={summary['combined_score']:+.3f} | "
            f"DNA={summary['dna_cohesion']['polarization']:.2f} | "
            f"Overlay={summary['overlay_intensity']['polarization']:.2f} | "
            f"Fragmentierung={summary['fragmentation']['polarization']:.2f}"
        )

    best = max(zusammenfassungen, key=lambda item: item['combined_score'])
    baseline = next(item for item in zusammenfassungen if item['name'] == 'homogen')

    print('\nBeste Identitaetsarchitektur:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur Homogenitaet {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"DNA-Kohäsion {best['dna_cohesion']['polarization']:.2f}, "
        f"Overlay-Intensitaet {best['overlay_intensity']['polarization']:.2f}, "
        f"Fragmentierungsrisiko {best['fragmentation']['polarization']:.2f}"
    )

    labels = [item['label'] for item in zusammenfassungen]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#4e79a7', '#59a14f', '#f28e2b', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in zusammenfassungen], color=colors)
    axes[0, 0].set_title('Kombinierter DNA-/Overlay-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['dna_cohesion']['polarization'] for item in zusammenfassungen],
        width,
        label='DNA-Kohäsion',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['overlay_intensity']['polarization'] for item in zusammenfassungen],
        width,
        label='Overlay-Intensitaet',
        color='#59a14f',
    )
    axes[0, 1].set_title('Grund-DNA vs. Overlay')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['detection']['stress'] * 100.0 for item in zusammenfassungen],
        width,
        label='Detektion (%)',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [(1.0 - item['corruption']['stress']) * 100.0 for item in zusammenfassungen],
        width,
        label='Integritaet (%)',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Stressrobustheit')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['dna_cohesion']['polarization'],
                item['overlay_intensity']['polarization'],
                item['fragmentation']['polarization'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
            ]
            for item in zusammenfassungen
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='magma_r', aspect='auto')
    axes[1, 0].set_title('Identitaetsmetriken')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['DNA', 'Overlay', 'Frag', 'Kon', 'Stress'])
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
            f"- Beste Architektur: {best['label']}\n"
            f"- Delta zur Homogenitaet: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- DNA-Kohäsion: {best['dna_cohesion']['polarization']:.2f}\n"
            f"- Overlay-Intensitaet: {best['overlay_intensity']['polarization']:.2f}\n"
            f"- Fragmentierungsrisiko: {best['fragmentation']['polarization']:.2f}\n"
            f"- Stress-Detektion: {best['detection']['stress']:.1%}\n"
            f"- Stress-Korruption: {best['corruption']['stress']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_gruppenidentitaet.png', dpi=150)


if __name__ == '__main__':
    main()
