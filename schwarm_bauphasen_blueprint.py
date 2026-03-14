"""
KKI Bauphasen-Blueprint-Gesamtstudie
====================================
Vergleicht finale Bauphasen-Blueprints, die die Siegerbausteine der Reihe zu
konkreten Gesamtarchitekturen zusammenfuehren, und misst, welche Kombination
als erster Blueprint fuer die spaetere reale Bauphase uebernommen werden sollte.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_bauphasen_stresstest import apply_overlay_modules, architecture_profiles
from schwarm_dna_schema import get_named, schema_metrics, schema_profiles
from schwarm_governance_layer import governance_profiles
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenbootstrap import bootstrap_profiles
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_handoff_vertraege import contract_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_laufzeitsupervision import supervision_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_protokollstack import protocol_profiles
from schwarm_werkzeugbindung import tool_binding_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_BLUEPRINT_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 3)
        failure_round = min(rounds - 2, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_BLUEPRINT_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_BLUEPRINT_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_BLUEPRINT_STRESS_STRENGTH', '0.50')),
        'stress_sources': int(os.getenv('KKI_BLUEPRINT_STRESS_SOURCES', '10')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_BLUEPRINT_FAILURE_FRACTION', '0.20')),
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
        {'name': 'bootstrap', 'label': 'Bootstrap', 'scenario': 'consensus', 'startup_mode': True},
        {'name': 'operations', 'label': 'Operation', 'scenario': 'consensus'},
        {
            'name': 'stress',
            'label': 'Stress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
        {
            'name': 'blueprint',
            'label': 'Blueprint',
            'scenario': 'consensus',
            'blueprint_mode': True,
        },
    ]


def blueprint_profiles(katalog, params):
    schema_entries = schema_profiles(katalog)
    minimal = get_named(schema_entries, 'minimal-contract')['config']
    learning = get_named(schema_entries, 'learning-contract')['config']
    balanced = get_named(schema_entries, 'balanced-contract')['config']
    bootstrap = get_named(bootstrap_profiles(katalog, params), 'resilienter-bootstrap')['config']
    protocol = get_named(protocol_profiles(katalog, params), 'resilienter-protokollstack')['config']
    contract = get_named(contract_profiles(katalog, params), 'resilienter-handoff-vertrag')['config']
    governance = get_named(governance_profiles(katalog, params), 'resilienter-governance-layer')['config']
    tool_binding = get_named(tool_binding_profiles(katalog, params), 'resiliente-werkzeugfoederation')
    supervision = get_named(supervision_profiles(katalog, params), 'resiliente-supervisor-foederation')['config']
    stress_stack = get_named(architecture_profiles(katalog, params), 'resilienter-bauphasen-stack')['config']

    compatible_overlay = apply_overlay_modules(balanced, ['analysis', 'bridge', 'shield', 'recovery'], 0.88)
    learning_overlay = apply_overlay_modules(learning, ['analysis', 'bridge', 'recovery'], 0.92)

    return [
        {
            'name': 'minimaler-blueprint',
            'label': 'Minimaler Blueprint',
            'config': {
                **minimal,
                **bootstrap,
                **contract,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'resource_share_factor': 0.22,
            },
            'bias': {'coverage': 0.42, 'readiness': 0.50, 'resilience': 0.36, 'extensibility': 0.40, 'operability': 0.56, 'overhead': 0.10},
        },
        {
            'name': 'lernorientierter-blueprint',
            'label': 'Lernorientierter Blueprint',
            'config': {
                **learning,
                **learning_overlay,
                **bootstrap,
                **contract,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'resource_share_factor': 0.26,
                'meta_update_interval': 5,
            },
            'bias': {'coverage': 0.62, 'readiness': 0.64, 'resilience': 0.54, 'extensibility': 0.84, 'operability': 0.68, 'overhead': 0.20},
        },
        {
            'name': 'governance-blueprint',
            'label': 'Governance-Blueprint',
            'config': {
                **balanced,
                **compatible_overlay,
                **bootstrap,
                **protocol,
                **contract,
                **governance,
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.94,
                'bottleneck_triage_intensity': 0.90,
            },
            'bias': {'coverage': 0.84, 'readiness': 0.80, 'resilience': 0.82, 'extensibility': 0.76, 'operability': 0.76, 'overhead': 0.28},
        },
        {
            'name': 'operativer-blueprint',
            'label': 'Operativer Blueprint',
            'config': {
                **balanced,
                **compatible_overlay,
                **bootstrap,
                **protocol,
                **contract,
                **governance,
                **tool_binding['base_config'],
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.94,
                'bottleneck_triage_intensity': 0.92,
            },
            'bias': {'coverage': 0.90, 'readiness': 0.86, 'resilience': 0.84, 'extensibility': 0.82, 'operability': 0.88, 'overhead': 0.30},
        },
        {
            'name': 'resilienter-blueprint',
            'label': 'Resilienter Blueprint',
            'config': {
                **stress_stack,
                **supervision,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'meta_update_interval': 4,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.05),
                'resync_strength': min(0.54, supervision.get('resync_strength', params['resync_strength']) + 0.02),
            },
            'bias': {'coverage': 0.96, 'readiness': 0.94, 'resilience': 0.96, 'extensibility': 0.90, 'operability': 0.90, 'overhead': 0.30},
        },
    ]


def blueprint_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    arbitration_activity = normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0)

    architectural_coverage = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                1.0 if config.get('enable_meta_coordination', False) else 0.0,
                1.0 if config.get('mission_arbitration_enabled', False) else 0.0,
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                1.0 if config.get('enable_bottleneck_management', False) else 0.0,
                bias['coverage'],
            ]
        )
    )
    blueprint_readiness = clamp01(
        mittelwert(
            [
                schema['startup_readiness'],
                workflow.get('completion_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                groups['functional_group_share'],
                bias['readiness'],
            ]
        )
    )
    blueprint_resilience = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                recoveries,
                1.0 - failed_share,
                bias['resilience'],
            ]
        )
    )
    blueprint_extensibility = clamp01(
        mittelwert(
            [
                schema['extensibility'],
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                result['cross_group_cooperation_rate'],
                bias['extensibility'],
            ]
        )
    )
    operational_flow = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                bias['operability'],
            ]
        )
    )
    blueprint_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 8.0),
                arbitration_activity,
                normalize(config.get('resource_share_factor', 0.20), 0.20, 0.30),
                normalize(config.get('bottleneck_triage_intensity', 0.80), 0.80, 0.96),
                bias['overhead'],
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
        'detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'architectural_coverage': architectural_coverage,
        'blueprint_readiness': blueprint_readiness,
        'blueprint_resilience': blueprint_resilience,
        'blueprint_extensibility': blueprint_extensibility,
        'operational_flow': operational_flow,
        'blueprint_overhead': blueprint_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    profile_config = dict(profile['config'])

    if kontext.get('blueprint_mode'):
        profile_config['resource_budget'] = min(0.82, profile_config.get('resource_budget', 0.72) + 0.02)
        profile_config['resource_share_factor'] = min(0.30, profile_config.get('resource_share_factor', 0.24) + 0.01)

    config.update(profile_config)
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
    result['blueprint_metrics'] = blueprint_metrics(config, result, params, profile['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['blueprint_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)

    if kontext_name == 'bootstrap':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['blueprint_readiness']
            + 0.12 * metrics['architectural_coverage']
            + 0.10 * metrics['blueprint_extensibility']
            - 0.10 * metrics['blueprint_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['operational_flow']
            + 0.14 * metrics['blueprint_extensibility']
            + 0.10 * metrics['architectural_coverage']
            - 0.10 * metrics['blueprint_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['blueprint_resilience']
            + 0.10 * metrics['architectural_coverage']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['blueprint_overhead']
        )
    if kontext_name == 'recovery':
        return (
            base
            + 0.18 * metrics['blueprint_resilience']
            + 0.12 * recoveries
            + 0.08 * metrics['operational_flow']
            - 0.12 * failed_share
            - 0.08 * metrics['blueprint_overhead']
        )
    return (
        metrics['completion_rate']
        + 0.18 * metrics['architectural_coverage']
        + 0.16 * metrics['blueprint_readiness']
        + 0.14 * metrics['blueprint_extensibility']
        + 0.12 * metrics['blueprint_resilience']
        + 0.10 * metrics['operational_flow']
        - 0.10 * metrics['blueprint_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'architectural_coverage': {},
        'blueprint_readiness': {},
        'blueprint_resilience': {},
        'blueprint_extensibility': {},
        'operational_flow': {},
        'blueprint_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['blueprint_metrics'][metric_name] for run in runs])

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
    profiles = blueprint_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI BAUPHASEN-BLUEPRINT-GESAMTSTUDIE')
    print('=' * 84)
    print('Vergleicht finale Bauphasen-Blueprints aus den Siegerbausteinen der Reihe,')
    print('um die empfohlene Gesamtarchitektur fuer den Uebergang in die Bauphase zu bestimmen.\n')

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
            f"Coverage={summary['architectural_coverage']['blueprint']:.2f} | "
            f"Readiness={summary['blueprint_readiness']['bootstrap']:.2f} | "
            f"Resilienz={summary['blueprint_resilience']['stress']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'minimaler-blueprint')

    print('\nBester Bauphasen-Blueprint:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum minimalen Blueprint {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Coverage {best['architectural_coverage']['blueprint']:.2f}, "
        f"Readiness {best['blueprint_readiness']['bootstrap']:.2f}, "
        f"Resilienz {best['blueprint_resilience']['stress']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Blueprint-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['architectural_coverage']['blueprint'] for item in summaries],
        width,
        label='Coverage',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['blueprint_readiness']['bootstrap'] for item in summaries],
        width,
        label='Readiness',
        color='#59a14f',
    )
    axes[0, 1].set_title('Abdeckung und Startreife')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['blueprint_resilience']['stress'] for item in summaries],
        width,
        label='Resilienz',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['operational_flow']['operations'] for item in summaries],
        width,
        label='Flow',
        color='#e15759',
    )
    axes[0, 2].set_title('Resilienz und operativer Fluss')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['bootstrap'],
                item['context_scores']['operations'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['context_scores']['blueprint'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Blueprint-Kontexte')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Boot', 'Ops', 'Stress', 'Rec', 'Plan'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['blueprint_extensibility']['blueprint'] for item in summaries],
        width,
        label='Erweiterbarkeit',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['blueprint_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Erweiterbarkeit und Kosten')
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
            f"- Bester Blueprint: {best['label']}\n"
            f"- Delta zum minimalen Blueprint: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Coverage: {best['architectural_coverage']['blueprint']:.2f}\n"
            f"- Readiness: {best['blueprint_readiness']['bootstrap']:.2f}\n"
            f"- Resilienz: {best['blueprint_resilience']['stress']:.2f}\n"
            f"- Erweiterbarkeit: {best['blueprint_extensibility']['blueprint']:.2f}\n"
            f"- Operativer Fluss: {best['operational_flow']['operations']:.2f}\n"
            f"- Overhead: {best['blueprint_overhead']['operations']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_bauphasen_blueprint.png', dpi=150)


if __name__ == '__main__':
    main()
