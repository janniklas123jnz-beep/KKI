"""
KKI Netzwerk-Parameterstudie
============================
Vergleicht Netzwerkeinstellungen darauf, wie gut sie Polarisierung reduzieren,
ohne robuste Konsenszonen zu verlieren.
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


def parse_int_grid(name: str, default_values):
    raw = os.getenv(name)
    if not raw:
        return list(default_values)
    return [int(value.strip()) for value in raw.split(',') if value.strip()]


def parse_float_grid(name: str, default_values):
    raw = os.getenv(name)
    if not raw:
        return list(default_values)
    return [float(value.strip()) for value in raw.split(',') if value.strip()]


def studienparameter():
    if is_test_mode():
        degrees = parse_int_grid('KKI_STUDY_DEGREES', [4, 8])
        cross_group = parse_float_grid('KKI_STUDY_CROSS_GROUPS', [0.08, 0.25])
        repetitions = int(os.getenv('KKI_STUDY_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
    else:
        degrees = parse_int_grid('KKI_STUDY_DEGREES', [4, 6, 8, 10])
        cross_group = parse_float_grid('KKI_STUDY_CROSS_GROUPS', [0.05, 0.15, 0.25, 0.35, 0.45])
        repetitions = int(os.getenv('KKI_STUDY_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND

    return {
        'degrees': degrees,
        'cross_group': cross_group,
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
    }


def mittelwerte(values):
    return float(np.mean(values)) if values else 0.0


def main():
    configure_matplotlib(plt)

    params = studienparameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))
    print("=" * 84)
    print("KKI NETZWERK-PARAMETERSTUDIE")
    print("=" * 84)
    print(f"Seed-Basis: {base_seed}")
    print(
        f"Grad-Grid: {params['degrees']} | Cross-Group-Grid: {params['cross_group']} | "
        f"Wiederholungen: {params['repetitions']}"
    )
    print("\nStudie läuft...\n")

    degrees = params['degrees']
    cross_group_values = params['cross_group']
    shape = (len(degrees), len(cross_group_values))

    polarization_pi = np.zeros(shape)
    consensus_score = np.zeros(shape)
    stability_score = np.zeros(shape)
    cross_group_rate = np.zeros(shape)

    best_score = None
    best_setting = None

    for i, degree in enumerate(degrees):
        for j, cross_group in enumerate(cross_group_values):
            polarization_runs = []
            consensus_runs = []
            cross_group_runs = []

            for repetition in range(params['repetitions']):
                seed = base_seed + i * 100 + j * 10 + repetition
                for scenario in ('polarization', 'consensus'):
                    random.seed(seed)
                    np.random.seed(seed)
                    result = run_polarization_experiment(
                        {
                            'scenario': scenario,
                            'agent_count': DEFAULT_AGENT_COUNT,
                            'rounds': params['rounds'],
                            'interactions_per_round': params['interactions'],
                            'connections_per_agent': degree,
                            'cross_group_chance': cross_group,
                            'random_edge_chance': DEFAULT_RANDOM_EDGE_CHANCE,
                        },
                        make_plot=False,
                        print_summary=False,
                    )

                    if scenario == 'polarization':
                        polarization_runs.append(result['final_polarization_index'])
                    else:
                        consensus_runs.append(result['final_consensus_score'])

                    cross_group_runs.append(result['cross_group_interaction_rate'])

            polarization_pi[i, j] = mittelwerte(polarization_runs)
            consensus_score[i, j] = mittelwerte(consensus_runs)
            cross_group_rate[i, j] = mittelwerte(cross_group_runs)
            stability_score[i, j] = consensus_score[i, j] - polarization_pi[i, j]

            print(
                f"Grad={degree:2d}, Cross={cross_group:.2f} -> "
                f"PI={polarization_pi[i, j]:.3f}, "
                f"Konsens={consensus_score[i, j]:.3f}, "
                f"Stabilität={stability_score[i, j]:+.3f}"
            )

            if best_score is None or stability_score[i, j] > best_score:
                best_score = stability_score[i, j]
                best_setting = {
                    'degree': degree,
                    'cross_group': cross_group,
                    'polarization_pi': polarization_pi[i, j],
                    'consensus_score': consensus_score[i, j],
                    'stability_score': stability_score[i, j],
                    'cross_group_rate': cross_group_rate[i, j],
                }

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste Konfiguration (Stabilität = Konsens-Score - Polarisierungs-Index):\n"
        f"  Verbindungen pro Agent: {best_setting['degree']}\n"
        f"  Cross-Group-Chance:     {best_setting['cross_group']:.2f}\n"
        f"  Polarisierungs-Index:   {best_setting['polarization_pi']:.3f}\n"
        f"  Konsens-Score:          {best_setting['consensus_score']:.3f}\n"
        f"  Stabilitäts-Score:      {best_setting['stability_score']:+.3f}\n"
        f"  Ø gruppenübergreifende Interaktionen: {best_setting['cross_group_rate']:.1%}"
    )

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle(
        'KKI Netzwerk-Parameterstudie: Polarisierung reduzieren, Konsens bewahren',
        fontsize=14,
        fontweight='bold',
    )

    heatmaps = [
        (axes[0, 0], polarization_pi, 'Polarisierungs-Index\n(kleiner ist besser)', 'magma_r'),
        (axes[0, 1], consensus_score, 'Konsens-Score\n(größer ist besser)', 'viridis'),
        (axes[1, 0], stability_score, 'Stabilitäts-Score\n(Konsens - Polarisierung)', 'coolwarm'),
        (axes[1, 1], cross_group_rate, 'Ø gruppenübergreifende Interaktionen', 'Blues'),
    ]

    for axis, matrix, title, cmap in heatmaps:
        image = axis.imshow(matrix, cmap=cmap, aspect='auto')
        axis.set_title(title)
        axis.set_xlabel('Cross-Group-Chance')
        axis.set_ylabel('Verbindungen pro Agent')
        axis.set_xticks(range(len(cross_group_values)))
        axis.set_xticklabels([f'{value:.2f}' for value in cross_group_values])
        axis.set_yticks(range(len(degrees)))
        axis.set_yticklabels([str(value) for value in degrees])

        for row in range(matrix.shape[0]):
            for col in range(matrix.shape[1]):
                axis.text(col, row, f'{matrix[row, col]:.2f}', ha='center', va='center', fontsize=9)

        if title.startswith('Stabilitäts'):
            best_row = degrees.index(best_setting['degree'])
            best_col = cross_group_values.index(best_setting['cross_group'])
            axis.scatter(best_col, best_row, s=140, facecolors='none', edgecolors='white', linewidths=2)

        fig.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    plt.tight_layout()
    save_and_maybe_show(plt, 'kki_netzwerk_parameterstudie.png', dpi=150)


if __name__ == '__main__':
    main()
