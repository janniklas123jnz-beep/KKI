"""
KKI Schattenbetriebs-Studie
===========================
Vergleicht Schattenbetrieb und Parallelvalidierung fuer reale Baugruppen und
misst, welche beobachtete Live-Naehe die beste Vorhersage fuer spaetere
Produktivstabilitaet liefert, ohne den operativen Fluss zu stark zu duplizieren.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_audit_telemetrie import telemetry_profiles
from schwarm_dna_schema import get_named
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_missions_dry_run import mission_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_sicherheits_policies import security_policy_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog



def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_SHADOW_MODE_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_SHADOW_MODE_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_SHADOW_MODE_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_SHADOW_MODE_STRESS_STRENGTH', '0.49')),
        'stress_sources': int(os.getenv('KKI_SHADOW_MODE_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_SHADOW_MODE_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
        'memory_window': int(os.getenv('KKI_MEMORY_WINDOW', '36')),
        'audit_depth': int(os.getenv('KKI_MEMORY_AUDIT_DEPTH', '4')),
    }



def clamp01(value):
    return max(0.0, min(1.0, float(value)))



def normalize(value, minimum, maximum):
    if maximum <= minimum:
        return 0.0
    return clamp01((float(value) - minimum) / (maximum - minimum))



def kontexte():
    return [
        {
            'name': 'preview',
            'label': 'Preview',
            'scenario': 'consensus',
            'startup_mode': True,
        },
        {
            'name': 'parallel',
            'label': 'Parallelbetrieb',
            'scenario': 'consensus',
            'parallel_mode': True,
        },
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
    ]



def shadow_profiles(katalog, params):
    mission = get_named(mission_profiles(katalog, params), 'foederierter-missions-dry-run')
    telemetry = get_named(telemetry_profiles(katalog, params), 'forensischer-kanal')
    security = get_named(security_policy_profiles(katalog, params), 'foederierte-sicherheitskette')

    runtime = {
        **mission['base_config'],
        **telemetry['base_config'],
        **security['base_config'],
    }

    return [
        {
            'name': 'stilles-monitoring',
            'label': 'Stilles Monitoring',
            'selected_tools': ['memory', 'execution'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'enable_parallel_workflow_cells': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 6,
                'mission_switch_interval': 6,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.28,
            },
            'shadow_depth': 1,
            'validation_depth': 1,
            'forecast_depth': 1,
            'replay_depth': 1,
            'bias': {
                'preview': 0.34,
                'validation': 0.30,
                'forecast': 0.26,
                'continuity': 0.86,
                'recovery': 0.34,
                'overhead': 0.08,
            },
        },
        {
            'name': 'probe-kanal',
            'label': 'Probe-Kanal',
            'selected_tools': ['memory', 'analysis', 'execution'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'enable_parallel_workflow_cells': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.32,
            },
            'shadow_depth': 2,
            'validation_depth': 2,
            'forecast_depth': 2,
            'replay_depth': 1,
            'bias': {
                'preview': 0.58,
                'validation': 0.56,
                'forecast': 0.54,
                'continuity': 0.80,
                'recovery': 0.48,
                'overhead': 0.16,
            },
        },
        {
            'name': 'spiegel-routing',
            'label': 'Spiegel-Routing',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge'],
            'multiplier': 0.95,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': False,
                'enable_parallel_workflow_cells': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.35,
            },
            'shadow_depth': 3,
            'validation_depth': 3,
            'forecast_depth': 3,
            'replay_depth': 2,
            'bias': {
                'preview': 0.80,
                'validation': 0.78,
                'forecast': 0.78,
                'continuity': 0.76,
                'recovery': 0.68,
                'overhead': 0.22,
            },
        },
        {
            'name': 'foederierter-schattenbetrieb',
            'label': 'Foederierter Schattenbetrieb',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.99,
            'base_config': {
                **runtime,
                **mission['base_config'],
                **telemetry['base_config'],
                **security['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'enable_parallel_workflow_cells': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
            },
            'shadow_depth': 4,
            'validation_depth': 4,
            'forecast_depth': 4,
            'replay_depth': 3,
            'bias': {
                'preview': 0.90,
                'validation': 0.88,
                'forecast': 0.88,
                'continuity': 0.84,
                'recovery': 0.84,
                'overhead': 0.26,
            },
        },
        {
            'name': 'parallel-validierung',
            'label': 'Parallelvalidierung',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **telemetry['base_config'],
                **security['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'enable_parallel_workflow_cells': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.39,
            },
            'shadow_depth': 4,
            'validation_depth': 5,
            'forecast_depth': 4,
            'replay_depth': 4,
            'bias': {
                'preview': 0.92,
                'validation': 0.92,
                'forecast': 0.88,
                'continuity': 0.78,
                'recovery': 0.86,
                'overhead': 0.32,
            },
        },
        {
            'name': 'maximaler-schattenstack',
            'label': 'Maximaler Schattenstack',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **runtime,
                **mission['base_config'],
                **telemetry['base_config'],
                **security['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'enable_parallel_workflow_cells': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 3,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.31,
                'trust_shield_strength': 0.40,
                'resource_budget': 0.80,
            },
            'shadow_depth': 5,
            'validation_depth': 5,
            'forecast_depth': 5,
            'replay_depth': 5,
            'bias': {
                'preview': 0.86,
                'validation': 0.88,
                'forecast': 0.82,
                'continuity': 0.42,
                'recovery': 0.66,
                'overhead': 0.92,
            },
        },
    ]



def shadow_metrics(config, result, params, profile):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    traces = [catalog[name]['scores']['trace'] for name in selected_tools]
    exposures = [catalog[name]['scores']['exposure'] for name in selected_tools]
    traceability = clamp01(mittelwert(traces or [0.0]))
    exposure = clamp01(mittelwert(exposures or [0.0]))
    agent_count = max(1.0, params['agent_count'])
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    shadow_depth_score = normalize(profile['shadow_depth'], 1.0, 5.0)
    validation_depth_score = normalize(profile['validation_depth'], 1.0, 5.0)
    forecast_depth_score = normalize(profile['forecast_depth'], 1.0, 5.0)
    replay_depth_score = normalize(profile['replay_depth'], 1.0, 5.0)

    preview_reliability = clamp01(
        mittelwert(
            [
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('completion_rate', 0.0),
                traceability,
                shadow_depth_score,
                profile['bias']['preview'],
            ]
        )
    )
    validation_strength = clamp01(
        mittelwert(
            [
                validation_depth_score,
                workflow.get('misinformation_detection_rate', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                profile['bias']['validation'],
            ]
        )
    )
    forecast_quality = clamp01(
        mittelwert(
            [
                forecast_depth_score,
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                groups['functional_group_share'],
                profile['bias']['forecast'],
            ]
        )
    )
    shadow_continuity = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                1.0 if config.get('enable_parallel_workflow_cells', False) else 0.0,
                profile['bias']['continuity'],
            ]
        )
    )
    replay_recovery = clamp01(
        mittelwert(
            [
                replay_depth_score,
                recoveries,
                1.0 - failed_share,
                1.0 - exposure,
                profile['bias']['recovery'],
            ]
        )
    )
    shadow_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_share_factor', 0.28), 0.28, 0.30),
                shadow_depth_score,
                validation_depth_score,
                replay_depth_score,
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'preview_reliability': preview_reliability,
        'validation_strength': validation_strength,
        'forecast_quality': forecast_quality,
        'shadow_continuity': shadow_continuity,
        'replay_recovery': replay_recovery,
        'shadow_overhead': shadow_overhead,
    }



def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    shadow_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(shadow_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('parallel_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 2)
        config['enable_parallel_workflow_cells'] = True
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
    result['shadow_metrics'] = shadow_metrics(config, result, params, profile)
    return result



def context_score(kontext_name, result, agent_count):
    metrics = result['shadow_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'preview':
        return (
            metrics['preview_reliability']
            + 0.18 * metrics['forecast_quality']
            + 0.12 * metrics['shadow_continuity']
            - 0.10 * metrics['shadow_overhead']
        )
    if kontext_name == 'parallel':
        return (
            metrics['validation_strength']
            + 0.18 * metrics['forecast_quality']
            + 0.12 * metrics['shadow_continuity']
            - 0.10 * metrics['shadow_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['validation_strength']
            + 0.14 * metrics['forecast_quality']
            + 0.10 * metrics['replay_recovery']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['shadow_overhead']
        )
    return (
        base
        + 0.20 * metrics['replay_recovery']
        + 0.12 * metrics['validation_strength']
        + 0.08 * metrics['shadow_continuity']
        - 0.12 * failed_share
        - 0.08 * metrics['shadow_overhead']
    )



def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'preview_reliability': {},
        'validation_strength': {},
        'forecast_quality': {},
        'shadow_continuity': {},
        'replay_recovery': {},
        'shadow_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['shadow_metrics'][metric_name] for run in runs])

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
    profiles = shadow_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI SCHATTENBETRIEBS-STUDIE')
    print('=' * 84)
    print('Vergleicht beobachtete Parallelvalidierung fuer reale Baugruppen,')
    print('damit Live-Naehe, Sicherheitsketten und Telemetrie belastbar auf den Rollout vorbereiten.\n')

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
            f"Preview={summary['preview_reliability']['preview']:.2f} | "
            f"Validierung={summary['validation_strength']['parallel']:.2f} | "
            f"Recovery={summary['replay_recovery']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'stilles-monitoring')

    print('\nBester Schattenbetrieb:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Stilles Monitoring {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Preview {best['preview_reliability']['preview']:.2f}, "
        f"Validierung {best['validation_strength']['parallel']:.2f}, "
        f"Recovery {best['replay_recovery']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Schatten-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['preview_reliability']['preview'] for item in summaries],
        width,
        label='Preview',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['forecast_quality']['parallel'] for item in summaries],
        width,
        label='Prognose',
        color='#59a14f',
    )
    axes[0, 1].set_title('Preview und Prognose')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['validation_strength']['parallel'] for item in summaries],
        width,
        label='Validierung',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['shadow_continuity']['parallel'] for item in summaries],
        width,
        label='Kontinuitaet',
        color='#f28e2b',
    )
    axes[0, 2].set_title('Validierung und Kontinuitaet')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['replay_recovery']['recovery'] for item in summaries],
        width,
        label='Replay-Recovery',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['shadow_overhead']['parallel'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Recovery gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['parallel'] for item in summaries], color=colors)
    axes[1, 1].set_title('Parallelvalidierungs-Score')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].bar(
        x - width / 2,
        [item['context_scores']['stress'] for item in summaries],
        width,
        label='Stress',
        color='#e15759',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['context_scores']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#4e79a7',
    )
    axes[1, 2].set_title('Stress- und Recovery-Kontexte')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_schattenbetrieb.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
