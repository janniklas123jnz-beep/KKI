"""
KKI Sicherheits-Policies-Studie
===============================
Vergleicht Policy-, Filter- und Eskalationsketten fuer reale Schnittstellen und
misst, welche Sicherheitsarchitektur Prompt-Injektion, Manipulation und Drift
am wirksamsten begrenzt, ohne den operativen Baufluss zu blockieren.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_audit_telemetrie import telemetry_profiles
from schwarm_dna_schema import get_named
from schwarm_governance_layer import governance_profiles
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
from schwarm_rollenassembler import normalize_role_shares
from schwarm_werkzeugadapter import adapter_profiles
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import (
    required_domain_coverage,
    required_domain_redundancy,
    route_specificity,
)



def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_SECURITY_POLICY_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_SECURITY_POLICY_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_SECURITY_POLICY_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_SECURITY_POLICY_STRESS_STRENGTH', '0.49')),
        'stress_sources': int(os.getenv('KKI_SECURITY_POLICY_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_SECURITY_POLICY_FAILURE_FRACTION', '0.18')),
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
            'name': 'policy-fit',
            'label': 'Policy-Fit',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('security', 'approval', 'trace'),
        },
        {
            'name': 'gatekeeping',
            'label': 'Gatekeeping',
            'scenario': 'consensus',
            'gatekeeping_mode': True,
            'required_domains': ('security', 'approval', 'analysis', 'coordination'),
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
            'required_domains': ('security', 'trace', 'handoff', 'memory'),
        },
    ]



def security_policy_profiles(katalog, params):
    telemetry = get_named(telemetry_profiles(katalog, params), 'forensischer-kanal')
    governance = {item['name']: item for item in governance_profiles(katalog, params)}
    governance_fed = governance['foederierte-governance']
    governance_res = governance['resilienter-governance-layer']
    adapter = get_named(adapter_profiles(katalog, params), 'audit-gateway')

    runtime = {
        **telemetry['base_config'],
        **governance_fed['config'],
        **adapter['base_config'],
    }

    return [
        {
            'name': 'offene-richtlinien',
            'label': 'Offene Richtlinien',
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
                'trust_shield_strength': 0.24,
            },
            'policy_depth': 1,
            'filter_depth': 0,
            'escalation_depth': 0,
            'recovery_depth': 1,
            'bias': {
                'policy': 0.30,
                'defense': 0.22,
                'escalation': 0.18,
                'continuity': 0.86,
                'recovery': 0.34,
                'overhead': 0.06,
            },
        },
        {
            'name': 'regel-filter',
            'label': 'Regel-Filter',
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
                'trust_shield_strength': 0.29,
            },
            'policy_depth': 2,
            'filter_depth': 2,
            'escalation_depth': 1,
            'recovery_depth': 1,
            'bias': {
                'policy': 0.58,
                'defense': 0.56,
                'escalation': 0.44,
                'continuity': 0.78,
                'recovery': 0.48,
                'overhead': 0.14,
            },
        },
        {
            'name': 'eskalationskette',
            'label': 'Eskalationskette',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge'],
            'multiplier': 0.94,
            'base_config': {
                **runtime,
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.34,
            },
            'policy_depth': 3,
            'filter_depth': 3,
            'escalation_depth': 3,
            'recovery_depth': 2,
            'bias': {
                'policy': 0.80,
                'defense': 0.74,
                'escalation': 0.82,
                'continuity': 0.76,
                'recovery': 0.68,
                'overhead': 0.22,
            },
        },
        {
            'name': 'policy-gateway',
            'label': 'Policy-Gateway',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.98,
            'base_config': {
                **runtime,
                **adapter['base_config'],
                **governance_fed['config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.37,
            },
            'policy_depth': 4,
            'filter_depth': 4,
            'escalation_depth': 3,
            'recovery_depth': 3,
            'bias': {
                'policy': 0.90,
                'defense': 0.88,
                'escalation': 0.84,
                'continuity': 0.82,
                'recovery': 0.82,
                'overhead': 0.26,
            },
        },
        {
            'name': 'foederierte-sicherheitskette',
            'label': 'Foederierte Sicherheitskette',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **telemetry['base_config'],
                **governance_fed['config'],
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
            'policy_depth': 4,
            'filter_depth': 4,
            'escalation_depth': 4,
            'recovery_depth': 4,
            'bias': {
                'policy': 0.92,
                'defense': 0.90,
                'escalation': 0.88,
                'continuity': 0.84,
                'recovery': 0.86,
                'overhead': 0.28,
            },
        },
        {
            'name': 'resiliente-injektionsabwehr',
            'label': 'Resiliente Injektionsabwehr',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.02,
            'base_config': {
                **runtime,
                **telemetry['base_config'],
                **governance_res['config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'resource_budget': 0.80,
            },
            'policy_depth': 5,
            'filter_depth': 5,
            'escalation_depth': 5,
            'recovery_depth': 5,
            'bias': {
                'policy': 0.90,
                'defense': 0.90,
                'escalation': 0.88,
                'continuity': 0.58,
                'recovery': 0.80,
                'overhead': 0.62,
            },
        },
    ]



def security_metrics(config, result, params, profile, kontext):
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
    policy_depth_score = normalize(profile['policy_depth'], 1.0, 5.0)
    filter_depth_score = normalize(profile['filter_depth'], 0.0, 5.0)
    escalation_depth_score = normalize(profile['escalation_depth'], 0.0, 5.0)
    recovery_depth_score = normalize(profile['recovery_depth'], 1.0, 5.0)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    quarantine_share = workflow.get('quarantined_agents_mean', 0.0) / agent_count

    policy_coverage = clamp01(
        mittelwert(
            [
                coverage,
                redundancy,
                traceability,
                workflow.get('meta_alignment_rate', 0.0),
                profile['bias']['policy'],
            ]
        )
    )
    defense_chain = clamp01(
        mittelwert(
            [
                filter_depth_score,
                1.0 - workflow.get('misinformation_corruption_mean', 0.0),
                1.0 - workflow.get('cluster_compromise_mean', 0.0),
                workflow.get('trust_shield_mean', 0.0),
                profile['bias']['defense'],
            ]
        )
    )
    escalation_quality = clamp01(
        mittelwert(
            [
                escalation_depth_score,
                normalize(quarantine_share, 0.0, 0.20),
                workflow.get('misinformation_detection_rate', 0.0),
                workflow.get('bottleneck_relief_rate', 0.0),
                profile['bias']['escalation'],
            ]
        )
    )
    continuity_balance = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('resource_share_rate', 0.0),
                groups['functional_group_share'],
                profile['bias']['continuity'],
            ]
        )
    )
    recovery_resilience = clamp01(
        mittelwert(
            [
                recovery_depth_score,
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                profile['bias']['recovery'],
            ]
        )
    )
    security_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_budget', 0.76), 0.76, 0.80),
                policy_depth_score,
                escalation_depth_score,
                normalize(quarantine_share, 0.0, 0.20),
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
        'trust_shield_mean': workflow.get('trust_shield_mean', 0.0),
        'quarantined_agents_mean': workflow.get('quarantined_agents_mean', 0.0),
        'recovery_events_total': workflow.get('recovery_events_total', 0.0),
        'sync_strength_mean': workflow.get('sync_strength_mean', 0.0),
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'bottleneck_relief_rate': workflow.get('bottleneck_relief_rate', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'policy_coverage': policy_coverage,
        'defense_chain': defense_chain,
        'escalation_quality': escalation_quality,
        'continuity_balance': continuity_balance,
        'recovery_resilience': recovery_resilience,
        'security_overhead': security_overhead,
        'route_exposure': exposure,
        'traceability': traceability,
        'specificity': specificity,
    }



def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    policy_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(policy_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('gatekeeping_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = max(config.get('workflow_stage_min_tenure', 2), 2)
        config['enable_meta_coordination'] = True
        config['enable_fault_isolation'] = True
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
    result['security_metrics'] = security_metrics(config, result, params, profile, kontext)
    return result



def context_score(kontext_name, result, agent_count):
    metrics = result['security_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'policy-fit':
        return (
            metrics['policy_coverage']
            + 0.18 * metrics['continuity_balance']
            + 0.12 * metrics['defense_chain']
            - 0.10 * metrics['security_overhead']
        )
    if kontext_name == 'gatekeeping':
        return (
            metrics['escalation_quality']
            + 0.18 * metrics['policy_coverage']
            + 0.12 * metrics['continuity_balance']
            - 0.10 * metrics['security_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['defense_chain']
            + 0.14 * metrics['escalation_quality']
            + 0.10 * metrics['recovery_resilience']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['security_overhead']
        )
    return (
        base
        + 0.20 * metrics['recovery_resilience']
        + 0.12 * metrics['defense_chain']
        + 0.08 * metrics['continuity_balance']
        - 0.12 * failed_share
        - 0.08 * metrics['security_overhead']
    )



def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'policy_coverage': {},
        'defense_chain': {},
        'escalation_quality': {},
        'continuity_balance': {},
        'recovery_resilience': {},
        'security_overhead': {},
        'route_exposure': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['security_metrics'][metric_name] for run in runs])

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
    profiles = security_policy_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI SICHERHEITS-POLICIES-STUDIE')
    print('=' * 84)
    print('Vergleicht Policy-, Filter- und Eskalationsketten fuer reale Baugruppen,')
    print('damit Injektionsabwehr, Policy-Durchsetzung und Recovery kontrolliert zusammenspielen.\n')

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
            f"Policy={summary['policy_coverage']['policy-fit']:.2f} | "
            f"Defense={summary['defense_chain']['stress']:.2f} | "
            f"Recovery={summary['recovery_resilience']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'offene-richtlinien')

    print('\nBeste Sicherheitskette:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Offene Richtlinien {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Policy {best['policy_coverage']['policy-fit']:.2f}, "
        f"Abwehr {best['defense_chain']['stress']:.2f}, "
        f"Recovery {best['recovery_resilience']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Sicherheits-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['policy_coverage']['policy-fit'] for item in summaries],
        width,
        label='Policy-Abdeckung',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['continuity_balance']['gatekeeping'] for item in summaries],
        width,
        label='Kontinuitaet',
        color='#59a14f',
    )
    axes[0, 1].set_title('Policy und Kontinuitaet')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['defense_chain']['stress'] for item in summaries],
        width,
        label='Abwehrkette',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['escalation_quality']['gatekeeping'] for item in summaries],
        width,
        label='Eskalation',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Abwehr und Eskalation')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['recovery_resilience']['recovery'] for item in summaries],
        width,
        label='Recovery',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['security_overhead']['gatekeeping'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Recovery gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['context_scores']['gatekeeping'] for item in summaries], color=colors)
    axes[1, 1].set_title('Gatekeeping-Kontextscore')
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
    output = save_and_maybe_show(plt, 'kki_sicherheits_policies.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
