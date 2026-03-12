"""
KKI Rollen- und Lernprofilstudie
================================
Vergleicht verfeinerte Rollen und Lernprofile auf gemeinsamer Agenten-DNA.
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
        repetitions = int(os.getenv('KKI_ROLLENLERNEN_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
    else:
        repetitions = int(os.getenv('KKI_ROLLENLERNEN_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'agent_count': int(os.getenv('KKI_ROLLENLERNEN_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def lernprofile():
    return [
        {'name': 'homogen', 'label': 'Homogen'},
        {
            'name': 'connector-learning',
            'label': 'Bruecken-Lernen',
            'roles_enabled': True,
            'generalist_share': 0.70,
            'connector_share': 0.30,
            'sentinel_share': 0.0,
            'mediator_share': 0.0,
            'analyzer_share': 0.0,
            'connector_bridge_bonus': 0.10,
            'connector_cross_group_learning_bonus': 0.18,
            'enable_bridge_mechanism': True,
        },
        {
            'name': 'sentinel-learning',
            'label': 'Waechter-Lernen',
            'roles_enabled': True,
            'generalist_share': 0.75,
            'connector_share': 0.0,
            'sentinel_share': 0.25,
            'mediator_share': 0.0,
            'analyzer_share': 0.0,
            'sentinel_rep_threshold': 0.42,
            'sentinel_cooperation_penalty': 0.08,
            'sentinel_reputation_learning_multiplier': 1.35,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 3,
            'rewire_reputation_threshold': 0.35,
            'rewire_opinion_distance_threshold': 0.55,
            'rewire_proximity_weight': 0.65,
            'rewire_removal_probability': 0.35,
            'rewire_addition_probability': 0.75,
            'rewire_cross_group_bonus': 0.08,
        },
        {
            'name': 'mediator-learning',
            'label': 'Vermittler',
            'roles_enabled': True,
            'generalist_share': 0.75,
            'connector_share': 0.0,
            'sentinel_share': 0.0,
            'mediator_share': 0.25,
            'analyzer_share': 0.0,
            'mediator_bridge_bonus': 0.07,
            'mediator_partner_bias': 0.75,
            'mediator_partner_distance': 0.25,
            'enable_centrist_moderation': True,
            'enable_mediator_encouragement': True,
            'mediator_contact_bias': 0.65,
            'centrist_pull_strength': 0.08,
        },
        {
            'name': 'analyzer-learning',
            'label': 'Analytiker',
            'roles_enabled': True,
            'generalist_share': 0.75,
            'connector_share': 0.0,
            'sentinel_share': 0.0,
            'mediator_share': 0.0,
            'analyzer_share': 0.25,
            'analyzer_memory_window': 18,
            'analyzer_learning_multiplier': 1.12,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 3,
            'rewire_reputation_threshold': 0.35,
            'rewire_opinion_distance_threshold': 0.55,
            'rewire_proximity_weight': 0.65,
            'rewire_removal_probability': 0.35,
            'rewire_addition_probability': 0.75,
            'rewire_cross_group_bonus': 0.08,
        },
        {
            'name': 'learning-mix',
            'label': 'Lernmix',
            'roles_enabled': True,
            'generalist_share': 0.35,
            'connector_share': 0.20,
            'sentinel_share': 0.15,
            'mediator_share': 0.15,
            'analyzer_share': 0.15,
            'connector_bridge_bonus': 0.10,
            'connector_cross_group_learning_bonus': 0.18,
            'sentinel_rep_threshold': 0.42,
            'sentinel_cooperation_penalty': 0.08,
            'sentinel_reputation_learning_multiplier': 1.35,
            'mediator_bridge_bonus': 0.07,
            'mediator_partner_bias': 0.75,
            'mediator_partner_distance': 0.25,
            'analyzer_memory_window': 18,
            'analyzer_learning_multiplier': 1.12,
            'enable_bridge_mechanism': True,
            'enable_centrist_moderation': True,
            'enable_mediator_encouragement': True,
            'mediator_contact_bias': 0.65,
            'centrist_pull_strength': 0.08,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 3,
            'rewire_reputation_threshold': 0.35,
            'rewire_opinion_distance_threshold': 0.55,
            'rewire_proximity_weight': 0.65,
            'rewire_removal_probability': 0.35,
            'rewire_addition_probability': 0.75,
            'rewire_cross_group_bonus': 0.08,
        },
    ]


def base_config(params, scenario):
    return {
        'scenario': scenario,
        'agent_count': params['agent_count'],
        'rounds': params['rounds'],
        'interactions_per_round': params['interactions'],
        'connections_per_agent': params['degree'],
        'cross_group_chance': 0.35 if scenario == 'consensus' else 0.08,
        'random_edge_chance': DEFAULT_RANDOM_EDGE_CHANCE,
        'enable_dynamic_rewiring': False,
        'rewire_target_degree': params['degree'],
    }


def run_once(seed, params, overrides):
    random.seed(seed)
    np.random.seed(seed)
    pol_config = base_config(params, 'polarization')
    pol_config.update(overrides)
    pol_result = run_polarization_experiment(pol_config, make_plot=False, print_summary=False)

    random.seed(seed)
    np.random.seed(seed)
    con_config = base_config(params, 'consensus')
    con_config.update(overrides)
    con_result = run_polarization_experiment(con_config, make_plot=False, print_summary=False)
    return pol_result, con_result


def summarize_runs(runs, item):
    polarization_runs = [run[0] for run in runs]
    consensus_runs = [run[1] for run in runs]
    return {
        'name': item['name'],
        'label': item['label'],
        'combined_score': mittelwert(
            [
                pol['final_consensus_score'] - pol['final_polarization_index'] + con['final_consensus_score']
                for pol, con in runs
            ]
        ),
        'polarization_index': mittelwert([run['final_polarization_index'] for run in polarization_runs]),
        'consensus_score': mittelwert([run['final_consensus_score'] for run in consensus_runs]),
        'cross_group_cooperation': mittelwert(
            [run['cross_group_cooperation_rate'] for run in polarization_runs]
        ),
        'connector_learning_gain': mittelwert(
            [run['role_mean_intelligence'].get('connector', 0.0) for run in polarization_runs]
        ),
        'sentinel_reputation': mittelwert(
            [run['role_mean_reputation'].get('sentinel', 0.0) for run in polarization_runs]
        ),
        'mediator_cooperation': mittelwert(
            [run['role_cross_group_cooperation_rate'].get('mediator', 0.0) for run in polarization_runs]
        ),
        'analyzer_learning_gain': mittelwert(
            [run['role_mean_intelligence'].get('analyzer', 0.0) for run in polarization_runs]
        ),
        'mediator_opinion_shift': mittelwert(
            [run['role_mean_opinion_shift'].get('mediator', 0.0) for run in polarization_runs]
        ),
        'analyzer_opinion_shift': mittelwert(
            [run['role_mean_opinion_shift'].get('analyzer', 0.0) for run in polarization_runs]
        ),
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    profiles = lernprofile()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI ROLLENLERNEN-STUDIE")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Agenten: {params['agent_count']} | "
        f"Runden: {params['rounds']} | Wiederholungen: {params['repetitions']}"
    )
    print(f"Profile: {', '.join(profile['label'] for profile in profiles)}")
    print("\nStudie laeuft...\n")

    summaries = []
    best_score = None
    best_profile = None

    for index, profile in enumerate(profiles):
        overrides = {key: value for key, value in profile.items() if key not in {'name', 'label'}}
        runs = []
        for repetition in range(params['repetitions']):
            seed = base_seed + index * 100 + repetition
            runs.append(run_once(seed, params, overrides))
        summary = summarize_runs(runs, profile)
        summaries.append(summary)
        print(
            f"{summary['label']:>18s} -> "
            f"Score={summary['combined_score']:+.3f}, "
            f"PI={summary['polarization_index']:.3f}, "
            f"Konsens={summary['consensus_score']:.3f}, "
            f"Cross-Group-Koop={summary['cross_group_cooperation']:.1%}"
        )
        if best_score is None or summary['combined_score'] > best_score:
            best_score = summary['combined_score']
            best_profile = summary

    baseline = next(summary for summary in summaries if summary['name'] == 'homogen')

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Bestes Lernprofil:\n"
        f"  Profil:                   {best_profile['label']}\n"
        f"  Kombinierter Score:       {best_profile['combined_score']:+.3f}\n"
        f"  Delta zur Homogenitaet:   {best_profile['combined_score'] - baseline['combined_score']:+.3f}\n"
        f"  Polarisierungs-Index:     {best_profile['polarization_index']:.3f}\n"
        f"  Konsens-Szenario:         {best_profile['consensus_score']:.3f}\n"
        f"  Cross-Group-Kooperation:  {best_profile['cross_group_cooperation']:.1%}\n"
        f"  Vermittler-Kooperation:   {best_profile['mediator_cooperation']:.1%}\n"
        f"  Analytiker-Lerngewinn:    {best_profile['analyzer_learning_gain']:.3f}"
    )
    print(
        "\nInterpretation:\n"
        "Die Studie prueft, ob sich aus den ersten Rollen bereits verfeinerte "
        "Lernprofile ableiten lassen, die Kooperation, Stabilitaet und Auswertung zugleich verbessern."
    )

    labels = [summary['label'] for summary in summaries]
    x = np.arange(len(labels))
    width = 0.35

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        'KKI Rollenlernen: Verfeinerte Rollen und Lernprofile',
        fontsize=14,
        fontweight='bold',
    )

    axes[0, 0].bar(x, [summary['combined_score'] for summary in summaries], color='#4C72B0')
    axes[0, 0].set_title('Kombinierter Lernprofil-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=20)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [summary['polarization_index'] for summary in summaries],
        width,
        label='Polarisierungs-Index',
        color='#C44E52',
    )
    axes[0, 1].bar(
        x + width / 2,
        [summary['consensus_score'] for summary in summaries],
        width,
        label='Konsens-Szenario',
        color='#55A868',
    )
    axes[0, 1].set_title('Polarisierung vs. Konsens')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=20)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [summary['mediator_cooperation'] for summary in summaries],
        width,
        label='Vermittler-Kooperation',
        color='#8172B2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [summary['cross_group_cooperation'] for summary in summaries],
        width,
        label='Gesamt Cross-Group',
        color='#CCB974',
    )
    axes[1, 0].set_title('Kooperationswirkung der Lernprofile')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=20)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(
        x - width / 2,
        [summary['analyzer_learning_gain'] for summary in summaries],
        width,
        label='Analytiker-Lerngewinn',
        color='#64B5CD',
    )
    axes[1, 1].bar(
        x + width / 2,
        [summary['mediator_opinion_shift'] + summary['analyzer_opinion_shift'] for summary in summaries],
        width,
        label='Meinungsdrift Spezialrollen',
        color='#8C8C8C',
    )
    axes[1, 1].set_title('Lern- und Driftprofil')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=20)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    fig.text(
        0.5,
        0.02,
        (
            f"Bestes Lernprofil: {best_profile['label']} | "
            f"Delta zur Homogenitaet: {best_profile['combined_score'] - baseline['combined_score']:+.3f}"
        ),
        ha='center',
        fontsize=10,
    )
    plt.tight_layout(rect=(0, 0.04, 1, 0.98))
    save_and_maybe_show(plt, 'kki_rollenlernen.png', dpi=150)


if __name__ == '__main__':
    main()
