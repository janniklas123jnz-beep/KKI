"""
KKI Adaptive Netzwerk-Studie
============================
Vergleicht adaptive Rewiring-Konfigurationen mit einem statischen Basisnetzwerk.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_RANDOM_EDGE_CHANCE,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def parse_float_grid(name: str, default_values):
    raw = os.getenv(name)
    if not raw:
        return list(default_values)
    return [float(value.strip()) for value in raw.split(',') if value.strip()]


def adaptive_parameter():
    if is_test_mode():
        rep_thresholds = parse_float_grid('KKI_ADAPTIVE_REP_THRESHOLDS', [0.25, 0.4])
        proximity_weights = parse_float_grid('KKI_ADAPTIVE_PROXIMITY_WEIGHTS', [0.25, 0.55])
        repetitions = int(os.getenv('KKI_ADAPTIVE_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
    else:
        rep_thresholds = parse_float_grid('KKI_ADAPTIVE_REP_THRESHOLDS', [0.25, 0.35, 0.45, 0.55])
        proximity_weights = parse_float_grid('KKI_ADAPTIVE_PROXIMITY_WEIGHTS', [0.25, 0.45, 0.65, 0.85])
        repetitions = int(os.getenv('KKI_ADAPTIVE_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND

    return {
        'rep_thresholds': rep_thresholds,
        'proximity_weights': proximity_weights,
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'degree': int(os.getenv('KKI_ADAPTIVE_BASE_DEGREE', '8')),
        'cross_group': float(os.getenv('KKI_ADAPTIVE_BASE_CROSS_GROUP', '0.45')),
        'random_edge_chance': float(os.getenv('KKI_RANDOM_EDGE_CHANCE', str(DEFAULT_RANDOM_EDGE_CHANCE))),
        'target_degree': int(os.getenv('KKI_REWIRE_TARGET_DEGREE', '8')),
        'cross_group_bonus': float(os.getenv('KKI_REWIRE_CROSS_GROUP_BONUS', '0.08')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def run_once(seed, scenario, params, *, rewiring_enabled, rep_threshold=None, proximity_weight=None):
    random.seed(seed)
    np.random.seed(seed)

    config = {
        'scenario': scenario,
        'agent_count': DEFAULT_AGENT_COUNT,
        'rounds': params['rounds'],
        'interactions_per_round': params['interactions'],
        'connections_per_agent': params['degree'],
        'cross_group_chance': params['cross_group'],
        'random_edge_chance': params['random_edge_chance'],
        'enable_dynamic_rewiring': rewiring_enabled,
        'rewire_min_interactions': 3,
        'rewire_reputation_threshold': rep_threshold if rep_threshold is not None else 0.35,
        'rewire_opinion_distance_threshold': 0.55,
        'rewire_proximity_weight': proximity_weight if proximity_weight is not None else 0.45,
        'rewire_removal_probability': 0.35,
        'rewire_addition_probability': 0.75,
        'rewire_cross_group_bonus': params['cross_group_bonus'],
        'rewire_target_degree': params['target_degree'],
    }
    return run_polarization_experiment(config, make_plot=False, print_summary=False)


def baseline_metrics(params, base_seed):
    polarization_runs = []
    consensus_runs = []

    for repetition in range(params['repetitions']):
        seed = base_seed + repetition
        polarization = run_once(seed, 'polarization', params, rewiring_enabled=False)
        consensus = run_once(seed, 'consensus', params, rewiring_enabled=False)
        polarization_runs.append(polarization['final_polarization_index'])
        consensus_runs.append(consensus['final_consensus_score'])

    baseline_polarization = mittelwert(polarization_runs)
    baseline_consensus = mittelwert(consensus_runs)
    return {
        'polarization': baseline_polarization,
        'consensus': baseline_consensus,
        'stability': baseline_consensus - baseline_polarization,
    }


def main():
    configure_matplotlib(plt)

    params = adaptive_parameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))
    print("=" * 84)
    print("KKI ADAPTIVE NETZWERK-STUDIE")
    print("=" * 84)
    print(f"Seed-Basis: {base_seed}")
    print(
        f"Basisnetz: Grad={params['degree']}, Cross-Group={params['cross_group']:.2f}, "
        f"Repetitionen={params['repetitions']}"
    )
    print(
        f"Rep-Schwellen: {params['rep_thresholds']} | "
        f"Proximity-Gewichte: {params['proximity_weights']}"
    )
    print("\nStudie läuft...\n")

    baseline = baseline_metrics(params, base_seed)
    print(
        "Statisches Basisnetz:\n"
        f"  Polarisierungs-Index: {baseline['polarization']:.3f}\n"
        f"  Konsens-Score:        {baseline['consensus']:.3f}\n"
        f"  Stabilitäts-Score:    {baseline['stability']:+.3f}\n"
    )

    rep_thresholds = params['rep_thresholds']
    proximity_weights = params['proximity_weights']
    shape = (len(rep_thresholds), len(proximity_weights))

    polarization_matrix = np.zeros(shape)
    consensus_matrix = np.zeros(shape)
    stability_matrix = np.zeros(shape)
    rewiring_matrix = np.zeros(shape)

    best_score = None
    best_setting = None

    for row, rep_threshold in enumerate(rep_thresholds):
        for col, proximity_weight in enumerate(proximity_weights):
            polarization_runs = []
            consensus_runs = []
            rewiring_runs = []

            for repetition in range(params['repetitions']):
                seed = base_seed + row * 100 + col * 10 + repetition
                polarization = run_once(
                    seed,
                    'polarization',
                    params,
                    rewiring_enabled=True,
                    rep_threshold=rep_threshold,
                    proximity_weight=proximity_weight,
                )
                consensus = run_once(
                    seed,
                    'consensus',
                    params,
                    rewiring_enabled=True,
                    rep_threshold=rep_threshold,
                    proximity_weight=proximity_weight,
                )

                polarization_runs.append(polarization['final_polarization_index'])
                consensus_runs.append(consensus['final_consensus_score'])
                rewiring_runs.append(polarization['average_rewired_edges_per_round'])
                rewiring_runs.append(consensus['average_rewired_edges_per_round'])

            polarization_matrix[row, col] = mittelwert(polarization_runs)
            consensus_matrix[row, col] = mittelwert(consensus_runs)
            rewiring_matrix[row, col] = mittelwert(rewiring_runs)
            stability_matrix[row, col] = consensus_matrix[row, col] - polarization_matrix[row, col]

            print(
                f"Rep={rep_threshold:.2f}, Proximity={proximity_weight:.2f} -> "
                f"PI={polarization_matrix[row, col]:.3f}, "
                f"Konsens={consensus_matrix[row, col]:.3f}, "
                f"Stabilität={stability_matrix[row, col]:+.3f}, "
                f"Rewiring={rewiring_matrix[row, col]:.2f}/Runde"
            )

            if best_score is None or stability_matrix[row, col] > best_score:
                best_score = stability_matrix[row, col]
                best_setting = {
                    'rep_threshold': rep_threshold,
                    'proximity_weight': proximity_weight,
                    'polarization': polarization_matrix[row, col],
                    'consensus': consensus_matrix[row, col],
                    'stability': stability_matrix[row, col],
                    'rewiring': rewiring_matrix[row, col],
                }

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste adaptive Konfiguration:\n"
        f"  Reputations-Schwelle: {best_setting['rep_threshold']:.2f}\n"
        f"  Proximity-Gewicht:    {best_setting['proximity_weight']:.2f}\n"
        f"  Polarisierungs-Index: {best_setting['polarization']:.3f}\n"
        f"  Konsens-Score:        {best_setting['consensus']:.3f}\n"
        f"  Stabilitäts-Score:    {best_setting['stability']:+.3f}\n"
        f"  Ø Rewiring/Runde:     {best_setting['rewiring']:.2f}"
    )
    print(
        "\nDelta zum statischen Basisnetz:\n"
        f"  Δ Polarisierung: {best_setting['polarization'] - baseline['polarization']:+.3f}\n"
        f"  Δ Konsens:       {best_setting['consensus'] - baseline['consensus']:+.3f}\n"
        f"  Δ Stabilität:    {best_setting['stability'] - baseline['stability']:+.3f}"
    )

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle(
        'KKI Adaptive Netzwerke: Rewiring gegen Polarisierung',
        fontsize=14,
        fontweight='bold',
    )

    heatmaps = [
        (axes[0, 0], polarization_matrix, 'Polarisierungs-Index\n(kleiner ist besser)', 'magma_r'),
        (axes[0, 1], consensus_matrix, 'Konsens-Score\n(größer ist besser)', 'viridis'),
        (axes[1, 0], stability_matrix, 'Stabilitäts-Score\n(Konsens - Polarisierung)', 'coolwarm'),
        (axes[1, 1], rewiring_matrix, 'Ø Rewiring pro Runde', 'Blues'),
    ]

    for axis, matrix, title, cmap in heatmaps:
        image = axis.imshow(matrix, cmap=cmap, aspect='auto')
        axis.set_title(title)
        axis.set_xlabel('Proximity-Gewicht')
        axis.set_ylabel('Reputations-Schwelle')
        axis.set_xticks(range(len(proximity_weights)))
        axis.set_xticklabels([f'{value:.2f}' for value in proximity_weights])
        axis.set_yticks(range(len(rep_thresholds)))
        axis.set_yticklabels([f'{value:.2f}' for value in rep_thresholds])

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, f'{matrix[row, col]:.2f}', ha='center', va='center', fontsize=9)

        if title.startswith('Stabilitäts'):
            best_row = rep_thresholds.index(best_setting['rep_threshold'])
            best_col = proximity_weights.index(best_setting['proximity_weight'])
            axis.scatter(best_col, best_row, s=140, facecolors='none', edgecolors='white', linewidths=2)

        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    fig.text(
        0.5,
        0.02,
        (
            f"Statisches Basisnetz: PI={baseline['polarization']:.3f}, "
            f"Konsens={baseline['consensus']:.3f}, Stabilität={baseline['stability']:+.3f}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_adaptive_netzwerke.png', dpi=150)


if __name__ == '__main__':
    main()
