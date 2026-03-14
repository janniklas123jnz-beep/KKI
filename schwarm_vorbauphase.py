"""
KKI Vor-Bauphasen-Studie
========================
Integrierter Vergleich der besten Interaktions-, Gruppen- und Robustheitsmuster
als letzte Simulationsstufe vor einer praktischen Bauphase.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_gruppenidentitaet import (
    build_profile as build_identity_profile,
    modellkatalog,
    mittelwert,
    overlay_profiles,
)
from schwarm_gruppentalente import build_profile as build_talent_profile
from schwarm_gruppentalente import talent_profile
from schwarm_gruppenhandoff import handoff_profiles
from schwarm_faehigkeitsarbitration import arbitration_profiles
from schwarm_gruppenrobustheit import robustness_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_PREBUILD_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_PREBUILD_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))
        failure_round = int(os.getenv('KKI_FAILURE_ROUND', '110'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'failure_round': min(rounds - 1, max(attack_round + 1, failure_round)),
        'agent_count': int(os.getenv('KKI_PREBUILD_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_PREBUILD_STRESS_STRENGTH', '0.46')),
        'stress_sources': int(os.getenv('KKI_PREBUILD_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_FAILURE_FRACTION', '0.20')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
    }


def get_named(items, name):
    return next(item for item in items if item['name'] == name)


def kontexte():
    return [
        {'name': 'polarization', 'label': 'Polarisierung', 'scenario': 'polarization'},
        {'name': 'consensus', 'label': 'Konsens', 'scenario': 'consensus'},
        {
            'name': 'stress',
            'label': 'Manipulationsstress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
        },
        {
            'name': 'recovery',
            'label': 'Ausfall + Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def prebuild_profiles(katalog, params):
    identity_shared = build_identity_profile(katalog, get_named(overlay_profiles(), 'shared-dna'))
    talent_regen = build_talent_profile(katalog, get_named(talent_profile(), 'regeneration-fokus'))
    handoff_parallel = get_named(handoff_profiles(katalog), 'parallele-resiliente-handoffs')['config']
    meta_arb = get_named(arbitration_profiles(katalog), 'meta-arbitration')['config']
    robust_balance = get_named(robustness_profiles(katalog), 'robuste-balance')['config']

    prebuild_candidate = {
        **robust_balance,
        'analyzer_memory_window': max(
            robust_balance.get('analyzer_memory_window', 18),
            identity_shared.get('analyzer_memory_window', 18),
        ),
        'analyzer_learning_multiplier': max(
            robust_balance.get('analyzer_learning_multiplier', 1.12),
            identity_shared.get('analyzer_learning_multiplier', 1.12),
        ),
        'group_learning_rate': max(
            robust_balance.get('group_learning_rate', 0.0),
            talent_regen.get('group_learning_rate', 0.0),
            meta_arb.get('group_learning_rate', 0.0),
        )
        + 0.02,
        'meta_priority_strength': max(
            robust_balance.get('meta_priority_strength', 0.0),
            meta_arb.get('meta_priority_strength', 0.0),
        )
        + 0.04,
        'resource_budget': max(
            robust_balance.get('resource_budget', 0.0),
            handoff_parallel.get('resource_budget', 0.0),
            meta_arb.get('resource_budget', 0.0),
        )
        + 0.04,
        'resource_share_factor': max(
            robust_balance.get('resource_share_factor', 0.0),
            handoff_parallel.get('resource_share_factor', 0.0),
            meta_arb.get('resource_share_factor', 0.0),
        ),
        'trust_shield_strength': max(
            robust_balance.get('trust_shield_strength', 0.0),
            0.36,
        )
        + 0.02,
        'rewire_cross_group_bonus': max(
            robust_balance.get('rewire_cross_group_bonus', 0.0),
            handoff_parallel.get('rewire_cross_group_bonus', 0.0),
            identity_shared.get('rewire_cross_group_bonus', 0.0),
        )
        + 0.02,
        'cluster_budget_skew': max(
            0.16,
            min(
                robust_balance.get('cluster_budget_skew', 0.55),
                meta_arb.get('cluster_budget_skew', 0.55),
            )
            - 0.02,
        ),
        'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
        'resync_strength': params['resync_strength'] + 0.08,
    }

    return [
        {'name': 'homogen', 'label': 'Homogen', 'config': {}},
        {'name': 'shared-dna', 'label': 'Gemeinsame DNA', 'config': identity_shared},
        {'name': 'regeneration-fokus', 'label': 'Regeneration-Fokus', 'config': talent_regen},
        {'name': 'parallel-handoffs', 'label': 'Resiliente Parallel-Handoffs', 'config': handoff_parallel},
        {'name': 'meta-arbitration', 'label': 'Meta-Arbitration', 'config': meta_arb},
        {'name': 'robuste-balance', 'label': 'Robuste Balance', 'config': robust_balance},
        {'name': 'prebuild-candidate', 'label': 'Vor-Bauphasen-Kandidat', 'config': prebuild_candidate},
    ]


def prebuild_metrics(result, params):
    workflow = result['workflow_metrics']
    completion_rate = workflow.get('completion_rate', 0.0)
    resource_efficiency = workflow.get('resource_efficiency', 0.0)
    meta_alignment_rate = workflow.get('meta_alignment_rate', 0.0)
    skill_alignment_rate = workflow.get('skill_alignment_rate', 0.0)
    handoff_rate = workflow.get('handoff_rate', 0.0)
    resource_share_rate = workflow.get('resource_share_rate', 0.0)
    bottleneck_relief_rate = workflow.get('bottleneck_relief_rate', 0.0)
    detection_rate = workflow.get('misinformation_detection_rate', 0.0)
    corruption_mean = workflow.get('misinformation_corruption_mean', 0.0)
    cluster_compromise_mean = workflow.get('cluster_compromise_mean', 0.0)
    trust_shield_mean = workflow.get('trust_shield_mean', 0.0)
    recovery_events_total = workflow.get('recovery_events_total', 0.0)
    sync_strength_mean = workflow.get('sync_strength_mean', 0.0)
    reconfiguration_switch_total = workflow.get('reconfiguration_switch_total', 0.0)
    failed_agents_mean = workflow.get('failed_agents_mean', 0.0)
    mission_success = mittelwert(list(result.get('mission_success_rates', {}).values()))
    stress_integrity = max(0.0, 1.0 - corruption_mean)
    compromise_reserve = max(0.0, 1.0 - cluster_compromise_mean)
    failed_share = failed_agents_mean / max(1.0, params['agent_count'])
    recovery_load = min(1.0, recovery_events_total / max(1.0, params['agent_count'] * 0.25))
    recovery_efficiency = mittelwert(
        [
            min(1.0, sync_strength_mean),
            max(0.0, 1.0 - failed_share),
            max(0.0, 1.0 - recovery_load),
            min(1.0, bottleneck_relief_rate),
        ]
    )
    build_readiness = mittelwert(
        [
            completion_rate,
            resource_efficiency,
            meta_alignment_rate,
            mission_success,
            compromise_reserve,
            stress_integrity,
            recovery_efficiency,
        ]
    )
    return {
        'completion_rate': completion_rate,
        'resource_efficiency': resource_efficiency,
        'meta_alignment_rate': meta_alignment_rate,
        'skill_alignment_rate': skill_alignment_rate,
        'handoff_rate': handoff_rate,
        'resource_share_rate': resource_share_rate,
        'bottleneck_relief_rate': bottleneck_relief_rate,
        'detection_rate': detection_rate,
        'corruption_mean': corruption_mean,
        'stress_integrity': stress_integrity,
        'cluster_compromise_mean': cluster_compromise_mean,
        'compromise_reserve': compromise_reserve,
        'trust_shield_mean': trust_shield_mean,
        'recovery_events_total': recovery_events_total,
        'sync_strength_mean': sync_strength_mean,
        'reconfiguration_switch_total': reconfiguration_switch_total,
        'failed_agents_mean': failed_agents_mean,
        'recovery_load': recovery_load,
        'recovery_efficiency': recovery_efficiency,
        'build_readiness': build_readiness,
        'mission_success': mission_success,
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
    }


def run_context(seed, params, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(eintrag['config'])
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('enable_prompt_injection'):
        config['enable_prompt_injection'] = True
        config['injection_attack_round'] = params['attack_round']
        config['injection_strength'] = params['stress_strength']
        config['injection_source_count'] = params['stress_sources']
    else:
        config['enable_prompt_injection'] = False

    if kontext.get('enable_failures'):
        config['enable_cluster_failures'] = True
        config['enable_restart_recovery'] = True
        config['failure_round'] = params['failure_round']
        config['failure_duration'] = params['failure_duration']
        config.setdefault('failure_fraction', params['failure_fraction'])
        config.setdefault('resync_strength', params['resync_strength'])

    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    result['prebuild_metrics'] = prebuild_metrics(result, params)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['prebuild_metrics']
    base = metrics['consensus'] - metrics['polarization']
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)
    reconfigs = metrics['reconfiguration_switch_total'] / max(1.0, agent_count)
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    if kontext_name == 'polarization':
        return (
            base
            + 0.14 * metrics['cross_group_cooperation']
            + 0.10 * metrics['skill_alignment_rate']
            + 0.08 * metrics['mission_success']
            + 0.08 * metrics['meta_alignment_rate']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.10 * metrics['resource_efficiency']
            + 0.10 * metrics['meta_alignment_rate']
            + 0.08 * metrics['handoff_rate']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['detection_rate']
            + 0.10 * metrics['trust_shield_mean']
            + 0.08 * metrics['bottleneck_relief_rate']
            + 0.08 * metrics['resource_share_rate']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
        )
    return (
        base
        + 0.18 * metrics['trust_shield_mean']
        + 0.18 * metrics['sync_strength_mean']
        + 0.16 * recoveries
        + 0.10 * reconfigs
        + 0.08 * metrics['detection_rate']
        - 0.12 * failed_share
        - 0.08 * metrics['cluster_compromise_mean']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'resource_efficiency': {},
        'meta_alignment_rate': {},
        'skill_alignment_rate': {},
        'handoff_rate': {},
        'resource_share_rate': {},
        'bottleneck_relief_rate': {},
        'detection_rate': {},
        'corruption_mean': {},
        'stress_integrity': {},
        'cluster_compromise_mean': {},
        'compromise_reserve': {},
        'trust_shield_mean': {},
        'recovery_events_total': {},
        'sync_strength_mean': {},
        'reconfiguration_switch_total': {},
        'failed_agents_mean': {},
        'recovery_load': {},
        'recovery_efficiency': {},
        'build_readiness': {},
        'mission_success': {},
        'cross_group_cooperation': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['prebuild_metrics'][metric_name] for run in runs])

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']], agent_count) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        **metrics,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    eintraege = prebuild_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI VOR-BAUPHASEN-STUDIE')
    print('=' * 84)
    print('Integriert die besten Muster aus Identitaet, Talenten, Handoffs, Arbitration')
    print('und Robustheit als letzten Architekturvergleich vor der Bauphase.\n')

    summaries = []
    for profil_index, eintrag in enumerate(eintraege):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + profil_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                run[kontext['name']] = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    eintrag,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, eintrag, context_list, params['agent_count'])
        summaries.append(summary)
        print(
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"Readiness={summary['build_readiness']['recovery']:.1%} | "
            f"Recovery-Eff={summary['recovery_efficiency']['recovery']:.1%} | "
            f"Stress-Int={summary['stress_integrity']['stress']:.1%}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'shared-dna')
    print('\nBeste Vor-Bauphasen-Architektur:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur gemeinsamen DNA {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Build-Readiness {best['build_readiness']['recovery']:.1%}, "
        f"Recovery-Effizienz {best['recovery_efficiency']['recovery']:.1%}, "
        f"Stress-Integritaet {best['stress_integrity']['stress']:.1%}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#4e79a7', '#f28e2b', '#76b7b2', '#59a14f', '#e15759', '#b07aa1']

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Vor-Bauphasen-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['completion_rate']['consensus'] * 100.0 for item in summaries],
        width,
        label='Completion',
        color='#59a14f',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['meta_alignment_rate']['consensus'] * 100.0 for item in summaries],
        width,
        label='Meta-Ausrichtung',
        color='#4e79a7',
    )
    axes[0, 1].set_title('Konsens und Koordination')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['stress_integrity']['stress'] * 100.0 for item in summaries],
        width,
        label='Stress-Integritaet',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['compromise_reserve']['stress'] * 100.0 for item in summaries],
        width,
        label='Reserve',
        color='#e15759',
    )
    axes[0, 2].set_title('Stressabwehr')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['polarization'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['build_readiness']['recovery'],
                item['recovery_efficiency']['recovery'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4, 5])
    axes[1, 0].set_xticklabels(['Pol', 'Kon', 'Stress', 'Rec', 'Ready', 'Eff'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['recovery_events_total']['recovery'] for item in summaries],
        width,
        label='Recovery-Events',
        color='#b07aa1',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['recovery_load']['recovery'] * 100.0 for item in summaries],
        width,
        label='Recovery-Last',
        color='#9c755f',
    )
    axes[1, 1].set_title('Wiederherstellung')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].legend()
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].axis('off')
    axes[1, 2].text(
        0.0,
        0.98,
        (
            "Zusammenfassung\n"
            f"- Bestes Profil: {best['label']}\n"
            f"- Delta zur gemeinsamen DNA: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Completion: {best['completion_rate']['consensus']:.1%}\n"
            f"- Meta-Ausrichtung: {best['meta_alignment_rate']['consensus']:.1%}\n"
            f"- Build-Readiness: {best['build_readiness']['recovery']:.1%}\n"
            f"- Stress-Integritaet: {best['stress_integrity']['stress']:.1%}\n"
            f"- Reserve: {best['compromise_reserve']['stress']:.1%}\n"
            f"- Recovery-Events: {best['recovery_events_total']['recovery']:.2f}\n"
            f"- Recovery-Effizienz: {best['recovery_efficiency']['recovery']:.1%}\n"
            f"- Recovery-Last: {best['recovery_load']['recovery']:.1%}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_vorbauphase.png', dpi=150)


if __name__ == '__main__':
    main()
