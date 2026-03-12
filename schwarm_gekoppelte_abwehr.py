"""
KKI Gekoppelte Abwehrstudie
===========================
Vergleicht Architekturprofile ueber Polarisierung, Invasion und
Commitment-Angriffe hinweg.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_anti_polarisierung import mechanismen
from schwarm_grossstudie import evaluate_commitment, evaluate_invasion
from schwarm_polarisierung import DEFAULT_RANDOM_EDGE_CHANCE, run_polarization_experiment


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_COUPLED_REPETITIONS', '2'))
        rounds = int(os.getenv('KKI_TEST_ROUNDS', '6'))
        interactions = int(os.getenv('KKI_TEST_INTERACTIONS', '8'))
        stress_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_COUPLED_REPETITIONS', '3'))
        rounds = int(os.getenv('KKI_COUPLED_ROUNDS', '180'))
        interactions = int(os.getenv('KKI_COUPLED_INTERACTIONS', '90'))
        stress_round = int(os.getenv('KKI_COUPLED_STRESS_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'stress_round': stress_round,
        'agent_count': int(os.getenv('KKI_COUPLED_AGENT_COUNT', '60')),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', '8')),
        'cross_group': float(os.getenv('KKI_CROSS_GROUP_CHANCE', '0.35')),
        'invasion_count': int(os.getenv('KKI_INVASION_AGENT_COUNT', '12')),
        'attacker_count': int(os.getenv('KKI_ATTACKER_AGENT_COUNT', '8')),
        'attack_strength': float(os.getenv('KKI_COMMITMENT_ATTACK_STRENGTH', '0.45')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def adaptive_polarization_config():
    return {
        'name': 'adaptive',
        'label': 'Adaptive Abwehr',
        'enable_dynamic_rewiring': True,
        'rewire_min_interactions': 3,
        'rewire_reputation_threshold': 0.35,
        'rewire_opinion_distance_threshold': 0.55,
        'rewire_proximity_weight': 0.65,
        'rewire_removal_probability': 0.35,
        'rewire_addition_probability': 0.75,
        'rewire_cross_group_bonus': 0.08,
    }


def architekturprofile(params):
    mechanismen_map = {mechanism['name']: mechanism for mechanism in mechanismen()}
    adaptive_only = adaptive_polarization_config()
    adaptive_only['rewire_target_degree'] = params['degree']

    anti_polar = dict(mechanismen_map['hybrid'])
    anti_polar['rewire_target_degree'] = params['degree']

    coupled = dict(anti_polar)
    coupled['name'] = 'coupled'
    coupled['label'] = 'Gekoppelt'

    return [
        {
            'name': 'static',
            'label': 'Statisch',
            'polarization_config': dict(mechanismen_map['baseline']),
            'adaptive_other': False,
        },
        {
            'name': 'anti-polarization',
            'label': 'Nur Anti-Pol',
            'polarization_config': anti_polar,
            'adaptive_other': False,
        },
        {
            'name': 'adaptive-defense',
            'label': 'Nur Abwehr',
            'polarization_config': adaptive_only,
            'adaptive_other': True,
        },
        {
            'name': 'coupled',
            'label': 'Gekoppelt',
            'polarization_config': coupled,
            'adaptive_other': True,
        },
    ]


def evaluate_polarization_profile(seed, params, mechanism):
    random.seed(seed)
    np.random.seed(seed)
    config = {
        'scenario': 'polarization',
        'agent_count': params['agent_count'],
        'rounds': params['rounds'],
        'interactions_per_round': params['interactions'],
        'connections_per_agent': params['degree'],
        'cross_group_chance': 0.08,
        'random_edge_chance': DEFAULT_RANDOM_EDGE_CHANCE,
        'enable_dynamic_rewiring': False,
        'center_zone_min': 0.35,
        'center_zone_max': 0.65,
    }
    config.update(
        {
            key: value
            for key, value in mechanism.items()
            if key not in {'name', 'label'}
        }
    )
    config.setdefault('rewire_target_degree', params['degree'])
    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    return {
        'score': result['final_consensus_score'] - result['final_polarization_index'],
        'primary_metric': result['final_consensus_score'],
        'threat_metric': result['final_polarization_index'],
        'edge_metric': result['cross_group_cooperation_rate'],
    }


def evaluate_commitment_profile(seed, params, profile):
    return evaluate_commitment(seed, params, profile['adaptive_other'])


def run_profiles(seed, params, profiles):
    scenario_names = ['Polarisierung', 'Invasion', 'Commitment']
    results = {}
    for index, profile in enumerate(profiles):
        profile_seed = seed + index * 100
        results[profile['label']] = {
            'Polarisierung': evaluate_polarization_profile(
                profile_seed,
                params,
                profile['polarization_config'],
            ),
            'Invasion': evaluate_invasion(profile_seed + 1, params, profile['adaptive_other']),
            'Commitment': evaluate_commitment_profile(profile_seed + 2, params, profile),
        }
    return scenario_names, results


def aggregate_results(runs, profile_labels, scenario_names):
    aggregated = {}
    for profile_label in profile_labels:
        aggregated[profile_label] = {}
        for scenario in scenario_names:
            scenario_runs = [run[profile_label][scenario] for run in runs]
            aggregated[profile_label][scenario] = {
                'score': mittelwert([item['score'] for item in scenario_runs]),
                'primary_metric': mittelwert([item['primary_metric'] for item in scenario_runs]),
                'threat_metric': mittelwert([item['threat_metric'] for item in scenario_runs]),
                'edge_metric': mittelwert([item['edge_metric'] for item in scenario_runs]),
            }

        scores = [aggregated[profile_label][scenario]['score'] for scenario in scenario_names]
        aggregated[profile_label]['combined_score'] = mittelwert(scores)
        aggregated[profile_label]['combined_edge'] = mittelwert(
            [aggregated[profile_label][scenario]['edge_metric'] for scenario in scenario_names]
        )
    return aggregated


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    profiles = architekturprofile(params)
    profile_labels = [profile['label'] for profile in profiles]
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI GEKOPPELTE ABWEHRSTUDIE")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Agenten-Grund-DNA: {params['agent_count']} | "
        f"Runden: {params['rounds']} | Stress ab Runde {params['stress_round']}"
    )
    print(f"Architekturen: {', '.join(profile_labels)}")
    print("\nStudie läuft...\n")

    scenario_names = []
    runs = []
    for repetition in range(params['repetitions']):
        seed = base_seed + repetition
        scenario_names, result = run_profiles(seed, params, profiles)
        runs.append(result)

    aggregated = aggregate_results(runs, profile_labels, scenario_names)
    baseline_label = profile_labels[0]
    best_profile = max(profile_labels, key=lambda label: aggregated[label]['combined_score'])

    for label in profile_labels:
        print(
            f"{label:>12s} -> "
            f"Score={aggregated[label]['combined_score']:+.3f}, "
            f"Pol={aggregated[label]['Polarisierung']['score']:+.3f}, "
            f"Inv={aggregated[label]['Invasion']['score']:+.3f}, "
            f"Com={aggregated[label]['Commitment']['score']:+.3f}"
        )

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste gekoppelte Abwehrarchitektur:\n"
        f"  Profil:                   {best_profile}\n"
        f"  Gemittelter Score:        {aggregated[best_profile]['combined_score']:+.3f}\n"
        f"  Delta zur Baseline:       {aggregated[best_profile]['combined_score'] - aggregated[baseline_label]['combined_score']:+.3f}\n"
        f"  Polarisierung:            {aggregated[best_profile]['Polarisierung']['score']:+.3f}\n"
        f"  Invasion:                 {aggregated[best_profile]['Invasion']['score']:+.3f}\n"
        f"  Commitment:               {aggregated[best_profile]['Commitment']['score']:+.3f}\n"
        f"  Gemittelter Kantenwert:   {aggregated[best_profile]['combined_edge']:.3f}"
    )
    print(
        "\nInterpretation:\n"
        "Die Studie zeigt, ob Anti-Polarisierung nur lokal hilft oder als Teil einer "
        "breiteren Abwehrarchitektur auch neben Invasions- und Commitment-Schutz bestehen kann."
    )

    score_matrix = np.array(
        [[aggregated[label][scenario]['score'] for scenario in scenario_names] for label in profile_labels],
        dtype=float,
    )
    threat_matrix = np.array(
        [[aggregated[label][scenario]['threat_metric'] for scenario in scenario_names] for label in profile_labels],
        dtype=float,
    )
    edge_matrix = np.array(
        [[aggregated[label][scenario]['edge_metric'] for scenario in scenario_names] for label in profile_labels],
        dtype=float,
    )
    combined_scores = np.array([aggregated[label]['combined_score'] for label in profile_labels], dtype=float)
    deltas = combined_scores - aggregated[baseline_label]['combined_score']

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        'KKI Gekoppelte Abwehr: Anti-Polarisierung, Invasion und Commitment',
        fontsize=14,
        fontweight='bold',
    )

    x = np.arange(len(profile_labels))
    axes[0, 0].bar(x, combined_scores, color='#4C72B0')
    axes[0, 0].set_title('Gemittelte Architektur-Scores')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(profile_labels, rotation=20)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(x, deltas, color='#55A868')
    axes[0, 1].axhline(0.0, color='black', linewidth=1)
    axes[0, 1].set_title('Delta zur statischen Baseline')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(profile_labels, rotation=20)
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    heatmaps = [
        (axes[1, 0], score_matrix, 'Szenario-Scores', 'Blues'),
        (axes[1, 1], edge_matrix, 'Kanten- / Brueckenmetriken', 'magma_r'),
    ]

    for axis, matrix, title, cmap in heatmaps:
        image = axis.imshow(matrix, cmap=cmap, aspect='auto')
        axis.set_title(title)
        axis.set_xticks(range(len(scenario_names)))
        axis.set_xticklabels(scenario_names)
        axis.set_yticks(range(len(profile_labels)))
        axis.set_yticklabels(profile_labels)

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, f'{matrix[row, col]:.2f}', ha='center', va='center', fontsize=9)

        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    fig.text(
        0.5,
        0.02,
        (
            f"Beste Architektur: {best_profile} | "
            f"Delta zur Baseline: {aggregated[best_profile]['combined_score'] - aggregated[baseline_label]['combined_score']:+.3f}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_gekoppelte_abwehr.png', dpi=150)


if __name__ == '__main__':
    main()
