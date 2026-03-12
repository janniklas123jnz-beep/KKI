"""
KKI Benchmark fuer Vertrauenssignale
===================================
Vergleicht adaptive Netzwerkstrategien mit Reputation, Commitment,
Meinungsnaehe und hybriden Signalen unter demselben Commitment-Angriff.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_commitment_resilienz import (
    DEFAULT_ATTACKER_COUNT,
    DEFAULT_ATTACK_ROUND,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_NATIVE_AGENT_COUNT,
    DEFAULT_TOTAL_ROUNDS,
    run_commitment_experiment,
    strategieprofil,
)


def benchmark_parameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_BENCHMARK_REPETITIONS', '2'))
        rounds = min(DEFAULT_TOTAL_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_BENCHMARK_REPETITIONS', '3'))
        rounds = DEFAULT_TOTAL_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_COMMITMENT_ATTACK_ROUND', str(DEFAULT_ATTACK_ROUND)))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'native_count': int(os.getenv('KKI_NATIVE_AGENT_COUNT', str(DEFAULT_NATIVE_AGENT_COUNT))),
        'attacker_count': int(os.getenv('KKI_ATTACKER_AGENT_COUNT', str(DEFAULT_ATTACKER_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'attack_strength': float(os.getenv('KKI_COMMITMENT_ATTACK_STRENGTH', '0.45')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def strategie_konfigurationen():
    return [
        {
            'name': 'static',
            'label': 'Statisch',
            'adaptive_enabled': False,
        },
        {
            'name': 'reputation',
            'label': 'Reputation',
            'adaptive_enabled': True,
            'strategy_weights': strategieprofil('reputation')['weights'],
            'signal_threshold': strategieprofil('reputation')['threshold'],
        },
        {
            'name': 'commitment',
            'label': 'Commitment',
            'adaptive_enabled': True,
            'strategy_weights': strategieprofil('commitment')['weights'],
            'signal_threshold': strategieprofil('commitment')['threshold'],
        },
        {
            'name': 'opinion',
            'label': 'Meinung',
            'adaptive_enabled': True,
            'strategy_weights': strategieprofil('opinion')['weights'],
            'signal_threshold': strategieprofil('opinion')['threshold'],
        },
        {
            'name': 'hybrid',
            'label': 'Hybrid',
            'adaptive_enabled': True,
            'strategy_weights': strategieprofil('hybrid')['weights'],
            'signal_threshold': strategieprofil('hybrid')['threshold'],
        },
    ]


def run_once(seed, params, strategy):
    random.seed(seed)
    np.random.seed(seed)
    config = dict(params)
    config.update(
        {
            'strategy_name': strategy['name'],
            'strategy_weights': strategy.get('strategy_weights'),
            'signal_threshold': strategy.get('signal_threshold'),
        }
    )
    return run_commitment_experiment(
        config,
        adaptive_enabled=bool(strategy['adaptive_enabled']),
        rep_threshold=0.35,
        trust_threshold=0.75,
    )


def main():
    configure_matplotlib(plt)
    params = benchmark_parameter()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))
    strategies = strategie_konfigurationen()

    print("=" * 84)
    print("KKI BENCHMARK FUER VERTRAUENSSIGNALE")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Runden: {params['rounds']} | "
        f"Angriff ab Runde {params['attack_round']}"
    )
    print(
        f"Basisnetz: Agenten={params['native_count']} + Manipulatoren={params['attacker_count']}, "
        f"Grad={params['degree']} | Angriffsstärke={params['attack_strength']:.2f}"
    )
    print(
        f"Strategien: {', '.join(strategy['label'] for strategy in strategies)} | "
        f"Wiederholungen: {params['repetitions']}"
    )
    print("\nBenchmark läuft...\n")

    strategy_results = []
    best_score = None
    best_strategy = None

    for index, strategy in enumerate(strategies):
        runs = []
        for repetition in range(params['repetitions']):
            seed = base_seed + index * 100 + repetition
            runs.append(run_once(seed, params, strategy))

        summary = {
            'name': strategy['name'],
            'label': strategy['label'],
            'adaptive_enabled': strategy['adaptive_enabled'],
            'resilience_score': mittelwert([run['resilience_score'] for run in runs]),
            'native_retention': mittelwert([run['native_retention'] for run in runs]),
            'detection_rate': mittelwert([run['detection_rate'] for run in runs]),
            'commitment_divergence': mittelwert([run['commitment_divergence'] for run in runs]),
            'manipulator_edge_share': mittelwert([run['manipulator_edge_share'] for run in runs]),
            'average_rewiring': mittelwert([run['average_rewiring'] for run in runs]),
        }
        strategy_results.append(summary)

        print(
            f"{summary['label']:>10s} -> "
            f"Score={summary['resilience_score']:+.3f}, "
            f"Retention={summary['native_retention']:.3f}, "
            f"Erkennung={summary['detection_rate']:.1%}, "
            f"Manipulator-Kanten={summary['manipulator_edge_share']:.1%}"
        )

        if best_score is None or summary['resilience_score'] > best_score:
            best_score = summary['resilience_score']
            best_strategy = summary

    static_summary = next(result for result in strategy_results if result['name'] == 'static')

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste Vertrauensstrategie:\n"
        f"  Strategie:              {best_strategy['label']}\n"
        f"  Resilienz-Score:        {best_strategy['resilience_score']:+.3f}\n"
        f"  Native-Retention:       {best_strategy['native_retention']:.3f}\n"
        f"  Erkennungsrate:         {best_strategy['detection_rate']:.1%}\n"
        f"  Commitment-Divergenz:   {best_strategy['commitment_divergence']:+.3f}\n"
        f"  Manipulator-Kantenanteil:{best_strategy['manipulator_edge_share']:.1%}\n"
        f"  Ø Rewiring/Runde:       {best_strategy['average_rewiring']:.2f}"
    )
    print(
        "\nDelta zu statisch:\n"
        f"  Δ Resilienz:    {best_strategy['resilience_score'] - static_summary['resilience_score']:+.3f}\n"
        f"  Δ Retention:    {best_strategy['native_retention'] - static_summary['native_retention']:+.3f}\n"
        f"  Δ Kantenanteil: {best_strategy['manipulator_edge_share'] - static_summary['manipulator_edge_share']:+.3f}"
    )

    labels = [result['label'] for result in strategy_results]
    x = np.arange(len(labels))

    fig, axes = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle(
        'KKI Benchmark fuer Vertrauenssignale in adaptiven Netzwerken',
        fontsize=14,
        fontweight='bold',
    )

    axes[0, 0].bar(x, [result['resilience_score'] for result in strategy_results], color='#4C72B0')
    axes[0, 0].set_title('Resilienz-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=20)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(x, [result['native_retention'] for result in strategy_results], color='#55A868')
    axes[0, 1].set_title('Native-Retention')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=20)
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(x, [result['manipulator_edge_share'] for result in strategy_results], color='#C44E52')
    axes[1, 0].set_title('Manipulator-Kantenanteil')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=20)
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [result['average_rewiring'] for result in strategy_results], color='#8172B2')
    axes[1, 1].set_title('Ø Rewiring pro Runde')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=20)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    fig.text(
        0.5,
        0.02,
        (
            f"Beste Strategie: {best_strategy['label']} | "
            f"Score={best_strategy['resilience_score']:+.3f} | "
            f"Statisch={static_summary['resilience_score']:+.3f}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_vertrauens_benchmark.png', dpi=150)


if __name__ == '__main__':
    main()
