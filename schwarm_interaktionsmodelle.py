"""
KKI Interaktionsmodell-Studie
==============================
Vergleicht neue Interaktionsmodelle fuer adaptive Netzwerke:
bounded-confidence, vertrauensgewichtet, gedaechtnisbasiert und adaptiv hybrid.
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
        repetitions = int(os.getenv('KKI_INTERACTION_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_INTERACTION_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_INTERACTION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def profile(params):
    common_roles = {
        'roles_enabled': True,
        'enable_bridge_mechanism': True,
        'enable_centrist_moderation': True,
        'enable_mediator_encouragement': True,
        'mediator_contact_bias': 0.65,
        'centrist_pull_strength': 0.08,
        'mission_switch_interval': int(os.getenv('KKI_MISSION_SWITCH_INTERVAL', '20')),
        'role_switch_interval': int(os.getenv('KKI_ROLE_SWITCH_INTERVAL', '20')),
        'role_switch_min_tenure': int(os.getenv('KKI_ROLE_SWITCH_MIN_TENURE', '20')),
        'role_switch_reputation_cost': float(os.getenv('KKI_ROLE_SWITCH_REPUTATION_COST', '0.02')),
        'workflow_stage_min_tenure': int(os.getenv('KKI_WORKFLOW_STAGE_MIN_TENURE', '2')),
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
        'enable_emergent_skills': True,
        'enable_fault_isolation': False,
        'enable_cluster_failures': False,
        'enable_restart_recovery': False,
        'injection_attack_round': params['attack_round'],
        'injection_strength': float(os.getenv('KKI_INJECTION_STRENGTH', '0.38')),
        'injection_source_count': int(os.getenv('KKI_INJECTION_SOURCE_COUNT', '6')),
        'handoff_priority_bonus': float(os.getenv('KKI_HANDOFF_PRIORITY_BONUS', '0.12')),
        'resource_budget': float(os.getenv('KKI_INTERACTION_RESOURCE_BUDGET', '0.55')),
        'resource_share_factor': float(os.getenv('KKI_RESOURCE_SHARE_FACTOR', '0.20')),
        'cluster_budget_skew': float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')),
        'bottleneck_threshold': float(os.getenv('KKI_BOTTLENECK_THRESHOLD', '1.00')),
        'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')),
        'meta_update_interval': int(os.getenv('KKI_META_UPDATE_INTERVAL', '6')),
        'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')),
        'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')),
        'skill_specialization_threshold': float(os.getenv('KKI_SKILL_SPECIALIZATION_THRESHOLD', '0.58')),
        'mission_conflict_threshold': 0.50,
    }

    return [
        # 1. Homogener Schwarm ohne spezielle Interaktionsregeln
        {'name': 'homogen', 'label': 'Homogen'},

        # 2. Bounded-Confidence: Interaktionen nur bei aehnlichen Meinungen
        {
            'name': 'bounded-confidence',
            'label': 'Bounded Confidence',
            **common_roles,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 3,
            'rewire_reputation_threshold': 0.25,
            'rewire_opinion_distance_threshold': 0.30,
            'rewire_proximity_weight': 0.85,
            'rewire_removal_probability': 0.55,
            'rewire_addition_probability': 0.65,
            'rewire_cross_group_bonus': 0.04,
            'rewire_target_degree': params['degree'],
            'generalist_share': 0.40,
            'connector_share': 0.18,
            'sentinel_share': 0.22,
            'mediator_share': 0.12,
            'analyzer_share': 0.08,
            'connector_bridge_bonus': 0.06,
            'connector_cross_group_learning_bonus': 0.10,
            'sentinel_rep_threshold': 0.48,
            'sentinel_cooperation_penalty': 0.10,
            'sentinel_reputation_learning_multiplier': 1.30,
            'mediator_bridge_bonus': 0.05,
            'mediator_partner_bias': 0.60,
            'mediator_partner_distance': 0.20,
            'analyzer_memory_window': 10,
            'analyzer_learning_multiplier': 1.05,
        },

        # 3. Vertrauensgewichtetes Modell: Reputation als primaere Einflussgrösse
        {
            'name': 'trust-weighted',
            'label': 'Vertrauensgewichtet',
            **common_roles,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 2,
            'rewire_reputation_threshold': 0.50,
            'rewire_opinion_distance_threshold': 0.65,
            'rewire_proximity_weight': 0.35,
            'rewire_removal_probability': 0.40,
            'rewire_addition_probability': 0.80,
            'rewire_cross_group_bonus': 0.12,
            'rewire_target_degree': params['degree'],
            'generalist_share': 0.20,
            'connector_share': 0.20,
            'sentinel_share': 0.35,
            'mediator_share': 0.15,
            'analyzer_share': 0.10,
            'connector_bridge_bonus': 0.12,
            'connector_cross_group_learning_bonus': 0.20,
            'sentinel_rep_threshold': 0.38,
            'sentinel_cooperation_penalty': 0.06,
            'sentinel_reputation_learning_multiplier': 1.55,
            'mediator_bridge_bonus': 0.10,
            'mediator_partner_bias': 0.80,
            'mediator_partner_distance': 0.30,
            'analyzer_memory_window': 12,
            'analyzer_learning_multiplier': 1.08,
        },

        # 4. Gedaechtnisbasiertes Modell: Analytiker mit erweitertem Gedaechtnisfenster
        {
            'name': 'memory-enhanced',
            'label': 'Gedaechtnisbasiert',
            **common_roles,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 4,
            'rewire_reputation_threshold': 0.35,
            'rewire_opinion_distance_threshold': 0.55,
            'rewire_proximity_weight': 0.55,
            'rewire_removal_probability': 0.30,
            'rewire_addition_probability': 0.70,
            'rewire_cross_group_bonus': 0.09,
            'rewire_target_degree': params['degree'],
            'generalist_share': 0.15,
            'connector_share': 0.18,
            'sentinel_share': 0.17,
            'mediator_share': 0.20,
            'analyzer_share': 0.30,
            'connector_bridge_bonus': 0.09,
            'connector_cross_group_learning_bonus': 0.16,
            'sentinel_rep_threshold': 0.42,
            'sentinel_cooperation_penalty': 0.07,
            'sentinel_reputation_learning_multiplier': 1.35,
            'mediator_bridge_bonus': 0.08,
            'mediator_partner_bias': 0.72,
            'mediator_partner_distance': 0.28,
            'analyzer_memory_window': 30,
            'analyzer_learning_multiplier': 1.22,
        },

        # 5. Adaptiver Hybrid: kombiniert Vertrauen, Gedaechtnis und soziale Bruecken
        {
            'name': 'adaptive-hybrid',
            'label': 'Adaptiver Hybrid',
            **common_roles,
            'enable_dynamic_rewiring': True,
            'rewire_min_interactions': 3,
            'rewire_reputation_threshold': 0.40,
            'rewire_opinion_distance_threshold': 0.50,
            'rewire_proximity_weight': 0.60,
            'rewire_removal_probability': 0.38,
            'rewire_addition_probability': 0.78,
            'rewire_cross_group_bonus': 0.10,
            'rewire_target_degree': params['degree'],
            'generalist_share': 0.14,
            'connector_share': 0.20,
            'sentinel_share': 0.25,
            'mediator_share': 0.22,
            'analyzer_share': 0.19,
            'connector_bridge_bonus': 0.11,
            'connector_cross_group_learning_bonus': 0.19,
            'sentinel_rep_threshold': 0.40,
            'sentinel_cooperation_penalty': 0.07,
            'sentinel_reputation_learning_multiplier': 1.45,
            'mediator_bridge_bonus': 0.09,
            'mediator_partner_bias': 0.76,
            'mediator_partner_distance': 0.27,
            'analyzer_memory_window': 22,
            'analyzer_learning_multiplier': 1.16,
            'enable_prompt_injection': True,
            'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.05,
            'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.02,
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
                + 0.24 * pol['cross_group_cooperation_rate']
                + 0.10 * pol['workflow_metrics'].get('resource_efficiency', 0.0)
                + 0.06 * pol['workflow_metrics'].get('bottleneck_relief_rate', 0.0)
                + 0.08 * pol['workflow_metrics'].get('meta_alignment_rate', 0.0)
                + 0.08 * pol['workflow_metrics'].get('misinformation_detection_rate', 0.0)
                + 0.07 * pol['workflow_metrics'].get('skill_alignment_rate', 0.0)
                for pol, con in runs
            ]
        ),
        'polarization_index': mittelwert([run['final_polarization_index'] for run in polarization_runs]),
        'consensus_score': mittelwert([run['final_consensus_score'] for run in consensus_runs]),
        'cross_group_cooperation': mittelwert([run['cross_group_cooperation_rate'] for run in polarization_runs]),
        'resource_efficiency': mittelwert([run['workflow_metrics'].get('resource_efficiency', 0.0) for run in polarization_runs]),
        'meta_alignment': mittelwert([run['workflow_metrics'].get('meta_alignment_rate', 0.0) for run in polarization_runs]),
        'skill_alignment': mittelwert([run['workflow_metrics'].get('skill_alignment_rate', 0.0) for run in polarization_runs]),
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    items = profile(params)
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI INTERAKTIONSMODELL-STUDIE')
    print('=' * 84)
    print('Vergleicht bounded-confidence, vertrauensgewichtete, gedaechtnisbasierte')
    print('und adaptive Hybridmodelle in polarisierten und Konsens-Szenarien.\n')

    summaries = []
    for index, item in enumerate(items):
        runs = []
        for repetition in range(params['repetitions']):
            seed = base_seed + index * 100 + repetition
            runs.append(run_once(seed, params, item))
        summary = summarize_runs(runs, item)
        summaries.append(summary)
        print(
            f"{summary['label']:<24} Score={summary['combined_score']:+.3f} | "
            f"PI={summary['polarization_index']:.3f} | "
            f"Koop={summary['cross_group_cooperation']:.1%} | "
            f"Skill={summary['skill_alignment']:.1%}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    print('\nBestes Interaktionsmodell:', best['label'])
    print(f"Score {best['combined_score']:+.3f} bei Polarisierungsindex {best['polarization_index']:.3f}")
    print(
        f"Cross-Group-Kooperation {best['cross_group_cooperation']:.1%}, "
        f"Skill-Ausrichtung {best['skill_alignment']:.1%}"
    )

    labels = [item['label'] for item in summaries]
    scores = [item['combined_score'] for item in summaries]
    cooperation = [item['cross_group_cooperation'] * 100.0 for item in summaries]
    polarization = [item['polarization_index'] for item in summaries]
    skill = [item['skill_alignment'] * 100.0 for item in summaries]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    ax1, ax2, ax3, ax4 = axes.flat
    colors = ['#9aa0a6', '#4e79a7', '#f28e2b', '#59a14f', '#b07aa1']

    ax1.bar(labels, scores, color=colors)
    ax1.set_title('Kombinierter Score nach Interaktionsmodell')
    ax1.tick_params(axis='x', rotation=18)

    ax2.bar(labels, cooperation, color=colors)
    ax2.set_title('Cross-Group-Kooperation (%)')
    ax2.tick_params(axis='x', rotation=18)

    ax3.bar(labels, polarization, color=colors)
    ax3.set_title('Finaler Polarisierungsindex')
    ax3.tick_params(axis='x', rotation=18)

    ax4.bar(labels, skill, color=colors)
    ax4.set_title('Skill-Ausrichtung (%)')
    ax4.tick_params(axis='x', rotation=18)

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_interaktionsmodelle.png', dpi=150)


if __name__ == '__main__':
    main()
