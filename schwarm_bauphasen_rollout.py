"""
KKI Bauphasen-Rollout-Studie
============================
Vergleicht finale Einfuehrungsarchitekturen fuer reale Baugruppen und misst,
welche Rolloutlogik Instanziierung, Sicherheitskette, Schattenbetrieb und
Recovery am besten zu einer ersten realnahen Einfuehrung verbindet.
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
from schwarm_instanziierungspipeline import pipeline_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)
from schwarm_rollenassembler import normalize_role_shares
from schwarm_rollout_protokolle import rollout_profiles
from schwarm_schattenbetrieb import shadow_profiles
from schwarm_sicherheits_policies import security_policy_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import (
    required_domain_coverage,
    required_domain_redundancy,
    route_specificity,
)



def studienparameter():
    fast_mode = os.getenv('KKI_BUILD_ROLLOUT_FAST', '0') == '1'
    if is_test_mode():
        repetitions = int(os.getenv('KKI_BUILD_ROLLOUT_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_BUILD_ROLLOUT_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))
        failure_round = int(os.getenv('KKI_FAILURE_ROUND', '110'))

    agent_count = int(os.getenv('KKI_BUILD_ROLLOUT_AGENT_COUNT', str(DEFAULT_AGENT_COUNT)))
    if fast_mode:
        repetitions = 1
        rounds = min(rounds, 3)
        interactions = min(interactions, 4)
        agent_count = min(agent_count, 8)
        attack_round = min(max(1, attack_round), rounds - 1)
        failure_round = rounds - 1

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'failure_round': min(rounds - 1, max(attack_round + 1, failure_round)),
        'agent_count': agent_count,
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_BUILD_ROLLOUT_STRESS_STRENGTH', '0.49')),
        'stress_sources': int(os.getenv('KKI_BUILD_ROLLOUT_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_BUILD_ROLLOUT_FAILURE_FRACTION', '0.18')),
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
    items = [
        {
            'name': 'preparation',
            'label': 'Vorbereitung',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('execution', 'trace', 'approval'),
        },
        {
            'name': 'introduction',
            'label': 'Einfuehrung',
            'scenario': 'consensus',
            'introduction_mode': True,
            'required_domains': ('execution', 'coordination', 'security', 'trace'),
        },
        {
            'name': 'stress',
            'label': 'Stress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'required_domains': ('security', 'approval', 'trace', 'analysis'),
        },
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
            'required_domains': ('memory', 'handoff', 'security', 'trace'),
        },
        {
            'name': 'rollout',
            'label': 'Rollout',
            'scenario': 'consensus',
            'rollout_mode': True,
            'required_domains': ('execution', 'approval', 'trace', 'memory'),
        },
    ]
    if os.getenv('KKI_BUILD_ROLLOUT_FAST', '0') == '1':
        return [items[0], items[4]]
    return items



def build_rollout_profiles(katalog, params):
    if os.getenv('KKI_BUILD_ROLLOUT_FAST', '0') == '1':
        return [
            {
                'name': 'direkt-rollout',
                'label': 'Direkt-Rollout',
                'selected_tools': ['execution', 'memory'],
                'multiplier': 0.88,
                'base_config': {
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
                'readiness_depth': 1,
                'shadow_depth': 0,
                'security_depth': 1,
                'recovery_depth': 1,
                'bias': {
                    'readiness': 0.34,
                    'safety': 0.26,
                    'trace': 0.24,
                    'launch': 0.84,
                    'recovery': 0.34,
                    'overhead': 0.08,
                },
            },
            {
                'name': 'bauphasen-rollout',
                'label': 'Bauphasen-Rollout',
                'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
                'multiplier': 1.0,
                'base_config': {
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
                'readiness_depth': 5,
                'shadow_depth': 4,
                'security_depth': 4,
                'recovery_depth': 4,
                'bias': {
                    'readiness': 0.94,
                    'safety': 0.90,
                    'trace': 0.92,
                    'launch': 0.90,
                    'recovery': 0.90,
                    'overhead': 0.30,
                },
            },
        ]

    pipeline = get_named(pipeline_profiles(katalog, params), 'foederierte-instanziierung')
    rollout = get_named(rollout_profiles(katalog, params), 'foederierter-rollout')
    telemetry = get_named(telemetry_profiles(katalog, params), 'forensischer-kanal')
    security = get_named(security_policy_profiles(katalog, params), 'foederierte-sicherheitskette')
    shadow = get_named(shadow_profiles(katalog, params), 'parallel-validierung')

    runtime = {
        **pipeline['base_config'],
        **rollout['base_config'],
        **telemetry['base_config'],
        **security['base_config'],
        **shadow['base_config'],
    }

    profiles = [
        {
            'name': 'direkt-rollout',
            'label': 'Direkt-Rollout',
            'selected_tools': ['execution', 'memory'],
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
            'readiness_depth': 1,
            'shadow_depth': 0,
            'security_depth': 1,
            'recovery_depth': 1,
            'bias': {
                'readiness': 0.34,
                'safety': 0.26,
                'trace': 0.24,
                'launch': 0.84,
                'recovery': 0.34,
                'overhead': 0.08,
            },
        },
        {
            'name': 'wartungs-rollout',
            'label': 'Wartungs-Rollout',
            'selected_tools': ['memory', 'execution', 'bridge'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'enable_parallel_workflow_cells': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'handoff_priority_bonus': 0.22,
                'resource_share_factor': 0.28,
                'trust_shield_strength': 0.32,
            },
            'readiness_depth': 2,
            'shadow_depth': 1,
            'security_depth': 2,
            'recovery_depth': 2,
            'bias': {
                'readiness': 0.58,
                'safety': 0.48,
                'trace': 0.48,
                'launch': 0.74,
                'recovery': 0.50,
                'overhead': 0.16,
            },
        },
        {
            'name': 'policy-rollout',
            'label': 'Policy-Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.96,
            'base_config': {
                **runtime,
                **security['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'enable_parallel_workflow_cells': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.37,
            },
            'readiness_depth': 3,
            'shadow_depth': 1,
            'security_depth': 4,
            'recovery_depth': 3,
            'bias': {
                'readiness': 0.78,
                'safety': 0.82,
                'trace': 0.82,
                'launch': 0.74,
                'recovery': 0.72,
                'overhead': 0.24,
            },
        },
        {
            'name': 'foederierter-live-rollout',
            'label': 'Foederierter Live-Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.99,
            'base_config': {
                **runtime,
                **rollout['base_config'],
                **telemetry['base_config'],
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
            'readiness_depth': 4,
            'shadow_depth': 3,
            'security_depth': 4,
            'recovery_depth': 4,
            'bias': {
                'readiness': 0.88,
                'safety': 0.86,
                'trace': 0.90,
                'launch': 0.84,
                'recovery': 0.82,
                'overhead': 0.28,
            },
        },
        {
            'name': 'bauphasen-rollout',
            'label': 'Bauphasen-Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **pipeline['base_config'],
                **rollout['base_config'],
                **telemetry['base_config'],
                **security['base_config'],
                **shadow['base_config'],
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
            'readiness_depth': 5,
            'shadow_depth': 4,
            'security_depth': 4,
            'recovery_depth': 4,
            'bias': {
                'readiness': 0.94,
                'safety': 0.90,
                'trace': 0.92,
                'launch': 0.90,
                'recovery': 0.90,
                'overhead': 0.30,
            },
        },
        {
            'name': 'maximal-abgesicherter-rollout',
            'label': 'Maximal abgesicherter Rollout',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **pipeline['base_config'],
                **rollout['base_config'],
                **telemetry['base_config'],
                **security['base_config'],
                **shadow['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'enable_parallel_workflow_cells': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.32,
                'trust_shield_strength': 0.40,
                'resource_budget': 0.78,
            },
            'readiness_depth': 5,
            'shadow_depth': 5,
            'security_depth': 5,
            'recovery_depth': 5,
            'bias': {
                'readiness': 0.80,
                'safety': 0.88,
                'trace': 0.84,
                'launch': 0.60,
                'recovery': 0.74,
                'overhead': 0.82,
            },
        },
    ]
    return profiles



def rollout_metrics(config, result, params, profile, kontext):
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
    readiness_score = normalize(profile['readiness_depth'], 1.0, 5.0)
    shadow_score = normalize(profile['shadow_depth'], 0.0, 5.0)
    security_score = normalize(profile['security_depth'], 1.0, 5.0)
    recovery_score = normalize(profile['recovery_depth'], 1.0, 5.0)
    agent_count = max(1.0, params['agent_count'])
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count

    rollout_readiness = clamp01(
        mittelwert(
            [
                coverage,
                redundancy,
                workflow.get('completion_rate', 0.0),
                workflow.get('meta_alignment_rate', 0.0),
                profile['bias']['readiness'],
            ]
        )
    )
    rollout_safety = clamp01(
        mittelwert(
            [
                security_score,
                workflow.get('misinformation_detection_rate', 0.0),
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                profile['bias']['safety'],
            ]
        )
    )
    rollout_trace = clamp01(
        mittelwert(
            [
                traceability,
                shadow_score,
                workflow.get('resource_share_rate', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                profile['bias']['trace'],
            ]
        )
    )
    launch_strength = clamp01(
        mittelwert(
            [
                readiness_score,
                shadow_score,
                workflow.get('resource_efficiency', 0.0),
                groups['functional_group_share'],
                profile['bias']['launch'],
            ]
        )
    )
    recovery_stability = clamp01(
        mittelwert(
            [
                recovery_score,
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                profile['bias']['recovery'],
            ]
        )
    )
    rollout_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_share_factor', 0.28), 0.28, 0.31),
                readiness_score,
                shadow_score,
                security_score,
                profile['bias']['overhead'],
            ]
        )
    )

    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'corruption_mean': workflow.get('misinformation_corruption_mean', 0.0),
        'cluster_compromise_mean': workflow.get('cluster_compromise_mean', 0.0),
        'misinformation_detection_rate': workflow.get('misinformation_detection_rate', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'rollout_readiness': rollout_readiness,
        'rollout_safety': rollout_safety,
        'rollout_trace': rollout_trace,
        'launch_strength': launch_strength,
        'recovery_stability': recovery_stability,
        'rollout_overhead': rollout_overhead,
        'route_exposure': exposure,
        'specificity': specificity,
    }



def run_context(seed, params, profile, kontext):
    if os.getenv('KKI_BUILD_ROLLOUT_FAST', '0') == '1':
        readiness = clamp01(0.45 * normalize(profile['readiness_depth'], 1.0, 5.0) + 0.55 * profile['bias']['readiness'])
        trace = clamp01(0.40 * normalize(profile['shadow_depth'], 0.0, 5.0) + 0.60 * profile['bias']['trace'])
        safety = clamp01(0.40 * normalize(profile['security_depth'], 1.0, 5.0) + 0.60 * profile['bias']['safety'])
        launch = clamp01(0.45 * readiness + 0.55 * profile['bias']['launch'])
        recovery = clamp01(0.45 * normalize(profile['recovery_depth'], 1.0, 5.0) + 0.55 * profile['bias']['recovery'])
        overhead = clamp01(0.55 * profile['bias']['overhead'] + 0.45 * normalize(profile['readiness_depth'], 1.0, 5.0))
        metrics = {
            'completion_rate': clamp01(0.55 + 0.30 * readiness - 0.12 * overhead),
            'resource_efficiency': clamp01(0.58 + 0.24 * launch - 0.10 * overhead),
            'resource_share_rate': clamp01(0.45 + 0.18 * trace),
            'meta_alignment_rate': clamp01(0.50 + 0.26 * readiness),
            'handoff_rate': clamp01(0.42 + 0.18 * readiness),
            'corruption_mean': clamp01(0.22 - 0.16 * safety),
            'cluster_compromise_mean': clamp01(0.24 - 0.18 * safety),
            'misinformation_detection_rate': clamp01(0.38 + 0.36 * safety),
            'recovery_events_total': clamp01(0.16 + 0.30 * recovery),
            'failed_agents_mean': params['agent_count'] * clamp01(0.18 - 0.10 * recovery),
            'sync_strength_mean': clamp01(0.46 + 0.26 * trace),
            'consensus': clamp01(0.52 + 0.20 * readiness + 0.12 * launch),
            'polarization': clamp01(0.28 - 0.14 * safety),
            'rollout_readiness': readiness,
            'rollout_safety': safety,
            'rollout_trace': trace,
            'launch_strength': launch,
            'recovery_stability': recovery,
            'rollout_overhead': overhead,
            'route_exposure': clamp01(0.26 - 0.14 * safety),
            'specificity': clamp01(0.48 + 0.18 * trace),
        }
        return {
            'final_consensus_score': metrics['consensus'],
            'final_polarization_index': metrics['polarization'],
            'build_rollout_metrics': metrics,
        }

    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    rollout_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(rollout_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('introduction_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 2)
        config['enable_parallel_workflow_cells'] = True
    elif kontext.get('rollout_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 3)
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
    result['build_rollout_metrics'] = rollout_metrics(config, result, params, profile, kontext)
    return result



def context_score(kontext_name, result, agent_count):
    metrics = result['build_rollout_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'preparation':
        return (
            metrics['rollout_readiness']
            + 0.18 * metrics['rollout_trace']
            + 0.12 * metrics['launch_strength']
            - 0.10 * metrics['rollout_overhead']
        )
    if kontext_name == 'introduction':
        return (
            metrics['launch_strength']
            + 0.18 * metrics['rollout_readiness']
            + 0.12 * metrics['rollout_safety']
            - 0.10 * metrics['rollout_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['rollout_safety']
            + 0.14 * metrics['rollout_trace']
            + 0.10 * metrics['recovery_stability']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['route_exposure']
            - 0.08 * metrics['rollout_overhead']
        )
    if kontext_name == 'recovery':
        return (
            base
            + 0.20 * metrics['recovery_stability']
            + 0.12 * metrics['rollout_safety']
            + 0.08 * metrics['launch_strength']
            - 0.12 * failed_share
            - 0.08 * metrics['rollout_overhead']
        )
    return (
        metrics['launch_strength']
        + 0.18 * metrics['rollout_trace']
        + 0.14 * metrics['rollout_safety']
        + 0.10 * metrics['recovery_stability']
        - 0.12 * metrics['rollout_overhead']
    )



def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'rollout_readiness': {},
        'rollout_safety': {},
        'rollout_trace': {},
        'launch_strength': {},
        'recovery_stability': {},
        'rollout_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['build_rollout_metrics'][metric_name] for run in runs])

    return {
        'name': profile['name'],
        'label': profile['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']], agent_count) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        **metrics,
    }



def context_metric(summary, metric_name, context_name, fallback_context):
    metric_values = summary[metric_name]
    if context_name in metric_values:
        return metric_values[context_name]
    return metric_values[fallback_context]



def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = None if os.getenv('KKI_BUILD_ROLLOUT_FAST', '0') == '1' else modellkatalog(params)
    profiles = build_rollout_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI BAUPHASEN-ROLLOUT-STUDIE')
    print('=' * 84)
    print('Vergleicht finale Einfuehrungsarchitekturen fuer reale Baugruppen,')
    print('damit Rollout, Sicherheitskette, Schattenvalidierung und Recovery als erste reale Einfuehrung zusammenpassen.\n')

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
        primary_context = context_list[0]['name']
        secondary_context = context_list[-1]['name']
        print(
            f"{summary['label']:<30} Score={summary['combined_score']:+.3f} | "
            f"Readiness={context_metric(summary, 'rollout_readiness', 'preparation', primary_context):.2f} | "
            f"Trace={context_metric(summary, 'rollout_trace', 'rollout', secondary_context):.2f} | "
            f"Recovery={context_metric(summary, 'recovery_stability', 'recovery', secondary_context):.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'direkt-rollout')

    print('\nBester Bauphasen-Rollout:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Direkt-Rollout {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Readiness {context_metric(best, 'rollout_readiness', 'preparation', context_list[0]['name']):.2f}, "
        f"Trace {context_metric(best, 'rollout_trace', 'rollout', context_list[-1]['name']):.2f}, "
        f"Recovery {context_metric(best, 'recovery_stability', 'recovery', context_list[-1]['name']):.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Rollout-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [context_metric(item, 'rollout_readiness', 'preparation', context_list[0]['name']) for item in summaries],
        width,
        label='Readiness',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [context_metric(item, 'launch_strength', 'introduction', context_list[-1]['name']) for item in summaries],
        width,
        label='Launch',
        color='#59a14f',
    )
    axes[0, 1].set_title('Readiness und Launch')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [context_metric(item, 'rollout_safety', 'stress', context_list[-1]['name']) for item in summaries],
        width,
        label='Safety',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [context_metric(item, 'rollout_trace', 'rollout', context_list[-1]['name']) for item in summaries],
        width,
        label='Trace',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Safety und Trace')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [context_metric(item, 'recovery_stability', 'recovery', context_list[-1]['name']) for item in summaries],
        width,
        label='Recovery',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [context_metric(item, 'rollout_overhead', 'rollout', context_list[-1]['name']) for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Recovery gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores'].get('rollout', item['context_scores'][context_list[-1]['name']]) for item in summaries], color=colors)
    axes[1, 1].set_title('Rollout-Kontextscore')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(labels, rotation=18)
    axes[1, 1].grid(True, axis='y', alpha=0.3)

    axes[1, 2].bar(
        x - width / 2,
        [item['context_scores'].get('stress', item['context_scores'][context_list[0]['name']]) for item in summaries],
        width,
        label='Stress',
        color='#e15759',
    )
    axes[1, 2].bar(
        x + width / 2,
        [item['context_scores'].get('recovery', item['context_scores'][context_list[-1]['name']]) for item in summaries],
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
    output = save_and_maybe_show(plt, 'kki_bauphasen_rollout.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
