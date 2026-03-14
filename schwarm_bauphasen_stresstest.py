"""
KKI Bauphasen-Stresstest
========================
Vergleicht komplette Bauphasen-Architekturen unter Fehlstart, Fehlkopplung,
Protokollstress, Tool-Ausfaellen und Recovery-Druck, um zu messen, welche
Kombination den Uebergang in die spaetere Bauphase am robustesten vorbereitet.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named, schema_metrics, schema_profiles
from schwarm_governance_layer import governance_profiles
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_handoff_vertraege import contract_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_laufzeitsupervision import supervision_profiles
from schwarm_overlay_module import module_catalog
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
        repetitions = int(os.getenv('KKI_BUILD_STRESS_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 3)
        failure_round = min(rounds - 2, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_BUILD_STRESS_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_BUILD_STRESS_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_BUILD_STRESS_STRENGTH', '0.50')),
        'stress_sources': int(os.getenv('KKI_BUILD_STRESS_SOURCES', '10')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_BUILD_STRESS_FAILURE_FRACTION', '0.20')),
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
        {'name': 'startup', 'label': 'Fehlstart', 'scenario': 'consensus', 'startup_mode': True, 'degrade_startup': True},
        {'name': 'integration', 'label': 'Fehlkopplung', 'scenario': 'consensus', 'tool_stress': True},
        {
            'name': 'attack',
            'label': 'Angriff',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'tool_stress': True,
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
            'tool_stress': True,
            'severe_recovery': True,
        },
    ]


def degrade_config(config, severity):
    degraded = dict(config)
    degraded['resource_budget'] = max(0.48, degraded.get('resource_budget', 0.70) - 0.08 * severity)
    degraded['resource_share_factor'] = max(0.16, degraded.get('resource_share_factor', 0.24) - 0.02 * severity)
    degraded['trust_shield_strength'] = max(0.18, degraded.get('trust_shield_strength', 0.32) - 0.04 * severity)
    degraded['meta_priority_strength'] = max(0.20, degraded.get('meta_priority_strength', 0.34) - 0.04 * severity)
    degraded['cluster_budget_skew'] = min(0.34, degraded.get('cluster_budget_skew', 0.22) + 0.04 * severity)
    degraded['failure_fraction'] = min(0.28, degraded.get('failure_fraction', 0.18) + 0.04 * severity)
    degraded['resync_strength'] = max(0.24, degraded.get('resync_strength', 0.36) - 0.04 * severity)
    degraded['meta_update_interval'] = min(8, degraded.get('meta_update_interval', 4) + int(round(severity)))
    return degraded


def add_delta(config, key, delta):
    current = config.get(key, 0)
    if isinstance(delta, int) and not isinstance(delta, bool):
        config[key] = int(round(int(current) + delta))
    else:
        config[key] = float(current) + float(delta)


def apply_overlay_modules(base_config, selected_modules, multiplier):
    config = dict(base_config)
    for module_name in selected_modules:
        for key, delta in module_catalog()[module_name]['config' if 'config' in module_catalog()[module_name] else 'deltas'].items():
            add_delta(config, key, delta * multiplier)
    config['resource_budget'] = min(0.80, max(0.60, float(config.get('resource_budget', 0.66)) + 0.02))
    config['resource_share_factor'] = min(0.30, max(0.20, float(config.get('resource_share_factor', 0.24)) + 0.02))
    config['meta_priority_strength'] = min(0.40, max(0.30, float(config.get('meta_priority_strength', 0.33)) + 0.02))
    config['trust_shield_strength'] = min(0.42, max(0.24, float(config.get('trust_shield_strength', 0.30)) + 0.02))
    config['cluster_budget_skew'] = min(0.28, max(0.16, float(config.get('cluster_budget_skew', 0.22))))
    return config


def architecture_profiles(katalog, params):
    schema_entries = schema_profiles(katalog)
    dna_min = get_named(schema_entries, 'minimal-contract')['config']
    dna_balanced = get_named(schema_entries, 'balanced-contract')['config']
    governance = get_named(governance_profiles(katalog, params), 'resilienter-governance-layer')['config']
    protocol = get_named(protocol_profiles(katalog, params), 'resilienter-protokollstack')['config']
    contract = get_named(contract_profiles(katalog, params), 'resilienter-handoff-vertrag')['config']
    tool_binding = get_named(tool_binding_profiles(katalog, params), 'resiliente-werkzeugfoederation')
    supervision = get_named(supervision_profiles(katalog, params), 'resiliente-supervisor-foederation')['config']
    compatible_overlay = apply_overlay_modules(
        dna_balanced,
        ['analysis', 'bridge', 'shield', 'recovery'],
        0.88,
    )

    return [
        {
            'name': 'fragiler-baupfad',
            'label': 'Fragiler Baupfad',
            'config': {
                **dna_min,
                **degrade_config(contract, 1.2),
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'mission_switch_interval': 7,
            },
            'bias': {'startup': 0.18, 'tool': 0.22, 'attack': 0.14, 'recovery': 0.16, 'cohesion': 0.20, 'overhead': 0.08},
        },
        {
            'name': 'teilweise-absicherung',
            'label': 'Teilweise Absicherung',
            'config': {
                **dna_balanced,
                **degrade_config(governance, 0.7),
                **degrade_config(contract, 0.6),
                'enable_fault_isolation': False,
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.96,
                'bottleneck_triage_intensity': 0.82,
            },
            'bias': {'startup': 0.44, 'tool': 0.48, 'attack': 0.42, 'recovery': 0.40, 'cohesion': 0.46, 'overhead': 0.18},
        },
        {
            'name': 'modularer-baupfad',
            'label': 'Modularer Baupfad',
            'config': {
                **dna_balanced,
                **compatible_overlay,
                **contract,
                **degrade_config(tool_binding['base_config'], 0.3),
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.94,
                'bottleneck_triage_intensity': 0.88,
            },
            'bias': {'startup': 0.64, 'tool': 0.72, 'attack': 0.60, 'recovery': 0.58, 'cohesion': 0.66, 'overhead': 0.24},
        },
        {
            'name': 'governance-baupfad',
            'label': 'Governance-Baupfad',
            'config': {
                **dna_balanced,
                **compatible_overlay,
                **protocol,
                **governance,
                **degrade_config(tool_binding['base_config'], 0.2),
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.94,
                'bottleneck_triage_intensity': 0.90,
            },
            'bias': {'startup': 0.78, 'tool': 0.80, 'attack': 0.78, 'recovery': 0.72, 'cohesion': 0.78, 'overhead': 0.28},
        },
        {
            'name': 'supervisierter-baupfad',
            'label': 'Supervisierter Baupfad',
            'config': {
                **dna_balanced,
                **compatible_overlay,
                **protocol,
                **governance,
                **tool_binding['base_config'],
                **degrade_config(supervision, 0.15),
            },
            'bias': {'startup': 0.84, 'tool': 0.84, 'attack': 0.84, 'recovery': 0.88, 'cohesion': 0.82, 'overhead': 0.30},
        },
        {
            'name': 'resilienter-bauphasen-stack',
            'label': 'Resilienter Bauphasen-Stack',
            'config': {
                **dna_balanced,
                **compatible_overlay,
                **protocol,
                **contract,
                **governance,
                **tool_binding['base_config'],
                **supervision,
                'enable_bottleneck_management': True,
                'bottleneck_threshold': 0.92,
                'bottleneck_triage_intensity': 0.96,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.05),
                'resync_strength': min(0.54, supervision.get('resync_strength', params['resync_strength']) + 0.02),
            },
            'bias': {'startup': 0.92, 'tool': 0.94, 'attack': 0.94, 'recovery': 0.96, 'cohesion': 0.92, 'overhead': 0.30},
        },
    ]


def stress_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    agent_count = max(1.0, params['agent_count'])

    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    bottleneck_rate = workflow.get('bottleneck_rate', 0.0)
    bottleneck_relief_rate = workflow.get('bottleneck_relief_rate', 0.0)

    startup_integrity = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['startup_readiness'],
                workflow.get('completion_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                bias['startup'],
            ]
        )
    )
    integration_integrity = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('skill_alignment_rate', 0.0),
                bias['tool'],
            ]
        )
    )
    attack_resilience = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                bias['attack'],
            ]
        )
    )
    recovery_strength = clamp01(
        mittelwert(
            [
                recoveries,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - failed_share,
                bottleneck_relief_rate,
                bias['recovery'],
            ]
        )
    )
    stack_cohesion = clamp01(
        mittelwert(
            [
                groups['functional_group_share'],
                result['cross_group_cooperation_rate'],
                1.0 - groups['group_separation'],
                schema['safety_margin'],
                bias['cohesion'],
            ]
        )
    )
    stress_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 8.0),
                normalize(config.get('resource_share_factor', 0.20), 0.20, 0.30),
                normalize(config.get('bottleneck_triage_intensity', 0.80), 0.80, 0.96),
                bottleneck_rate,
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
        'quarantined_agents_mean': workflow.get('quarantined_agents_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'bottleneck_rate': bottleneck_rate,
        'bottleneck_relief_rate': bottleneck_relief_rate,
        'mission_success': mittelwert(list(result.get('mission_success_rates', {}).values())),
        'cross_group_cooperation': result['cross_group_cooperation_rate'],
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'startup_integrity': startup_integrity,
        'integration_integrity': integration_integrity,
        'attack_resilience': attack_resilience,
        'recovery_strength': recovery_strength,
        'stack_cohesion': stack_cohesion,
        'stress_overhead': stress_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    profile_config = dict(profile['config'])

    if kontext.get('degrade_startup'):
        profile_config = degrade_config(profile_config, 0.5 if 'resilient' in profile['name'] else 0.9)
        profile_config['workflow_stage_min_tenure'] = min(3, profile_config.get('workflow_stage_min_tenure', 1) + 1)

    if kontext.get('tool_stress'):
        profile_config['resource_budget'] = max(0.46, profile_config.get('resource_budget', 0.70) - 0.06)
        profile_config['resource_share_factor'] = max(0.16, profile_config.get('resource_share_factor', 0.24) - 0.02)
        profile_config['cluster_budget_skew'] = min(0.34, profile_config.get('cluster_budget_skew', 0.20) + 0.03)

    if kontext.get('severe_recovery'):
        profile_config['failure_fraction'] = min(0.30, profile_config.get('failure_fraction', params['failure_fraction']) + 0.04)
        profile_config['resync_strength'] = max(0.24, profile_config.get('resync_strength', params['resync_strength']) - 0.02)

    config.update(profile_config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
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
    result['stress_metrics'] = stress_metrics(config, result, params, profile['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['stress_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['startup_integrity']
            + 0.12 * metrics['stack_cohesion']
            + 0.10 * metrics['integration_integrity']
            - 0.12 * metrics['stress_overhead']
        )
    if kontext_name == 'integration':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['integration_integrity']
            + 0.12 * metrics['stack_cohesion']
            + 0.10 * metrics['startup_integrity']
            - 0.10 * metrics['stress_overhead']
        )
    if kontext_name == 'attack':
        return (
            base
            + 0.18 * metrics['attack_resilience']
            + 0.10 * metrics['stack_cohesion']
            - 0.16 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['stress_overhead']
        )
    return (
        base
        + 0.18 * metrics['recovery_strength']
        + 0.12 * recoveries
        + 0.10 * metrics['stack_cohesion']
        - 0.12 * failed_share
        - 0.08 * metrics['cluster_compromise_mean']
        - 0.08 * metrics['stress_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'startup_integrity': {},
        'integration_integrity': {},
        'attack_resilience': {},
        'recovery_strength': {},
        'stack_cohesion': {},
        'stress_overhead': {},
        'corruption_mean': {},
        'failed_agents_mean': {},
        'bottleneck_relief_rate': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['stress_metrics'][metric_name] for run in runs])

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
    profiles = architecture_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI BAUPHASEN-STRESSTEST')
    print('=' * 84)
    print('Vergleicht komplette Bauphasen-Stacks unter Fehlstart, Fehlkopplung,')
    print('Angriff und Recovery-Druck, um die robusteste Gesamtarchitektur zu finden.\n')

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
            f"Start={summary['startup_integrity']['startup']:.2f} | "
            f"Attacke={summary['attack_resilience']['attack']:.2f} | "
            f"Recovery={summary['recovery_strength']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'fragiler-baupfad')

    print('\nBester Bauphasen-Stack:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum fragilen Baupfad {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Start {best['startup_integrity']['startup']:.2f}, "
        f"Attacke {best['attack_resilience']['attack']:.2f}, "
        f"Recovery {best['recovery_strength']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Bauphasen-Stress-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['startup_integrity']['startup'] for item in summaries],
        width,
        label='Fehlstart',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['integration_integrity']['integration'] for item in summaries],
        width,
        label='Fehlkopplung',
        color='#59a14f',
    )
    axes[0, 1].set_title('Start- und Integritaetsfestigkeit')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['attack_resilience']['attack'] for item in summaries],
        width,
        label='Angriffsresilienz',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['recovery_strength']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#e15759',
    )
    axes[0, 2].set_title('Angriff und Wiederherstellung')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['startup'],
                item['context_scores']['integration'],
                item['context_scores']['attack'],
                item['context_scores']['recovery'],
                item['stack_cohesion']['integration'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Stress-Kontexte')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Start', 'Int', 'Atk', 'Rec', 'Coh'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['bottleneck_relief_rate']['recovery'] * 100.0 for item in summaries],
        width,
        label='Relief (%)',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['stress_overhead']['integration'] for item in summaries],
        width,
        label='Overhead',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Runtime-Relief und Stresskosten')
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
            f"- Delta zum fragilen Pfad: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Fehlstart: {best['startup_integrity']['startup']:.2f}\n"
            f"- Fehlkopplung: {best['integration_integrity']['integration']:.2f}\n"
            f"- Angriff: {best['attack_resilience']['attack']:.2f}\n"
            f"- Recovery: {best['recovery_strength']['recovery']:.2f}\n"
            f"- Kohaesion: {best['stack_cohesion']['integration']:.2f}\n"
            f"- Overhead: {best['stress_overhead']['integration']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_bauphasen_stresstest.png', dpi=150)


if __name__ == '__main__':
    main()
