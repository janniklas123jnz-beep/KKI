"""
KKI Ressourcen-Orchestrator-Studie
=================================
Vergleicht Orchestrierungslogiken fuer Budgets, Prioritaeten und Engpaesse in
laufenden Baugruppen und misst, welche Kopplung von Zustandstransfer, Rollout und
Budgetsteuerung Ressourcen ueber Zellwechsel hinweg am besten balanciert.
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
from schwarm_resilienzbudget import budget_profiles
from schwarm_rollenassembler import normalize_role_shares
from schwarm_werkzeugbindung import apply_tools, tool_catalog
from schwarm_werkzeugrouting import (
    required_domain_coverage,
    required_domain_redundancy,
    route_specificity,
)
from schwarm_zustandstransfer import state_transfer_profiles


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_RESOURCE_ORCHESTRATOR_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_RESOURCE_ORCHESTRATOR_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_RESOURCE_ORCHESTRATOR_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_RESOURCE_ORCHESTRATOR_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_RESOURCE_ORCHESTRATOR_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_RESOURCE_ORCHESTRATOR_FAILURE_FRACTION', '0.18')),
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
            'name': 'allocation',
            'label': 'Allokation',
            'scenario': 'consensus',
            'startup_mode': True,
            'required_domains': ('execution', 'coordination', 'memory'),
        },
        {
            'name': 'orchestration',
            'label': 'Orchestrierung',
            'scenario': 'consensus',
            'orchestration_mode': True,
            'required_domains': ('execution', 'handoff', 'coordination', 'approval'),
        },
        {
            'name': 'stress',
            'label': 'Stress',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'required_domains': ('execution', 'security', 'approval', 'trace'),
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


def orchestrator_profiles(katalog, params):
    transfer = get_named(state_transfer_profiles(katalog, params), 'foederierter-zustandstransfer')
    budgets = {item['name']: item for item in budget_profiles(katalog, params)}
    adaptive_budget = budgets['dynamisches-resilienzbudget']
    operative_budget = budgets['operatives-budget']
    peak_budget = budgets['spitzenbudget']

    runtime = {
        **transfer['base_config'],
        **adaptive_budget['base_config'],
    }

    return [
        {
            'name': 'starre-zuteilung',
            'label': 'Starre Zuteilung',
            'selected_tools': ['memory', 'execution'],
            'multiplier': 0.88,
            'base_config': {
                **runtime,
                **operative_budget['base_config'],
                'enable_meta_coordination': False,
                'mission_arbitration_enabled': False,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 1,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'resource_budget': 0.76,
                'resource_share_factor': 0.27,
            },
            'coordination_depth': 1,
            'budget_layers': 1,
            'triage_depth': 0,
            'transfer_awareness': 1,
            'bias': {
                'allocation': 0.42,
                'adaptivity': 0.24,
                'retention': 0.54,
                'efficiency': 0.84,
                'recovery': 0.34,
                'overhead': 0.08,
            },
        },
        {
            'name': 'prioritaets-broker',
            'label': 'Prioritaets-Broker',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge'],
            'multiplier': 0.92,
            'base_config': {
                **runtime,
                **operative_budget['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': False,
                'enable_bottleneck_management': False,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 5,
                'mission_switch_interval': 5,
                'handoff_priority_bonus': 0.24,
                'resource_budget': 0.78,
                'resource_share_factor': 0.28,
            },
            'coordination_depth': 2,
            'budget_layers': 2,
            'triage_depth': 1,
            'transfer_awareness': 2,
            'bias': {
                'allocation': 0.64,
                'adaptivity': 0.50,
                'retention': 0.68,
                'efficiency': 0.82,
                'recovery': 0.52,
                'overhead': 0.16,
            },
        },
        {
            'name': 'transfer-orchestrator',
            'label': 'Transfer-Orchestrator',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.96,
            'base_config': {
                **runtime,
                **adaptive_budget['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_budget': 0.79,
                'resource_share_factor': 0.29,
            },
            'coordination_depth': 3,
            'budget_layers': 3,
            'triage_depth': 2,
            'transfer_awareness': 3,
            'bias': {
                'allocation': 0.82,
                'adaptivity': 0.82,
                'retention': 0.82,
                'efficiency': 0.78,
                'recovery': 0.76,
                'overhead': 0.22,
            },
        },
        {
            'name': 'foederierter-orchestrator',
            'label': 'Foederierter Orchestrator',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 0.99,
            'base_config': {
                **runtime,
                **transfer['base_config'],
                **adaptive_budget['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 2,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_budget': 0.79,
                'resource_share_factor': 0.29,
                'trust_shield_strength': 0.38,
            },
            'coordination_depth': 4,
            'budget_layers': 4,
            'triage_depth': 3,
            'transfer_awareness': 4,
            'bias': {
                'allocation': 0.90,
                'adaptivity': 0.90,
                'retention': 0.90,
                'efficiency': 0.84,
                'recovery': 0.84,
                'overhead': 0.24,
            },
        },
        {
            'name': 'engpass-orchestrator',
            'label': 'Engpass-Orchestrator',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.0,
            'base_config': {
                **runtime,
                **transfer['base_config'],
                **peak_budget['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.39,
                'bottleneck_threshold': 0.92,
                'bottleneck_triage_intensity': 0.95,
            },
            'coordination_depth': 4,
            'budget_layers': 4,
            'triage_depth': 4,
            'transfer_awareness': 4,
            'bias': {
                'allocation': 0.92,
                'adaptivity': 0.88,
                'retention': 0.88,
                'efficiency': 0.76,
                'recovery': 0.88,
                'overhead': 0.30,
            },
        },
        {
            'name': 'maximaler-ressourcenschutz',
            'label': 'Maximaler Ressourcenschutz',
            'selected_tools': ['memory', 'analysis', 'execution', 'bridge', 'shield'],
            'multiplier': 1.01,
            'base_config': {
                **runtime,
                **transfer['base_config'],
                **peak_budget['base_config'],
                'enable_meta_coordination': True,
                'mission_arbitration_enabled': True,
                'enable_fault_isolation': True,
                'enable_bottleneck_management': True,
                'workflow_stage_min_tenure': 3,
                'meta_update_interval': 4,
                'mission_switch_interval': 4,
                'handoff_priority_bonus': 0.24,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'trust_shield_strength': 0.40,
                'bottleneck_threshold': 0.90,
                'bottleneck_triage_intensity': 0.96,
            },
            'coordination_depth': 5,
            'budget_layers': 5,
            'triage_depth': 5,
            'transfer_awareness': 5,
            'bias': {
                'allocation': 0.90,
                'adaptivity': 0.66,
                'retention': 0.84,
                'efficiency': 0.54,
                'recovery': 0.86,
                'overhead': 0.56,
            },
        },
    ]


def orchestrator_metrics(config, result, params, profile, kontext):
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
    coordination_score = normalize(profile['coordination_depth'], 1.0, 5.0)
    budget_layers_score = normalize(profile['budget_layers'], 1.0, 5.0)
    triage_score = normalize(profile['triage_depth'], 0.0, 5.0)
    transfer_score = normalize(profile['transfer_awareness'], 1.0, 5.0)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    bottleneck_rate = workflow.get('bottleneck_rate', 0.0)
    relief_rate = workflow.get('bottleneck_relief_rate', 0.0)
    rerouted_budget = workflow.get('rerouted_budget_total', 0.0) / agent_count

    allocation_fit = clamp01(
        mittelwert(
            [
                coverage,
                redundancy,
                specificity,
                relief_rate,
                profile['bias']['allocation'],
            ]
        )
    )
    adaptive_orchestration = clamp01(
        mittelwert(
            [
                coordination_score,
                budget_layers_score,
                triage_score,
                1.0 if config.get('enable_bottleneck_management', False) else 0.0,
                profile['bias']['adaptivity'],
            ]
        )
    )
    state_retention = clamp01(
        mittelwert(
            [
                transfer_score,
                workflow.get('meta_alignment_rate', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                workflow.get('resource_share_rate', 0.0),
                profile['bias']['retention'],
            ]
        )
    )
    efficiency_balance = clamp01(
        mittelwert(
            [
                workflow.get('resource_efficiency', 0.0),
                workflow.get('completion_rate', 0.0),
                groups['functional_group_share'],
                1.0 - bottleneck_rate,
                profile['bias']['efficiency'],
            ]
        )
    )
    recovery_reserve = clamp01(
        mittelwert(
            [
                recoveries,
                1.0 - failed_share,
                workflow.get('sync_strength_mean', 0.0),
                1.0 - bottleneck_rate,
                profile['bias']['recovery'],
            ]
        )
    )
    orchestrator_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('resource_budget', 0.76), 0.76, 0.80),
                budget_layers_score,
                triage_score,
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
        'failed_agents_mean': workflow.get('failed_agents_mean', 0.0),
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'bottleneck_rate': bottleneck_rate,
        'bottleneck_relief_rate': relief_rate,
        'rerouted_budget': rerouted_budget,
        'allocation_fit': allocation_fit,
        'adaptive_orchestration': adaptive_orchestration,
        'state_retention': state_retention,
        'efficiency_balance': efficiency_balance,
        'recovery_reserve': recovery_reserve,
        'orchestrator_overhead': orchestrator_overhead,
        'route_exposure': exposure,
        'traceability': traceability,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    orch_config = apply_tools(profile['base_config'], profile['selected_tools'], tool_catalog(), profile['multiplier'])
    config.update(orch_config)
    normalize_role_shares(config)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('startup_mode'):
        config['enable_prompt_injection'] = False
        config['workflow_stage_min_tenure'] = 1
    elif kontext.get('orchestration_mode'):
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
    result['orchestrator_metrics'] = orchestrator_metrics(config, result, params, profile, kontext)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['orchestrator_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'allocation':
        return (
            metrics['allocation_fit']
            + 0.18 * metrics['efficiency_balance']
            + 0.12 * metrics['state_retention']
            - 0.10 * metrics['orchestrator_overhead']
        )
    if kontext_name == 'orchestration':
        return (
            metrics['adaptive_orchestration']
            + 0.18 * metrics['allocation_fit']
            + 0.12 * metrics['efficiency_balance']
            - 0.10 * metrics['orchestrator_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['adaptive_orchestration']
            + 0.14 * metrics['state_retention']
            + 0.10 * metrics['recovery_reserve']
            - 0.12 * metrics['corruption_mean']
            - 0.10 * metrics['route_exposure']
            - 0.08 * metrics['orchestrator_overhead']
        )
    return (
        base
        + 0.20 * metrics['recovery_reserve']
        + 0.12 * metrics['state_retention']
        + 0.08 * metrics['efficiency_balance']
        - 0.12 * failed_share
        - 0.08 * metrics['orchestrator_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'allocation_fit': {},
        'adaptive_orchestration': {},
        'state_retention': {},
        'efficiency_balance': {},
        'recovery_reserve': {},
        'orchestrator_overhead': {},
        'bottleneck_rate': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['orchestrator_metrics'][metric_name] for run in runs])

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
    profiles = orchestrator_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI RESSOURCEN-ORCHESTRATOR-STUDIE')
    print('=' * 84)
    print('Vergleicht Budget- und Prioritaetsorchestrierung fuer laufende Baugruppen,')
    print('damit Ressourcen ueber Zustandstransfer, Rollout und Recovery hinweg balanciert bleiben.\n')

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
            f"Alloc={summary['allocation_fit']['allocation']:.2f} | "
            f"State={summary['state_retention']['orchestration']:.2f} | "
            f"Recovery={summary['recovery_reserve']['recovery']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'starre-zuteilung')

    print('\nBester Ressourcen-Orchestrator:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zu Starre Zuteilung {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Allokation {best['allocation_fit']['allocation']:.2f}, "
        f"Retention {best['state_retention']['orchestration']:.2f}, "
        f"Recovery {best['recovery_reserve']['recovery']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Orchestrator-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['allocation_fit']['allocation'] for item in summaries],
        width,
        label='Allokations-Fit',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['adaptive_orchestration']['orchestration'] for item in summaries],
        width,
        label='Adaptiver Orchestrator',
        color='#59a14f',
    )
    axes[0, 1].set_title('Allokation und Adaptivitaet')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['state_retention']['orchestration'] for item in summaries],
        width,
        label='Zustands-Retention',
        color='#e15759',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['recovery_reserve']['recovery'] for item in summaries],
        width,
        label='Recovery-Reserve',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Retention und Recovery')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    axes[1, 0].bar(
        x - width / 2,
        [item['efficiency_balance']['allocation'] for item in summaries],
        width,
        label='Effizienz',
        color='#76b7b2',
    )
    axes[1, 0].bar(
        x + width / 2,
        [item['orchestrator_overhead']['orchestration'] for item in summaries],
        width,
        label='Overhead',
        color='#bab0ab',
    )
    axes[1, 0].set_title('Effizienz gegen Overhead')
    axes[1, 0].set_xticks(x)
    axes[1, 0].set_xticklabels(labels, rotation=18)
    axes[1, 0].legend()
    axes[1, 0].grid(True, axis='y', alpha=0.3)

    axes[1, 1].bar(x, [item['bottleneck_rate']['stress'] for item in summaries], color=colors)
    axes[1, 1].set_title('Bottleneck-Rate im Stress')
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
    output = save_and_maybe_show(plt, 'kki_ressourcen_orchestrator.png')
    print(f'\nGraph gespeichert: {output}')


if __name__ == '__main__':
    main()
