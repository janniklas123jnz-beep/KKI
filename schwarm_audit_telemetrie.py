"""
KKI Audit-Telemetrie-Studie
===========================
Vergleicht Telemetrie-, Audit- und Diagnosearchitekturen fuer laufende Baugruppen
und misst, welche Nachvollziehbarkeitslogik Budgetfluesse, Rollouts und Recovery
sichtbar macht, ohne den operativen Fluss wieder im Monitoring zu verlieren.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named
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
from schwarm_ressourcen_orchestrator import orchestrator_profiles
from schwarm_rollenassembler import normalize_role_shares
from schwarm_rollout_protokolle import rollout_profiles
from schwarm_werkzeugadapter import adapter_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import (
    required_domain_coverage,
    required_domain_redundancy,
    route_specificity,
)
from schwarm_zustandstransfer import state_transfer_profiles



def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_AUDIT_TELEMETRY_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_AUDIT_TELEMETRY_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_AUDIT_TELEMETRY_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_AUDIT_TELEMETRY_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_AUDIT_TELEMETRY_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_AUDIT_TELEMETRY_FAILURE_FRACTION', '0.18')),
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
            'name': 'visibility',
            'label': 'Sichtbarkeit',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('trace', 'memory', 'coordination'),
        },
        {
            'name': 'diagnostics',
            'label': 'Diagnostik',
            'scenario': 'consensus',
            'diagnostics_mode': True,
            'required_domains': ('analysis', 'trace', 'approval', 'coordination'),
        },
        {
            'name': 'stress',
            'label': 'Stress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'required_domains': ('security', 'trace', 'approval', 'analysis'),
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
            'required_domains': ('memory', 'trace', 'handoff', 'security'),
        },
    ]



def telemetry_profiles(katalog, params):
    adapter = get_named(adapter_profiles(katalog, params), 'audit-gateway')
    rollout = get_named(rollout_profiles(katalog, params), 'foederierter-rollout')
    transfer = get_named(state_transfer_profiles(katalog, params), 'foederierter-zustandstransfer')
    orchestrator = get_named(orchestrator_profiles(katalog, params), 'foederierter-orchestrator')

    runtime = {
        **adapter['base_config'],
        **rollout['base_config'],
        **transfer['base_config'],
        **orchestrator['base_config'],
    }

    return [
        {
            'name': 'lokales-logging',
            'label': 'Lokales Logging',
            'selected_tools': ['memory', 'execution'],
            'multiplier': 0.86,
            'base_config': {
                **runtime,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 6,
                'mission_switch_interval': 6,
                'resource_share_factor': 0.27,
                'trust_shield_strength': 0.26,
            },
            'telemetry_depth': 1,
            'diagnostics_depth': 0,
            'federation_depth': 0,
            'forensics_depth': 1,
            'bias': {
                'visibility': 0.34,
                'audit': 0.30,
                'diagnostics': 0.22,
                'continuity': 0.84,
                'recovery': 0.34,
                'overhead': 0.06,
            },
        },
        {
            'name': 'ereignis-monitor',
            'label': 'Ereignis-Monitor',
            'selected_tools': ['memory', 'analysis', 'execution'],
            'multiplier': 0.90,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.30,
            },
            'telemetry_depth': 2,
            'diagnostics_depth': 2,
            'federation_depth': 1,
            'forensics_depth': 1,
            'bias': {
                'visibility': 0.62,
                'audit': 0.58,
                'diagnostics': 0.60,
                'continuity': 0.78,
                'recovery': 0.52,
                'overhead': 0.14,
            },
        },
        {
            'name': 'diagnose-kanal',
            'label': 'Diagnose-Kanal',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge'],
            'multiplier': 0.94,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.34,
            },
            'telemetry_depth': 3,
            'diagnostics_depth': 3,
            'federation_depth': 2,
            'forensics_depth': 2,
            'bias': {
                'visibility': 0.80,
                'audit': 0.76,
                'diagnostics': 0.82,
                'continuity': 0.76,
                'recovery': 0.70,
                'overhead': 0.20,
            },
        },
        {
            'name': 'audit-foederation',
            'label': 'Audit-Foederation',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                **adapter['base_config'],
                **transfer['base_config'],
                **orchestrator['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
            },
            'telemetry_depth': 4,
            'diagnostics_depth': 3,
            'federation_depth': 4,
            'forensics_depth': 3,
            'bias': {
                'visibility': 0.90,
                'audit': 0.92,
                'diagnostics': 0.86,
                'continuity': 0.84,
                'recovery': 0.84,
                'overhead': 0.26,
            },
        },
        {
            'name': 'forensischer-kanal',
            'label': 'Forensischer Kanal',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **rollout['base_config'],
                **transfer['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.39,
                'resource_budget': 0.80,
            },
            'telemetry_depth': 4,
            'diagnostics_depth': 4,
            'federation_depth': 3,
            'forensics_depth': 4,
            'bias': {
                'visibility': 0.92,
                'audit': 0.96,
                'diagnostics': 0.90,
                'continuity': 0.72,
                'recovery': 0.86,
                'overhead': 0.34,
            },
        },
        {
            'name': 'maximale-beobachtung',
            'label': 'Maximale Beobachtung',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **runtime,
                **rollout['base_config'],
                **transfer['base_config'],
                **orchestrator['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 3,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.31,
                'trust_shield_strength': 0.40,
                'resource_budget': 0.80,
            },
            'telemetry_depth': 5,
            'diagnostics_depth': 5,
            'federation_depth': 5,
            'forensics_depth': 5,
            'bias': {
                'visibility': 0.82,
                'audit': 0.86,
                'diagnostics': 0.78,
                'continuity': 0.42,
                'recovery': 0.74,
                'overhead': 0.82,
            },
        },
    ]



def telemetry_metrics(config, result, params, profile, kontext):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    required_domains = kontext['required_domains']
    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]

    coverage = required_domain_coverage(selected_tools, catalog, required_domains)
    redundancy = required_domain_redundancy(selected_tools, catalog, required_domains)
    specificity = route_specificity(selected_tools, required_domains)
    traceability = clamp01(mittelwert(trace_scores))
    exposure = clamp01(mittelwert(exposure_scores))
    telemetry_score = normalize(profile['telemetry_depth'], 1.0, 5.0)
    diagnostics_score = normalize(profile['diagnostics_depth'], 0.0, 5.0)
    federation_score = normalize(profile['federation_depth'], 0.0, 5.0)
    forensics_score = normalize(profile['forensics_depth'], 1.0, 5.0)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    rerouted_budget = workflow.get('rerouted_budget_total', 0.0) / agent_count

    telemetry_visibility = clamp01(
        mittelwert(
            [
                coverage,
                redundancy,
                traceability,
                workflow.get('meta_alignment_rate', 0.0),
                profile['bias']['visibility'],
            ]
        )
    )
    audit_continuity = clamp01(
        mittelwert(
            [
                traceability,
                workflow.get('resource_share_rate', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                federation_score,
                profile['bias']['audit'],
            ]
        )
    )
    diagnostics_quality = clamp01(
        mittelwert(
            [
                diagnostics_score,
                workflow.get('misinformation_detection_rate', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                workflow.get('bottleneck_relief_rate', 0.0),
                profile['bias']['diagnostics'],
            ]
        )
    )
    continuity_strength = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                groups['functional_group_share'],
                profile['bias']['continuity'],
            ]
        )
    )
    recovery_forensics = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                forensics_score,
                profile['bias']['recovery'],
            ]
        )
    )
    telemetry_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_budget', 0.76), 0.76, 0.80),
                telemetry_score,
                diagnostics_score,
                max(0.0, rerouted_budget),
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'bottleneck_rate': workflow.get('bottleneck_rate', 0.0),
        'bottleneck_relief_rate': workflow.get('bottleneck_relief_rate', 0.0),
        'rerouted_budget': rerouted_budget,
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'telemetry_visibility': telemetry_visibility,
        'audit_continuity': audit_continuity,
        'diagnostics_quality': diagnostics_quality,
        'continuity_strength': continuity_strength,
        'recovery_forensics': recovery_forensics,
        'telemetry_overhead': telemetry_overhead,
        'route_exposure': exposure,
        'traceability': traceability,
        'coverage': specificity,
    }



def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    telemetry_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(telemetry_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('diagnostics_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 2)
        config['enable_meta_coordination'] = True
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
    result['telemetry_metrics'] = telemetry_metrics(config, result, params, profile, kontext)
    return result



def context_score(kontext_name, result, agent_count):
    metrics = result['telemetry_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'visibility':
        return (
            metrics['telemetry_visibility']
            + 0.18 * metrics['audit_continuity']
            + 0.12 * metrics['continuity_strength']
            - 0.10 * metrics['telemetry_overhead']
        )
    if kontext_name == 'diagnostics':
        return (
            metrics['diagnostics_quality']
            + 0.18 * metrics['telemetry_visibility']
            + 0.12 * metrics['audit_continuity']
            - 0.10 * metrics['telemetry_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['diagnostics_quality']
            + 0.14 * metrics['audit_continuity']
            + 0.10 * metrics['recovery_forensics']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['route_exposure']
            - 0.08 * metrics['telemetry_overhead']
        )
    return (
        base
        + 0.20 * metrics['recovery_forensics']
        + 0.12 * metrics['audit_continuity']
        + 0.08 * metrics['continuity_strength']
        - 0.12 * failed_share
        - 0.08 * metrics['telemetry_overhead']
    )



def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'telemetry_visibility': {},
        'audit_continuity': {},
        'diagnostics_quality': {},
        'continuity_strength': {},
        'recovery_forensics': {},
        'telemetry_overhead': {},
        'route_exposure': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['telemetry_metrics'][metric_name] for run in runs])

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
    profiles = telemetry_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI AUDIT-TELEMETRIE-STUDIE')
    print('=' * 84)
    print('Vergleicht Telemetrie- und Nachvollziehbarkeitskanaele fuer laufende Baugruppen,')
    print('damit Budgetfluesse, Rollouts und Recovery sichtbar bleiben, ohne den Betrieb zu blockieren.\n')

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
            f"{summary['label']:<26} Score={summary['combined_score']:+.3f} | "
            f"Visibility={summary['telemetry_visibility']['visibility']:.2f} | "
            f"Audit={summary['audit_continuity']['diagnostics']:.2f} | "
            f"Recovery={summary['recovery_forensics']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'lokales-logging')

    print('\nBeste Audit-Telemetrie:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Lokales Logging {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Sichtbarkeit {best['telemetry_visibility']['visibility']:.2f}, "
        f"Audit {best['audit_continuity']['diagnostics']:.2f}, "
        f"Recovery {best['recovery_forensics']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Telemetrie-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['telemetry_visibility']['visibility'] for item in summaries],
        width,
        label='Sichtbarkeit',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['diagnostics_quality']['diagnostics'] for item in summaries],
        width,
        label='Diagnostik',
        color='#59a14f',
    )
    axes[0, 1].set_title('Sichtbarkeit und Diagnostik')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['audit_continuity']['diagnostics'] for item in summaries],
        width,
        label='Audit-Kontinuitaet',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['continuity_strength']['visibility'] for item in summaries],
        width,
        label='Betriebskontinuitaet',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Audit und Kontinuitaet')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['recovery_forensics']['recovery'] for item in summaries],
        width,
        label='Recovery-Forensik',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['telemetry_overhead']['diagnostics'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Recovery gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['diagnostics'] for item in summaries], color=colors)
    axes[1, 1].set_title('Diagnostik-Kontextscore')
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
    output = save_and_maybe_show(plt, 'kki_audit_telemetrie.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
