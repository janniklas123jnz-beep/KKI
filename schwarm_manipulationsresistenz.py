"""
KKI Manipulationsresistenz-Studie
=================================
Vergleicht heterogene Zellcluster unter Promptinjektion und strategischer Fehlinformation.
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
        repetitions = int(os.getenv('KKI_MANIPULATION_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_MANIPULATION_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_MANIPULATION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def basisprofil():
    return {
        'roles_enabled': True,
        'generalist_share': 0.28,
        'connector_share': 0.18,
        'sentinel_share': 0.16,
        'mediator_share': 0.20,
        'analyzer_share': 0.18,
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
        'enable_workflow_stages': True,
        'enable_workflow_cells': True,
        'enable_handoff_coordination': True,
        'enable_parallel_workflow_cells': True,
        'enable_resource_coordination': True,
        'enable_capability_clusters': True,
        'enable_asymmetric_cluster_budgets': True,
        'enable_bottleneck_management': True,
        'enable_meta_coordination': True,
    }


def profile(params):
    basis = basisprofil()
    common = {
        **basis,
        'mission_switch_interval': int(os.getenv('KKI_MISSION_SWITCH_INTERVAL', '20')),
        'role_switch_interval': int(os.getenv('KKI_ROLE_SWITCH_INTERVAL', '20')),
        'role_switch_min_tenure': int(os.getenv('KKI_ROLE_SWITCH_MIN_TENURE', '20')),
        'role_switch_reputation_cost': float(os.getenv('KKI_ROLE_SWITCH_REPUTATION_COST', '0.02')),
        'workflow_stage_min_tenure': int(os.getenv('KKI_WORKFLOW_STAGE_MIN_TENURE', '2')),
        'mission_conflict_threshold': 0.50,
        'handoff_priority_bonus': float(os.getenv('KKI_HANDOFF_PRIORITY_BONUS', '0.12')),
        'resource_budget': float(os.getenv('KKI_BOTTLENECK_RESOURCE_BUDGET', '0.55')),
        'resource_share_factor': float(os.getenv('KKI_RESOURCE_SHARE_FACTOR', '0.20')),
        'cluster_budget_skew': float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')),
        'bottleneck_threshold': float(os.getenv('KKI_BOTTLENECK_THRESHOLD', '1.00')),
        'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')),
        'meta_update_interval': int(os.getenv('KKI_META_UPDATE_INTERVAL', '6')),
        'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')),
        'injection_attack_round': params['attack_round'],
        'injection_strength': float(os.getenv('KKI_INJECTION_STRENGTH', '0.38')),
        'injection_source_count': int(os.getenv('KKI_INJECTION_SOURCE_COUNT', '6')),
    }
    return [
        {'name': 'homogen', 'label': 'Homogen'},
        {
            'name': 'meta-control',
            'label': 'Meta-Koordination',
            **common,
            'enable_prompt_injection': False,
        },
        {
            'name': 'cluster-attack',
            'label': 'Cluster unter Angriff',
            **common,
            'enable_meta_coordination': False,
            'enable_prompt_injection': True,
        },
        {
            'name': 'meta-attack',
            'label': 'Meta unter Angriff',
            **common,
            'enable_prompt_injection': True,
        },
        {
            'name': 'resilient-meta',
            'label': 'Resiliente Meta-Abwehr',
            **common,
            'enable_prompt_injection': True,
            'sentinel_share': 0.22,
            'analyzer_share': 0.20,
            'generalist_share': 0.18,
            'connector_share': 0.18,
            'mediator_share': 0.22,
            'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.06,
            'cluster_budget_skew': max(0.25, float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')) - 0.10),
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
                + 0.22 * pol['cross_group_cooperation_rate']
                + 0.16 * pol['workflow_metrics']['resource_efficiency']
                + 0.10 * pol['workflow_metrics']['misinformation_detection_rate']
                + 0.08 * pol['workflow_metrics']['meta_alignment_rate']
                - 0.10 * pol['workflow_metrics']['misinformation_corruption_mean']
                - 0.08 * pol['workflow_metrics']['cluster_compromise_mean']
                for pol, con in runs
            ]
        ),
        'polarization_index': mittelwert([run['final_polarization_index'] for run in polarization_runs]),
        'consensus_score': mittelwert([run['final_consensus_score'] for run in consensus_runs]),
        'cross_group_cooperation': mittelwert([run['cross_group_cooperation_rate'] for run in polarization_runs]),
        'mission_success': mittelwert(
            [mittelwert(list(run['mission_success_rates'].values())) for run in polarization_runs]
        ),
        'resource_efficiency': mittelwert(
            [run['workflow_metrics'].get('resource_efficiency', 0.0) for run in polarization_runs]
        ),
        'meta_alignment': mittelwert(
            [run['workflow_metrics'].get('meta_alignment_rate', 0.0) for run in polarization_runs]
        ),
        'detection_rate': mittelwert(
            [run['workflow_metrics'].get('misinformation_detection_rate', 0.0) for run in polarization_runs]
        ),
        'corruption_mean': mittelwert(
            [run['workflow_metrics'].get('misinformation_corruption_mean', 0.0) for run in polarization_runs]
        ),
        'compromise_mean': mittelwert(
            [run['workflow_metrics'].get('cluster_compromise_mean', 0.0) for run in polarization_runs]
        ),
        'attack_events': mittelwert(
            [run['workflow_metrics'].get('misinformation_events_total', 0.0) for run in polarization_runs]
        ),
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    items = profile(params)
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print("=" * 84)
    print("KKI MANIPULATIONSRESISTENZ-STUDIE")
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
            f"Det={summary['detection_rate']:.2f}, "
            f"Corr={summary['corruption_mean']:.2f}"
        )
        if best_score is None or summary['combined_score'] > best_score:
            best_score = summary['combined_score']
            best_profile = summary

    baseline = next(summary for summary in summaries if summary['name'] == 'homogen')

    print("\n" + "=" * 84)
    print("ERGEBNISSE")
    print("=" * 84)
    print(
        "Beste Abwehrarchitektur:\n"
        f"  Profil:                   {best_profile['label']}\n"
        f"  Kombinierter Score:       {best_profile['combined_score']:+.3f}\n"
        f"  Delta zur Homogenitaet:   {best_profile['combined_score'] - baseline['combined_score']:+.3f}\n"
        f"  Polarisierungs-Index:     {best_profile['polarization_index']:.3f}\n"
        f"  Konsens-Szenario:         {best_profile['consensus_score']:.3f}\n"
        f"  Missionserfolg:           {best_profile['mission_success']:.1%}\n"
        f"  Ressourcen-Effizienz:     {best_profile['resource_efficiency']:.2f}\n"
        f"  Meta-Ausrichtung:         {best_profile['meta_alignment']:.1%}\n"
        f"  Detektionsrate:           {best_profile['detection_rate']:.1%}\n"
        f"  Korruptionsniveau:        {best_profile['corruption_mean']:.2f}\n"
        f"  Kompromittierungsgrad:    {best_profile['compromise_mean']:.2f}\n"
        f"  Angriffsereignisse:       {best_profile['attack_events']:.1f}\n"
        f"  Cross-Group-Kooperation:  {best_profile['cross_group_cooperation']:.1%}"
    )
    print(
        "\nInterpretation:\n"
        "Die Studie prueft, ob Meta-Koordination und resiliente Clusterprofile "
        "Promptinjektion und strategische Fehlinformation besser abfedern als lokale Clusterlogik allein."
    )

    labels = [summary['label'] for summary in summaries]
    x = np.arange(len(labels))
    width = 0.35

    fig, axes = plt.subplots(2, 2, figsize=(16, 11))
    fig.suptitle(
        'KKI Manipulationsresistenz: Promptinjektion gegen Zellcluster und Meta-Koordination',
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
        [summary['detection_rate'] for summary in summaries],
        width,
        label='Detektionsrate',
        color='#8172B2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [summary['meta_alignment'] for summary in summaries],
        width,
        label='Meta-Ausrichtung',
        color='#64B5CD',
    )
    axes[1, 0].set_title('Detektion und Meta-Fokus')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=20)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(
        x - width / 2,
        [summary['corruption_mean'] for summary in summaries],
        width,
        label='Korruptionsniveau',
        color='#DD8452',
    )
    axes[1, 1].bar(
        x + width / 2,
        [summary['compromise_mean'] for summary in summaries],
        width,
        label='Kompromittierung',
        color='#8C8C8C',
    )
    axes[1, 1].set_title('Angriffsfolgen')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=20)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    plt.tight_layout(rect=(0, 0.02, 1, 0.95))
    save_and_maybe_show(plt, 'kki_manipulationsresistenz.png', dpi=150)


if __name__ == '__main__':
    main()
