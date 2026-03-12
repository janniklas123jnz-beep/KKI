"""
KKI Spezialfaehigkeits-Studie
============================
Vergleicht, ob sich aus gemeinsamer Agenten-DNA durch adaptives Gruppenlernen
emergente Spezialfaehigkeiten ausbilden, die Meta-Koordination weiter verbessern.
"""

from __future__ import annotations

import os
import random
from collections import Counter

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
        repetitions = int(os.getenv('KKI_SKILL_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
    else:
        repetitions = int(os.getenv('KKI_SKILL_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'agent_count': int(os.getenv('KKI_SKILL_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
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
    }


def profile():
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
        'resource_budget': float(os.getenv('KKI_SKILL_RESOURCE_BUDGET', '0.55')),
        'resource_share_factor': float(os.getenv('KKI_RESOURCE_SHARE_FACTOR', '0.20')),
        'cluster_budget_skew': float(os.getenv('KKI_CLUSTER_BUDGET_SKEW', '0.55')),
        'bottleneck_threshold': float(os.getenv('KKI_BOTTLENECK_THRESHOLD', '1.00')),
        'bottleneck_triage_intensity': float(os.getenv('KKI_BOTTLENECK_TRIAGE_INTENSITY', '0.90')),
        'meta_update_interval': int(os.getenv('KKI_META_UPDATE_INTERVAL', '6')),
        'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')),
        'injection_attack_round': int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90')),
        'injection_strength': float(os.getenv('KKI_INJECTION_STRENGTH', '0.38')),
        'injection_source_count': int(os.getenv('KKI_INJECTION_SOURCE_COUNT', '6')),
    }
    return [
        {'name': 'homogen', 'label': 'Homogen'},
        {
            'name': 'meta-coordination',
            'label': 'Meta-Koordination',
            **common,
            'enable_emergent_skills': False,
        },
        {
            'name': 'group-learning',
            'label': 'Gruppenlernen',
            **common,
            'enable_emergent_skills': True,
            'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.08')),
            'skill_specialization_threshold': float(os.getenv('KKI_SKILL_SPECIALIZATION_THRESHOLD', '0.68')),
        },
        {
            'name': 'emergent-specialization',
            'label': 'Emergente Spezialfaehigkeiten',
            **common,
            'enable_emergent_skills': True,
            'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')),
            'skill_specialization_threshold': float(os.getenv('KKI_SKILL_SPECIALIZATION_THRESHOLD', '0.60')),
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
                + 0.18 * pol['workflow_metrics']['completion_rate']
                + 0.06 * pol['workflow_metrics']['resource_efficiency']
                + 0.06 * pol['workflow_metrics']['meta_alignment_rate']
                + 0.08 * pol['workflow_metrics'].get('skill_alignment_rate', 0.0)
                + 0.03 * pol['workflow_metrics'].get('group_learning_gain_rate', 0.0)
                for pol, con in runs
            ]
        ),
        'polarization_index': mittelwert([run['final_polarization_index'] for run in polarization_runs]),
        'consensus_score': mittelwert([run['final_consensus_score'] for run in consensus_runs]),
        'cross_group_cooperation': mittelwert([run['cross_group_cooperation_rate'] for run in polarization_runs]),
        'resource_efficiency': mittelwert([run['workflow_metrics'].get('resource_efficiency', 0.0) for run in polarization_runs]),
        'meta_alignment_rate': mittelwert([run['workflow_metrics'].get('meta_alignment_rate', 0.0) for run in polarization_runs]),
        'skill_alignment_rate': mittelwert([run['workflow_metrics'].get('skill_alignment_rate', 0.0) for run in polarization_runs]),
        'skill_switches': mittelwert([run['workflow_metrics'].get('skill_switch_total', 0.0) for run in polarization_runs]),
        'learning_gain': mittelwert([run['workflow_metrics'].get('group_learning_gain_total', 0.0) for run in polarization_runs]),
        'dominant_skill': Counter(
            max(
                run['workflow_metrics'].get('emergent_skill_distribution', {'adaptive_generalist': 1}).items(),
                key=lambda item: item[1],
            )[0]
            for run in polarization_runs
        ).most_common(1)[0][0],
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    items = profile()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI SPEZIALFAEHIGKEITS-STUDIE')
    print('=' * 84)
    print('Untersucht, ob aus gemeinsamer Agenten-DNA durch Gruppenlernen stabile Talente')
    print('fuer Brueckenbau, Analyse, Abwehr und Erholung emergieren.\n')

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
            f"Skill={summary['skill_alignment_rate']:.1%} | "
            f"Dominant={summary['dominant_skill']}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    print('\nBeste Lernarchitektur:', best['label'])
    print(f"Score {best['combined_score']:+.3f} bei Polarisierungsindex {best['polarization_index']:.3f}")
    print(
        f"Cross-Group-Kooperation {best['cross_group_cooperation']:.1%}, "
        f"Skill-Ausrichtung {best['skill_alignment_rate']:.1%}, "
        f"dominante Faehigkeit {best['dominant_skill']}"
    )

    labels = [item['label'] for item in summaries]
    scores = [item['combined_score'] for item in summaries]
    polarization = [item['polarization_index'] for item in summaries]
    cooperation = [item['cross_group_cooperation'] * 100.0 for item in summaries]
    skill_alignment = [item['skill_alignment_rate'] * 100.0 for item in summaries]
    learning_gain = [item['learning_gain'] for item in summaries]

    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    ax1, ax2, ax3, ax4 = axes.flat

    ax1.bar(labels, scores, color=['#9aa0a6', '#6c8ebf', '#59a14f', '#f28e2b'])
    ax1.set_title('Kombinierter Gesamtscore')
    ax1.tick_params(axis='x', rotation=18)

    ax2.bar(labels, polarization, color=['#9aa0a6', '#6c8ebf', '#59a14f', '#f28e2b'])
    ax2.set_title('Finaler Polarisierungsindex')
    ax2.tick_params(axis='x', rotation=18)

    ax3.bar(labels, cooperation, color=['#9aa0a6', '#6c8ebf', '#59a14f', '#f28e2b'])
    ax3.set_title('Cross-Group-Kooperation (%)')
    ax3.tick_params(axis='x', rotation=18)

    ax4.bar(labels, skill_alignment, color=['#9aa0a6', '#6c8ebf', '#59a14f', '#f28e2b'], label='Skill-Ausrichtung')
    ax4.plot(labels, learning_gain, color='#222222', marker='o', linewidth=2, label='Lerngewinn gesamt')
    ax4.set_title('Lernen und emergente Spezialisierung')
    ax4.tick_params(axis='x', rotation=18)
    ax4.legend()

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_spezialfaehigkeiten.png', dpi=150)


if __name__ == '__main__':
    main()
