"""
KKI Anti-Polarisierungsstudie
=============================
Vergleicht Baseline, Brueckenagenten, Mittelzonen-Moderation und Hybrid
gegen reine Polarisierung.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_RANDOM_EDGE_CHANCE,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_ANTI_POL_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
    else:
        repetitions = int(os.getenv('KKI_ANTI_POL_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'agent_count': int(os.getenv('KKI_ANTI_POL_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def mechanismen():
    return [
        {'name': 'baseline', 'label': 'Baseline'},
        {
            'name': 'bridge',
            'label': 'Bruecken',
            'enable_bridge_mechanism': True,
            'bridge_cooperation_bonus': 0.08,
        },
        {
            'name': 'centrist',
            'label': 'Mittelzone',
            'enable_centrist_moderation': True,
            'centrist_pull_strength': 0.08,
            'enable_mediator_encouragement': True,
            'mediator_contact_bias': 0.60,
        },
        {
            'name': 'hybrid',
            'label': 'Hybrid',
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 3,
            'rewire_reputation_threshold': 0.30,
            'rewire_opinion_distance_threshold': 0.55,
            'rewire_proximity_weight': 0.65,
            'rewire_removal_probability': 0.35,
            'rewire_addition_probability': 0.75,
            'rewire_cross_group_bonus': 0.08,
            'rewire_target_degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
            'enable_bridge_mechanism': True,
            'bridge_cooperation_bonus': 0.08,
            'enable_centrist_moderation': True,
            'centrist_pull_strength': 0.08,
            'enable_mediator_encouragement': True,
            'mediator_contact_bias': 0.60,
        },
    ]


def run_once(seed, params, mechanism):
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
    config.update({key: value for key, value in mechanism.items() if key not in {'name', 'label'}})
    return run_polarization_experiment(config, make_plot=False, print_summary=False)


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))
    mechanisms = mechanismen()

    print("=" * 84)
    print("KKI ANTI-POLARISIERUNGSSTUDIE")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Agenten: {params['agent_count']} | "
        f"Runden: {params['rounds']} | Wiederholungen: {params['repetitions']}"
    )
    print(f"Mechanismen: {', '.join(mechanism['label'] for mechanism in mechanisms)}")
    print("\nStudie läuft...\n")

    summaries = []
    best_score = None
    best_mechanism = None

    for index, mechanism in enumerate(mechanisms):
        runs = []
        for repetition in range(params['repetitions']):
            seed = base_seed + index * 100 + repetition
            runs.append(run_once(seed, params, mechanism))

        summary = {
            'name': mechanism['name'],
            'label': mechanism['label'],
            'stability_score': mittelwert(
                [run['final_consensus_score'] - run['final_polarization_index'] for run in runs]
            ),
            'polarization_index': mittelwert([run['final_polarization_index'] for run in runs]),
            'consensus_score': mittelwert([run['final_consensus_score'] for run in runs]),
            'cross_group_cooperation_rate': mittelwert([run['cross_group_cooperation_rate'] for run in runs]),
            'bridge_agents': mittelwert([mittelwert(run['bridge_count_history']) for run in runs]),
            'center_zone_agents': mittelwert([mittelwert(run['center_zone_history']) for run in runs]),
        }
        summaries.append(summary)

        print(
            f"{summary['label']:>10s} -> "
            f"Stabilität={summary['stability_score']:+.3f}, "
            f"PI={summary['polarization_index']:.3f}, "
            f"Konsens={summary['consensus_score']:.3f}, "
            f"Cross-Group-Koop={summary['cross_group_cooperation_rate']:.1%}"
        )

        if best_score is None or summary['stability_score'] > best_score:
            best_score = summary['stability_score']
            best_mechanism = summary

    baseline = next(summary for summary in summaries if summary['name'] == 'baseline')

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste Anti-Polarisierungsstrategie:\n"
        f"  Mechanismus:             {best_mechanism['label']}\n"
        f"  Stabilitäts-Score:       {best_mechanism['stability_score']:+.3f}\n"
        f"  Polarisierungs-Index:    {best_mechanism['polarization_index']:.3f}\n"
        f"  Konsens-Score:           {best_mechanism['consensus_score']:.3f}\n"
        f"  Cross-Group-Kooperation: {best_mechanism['cross_group_cooperation_rate']:.1%}\n"
        f"  Ø Brückenagenten:        {best_mechanism['bridge_agents']:.2f}\n"
        f"  Ø Mittelzonen-Agenten:   {best_mechanism['center_zone_agents']:.2f}"
    )
    print(
        "\nDelta zur Baseline:\n"
        f"  Δ Stabilität:    {best_mechanism['stability_score'] - baseline['stability_score']:+.3f}\n"
        f"  Δ Polarisierung: {best_mechanism['polarization_index'] - baseline['polarization_index']:+.3f}\n"
        f"  Δ Konsens:       {best_mechanism['consensus_score'] - baseline['consensus_score']:+.3f}"
    )

    labels = [summary['label'] for summary in summaries]
    x = np.arange(len(labels))

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle(
        'KKI Anti-Polarisierung: Bruecken, Mittelzone und Hybrid',
        fontsize=14,
        fontweight='bold',
    )

    axes[0, 0].bar(x, [summary['stability_score'] for summary in summaries], color='#4C72B0')
    axes[0, 0].set_title('Stabilitäts-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=20)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(x, [summary['polarization_index'] for summary in summaries], color='#C44E52')
    axes[0, 1].set_title('Polarisierungs-Index')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=20)
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(x, [summary['cross_group_cooperation_rate'] for summary in summaries], color='#55A868')
    axes[1, 0].set_title('Cross-Group-Kooperation')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=20)
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x - 0.18, [summary['bridge_agents'] for summary in summaries], width=0.36, label='Brücken', color='#8172B2')
    axes[1, 1].bar(x + 0.18, [summary['center_zone_agents'] for summary in summaries], width=0.36, label='Mittelzone', color='#CCB974')
    axes[1, 1].set_title('Brücken- und Mittelzonen-Agenten')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=20)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    fig.text(
        0.5,
        0.02,
        (
            f"Beste Strategie: {best_mechanism['label']} | "
            f"Stabilität={best_mechanism['stability_score']:+.3f} | "
            f"Baseline={baseline['stability_score']:+.3f}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_anti_polarisierung.png', dpi=150)


if __name__ == '__main__':
    main()
