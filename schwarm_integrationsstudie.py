"""
KKI Integrationsstudie
======================
Integrierte Grossstudie ueber Heterogenitaet, Engpaesse, Angriffe, Eindämmung
und Wiederherstellung auf gemeinsamer Schwarm-DNA.
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
        repetitions = int(os.getenv('KKI_INTEGRATION_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
        failure_round = min(rounds, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_INTEGRATION_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))
        failure_round = int(os.getenv('KKI_FAILURE_ROUND', '110'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'failure_round': min(rounds, max(attack_round + 1, failure_round)),
        'agent_count': int(os.getenv('KKI_INTEGRATION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
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
        'enable_prompt_injection': True,
        'enable_emergent_skills': True,
        'enable_fault_isolation': True,
        'enable_cluster_failures': True,
        'enable_restart_recovery': True,
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
        'resource_budget': float(os.getenv('KKI_INTEGRATION_RESOURCE_BUDGET', '0.55')),
        'resource_share_factor': float(os.getenv('KKI_RESOURCE_SHARE_FACTOR', '0.20')),
        'cluster_budget_skew': float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')),
        'bottleneck_threshold': float(os.getenv('KKI_BOTTLENECK_THRESHOLD', '1.00')),
        'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')),
        'meta_update_interval': int(os.getenv('KKI_META_UPDATE_INTERVAL', '6')),
        'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')),
        'injection_attack_round': params['attack_round'],
        'injection_strength': float(os.getenv('KKI_INJECTION_STRENGTH', '0.38')),
        'injection_source_count': int(os.getenv('KKI_INJECTION_SOURCE_COUNT', '6')),
        'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')),
        'skill_specialization_threshold': float(os.getenv('KKI_SKILL_SPECIALIZATION_THRESHOLD', '0.58')),
        'quarantine_compromise_threshold': float(os.getenv('KKI_QUARANTINE_COMPROMISE_THRESHOLD', '0.24')),
        'quarantine_exposure_threshold': float(os.getenv('KKI_QUARANTINE_EXPOSURE_THRESHOLD', '0.30')),
        'trust_shield_strength': float(os.getenv('KKI_TRUST_SHIELD_STRENGTH', '0.30')),
        'failure_round': params['failure_round'],
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_FAILURE_FRACTION', '0.22')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.32')),
    }
    return [
        {'name': 'homogen', 'label': 'Homogen'},
        {
            'name': 'clustered',
            'label': 'Heterogene Cluster',
            **common,
            'enable_meta_coordination': False,
            'enable_prompt_injection': False,
            'enable_emergent_skills': False,
            'enable_fault_isolation': False,
            'enable_cluster_failures': False,
            'enable_restart_recovery': False,
        },
        {
            'name': 'meta-defense',
            'label': 'Meta unter Angriff',
            **common,
            'enable_emergent_skills': False,
            'enable_fault_isolation': False,
            'enable_cluster_failures': False,
            'enable_restart_recovery': False,
        },
        {
            'name': 'emergent-defense',
            'label': 'Emergente Skills',
            **common,
            'enable_fault_isolation': False,
            'enable_cluster_failures': False,
            'enable_restart_recovery': False,
        },
        {
            'name': 'shielded-recovery',
            'label': 'Isolation + Wiederanlauf',
            **common,
        },
        {
            'name': 'integrated-architecture',
            'label': 'Integrierte Gesamtarchitektur',
            **common,
            'generalist_share': 0.14,
            'connector_share': 0.18,
            'sentinel_share': 0.20,
            'mediator_share': 0.26,
            'analyzer_share': 0.22,
            'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.05,
            'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.02,
            'trust_shield_strength': float(os.getenv('KKI_TRUST_SHIELD_STRENGTH', '0.30')) + 0.04,
            'failure_fraction': max(0.10, float(os.getenv('KKI_FAILURE_FRACTION', '0.22')) - 0.06),
            'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.32')) + 0.06,
            'cluster_budget_skew': max(0.20, float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')) - 0.08),
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
                + 0.16 * pol['workflow_metrics'].get('trust_shield_mean', 0.0)
                + 0.14 * pol['workflow_metrics'].get('sync_strength_mean', 0.0)
                + 0.20 * pol['workflow_metrics'].get('recovery_events_total', 0.0) / max(1, pol['config'].get('agent_count', 1))
                + 0.08 * pol['workflow_metrics'].get('reconfiguration_switch_total', 0.0) / max(1, pol['config'].get('agent_count', 1))
                - 0.08 * pol['workflow_metrics'].get('misinformation_corruption_mean', 0.0)
                - 0.06 * pol['workflow_metrics'].get('cluster_compromise_mean', 0.0)
                - 0.05 * pol['workflow_metrics'].get('failed_agents_mean', 0.0) / max(1, pol['config'].get('agent_count', 1))
                for pol, con in runs
            ]
        ),
        'polarization_index': mittelwert([run['final_polarization_index'] for run in polarization_runs]),
        'consensus_score': mittelwert([run['final_consensus_score'] for run in consensus_runs]),
        'cross_group_cooperation': mittelwert([run['cross_group_cooperation_rate'] for run in polarization_runs]),
        'resource_efficiency': mittelwert([run['workflow_metrics'].get('resource_efficiency', 0.0) for run in polarization_runs]),
        'meta_alignment': mittelwert([run['workflow_metrics'].get('meta_alignment_rate', 0.0) for run in polarization_runs]),
        'skill_alignment': mittelwert([run['workflow_metrics'].get('skill_alignment_rate', 0.0) for run in polarization_runs]),
        'shield_mean': mittelwert([run['workflow_metrics'].get('trust_shield_mean', 0.0) for run in polarization_runs]),
        'sync_strength': mittelwert([run['workflow_metrics'].get('sync_strength_mean', 0.0) for run in polarization_runs]),
        'recoveries': mittelwert([run['workflow_metrics'].get('recovery_events_total', 0.0) for run in polarization_runs]),
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    items = profile(params)
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI INTEGRATIONSSTUDIE')
    print('=' * 84)
    print('Fasst Heterogenitaet, Engpaesse, Angriff, Isolation und Wiederherstellung auf')
    print('einer gemeinsamen Schwarm-DNA zu einer finalen Grossstudie zusammen.\n')

    summaries = []
    for index, item in enumerate(items):
        runs = []
        for repetition in range(params['repetitions']):
            seed = base_seed + index * 100 + repetition
            runs.append(run_once(seed, params, item))
        summary = summarize_runs(runs, item)
        summaries.append(summary)
        print(
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"PI={summary['polarization_index']:.3f} | "
            f"Koop={summary['cross_group_cooperation']:.1%} | "
            f"Shield={summary['shield_mean']:.2f} | "
            f"Restart={summary['recoveries']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    print('\nBeste Gesamtarchitektur:', best['label'])
    print(f"Score {best['combined_score']:+.3f} bei Polarisierungsindex {best['polarization_index']:.3f}")
    print(
        f"Cross-Group-Kooperation {best['cross_group_cooperation']:.1%}, "
        f"Abschirmniveau {best['shield_mean']:.2f}, "
        f"Restart-Ereignisse {best['recoveries']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    scores = [item['combined_score'] for item in summaries]
    cooperation = [item['cross_group_cooperation'] * 100.0 for item in summaries]
    polarization = [item['polarization_index'] for item in summaries]
    shield = [item['shield_mean'] for item in summaries]
    restart = [item['recoveries'] for item in summaries]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    ax1, ax2, ax3, ax4 = axes.flat
    colors = ['#9aa0a6', '#4e79a7', '#59a14f', '#f28e2b', '#e15759', '#b07aa1']

    ax1.bar(labels, scores, color=colors)
    ax1.set_title('Kombinierter Gesamtscore')
    ax1.tick_params(axis='x', rotation=18)

    ax2.bar(labels, cooperation, color=colors)
    ax2.set_title('Cross-Group-Kooperation (%)')
    ax2.tick_params(axis='x', rotation=18)

    ax3.bar(labels, polarization, color=colors)
    ax3.set_title('Finaler Polarisierungsindex')
    ax3.tick_params(axis='x', rotation=18)

    ax4.bar(labels, shield, color=colors, label='Abschirmniveau')
    ax4.plot(labels, restart, color='#222222', marker='o', linewidth=2, label='Restart-Ereignisse')
    ax4.set_title('Isolation und Wiederherstellung')
    ax4.tick_params(axis='x', rotation=18)
    ax4.legend()

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_integrationsstudie.png', dpi=150)


if __name__ == '__main__':
    main()
