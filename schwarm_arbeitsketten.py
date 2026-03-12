"""
KKI Arbeitsketten-Studie
========================
Vergleicht Missions-Arbitration mit mehrstufigen Teamaufgaben und Abhaengigkeiten.
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
        repetitions = int(os.getenv('KKI_WORKFLOW_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
    else:
        repetitions = int(os.getenv('KKI_WORKFLOW_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'agent_count': int(os.getenv('KKI_WORKFLOW_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def basisprofil():
    return {
        'roles_enabled': True,
        'generalist_share': 0.30,
        'connector_share': 0.20,
        'sentinel_share': 0.15,
        'mediator_share': 0.20,
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
        'enable_missions': True,
        'mission_assignment': 'arbitrated',
        'mission_arbitration_enabled': True,
        'enable_role_switching': True,
    }


def profile():
    basis = basisprofil()
    mission_interval = int(os.getenv('KKI_MISSION_SWITCH_INTERVAL', '20'))
    role_interval = int(os.getenv('KKI_ROLE_SWITCH_INTERVAL', '20'))
    role_tenure = int(os.getenv('KKI_ROLE_SWITCH_MIN_TENURE', '20'))
    conflict_threshold = float(os.getenv('KKI_MISSION_CONFLICT_THRESHOLD', '0.45'))
    arbitration_margin = float(os.getenv('KKI_MISSION_ARBITRATION_MARGIN', '0.08'))
    workflow_tenure = int(os.getenv('KKI_WORKFLOW_STAGE_MIN_TENURE', '2'))
    common = {
        **basis,
        'mission_switch_interval': mission_interval,
        'role_switch_interval': role_interval,
        'role_switch_min_tenure': role_tenure,
        'role_switch_reputation_cost': float(os.getenv('KKI_ROLE_SWITCH_REPUTATION_COST', '0.02')),
        'mission_conflict_threshold': conflict_threshold,
        'mission_arbitration_margin': arbitration_margin,
    }
    return [
        {'name': 'homogen', 'label': 'Homogen'},
        {
            'name': 'arbitration-baseline',
            'label': 'Arbitration-Basis',
            **common,
            'enable_workflow_stages': False,
        },
        {
            'name': 'workflow-pipeline',
            'label': 'Arbeitskette',
            **common,
            'enable_workflow_stages': True,
            'workflow_stage_min_tenure': workflow_tenure,
        },
        {
            'name': 'workflow-tight',
            'label': 'Arbeitskette Strikt',
            **common,
            'enable_workflow_stages': True,
            'workflow_stage_min_tenure': workflow_tenure + 1,
            'mission_conflict_threshold': conflict_threshold + 0.05,
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
                pol['final_consensus_score']
                - pol['final_polarization_index']
                + con['final_consensus_score']
                + 0.25 * pol['cross_group_cooperation_rate']
                + 0.20 * pol['workflow_metrics']['completion_rate']
                for pol, con in runs
            ]
        ),
        'polarization_index': mittelwert([run['final_polarization_index'] for run in polarization_runs]),
        'consensus_score': mittelwert([run['final_consensus_score'] for run in consensus_runs]),
        'cross_group_cooperation': mittelwert([run['cross_group_cooperation_rate'] for run in polarization_runs]),
        'mission_success': mittelwert(
            [mittelwert(list(run['mission_success_rates'].values())) for run in polarization_runs if run.get('missions_enabled')]
        ),
        'workflow_completion': mittelwert(
            [run['workflow_metrics'].get('completion_rate', 0.0) for run in polarization_runs]
        ),
        'workflow_failures': mittelwert(
            [run['workflow_metrics'].get('prerequisite_failures', 0) for run in polarization_runs]
        ),
        'workflow_recovery': mittelwert(
            [run['workflow_metrics'].get('stage_distribution', {}).get('recovery', 0) for run in polarization_runs]
        ),
        'mission_arbitration': mittelwert(
            [run.get('mission_arbitration_total', 0) for run in polarization_runs]
        ),
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    items = profile()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI ARBEITSKETTEN-STUDIE")
    print("=" * 84)
    print(
        f"Seed-Basis: {base_seed} | Agenten: {params['agent_count']} | "
        f"Runden: {params['rounds']} | Wiederholungen: {params['repetitions']}"
    )
    print(f"Profile: {', '.join(item['label'] for item in items)}")
    print("\nStudie laeuft...\n")

    summaries = []
    best_score = None
    best_profile = None

    for index, item in enumerate(items):
        overrides = {key: value for key, value in item.items() if key not in {'name', 'label'}}
        runs = []
        for repetition in range(params['repetitions']):
            seed = base_seed + index * 100 + repetition
            runs.append(run_once(seed, params, overrides))
        summary = summarize_runs(runs, item)
        summaries.append(summary)
        print(
            f"{summary['label']:>24s} -> "
            f"Score={summary['combined_score']:+.3f}, "
            f"PI={summary['polarization_index']:.3f}, "
            f"Konsens={summary['consensus_score']:.3f}, "
            f"Workflow={summary['workflow_completion']:.1%}"
        )
        if best_score is None or summary['combined_score'] > best_score:
            best_score = summary['combined_score']
            best_profile = summary

    baseline = next(summary for summary in summaries if summary['name'] == 'homogen')

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste Workflow-Architektur:\n"
        f"  Profil:                   {best_profile['label']}\n"
        f"  Kombinierter Score:       {best_profile['combined_score']:+.3f}\n"
        f"  Delta zur Homogenitaet:   {best_profile['combined_score'] - baseline['combined_score']:+.3f}\n"
        f"  Polarisierungs-Index:     {best_profile['polarization_index']:.3f}\n"
        f"  Konsens-Szenario:         {best_profile['consensus_score']:.3f}\n"
        f"  Missionserfolg:           {best_profile['mission_success']:.1%}\n"
        f"  Workflow-Abschluss:       {best_profile['workflow_completion']:.1%}\n"
        f"  Workflow-Blockaden:       {best_profile['workflow_failures']:.1f}\n"
        f"  Recovery-Anteil:          {best_profile['workflow_recovery']:.1f}\n"
        f"  Arbitrierungen:           {best_profile['mission_arbitration']:.1f}\n"
        f"  Cross-Group-Kooperation:  {best_profile['cross_group_cooperation']:.1%}"
    )
    print(
        "\nInterpretation:\n"
        "Die Studie prueft, ob aus Missionen echte Arbeitsketten mit Voraussetzungen "
        "entstehen koennen und ob diese Abfolge den Schwarm ueber reine Arbitration "
        "hinaus stabiler und kooperativer macht."
    )

    labels = [summary['label'] for summary in summaries]
    x = np.arange(len(labels))
    width = 0.35

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        'KKI Arbeitsketten: Mehrstufige Teamaufgaben im Schwarm',
        fontsize=14,
        fontweight='bold',
    )

    axes[0, 0].bar(x, [summary['combined_score'] for summary in summaries], color='#4C72B0')
    axes[0, 0].set_title('Kombinierter Score')
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
        [summary['mission_success'] for summary in summaries],
        width,
        label='Missionserfolg',
        color='#8172B2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [summary['workflow_completion'] for summary in summaries],
        width,
        label='Workflow-Abschluss',
        color='#64B5CD',
    )
    axes[1, 0].set_title('Mission und Workflow')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=20)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(
        x - width / 2,
        [summary['workflow_failures'] for summary in summaries],
        width,
        label='Workflow-Blockaden',
        color='#DD8452',
    )
    axes[1, 1].bar(
        x + width / 2,
        [summary['cross_group_cooperation'] for summary in summaries],
        width,
        label='Cross-Group-Koop',
        color='#8C8C8C',
    )
    axes[1, 1].set_title('Abhaengigkeiten und Kooperation')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=20)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    plt.tight_layout(rect=(0, 0.02, 1, 0.95))
    save_and_maybe_show(plt, 'kki_arbeitsketten.png', dpi=150)


if __name__ == '__main__':
    main()
