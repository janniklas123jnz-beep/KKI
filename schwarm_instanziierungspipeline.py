"""
KKI Instanziierungs-Pipeline-Studie
==================================
Vergleicht Instanziierungs-Pipelines fuer spaetere Bauagenten und misst, welche
Erzeugungslogik die Pilot-Architektur am belastbarsten in konkrete Agenten,
Rollen und Zellstarts ueberfuehrt.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_bauphasen_pilot import pilot_profiles
from schwarm_dna_schema import get_named, schema_metrics
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import (
    assembler_profiles,
    normalize_role_shares,
    role_target_distance,
)
from schwarm_runtime_dna import runtime_profiles
from schwarm_sandbox_zellen import sandbox_profiles
from schwarm_wissensspeicher import memory_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import broker_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_INSTANTIATION_PIPELINE_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_INSTANTIATION_PIPELINE_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_INSTANTIATION_PIPELINE_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_INSTANTIATION_PIPELINE_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_INSTANTIATION_PIPELINE_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_INSTANTIATION_PIPELINE_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
        'stable_min_history': int(os.getenv('KKI_RELATIONSHIP_STABLE_MIN_HISTORY', '18')),
        'stable_trust_threshold': float(os.getenv('KKI_RELATIONSHIP_STABLE_TRUST', '0.76')),
        'memory_window': int(os.getenv('KKI_MEMORY_WINDOW', '36')),
        'audit_depth': int(os.getenv('KKI_MEMORY_AUDIT_DEPTH', '4')),
        'approval_window': int(os.getenv('KKI_APPROVAL_WINDOW', '3')),
        'acceptance_cycles': int(os.getenv('KKI_MISSION_DRY_RUN_ACCEPTANCE_CYCLES', '3')),
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
        {'name': 'startup', 'label': 'Startup', 'scenario': 'consensus', 'startup_checks': True},
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def pipeline_profiles(katalog, params):
    pilot = get_named(pilot_profiles(katalog, params), 'pilot-architektur')
    runtime = get_named(runtime_profiles(katalog, params), 'operative-runtime-dna')
    runtime_resilient = get_named(runtime_profiles(katalog, params), 'resiliente-runtime-dna')
    assembler = get_named(assembler_profiles(katalog, params), 'resilienter-rollenassembler')
    missions = get_named(assembler_profiles(katalog, params), 'missions-assembler')
    broker = get_named(broker_profiles(katalog, params), 'resilienter-capability-broker')
    memory = get_named(memory_profiles(katalog, params), 'resilienter-wissensspeicher')
    sandbox = get_named(sandbox_profiles(katalog, params), 'foederierte-sandbox-zellen')

    return [
        {
            'name': 'direktklon',
            'label': 'Direktklon',
            'selected_tools': ['execution', 'memory'],
            'multiplier': 0.86,
            'targets': missions['targets'],
            'base_config': {
                **runtime['config'],
                'enable_role_switching': False,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.26,
            },
            'pipeline_depth': 1,
            'template_stages': 1,
            'bootstrap_checks': 0,
            'bias': {
                'fidelity': 0.34,
                'startup': 0.44,
                'assignment': 0.28,
                'safety': 0.24,
                'flow': 0.78,
                'recovery': 0.30,
                'overhead': 0.08,
            },
        },
        {
            'name': 'template-fabrik',
            'label': 'Template-Fabrik',
            'selected_tools': ['memory', 'analysis', 'execution'],
            'multiplier': 0.90,
            'targets': missions['targets'],
            'base_config': {
                **runtime['config'],
                'enable_role_switching': True,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_share_factor': 0.28,
                'handoff_priority_bonus': 0.20,
                'trust_shield_strength': 0.30,
            },
            'pipeline_depth': 2,
            'template_stages': 2,
            'bootstrap_checks': 1,
            'bias': {
                'fidelity': 0.54,
                'startup': 0.60,
                'assignment': 0.52,
                'safety': 0.42,
                'flow': 0.74,
                'recovery': 0.46,
                'overhead': 0.14,
            },
        },
        {
            'name': 'rollen-pipeline',
            'label': 'Rollen-Pipeline',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge'],
            'multiplier': 0.94,
            'targets': assembler['targets'],
            'base_config': {
                **runtime['config'],
                **assembler['config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.32,
            },
            'pipeline_depth': 3,
            'template_stages': 3,
            'bootstrap_checks': 2,
            'bias': {
                'fidelity': 0.76,
                'startup': 0.74,
                'assignment': 0.82,
                'safety': 0.56,
                'flow': 0.76,
                'recovery': 0.58,
                'overhead': 0.20,
            },
        },
        {
            'name': 'zell-bootstrap-pipeline',
            'label': 'Zell-Bootstrap-Pipeline',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.97,
            'targets': assembler['targets'],
            'base_config': {
                **runtime['config'],
                **assembler['config'],
                **sandbox['base_config'],
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.36,
            },
            'pipeline_depth': 4,
            'template_stages': 3,
            'bootstrap_checks': 3,
            'bias': {
                'fidelity': 0.86,
                'startup': 0.82,
                'assignment': 0.84,
                'safety': 0.80,
                'flow': 0.74,
                'recovery': 0.72,
                'overhead': 0.24,
            },
        },
        {
            'name': 'foederierte-instanziierung',
            'label': 'Foederierte Instanziierung',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'targets': assembler['targets'],
            'base_config': {
                **runtime['config'],
                **assembler['config'],
                **broker['base_config'],
                **memory['base_config'],
                **sandbox['base_config'],
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
                'bottleneck_triage_intensity': 0.92,
            },
            'pipeline_depth': 4,
            'template_stages': 4,
            'bootstrap_checks': 3,
            'bias': {
                'fidelity': 0.90,
                'startup': 0.88,
                'assignment': 0.90,
                'safety': 0.88,
                'flow': 0.82,
                'recovery': 0.82,
                'overhead': 0.26,
            },
        },
        {
            'name': 'resiliente-instanziierungspipeline',
            'label': 'Resiliente Instanziierungs-Pipeline',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'targets': assembler['targets'],
            'base_config': {
                **runtime_resilient['config'],
                **assembler['config'],
                **broker['base_config'],
                **memory['base_config'],
                **sandbox['base_config'],
                **pilot['base_config'],
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'bottleneck_triage_intensity': 0.94,
                'failure_fraction': max(0.10, params['failure_fraction'] - 0.04),
                'resync_strength': 0.48,
            },
            'pipeline_depth': 5,
            'template_stages': 4,
            'bootstrap_checks': 4,
            'bias': {
                'fidelity': 0.88,
                'startup': 0.76,
                'assignment': 0.86,
                'safety': 0.90,
                'flow': 0.64,
                'recovery': 0.88,
                'overhead': 0.48,
            },
        },
    ]


def pipeline_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    traceability = clamp01(mittelwert([catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]))
    exposure = clamp01(mittelwert([catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]))
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    pipeline_depth_score = normalize(profile['pipeline_depth'], 1.0, 5.0)
    stage_score = normalize(profile['template_stages'], 1.0, 4.0)
    bootstrap_score = normalize(profile['bootstrap_checks'], 0.0, 4.0)
    role_fit = role_target_distance(config, profile['targets'])

    template_fidelity = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                role_fit,
                stage_score,
                profile['bias']['fidelity'],
            ]
        )
    )
    startup_integrity = clamp01(
        mittelwert(
            [
                schema['startup_readiness'],
                workflow.get('completion_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                bootstrap_score,
                profile['bias']['startup'],
            ]
        )
    )
    assignment_quality = clamp01(
        mittelwert(
            [
                role_fit,
                workflow.get('skill_alignment_rate', 0.0),
                groups['functional_group_share'],
                workflow.get('handoff_rate', 0.0),
                profile['bias']['assignment'],
            ]
        )
    )
    pipeline_safety = clamp01(
        mittelwert(
            [
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                1.0 - exposure,
                bootstrap_score,
                profile['bias']['safety'],
            ]
        )
    )
    instantiation_flow = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('completion_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                1.0 - workflow.get('bottleneck_rate', 0.0),
                profile['bias']['flow'],
            ]
        )
    )
    pipeline_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_share_factor', 0.28), 0.28, 0.30),
                pipeline_depth_score,
                stage_score,
                bootstrap_score,
                profile['bias']['overhead'],
            ]
        )
    )
    instantiation_integrity = clamp01(
        mittelwert(
            [
                template_fidelity,
                assignment_quality,
                startup_integrity,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                traceability,
            ]
        )
    )
    recovery_margin = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                profile['bias']['recovery'],
            ]
        )
    )
    bootstrap_resilience = clamp01(
        mittelwert(
            [
                startup_integrity,
                recovery_margin,
                instantiation_flow,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - pipeline_overhead,
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'template_fidelity': template_fidelity,
        'startup_integrity': startup_integrity,
        'assignment_quality': assignment_quality,
        'pipeline_safety': pipeline_safety,
        'instantiation_flow': instantiation_flow,
        'instantiation_integrity': instantiation_integrity,
        'bootstrap_resilience': bootstrap_resilience,
        'pipeline_overhead': pipeline_overhead,
        'recovery_margin': recovery_margin,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    pipeline_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(pipeline_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('startup_checks'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 2)
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
    result['pipeline_metrics'] = pipeline_metrics(config, result, params, profile)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['pipeline_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'bootstrap':
        return (
            metrics['template_fidelity']
            + 0.18 * metrics['assignment_quality']
            + 0.12 * metrics['startup_integrity']
            - 0.10 * metrics['pipeline_overhead']
        )
    if kontext_name == 'startup':
        return (
            metrics['startup_integrity']
            + 0.18 * metrics['instantiation_flow']
            + 0.12 * metrics['assignment_quality']
            - 0.10 * metrics['pipeline_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['instantiation_integrity']
            + 0.12 * metrics['bootstrap_resilience']
            + 0.10 * metrics['pipeline_safety']
            - 0.10 * metrics['pipeline_overhead']
        )
    return (
        base
        + 0.20 * metrics['bootstrap_resilience']
        + 0.12 * metrics['instantiation_integrity']
        + 0.08 * metrics['pipeline_safety']
        - 0.12 * failed_share
        - 0.08 * metrics['pipeline_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'template_fidelity': {},
        'startup_integrity': {},
        'assignment_quality': {},
        'pipeline_safety': {},
        'instantiation_flow': {},
        'instantiation_integrity': {},
        'bootstrap_resilience': {},
        'pipeline_overhead': {},
        'recovery_margin': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['pipeline_metrics'][metric_name] for run in runs])

    return {
        'name': profile['name'],
        'label': profile['label'],
        'combined_score': mittelwert([
            sum(context_score(kontext['name'], run[kontext['name']], agent_count) for kontext in context_list)
            for run in runs
        ]),
        'context_scores': context_scores,
        **metrics,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    profiles = pipeline_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI INSTANZIERUNGS-PIPELINE-STUDIE')
    print('=' * 84)
    print('Vergleicht Erzeugungslogiken fuer spaetere Bauagenten,')
    print('damit die Pilot-Architektur belastbar in Rollen, Zellen und Startpakete ueberfuehrt wird.\n')

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
            f"{summary['label']:<34} Score={summary['combined_score']:+.3f} | "
            f"Integritaet={summary['instantiation_integrity']['stress']:.2f} | "
            f"Bootstrap-Resilienz={summary['bootstrap_resilience']['recovery']:.2f} | "
            f"Startup={summary['startup_integrity']['startup']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'direktklon')

    print('\nBeste Instanziierungs-Pipeline:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum Direktklon {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Integritaet {best['instantiation_integrity']['stress']:.2f}, "
        f"Startup {best['startup_integrity']['startup']:.2f}, "
        f"Bootstrap-Resilienz {best['bootstrap_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Pipeline-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['instantiation_integrity']['stress'] for item in summaries],
        width,
        label='Integritaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['startup_integrity']['startup'] for item in summaries],
        width,
        label='Startup',
        color='#59a14f',
    )
    axes[0, 1].set_title('Instanziierungs-Integritaet und Startup')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['assignment_quality']['startup'] for item in summaries],
        width,
        label='Rollenfit',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['instantiation_flow']['startup'] for item in summaries],
        width,
        label='Flow',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Rollenfit und Flow')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['bootstrap_resilience']['recovery'] for item in summaries],
        width,
        label='Bootstrap-Resilienz',
        color='#e15759',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['pipeline_overhead']['startup'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Bootstrap-Resilienz gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['stress'] for item in summaries], color=colors)
    axes[1, 1].set_title('Stress-Score')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].bar(
        x - width / 2,
        [item['context_scores']['bootstrap'] for item in summaries],
        width,
        label='Bootstrap',
        color='#59a14f',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['recovery_margin']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#4e79a7',
    )
    axes[1, 2].set_title('Bootstrap- und Recovery-Score')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_instanziierungspipeline.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
