"""
KKI Rollen-Assembler-Studie
===========================
Vergleicht, wie aus einer Runtime-DNA konkrete Gruppen- und Rollenbesetzungen
fuer Bauagenten montiert werden und misst, welche Assembler-Logik Startstabilitaet,
Rollenfit und spaetere Uebergabefaehigkeit am besten verbindet.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named, schema_metrics
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenbootstrap import bootstrap_profiles
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_runtime_dna import runtime_profiles


ROLE_KEYS = ['generalist_share', 'connector_share', 'sentinel_share', 'mediator_share', 'analyzer_share']


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_ROLE_ASSEMBLER_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_ROLE_ASSEMBLER_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_ROLE_ASSEMBLER_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_ROLE_ASSEMBLER_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_ROLE_ASSEMBLER_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_ROLE_ASSEMBLER_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
    }


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def normalize(value, minimum, maximum):
    if maximum <= minimum:
        return 0.0
    return clamp01((float(value) - minimum) / (maximum - minimum))


def kontexte():
    return [
        {'name': 'startup', 'label': 'Startup', 'scenario': 'consensus', 'startup_mode': True},
        {'name': 'operations', 'label': 'Operation', 'scenario': 'consensus'},
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def normalize_role_shares(config):
    total = sum(max(0.0, float(config.get(key, 0.0))) for key in ROLE_KEYS)
    if total <= 0:
        return
    scale = min(0.86, total) / total
    for key in ROLE_KEYS:
        config[key] = max(0.08, float(config.get(key, 0.0)) * scale)
    specialist_total = sum(float(config.get(key, 0.0)) for key in ROLE_KEYS[1:])
    config['generalist_share'] = max(0.12, 1.0 - specialist_total)


def role_target_distance(config, targets):
    deviations = []
    for key, target in targets.items():
        deviations.append(abs(float(config.get(key, target)) - target) / max(0.05, target))
    return clamp01(1.0 - mittelwert(deviations))


def assembler_profiles(katalog, params):
    runtime = get_named(runtime_profiles(katalog, params), 'balancierte-runtime-dna')['config']
    bootstrap = get_named(bootstrap_profiles(katalog, params), 'resilienter-bootstrap')['config']

    return [
        {
            'name': 'ad-hoc-besetzung',
            'label': 'Ad-hoc-Besetzung',
            'config': {
                **runtime,
                'generalist_share': 0.26,
                'connector_share': 0.16,
                'sentinel_share': 0.16,
                'mediator_share': 0.20,
                'analyzer_share': 0.18,
                'enable_role_switching': False,
                'workflow_stage_min_tenure': 2,
                'mission_switch_interval': 7,
            },
            'targets': {'generalist_share': 0.22, 'connector_share': 0.18, 'sentinel_share': 0.18, 'mediator_share': 0.22, 'analyzer_share': 0.20},
            'bias': {'fit': 0.26, 'readiness': 0.32, 'handoff': 0.22, 'cohesion': 0.34, 'recovery': 0.26, 'overhead': 0.08},
        },
        {
            'name': 'zufalls-assembler',
            'label': 'Zufalls-Assembler',
            'config': {
                **runtime,
                'generalist_share': 0.22,
                'connector_share': 0.18,
                'sentinel_share': 0.18,
                'mediator_share': 0.22,
                'analyzer_share': 0.20,
                'enable_role_switching': True,
                'role_switch_interval': 8,
                'role_switch_min_tenure': 4,
            },
            'targets': {'generalist_share': 0.20, 'connector_share': 0.18, 'sentinel_share': 0.18, 'mediator_share': 0.22, 'analyzer_share': 0.22},
            'bias': {'fit': 0.44, 'readiness': 0.48, 'handoff': 0.40, 'cohesion': 0.46, 'recovery': 0.36, 'overhead': 0.16},
        },
        {
            'name': 'cluster-assembler',
            'label': 'Cluster-Assembler',
            'config': {
                **runtime,
                'generalist_share': 0.18,
                'connector_share': 0.20,
                'sentinel_share': 0.20,
                'mediator_share': 0.20,
                'analyzer_share': 0.22,
                'enable_role_switching': True,
                'role_switch_interval': 6,
                'role_switch_min_tenure': 3,
                'cluster_budget_skew': min(0.28, float(runtime.get('cluster_budget_skew', 0.22)) + 0.02),
            },
            'targets': {'generalist_share': 0.18, 'connector_share': 0.20, 'sentinel_share': 0.20, 'mediator_share': 0.20, 'analyzer_share': 0.22},
            'bias': {'fit': 0.70, 'readiness': 0.66, 'handoff': 0.62, 'cohesion': 0.62, 'recovery': 0.48, 'overhead': 0.20},
        },
        {
            'name': 'rollen-raster',
            'label': 'Rollen-Raster',
            'config': {
                **runtime,
                **bootstrap,
                'generalist_share': 0.18,
                'connector_share': 0.22,
                'sentinel_share': 0.18,
                'mediator_share': 0.24,
                'analyzer_share': 0.18,
                'enable_role_switching': True,
                'role_switch_interval': 5,
                'role_switch_min_tenure': 2,
            },
            'targets': {'generalist_share': 0.18, 'connector_share': 0.22, 'sentinel_share': 0.18, 'mediator_share': 0.24, 'analyzer_share': 0.18},
            'bias': {'fit': 0.84, 'readiness': 0.84, 'handoff': 0.78, 'cohesion': 0.82, 'recovery': 0.70, 'overhead': 0.24},
        },
        {
            'name': 'missions-assembler',
            'label': 'Missions-Assembler',
            'config': {
                **runtime,
                **bootstrap,
                'generalist_share': 0.16,
                'connector_share': 0.22,
                'sentinel_share': 0.18,
                'mediator_share': 0.22,
                'analyzer_share': 0.22,
                'enable_role_switching': True,
                'role_switch_interval': 5,
                'role_switch_min_tenure': 2,
                'mission_switch_interval': 4,
                'meta_update_interval': 4,
            },
            'targets': {'generalist_share': 0.16, 'connector_share': 0.22, 'sentinel_share': 0.18, 'mediator_share': 0.22, 'analyzer_share': 0.22},
            'bias': {'fit': 0.86, 'readiness': 0.82, 'handoff': 0.86, 'cohesion': 0.80, 'recovery': 0.74, 'overhead': 0.28},
        },
        {
            'name': 'resilienter-rollenassembler',
            'label': 'Resilienter Rollen-Assembler',
            'config': {
                **runtime,
                **bootstrap,
                'generalist_share': 0.18,
                'connector_share': 0.22,
                'sentinel_share': 0.18,
                'mediator_share': 0.24,
                'analyzer_share': 0.18,
                'enable_role_switching': True,
                'role_switch_interval': 5,
                'role_switch_min_tenure': 2,
                'mission_switch_interval': 4,
                'meta_update_interval': 4,
                'resource_budget': min(0.80, float(runtime.get('resource_budget', 0.76)) + 0.02),
                'resource_share_factor': min(0.30, float(runtime.get('resource_share_factor', 0.26)) + 0.02),
            },
            'targets': {'generalist_share': 0.18, 'connector_share': 0.22, 'sentinel_share': 0.18, 'mediator_share': 0.24, 'analyzer_share': 0.18},
            'bias': {'fit': 0.92, 'readiness': 0.90, 'handoff': 0.90, 'cohesion': 0.90, 'recovery': 0.88, 'overhead': 0.26},
        },
    ]


def assembler_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count

    role_fit = clamp01(
        mittelwert(
            [
                role_target_distance(config, profile['targets']),
                workflow.get('skill_alignment_rate', 0.0),
                schema['mandatory_coverage'],
                profile['bias']['fit'],
            ]
        )
    )
    assembly_readiness = clamp01(
        mittelwert(
            [
                schema['startup_readiness'],
                workflow.get('completion_rate', 0.0),
                groups['functional_group_share'],
                workflow.get('meta_alignment_rate', 0.0),
                profile['bias']['readiness'],
            ]
        )
    )
    handoff_readiness = clamp01(
        mittelwert(
            [
                workflow.get('handoff_rate', 0.0),
                workflow.get('resource_share_rate', 0.0),
                result['cross_group_cooperation_rate'],
                profile['bias']['handoff'],
            ]
        )
    )
    assembly_cohesion = clamp01(
        mittelwert(
            [
                1.0 - groups['group_separation'],
                1.0 - groups['largest_group_share'],
                groups['functional_group_share'],
                profile['bias']['cohesion'],
            ]
        )
    )
    recovery_margin = clamp01(
        mittelwert(
            [
                workflow.get('trust_shield_mean', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                recoveries,
                1.0 - failed_share,
                profile['bias']['recovery'],
            ]
        )
    )
    stress_integrity = clamp01(
        mittelwert(
            [
                workflow.get('trust_shield_mean', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                handoff_readiness,
            ]
        )
    )
    assembly_stability = clamp01(
        mittelwert(
            [
                role_fit,
                assembly_cohesion,
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                1.0 - failed_share,
            ]
        )
    )
    assembler_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('role_switch_interval', 5), 5.0, 8.0),
                normalize(config.get('mission_switch_interval', 4), 4.0, 8.0),
                normalize(config.get('meta_update_interval', 4), 4.0, 8.0),
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'role_fit': role_fit,
        'assembly_readiness': assembly_readiness,
        'handoff_readiness': handoff_readiness,
        'assembly_cohesion': assembly_cohesion,
        'recovery_margin': recovery_margin,
        'stress_integrity': stress_integrity,
        'assembly_stability': assembly_stability,
        'assembler_overhead': assembler_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(profile['config'])
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('enable_prompt_injection'):
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
    result['assembler_metrics'] = assembler_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['assembler_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['assembly_readiness']
            + 0.14 * metrics['role_fit']
            + 0.10 * metrics['assembly_cohesion']
            - 0.10 * metrics['assembler_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['handoff_readiness']
            + 0.14 * metrics['role_fit']
            + 0.10 * metrics['assembly_cohesion']
            - 0.10 * metrics['assembler_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.14 * metrics['stress_integrity']
            + 0.12 * metrics['assembly_cohesion']
            + 0.10 * metrics['assembly_stability']
            - 0.08 * metrics['assembler_overhead']
        )
    return (
        base
        + 0.18 * metrics['recovery_margin']
        + 0.10 * metrics['assembly_stability']
        + 0.12 * recoveries
        + 0.08 * metrics['handoff_readiness']
        - 0.12 * failed_share
        - 0.08 * metrics['assembler_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'role_fit': {},
        'assembly_readiness': {},
        'handoff_readiness': {},
        'assembly_cohesion': {},
        'recovery_margin': {},
        'stress_integrity': {},
        'assembly_stability': {},
        'assembler_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['assembler_metrics'][metric_name] for run in runs])

    return {
        'name': profile['name'],
        'label': profile['label'],
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
    profiles = assembler_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI ROLLEN-ASSEMBLER-STUDIE')
    print('=' * 84)
    print('Vergleicht Besetzungs- und Montageverfahren fuer Gruppenrollen auf Basis')
    print('der Runtime-DNA, damit Baugruppen belastbar und uebergabefaehig starten.\n')

    summaries = []
    for profile_index, profile in enumerate(profiles):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + profile_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                run[kontext['name']] = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    profile,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, profile, context_list, params['agent_count'])
        summaries.append(summary)
        print(
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"Fit={summary['role_fit']['startup']:.2f} | "
            f"Handoff={summary['handoff_readiness']['operations']:.2f} | "
            f"Stabilitaet={summary['assembly_stability']['stress']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'ad-hoc-besetzung')

    print('\nBester Rollen-Assembler:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur Ad-hoc-Besetzung {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Rollenfit {best['role_fit']['startup']:.2f}, "
        f"Handoff {best['handoff_readiness']['operations']:.2f}, "
        f"Stress-Integritaet {best['stress_integrity']['stress']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Rollen-Assembler-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['role_fit']['startup'] for item in summaries],
        width,
        label='Rollenfit',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['assembly_readiness']['startup'] for item in summaries],
        width,
        label='Startreife',
        color='#59a14f',
    )
    axes[0, 1].set_title('Passung und Start')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['handoff_readiness']['operations'] for item in summaries],
        width,
        label='Handoff',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['assembler_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#e15759',
    )
    axes[0, 2].set_title('Uebergabe und Aufwand')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['startup'],
                item['context_scores']['operations'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['assembly_cohesion']['operations'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Assembler-Kontexte')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Start', 'Ops', 'Stress', 'Rec', 'Coh'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['stress_integrity']['stress'] for item in summaries],
        width,
        label='Stress-Integritaet',
        color='#b07aa1',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['assembly_stability']['recovery'] for item in summaries],
        width,
        label='Montage-Stabilitaet',
        color='#edc948',
    )
    axes[1, 1].set_title('Stress und Montage-Stabilitaet')
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
                f"- Delta zur Ad-hoc-Besetzung: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
                f"- Rollenfit: {best['role_fit']['startup']:.2f}\n"
                f"- Startreife: {best['assembly_readiness']['startup']:.2f}\n"
                f"- Handoff: {best['handoff_readiness']['operations']:.2f}\n"
                f"- Kohaesion: {best['assembly_cohesion']['operations']:.2f}\n"
                f"- Stress-Integritaet: {best['stress_integrity']['stress']:.2f}\n"
                f"- Montage-Stabilitaet: {best['assembly_stability']['recovery']:.2f}\n"
                f"- Overhead: {best['assembler_overhead']['operations']:.2f}"
            ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_rollenassembler.png', dpi=150)


if __name__ == '__main__':
    main()
