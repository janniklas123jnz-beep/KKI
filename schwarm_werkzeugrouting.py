"""
KKI Werkzeugrouting-Studie
==========================
Vergleicht operative Capability-Broker fuer den kontrollierten Zugriff auf
Werkzeuge, Speicher und Umweltkontakte und misst, welche Routing-Schicht
Sicherheit, Vermittlung und Ausfuehrungsfluss am besten verbindet.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_bauphasen_blueprint import blueprint_profiles
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
from schwarm_rollenassembler import assembler_profiles, normalize_role_shares
from schwarm_runtime_dna import runtime_profiles
from schwarm_werkzeugbindung import apply_tools, tool_binding_profiles, tool_catalog


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_TOOL_ROUTING_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_TOOL_ROUTING_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_TOOL_ROUTING_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_TOOL_ROUTING_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_TOOL_ROUTING_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_TOOL_ROUTING_FAILURE_FRACTION', '0.18')),
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
        {
            'name': 'startup',
            'label': 'Startup',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('memory', 'analysis', 'coordination'),
        },
        {
            'name': 'operations',
            'label': 'Operation',
            'scenario': 'consensus',
            'required_domains': ('execution', 'memory', 'handoff'),
        },
        {
            'name': 'stress',
            'label': 'Stress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'required_domains': ('security', 'analysis', 'approval', 'coordination'),
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
            'required_domains': ('execution', 'memory', 'handoff', 'security'),
        },
    ]


def required_domain_hits(selected_tools, catalog, required_domains):
    hits = {domain: 0 for domain in required_domains}
    for tool_name in selected_tools:
        for domain in catalog[tool_name]['domains']:
            if domain in hits:
                hits[domain] += 1
    return hits


def required_domain_coverage(selected_tools, catalog, required_domains):
    if not required_domains:
        return 0.0
    hits = required_domain_hits(selected_tools, catalog, required_domains)
    covered = sum(1 for domain in required_domains if hits[domain] > 0)
    return covered / float(len(required_domains))


def required_domain_redundancy(selected_tools, catalog, required_domains):
    if not required_domains:
        return 0.0
    hits = required_domain_hits(selected_tools, catalog, required_domains)
    return clamp01(mittelwert([min(1.0, hits[domain] / 2.0) for domain in required_domains]))


def route_specificity(selected_tools, required_domains):
    if not required_domains:
        return 0.0
    return clamp01(1.0 - abs(len(selected_tools) - len(required_domains)) / max(1.0, len(required_domains) + 1.0))


def broker_profiles(katalog, params):
    runtime = get_named(runtime_profiles(katalog, params), 'balancierte-runtime-dna')['config']
    assembler = get_named(assembler_profiles(katalog, params), 'resilienter-rollenassembler')['config']
    operative = get_named(blueprint_profiles(katalog, params), 'operativer-blueprint')['config']
    binding = get_named(tool_binding_profiles(katalog, params), 'resiliente-werkzeugfoederation')

    return [
        {
            'name': 'direktrouting',
            'label': 'Direktrouting',
            'selected_tools': ['execution', 'memory'],
            'multiplier': 0.82,
            'base_config': {
                **runtime,
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 7,
                'mission_switch_interval': 7,
                'resource_share_factor': 0.24,
                'trust_shield_strength': 0.20,
            },
            'broker_depth': 1,
            'approval_layers': 0,
            'fallback_depth': 1,
            'bias': {
                'coverage': 0.40,
                'dispatch': 0.42,
                'approval': 0.18,
                'fallback': 0.26,
                'flow': 0.86,
                'overhead': 0.08,
            },
        },
        {
            'name': 'queue-broker',
            'label': 'Queue-Broker',
            'selected_tools': ['execution', 'memory', 'bridge'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                **assembler,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 6,
                'mission_switch_interval': 6,
                'handoff_priority_bonus': 0.16,
                'resource_share_factor': 0.26,
            },
            'broker_depth': 2,
            'approval_layers': 1,
            'fallback_depth': 2,
            'bias': {
                'coverage': 0.58,
                'dispatch': 0.60,
                'approval': 0.38,
                'fallback': 0.48,
                'flow': 0.74,
                'overhead': 0.16,
            },
        },
        {
            'name': 'faehigkeits-broker',
            'label': 'Faehigkeits-Broker',
            'selected_tools': ['analysis', 'execution', 'memory', 'bridge'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                **assembler,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'handoff_priority_bonus': 0.20,
                'resource_share_factor': 0.27,
            },
            'broker_depth': 3,
            'approval_layers': 1,
            'fallback_depth': 2,
            'bias': {
                'coverage': 0.78,
                'dispatch': 0.78,
                'approval': 0.54,
                'fallback': 0.60,
                'flow': 0.76,
                'overhead': 0.22,
            },
        },
        {
            'name': 'governance-broker',
            'label': 'Governance-Broker',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.92,
            'base_config': {
                **operative,
                **binding['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'trust_shield_strength': max(0.34, float(operative.get('trust_shield_strength', 0.28))),
            },
            'broker_depth': 4,
            'approval_layers': 2,
            'fallback_depth': 3,
            'bias': {
                'coverage': 0.88,
                'dispatch': 0.80,
                'approval': 0.84,
                'fallback': 0.76,
                'flow': 0.68,
                'overhead': 0.28,
            },
        },
        {
            'name': 'missions-broker',
            'label': 'Missions-Broker',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.95,
            'base_config': {
                **operative,
                **assembler,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.22,
                'resource_budget': 0.80,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.34,
            },
            'broker_depth': 4,
            'approval_layers': 2,
            'fallback_depth': 3,
            'bias': {
                'coverage': 0.90,
                'dispatch': 0.90,
                'approval': 0.82,
                'fallback': 0.82,
                'flow': 0.84,
                'overhead': 0.28,
            },
        },
        {
            'name': 'resilienter-capability-broker',
            'label': 'Resilienter Capability-Broker',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **operative,
                **binding['base_config'],
                **assembler,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.36,
                'bottleneck_threshold': 0.94,
                'bottleneck_triage_intensity': 0.92,
            },
            'broker_depth': 5,
            'approval_layers': 3,
            'fallback_depth': 4,
            'bias': {
                'coverage': 0.96,
                'dispatch': 0.92,
                'approval': 0.94,
                'fallback': 0.92,
                'flow': 0.82,
                'overhead': 0.30,
            },
        },
    ]


def routing_metrics(config, result, params, profile, kontext):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    agent_count = max(1.0, params['agent_count'])
    catalog = tool_catalog()
    selected_tools = profile['selected_tools']
    required_domains = kontext['required_domains']

    trace_scores = [catalog[name]['scores']['trace'] for name in selected_tools] or [0.0]
    exposure_scores = [catalog[name]['scores']['exposure'] for name in selected_tools] or [0.0]
    route_coverage_base = required_domain_coverage(selected_tools, catalog, required_domains)
    route_redundancy = required_domain_redundancy(selected_tools, catalog, required_domains)
    dispatch_specificity = route_specificity(selected_tools, required_domains)
    route_traceability = clamp01(mittelwert(trace_scores))
    route_exposure = clamp01(mittelwert(exposure_scores))
    approval_layers_score = normalize(profile['approval_layers'], 0.0, 3.0)
    broker_depth_score = normalize(profile['broker_depth'], 1.0, 5.0)
    fallback_depth_score = normalize(profile['fallback_depth'], 1.0, 4.0)
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count

    route_coverage = clamp01(
        mittelwert(
            [
                route_coverage_base,
                route_redundancy,
                schema['mandatory_coverage'],
                workflow.get('completion_rate', 0.0),
                profile['bias']['coverage'],
            ]
        )
    )
    dispatch_quality = clamp01(
        mittelwert(
            [
                workflow.get('skill_alignment_rate', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                dispatch_specificity,
                profile['bias']['dispatch'],
            ]
        )
    )
    approval_safety = clamp01(
        mittelwert(
            [
                route_traceability,
                1.0 - route_exposure,
                workflow.get('trust_shield_mean', 0.0),
                workflow.get('misinformation_detection_rate', 0.0),
                approval_layers_score,
                profile['bias']['approval'],
            ]
        )
    )
    fallback_resilience = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                fallback_depth_score,
                1.0 if config.get('enable_fault_isolation', False) else 0.0,
                profile['bias']['fallback'],
            ]
        )
    )
    routing_flow = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                result['cross_group_cooperation_rate'],
                groups['functional_group_share'],
                profile['bias']['flow'],
            ]
        )
    )
    routing_integrity = clamp01(
        mittelwert(
            [
                approval_safety,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                route_traceability,
            ]
        )
    )
    routing_adaptivity = clamp01(
        mittelwert(
            [
                fallback_resilience,
                routing_flow,
                workflow.get('resource_efficiency', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                dispatch_quality,
            ]
        )
    )
    routing_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 5), 4.0, 8.0),
                normalize(config.get('mission_switch_interval', 4), 4.0, 8.0),
                broker_depth_score,
                approval_layers_score,
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
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'route_coverage': route_coverage,
        'dispatch_quality': dispatch_quality,
        'approval_safety': approval_safety,
        'fallback_resilience': fallback_resilience,
        'routing_flow': routing_flow,
        'routing_integrity': routing_integrity,
        'routing_adaptivity': routing_adaptivity,
        'routing_overhead': routing_overhead,
        'route_traceability': route_traceability,
        'route_exposure': route_exposure,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    routed_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(routed_config)
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
    result['routing_metrics'] = routing_metrics(config, result, params, profile, kontext)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['routing_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'startup':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['route_coverage']
            + 0.14 * metrics['dispatch_quality']
            + 0.08 * metrics['routing_flow']
            - 0.10 * metrics['routing_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.16 * metrics['dispatch_quality']
            + 0.14 * metrics['routing_flow']
            + 0.08 * metrics['route_coverage']
            - 0.10 * metrics['routing_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['routing_integrity']
            + 0.12 * metrics['routing_adaptivity']
            + 0.08 * metrics['route_coverage']
            - 0.08 * metrics['routing_overhead']
        )
    return (
        base
        + 0.18 * metrics['routing_adaptivity']
        + 0.12 * metrics['routing_flow']
        + 0.08 * metrics['approval_safety']
        - 0.12 * failed_share
        - 0.08 * metrics['routing_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'route_coverage': {},
        'dispatch_quality': {},
        'approval_safety': {},
        'fallback_resilience': {},
        'routing_flow': {},
        'routing_integrity': {},
        'routing_adaptivity': {},
        'routing_overhead': {},
        'route_exposure': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['routing_metrics'][metric_name] for run in runs])

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
    profiles = broker_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI WERKZEUGROUTING-STUDIE')
    print('=' * 84)
    print('Vergleicht Capability-Broker fuer Werkzeug-, Speicher- und Umweltzugriffe,')
    print('damit operative Baugruppen sicher und effizient zwischen Faehigkeiten routen.\n')

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
            f"{summary['label']:<30} Score={summary['combined_score']:+.3f} | "
            f"Coverage={summary['route_coverage']['startup']:.2f} | "
            f"Integritaet={summary['routing_integrity']['stress']:.2f} | "
            f"Adaptivitaet={summary['routing_adaptivity']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'direktrouting')

    print('\nBester Capability-Broker:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Direktrouting {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Coverage {best['route_coverage']['startup']:.2f}, "
        f"Integritaet {best['routing_integrity']['stress']:.2f}, "
        f"Adaptivitaet {best['routing_adaptivity']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Broker-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['route_coverage']['startup'] for item in summaries],
        width,
        label='Routing-Coverage',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['dispatch_quality']['operations'] for item in summaries],
        width,
        label='Dispatch-Qualitaet',
        color='#59a14f',
    )
    axes[0, 1].set_title('Coverage und Dispatch')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['routing_integrity']['stress'] for item in summaries],
        width,
        label='Routing-Integritaet',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['routing_adaptivity']['recovery'] for item in summaries],
        width,
        label='Routing-Adaptivitaet',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Integritaet und Adaptivitaet')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['routing_flow']['operations'] for item in summaries],
        width,
        label='Routing-Flow',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['routing_overhead']['operations'] for item in summaries],
        width,
        label='Routing-Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Flow gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['startup'] for item in summaries], color=colors)
    axes[1, 1].set_title('Startup-Kontextscore')
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
        color='#59a14f',
    )
    axes[1, 2].set_title('Stress- und Recovery-Score')
    axes[1, 2].set_xticks(x)
    axes[1, 2].set_xticklabels(labels, rotation=18)
    axes[1, 2].legend()
    axes[1, 2].grid(True, axis='y', alpha=0.3)

    fig.tight_layout()
    output = save_and_maybe_show(plt, 'kki_werkzeugrouting.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
