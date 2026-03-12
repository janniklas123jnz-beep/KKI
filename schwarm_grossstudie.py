"""
KKI Kombinierte Grossstudie
===========================
Fuehrt Polarisierung, Invasion und Commitment-Angriffe unter einer gemeinsamen
Agenten-Grundkonfiguration zusammen und vergleicht statische gegen adaptive
Abwehr.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_commitment_resilienz import run_commitment_experiment, strategieprofil
from schwarm_invasive_netzwerke import run_invasion_experiment
from schwarm_polarisierung import DEFAULT_RANDOM_EDGE_CHANCE, run_polarization_experiment


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_MEGASTUDY_REPETITIONS', '2'))
        rounds = int(os.getenv('KKI_TEST_ROUNDS', '6'))
        interactions = int(os.getenv('KKI_TEST_INTERACTIONS', '8'))
        stress_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_MEGASTUDY_REPETITIONS', '2'))
        rounds = int(os.getenv('KKI_MEGASTUDY_ROUNDS', '180'))
        interactions = int(os.getenv('KKI_MEGASTUDY_INTERACTIONS', '90'))
        stress_round = int(os.getenv('KKI_MEGASTUDY_STRESS_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'stress_round': stress_round,
        'agent_count': int(os.getenv('KKI_MEGASTUDY_AGENT_COUNT', '60')),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', '8')),
        'cross_group': float(os.getenv('KKI_CROSS_GROUP_CHANCE', '0.35')),
        'invasion_count': int(os.getenv('KKI_INVASION_AGENT_COUNT', '12')),
        'attacker_count': int(os.getenv('KKI_ATTACKER_AGENT_COUNT', '8')),
        'attack_strength': float(os.getenv('KKI_COMMITMENT_ATTACK_STRENGTH', '0.45')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def evaluate_polarization(seed, params, adaptive_enabled):
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
        'enable_dynamic_rewiring': adaptive_enabled,
        'rewire_min_interactions': 3,
        'rewire_reputation_threshold': 0.35,
        'rewire_opinion_distance_threshold': 0.55,
        'rewire_proximity_weight': 0.65,
        'rewire_removal_probability': 0.35,
        'rewire_addition_probability': 0.75,
        'rewire_cross_group_bonus': 0.08,
        'rewire_target_degree': params['degree'],
    }
    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    score = result['final_consensus_score'] - result['final_polarization_index']
    return {
        'score': score,
        'primary_metric': result['final_consensus_score'],
        'threat_metric': result['final_polarization_index'],
        'edge_metric': result['cross_group_interaction_rate'],
    }


def evaluate_invasion(seed, params, adaptive_enabled):
    random.seed(seed)
    np.random.seed(seed)
    result = run_invasion_experiment(
        {
            'native_count': params['agent_count'],
            'invasion_count': params['invasion_count'],
            'rounds': params['rounds'],
            'invasion_round': params['stress_round'],
            'interactions': params['interactions'],
            'degree': params['degree'],
            'cross_group': params['cross_group'],
            'random_edge_chance': DEFAULT_RANDOM_EDGE_CHANCE,
        },
        adaptive_enabled=adaptive_enabled,
        rep_threshold=0.35,
        proximity_weight=0.85,
    )
    return {
        'score': result['resilience_score'],
        'primary_metric': result['resilience_ratio'],
        'threat_metric': result['repulsion_index'],
        'edge_metric': result['final_invader_edge_share'],
    }


def evaluate_commitment(seed, params, adaptive_enabled):
    random.seed(seed)
    np.random.seed(seed)
    hybrid = strategieprofil('hybrid')
    config = {
        'native_count': params['agent_count'],
        'attacker_count': params['attacker_count'],
        'rounds': params['rounds'],
        'attack_round': params['stress_round'],
        'interactions': params['interactions'],
        'degree': params['degree'],
        'attack_strength': params['attack_strength'],
        'strategy_name': 'hybrid' if adaptive_enabled else 'static',
        'strategy_weights': hybrid['weights'] if adaptive_enabled else None,
        'signal_threshold': hybrid['threshold'] if adaptive_enabled else None,
    }
    result = run_commitment_experiment(
        config,
        adaptive_enabled=adaptive_enabled,
        rep_threshold=0.55,
        trust_threshold=0.55,
    )
    return {
        'score': result['resilience_score'],
        'primary_metric': result['native_retention'],
        'threat_metric': result['detection_rate'],
        'edge_metric': result['manipulator_edge_share'],
    }


def scenario_results(seed, params):
    evaluators = {
        'Polarisierung': evaluate_polarization,
        'Invasion': evaluate_invasion,
        'Commitment': evaluate_commitment,
    }
    results = {}
    for name, evaluator in evaluators.items():
        static = evaluator(seed, params, False)
        adaptive = evaluator(seed, params, True)
        results[name] = {'static': static, 'adaptive': adaptive}
    return results


def aggregate_results(runs):
    scenario_names = list(runs[0].keys())
    aggregated = {}
    for scenario in scenario_names:
        static_runs = [run[scenario]['static'] for run in runs]
        adaptive_runs = [run[scenario]['adaptive'] for run in runs]
        aggregated[scenario] = {
            'static_score': mittelwert([item['score'] for item in static_runs]),
            'adaptive_score': mittelwert([item['score'] for item in adaptive_runs]),
            'static_primary': mittelwert([item['primary_metric'] for item in static_runs]),
            'adaptive_primary': mittelwert([item['primary_metric'] for item in adaptive_runs]),
            'static_threat': mittelwert([item['threat_metric'] for item in static_runs]),
            'adaptive_threat': mittelwert([item['threat_metric'] for item in adaptive_runs]),
            'static_edge': mittelwert([item['edge_metric'] for item in static_runs]),
            'adaptive_edge': mittelwert([item['edge_metric'] for item in adaptive_runs]),
        }
        aggregated[scenario]['score_delta'] = (
            aggregated[scenario]['adaptive_score'] - aggregated[scenario]['static_score']
        )
        aggregated[scenario]['edge_delta'] = (
            aggregated[scenario]['adaptive_edge'] - aggregated[scenario]['static_edge']
        )
    return aggregated


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI KOMBINIERTE GROSSSTUDIE")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Agenten-Grund-DNA: {params['agent_count']} | "
        f"Runden: {params['rounds']} | Stress ab Runde {params['stress_round']}"
    )
    print(
        f"Bedrohungen: Polarisierung, Invasion, Commitment-Angriffe | "
        f"Wiederholungen: {params['repetitions']}"
    )
    print(
        "Ziel: Gleiche Grundarchitektur, aber statische gegen adaptive Zusammenarbeit "
        "unter mehreren Stressoren vergleichen."
    )
    print("\nGrossstudie läuft...\n")

    runs = []
    for repetition in range(params['repetitions']):
        seed = base_seed + repetition
        runs.append(scenario_results(seed, params))

    aggregated = aggregate_results(runs)
    scenarios = list(aggregated.keys())
    combined_delta = mittelwert([aggregated[name]['score_delta'] for name in scenarios])
    combined_edge_delta = mittelwert([aggregated[name]['edge_delta'] for name in scenarios])
    best_scenario = max(scenarios, key=lambda name: aggregated[name]['score_delta'])

    for scenario in scenarios:
        result = aggregated[scenario]
        print(
            f"{scenario:>13s} -> "
            f"statisch={result['static_score']:+.3f}, "
            f"adaptiv={result['adaptive_score']:+.3f}, "
            f"Delta={result['score_delta']:+.3f}"
        )

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Staerkster adaptiver Vorteil:\n"
        f"  Szenario:                 {best_scenario}\n"
        f"  Score-Delta:              {aggregated[best_scenario]['score_delta']:+.3f}\n"
        f"  Kanten-Delta:             {aggregated[best_scenario]['edge_delta']:+.3f}\n"
        f"  Adaptive Score:           {aggregated[best_scenario]['adaptive_score']:+.3f}\n"
        f"  Statischer Score:         {aggregated[best_scenario]['static_score']:+.3f}\n"
        f"  Gemitteltes Score-Delta:  {combined_delta:+.3f}\n"
        f"  Gemitteltes Kanten-Delta: {combined_edge_delta:+.3f}"
    )
    print(
        "\nInterpretation:\n"
        "Die gemeinsame Grund-DNA bleibt in allen drei Bedrohungsszenarien erhalten. "
        "Adaptive Zusammenarbeit verbessert die Resilienz dort am staerksten, wo "
        "soziale Isolation von Stoerern oder manipulativen Akteuren schnell greift."
    )

    static_scores = np.array([aggregated[name]['static_score'] for name in scenarios], dtype=float)
    adaptive_scores = np.array([aggregated[name]['adaptive_score'] for name in scenarios], dtype=float)
    score_deltas = np.array([aggregated[name]['score_delta'] for name in scenarios], dtype=float)
    primary_matrix = np.array(
        [
            [aggregated[name]['static_primary'], aggregated[name]['adaptive_primary']]
            for name in scenarios
        ],
        dtype=float,
    )
    threat_matrix = np.array(
        [
            [aggregated[name]['static_threat'], aggregated[name]['adaptive_threat']]
            for name in scenarios
        ],
        dtype=float,
    )
    edge_matrix = np.array(
        [
            [aggregated[name]['static_edge'], aggregated[name]['adaptive_edge']]
            for name in scenarios
        ],
        dtype=float,
    )

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        'KKI Grossstudie: Polarisierung, Invasion und Commitment-Angriffe',
        fontsize=14,
        fontweight='bold',
    )

    x = np.arange(len(scenarios))
    width = 0.35
    axes[0, 0].bar(x - width / 2, static_scores, width, label='Statisch', color='#5B84B1')
    axes[0, 0].bar(x + width / 2, adaptive_scores, width, label='Adaptiv', color='#48A868')
    axes[0, 0].set_title('Szenario-Scores')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(scenarios)
    axes[0, 0].legend()
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(x, score_deltas, color='#8172B2')
    axes[0, 1].axhline(0.0, color='black', linewidth=1)
    axes[0, 1].set_title('Adaptive Score-Deltas')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(scenarios)
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    heatmaps = [
        (
            axes[1, 0],
            primary_matrix,
            'Primaermetriken\n(statisch | adaptiv)',
            'Blues',
        ),
        (
            axes[1, 1],
            edge_matrix,
            'Stoerer-Einbettung / Brueckenrate\n(statisch | adaptiv)',
            'magma_r',
        ),
    ]

    for axis, matrix, title, cmap in heatmaps:
        image = axis.imshow(matrix, cmap=cmap, aspect='auto')
        axis.set_title(title)
        axis.set_xticks([0, 1])
        axis.set_xticklabels(['Statisch', 'Adaptiv'])
        axis.set_yticks(range(len(scenarios)))
        axis.set_yticklabels(scenarios)

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, f'{matrix[row, col]:.2f}', ha='center', va='center', fontsize=9)

        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    fig.text(
        0.5,
        0.02,
        (
            f"Gemitteltes adaptive Score-Delta: {combined_delta:+.3f} | "
            f"Staerkster Vorteil: {best_scenario}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_grossstudie.png', dpi=150)


if __name__ == '__main__':
    main()
