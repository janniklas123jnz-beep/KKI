"""
KKI Runtime-DNA-Studie
======================
Vergleicht konkrete Laufzeit-Templates fuer spaetere Bauagenten und misst,
welche Runtime-DNA aus dem Bauvertrag instanziierbar, identitaetsstabil,
erweiterbar und zugleich operativ tragfaehig bleibt.
"""

from __future__ import annotations

import os
import random

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_bauphasen_blueprint import blueprint_profiles
from schwarm_dna_schema import get_named, schema_metrics, schema_profiles
from schwarm_gruppenbildung import gruppenmetriken
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_gruppenbootstrap import bootstrap_profiles
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_RUNTIME_DNA_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_RUNTIME_DNA_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_RUNTIME_DNA_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_RUNTIME_DNA_STRESS_STRENGTH', '0.48')),
        'stress_sources': int(os.getenv('KKI_RUNTIME_DNA_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_RUNTIME_DNA_FAILURE_FRACTION', '0.18')),
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
        {'name': 'stress', 'label': 'Stress', 'scenario': 'polarization', 'enable_prompt_injection': True},
        {
            'name': 'recovery',
            'label': 'Recovery',
            'scenario': 'polarization',
            'enable_prompt_injection': True,
            'enable_failures': True,
        },
    ]


def runtime_profiles(katalog, params):
    schema_entries = schema_profiles(katalog)
    minimal = get_named(schema_entries, 'minimal-contract')['config']
    learning = get_named(schema_entries, 'learning-contract')['config']
    balanced = get_named(schema_entries, 'balanced-contract')['config']
    bootstrap = get_named(bootstrap_profiles(katalog, params), 'resilienter-bootstrap')['config']
    operative = get_named(blueprint_profiles(katalog, params), 'operativer-blueprint')['config']
    resilient = get_named(blueprint_profiles(katalog, params), 'resilienter-blueprint')['config']

    return [
        {
            'name': 'starres-template',
            'label': 'Starres Template',
            'config': {
                **minimal,
                **bootstrap,
                'enable_role_switching': False,
                'mission_arbitration_enabled': False,
                'enable_meta_coordination': False,
                'enable_fault_isolation': False,
                'resource_share_factor': 0.20,
                'meta_update_interval': 7,
            },
            'bias': {'instantiation': 0.52, 'identity': 0.62, 'hooks': 0.24, 'runtime': 0.42, 'resilience': 0.34, 'overhead': 0.08},
        },
        {
            'name': 'lern-template',
            'label': 'Lern-Template',
            'config': {
                **learning,
                **bootstrap,
                'enable_role_switching': True,
                'mission_arbitration_enabled': True,
                'enable_meta_coordination': True,
                'meta_update_interval': 5,
                'resource_share_factor': 0.24,
            },
            'bias': {'instantiation': 0.62, 'identity': 0.66, 'hooks': 0.76, 'runtime': 0.62, 'resilience': 0.52, 'overhead': 0.18},
        },
        {
            'name': 'balancierte-runtime-dna',
            'label': 'Balancierte Runtime-DNA',
            'config': {
                **balanced,
                **bootstrap,
                'enable_role_switching': True,
                'mission_arbitration_enabled': True,
                'enable_meta_coordination': True,
                'enable_fault_isolation': True,
                'resource_share_factor': 0.26,
                'meta_update_interval': 5,
            },
            'bias': {'instantiation': 0.78, 'identity': 0.82, 'hooks': 0.74, 'runtime': 0.74, 'resilience': 0.70, 'overhead': 0.22},
        },
        {
            'name': 'operative-runtime-dna',
            'label': 'Operative Runtime-DNA',
            'config': {
                **balanced,
                **operative,
                'enable_role_switching': True,
                'meta_update_interval': 4,
                'resource_budget': 0.79,
                'resource_share_factor': 0.29,
            },
            'bias': {'instantiation': 0.90, 'identity': 0.88, 'hooks': 0.84, 'runtime': 0.90, 'resilience': 0.82, 'overhead': 0.28},
        },
        {
            'name': 'resiliente-runtime-dna',
            'label': 'Resiliente Runtime-DNA',
            'config': {
                **balanced,
                **resilient,
                'enable_role_switching': True,
                'meta_update_interval': 4,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
            },
            'bias': {'instantiation': 0.90, 'identity': 0.90, 'hooks': 0.88, 'runtime': 0.86, 'resilience': 0.92, 'overhead': 0.32},
        },
        {
            'name': 'uebersteuerte-runtime',
            'label': 'Uebersteuerte Runtime',
            'config': {
                **balanced,
                **resilient,
                'enable_role_switching': True,
                'resource_budget': 0.80,
                'resource_share_factor': 0.30,
                'meta_update_interval': 3,
                'bottleneck_triage_intensity': 0.98,
                'mission_switch_interval': 3,
            },
            'bias': {'instantiation': 0.82, 'identity': 0.86, 'hooks': 0.84, 'runtime': 0.70, 'resilience': 0.88, 'overhead': 0.42},
        },
    ]


def runtime_metrics(config, result, params, bias):
    workflow = result['workflow_metrics']
    groups = gruppenmetriken(result['agents'], params)
    schema = schema_metrics(config)
    agent_count = max(1.0, params['agent_count'])
    recoveries = workflow.get('recovery_events_total', 0.0) / agent_count
    failed_share = workflow.get('failed_agents_mean', 0.0) / agent_count
    arbitration_activity = normalize(result.get('mission_arbitration_total', 0.0), 0.0, 40.0)

    instantiation_ready = clamp01(
        mittelwert(
            [
                schema['startup_readiness'],
                workflow.get('completion_rate', 0.0),
                groups['functional_group_share'],
                workflow.get('skill_alignment_rate', 0.0),
                bias['instantiation'],
            ]
        )
    )
    identity_coherence = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                schema['safety_margin'],
                1.0 - groups['group_separation'],
                bias['identity'],
            ]
        )
    )
    extension_hooks = clamp01(
        mittelwert(
            [
                schema['extensibility'],
                1.0 if config.get('enable_role_switching', False) else 0.0,
                1.0 if config.get('enable_meta_coordination', False) else 0.0,
                workflow.get('resource_share_rate', 0.0),
                bias['hooks'],
            ]
        )
    )
    runtime_operability = clamp01(
        mittelwert(
            [
                workflow.get('completion_rate', 0.0),
                workflow.get('resource_efficiency', 0.0),
                workflow.get('handoff_rate', 0.0),
                workflow.get('sync_strength_mean', 0.0),
                bias['runtime'],
            ]
        )
    )
    resilience_margin = clamp01(
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
    runtime_overhead = clamp01(
        mittelwert(
            [
                normalize(config.get('meta_update_interval', 4), 4.0, 8.0),
                arbitration_activity,
                normalize(config.get('resource_share_factor', 0.20), 0.20, 0.30),
                normalize(config.get('mission_switch_interval', 4), 4.0, 8.0),
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
        'consensus': result['final_consensus_score'],
        'polarization': result['final_polarization_index'],
        'instantiation_ready': instantiation_ready,
        'identity_coherence': identity_coherence,
        'extension_hooks': extension_hooks,
        'runtime_operability': runtime_operability,
        'resilience_margin': resilience_margin,
        'runtime_overhead': runtime_overhead,
    }


def run_context(seed, params, profile, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(profile['config'])
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
    result['runtime_metrics'] = runtime_metrics(config, result, params, profile['bias'])
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['runtime_metrics']
    base = metrics['consensus'] - metrics['polarization']
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)

    if kontext_name == 'bootstrap':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['instantiation_ready']
            + 0.14 * metrics['identity_coherence']
            + 0.10 * metrics['extension_hooks']
            - 0.10 * metrics['runtime_overhead']
        )
    if kontext_name == 'operations':
        return (
            metrics['completion_rate']
            + 0.18 * metrics['runtime_operability']
            + 0.14 * metrics['extension_hooks']
            + 0.10 * metrics['identity_coherence']
            - 0.10 * metrics['runtime_overhead']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.18 * metrics['resilience_margin']
            + 0.10 * metrics['identity_coherence']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.08 * metrics['runtime_overhead']
        )
    return (
        base
        + 0.18 * metrics['resilience_margin']
        + 0.12 * recoveries
        + 0.08 * metrics['runtime_operability']
        - 0.12 * failed_share
        - 0.08 * metrics['runtime_overhead']
    )


def summarize_runs(runs, profile, context_list, agent_count):
    context_scores = {}
    metrics = {
        'instantiation_ready': {},
        'identity_coherence': {},
        'extension_hooks': {},
        'runtime_operability': {},
        'resilience_margin': {},
        'runtime_overhead': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in metrics:
            metrics[metric_name][name] = mittelwert([run[name]['runtime_metrics'][metric_name] for run in runs])

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
    profiles = runtime_profiles(katalog, params)
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI RUNTIME-DNA-STUDIE')
    print('=' * 84)
    print('Vergleicht konkrete Laufzeit-Templates fuer Bauagenten, damit der')
    print('Bauvertrag in instanziierbare, erweiterbare und belastbare Runtime-DNA uebergeht.\n')

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
            f"Instanz={summary['instantiation_ready']['bootstrap']:.2f} | "
            f"Hooks={summary['extension_hooks']['operations']:.2f} | "
            f"Resilienz={summary['resilience_margin']['stress']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'starres-template')

    print('\nBeste Runtime-DNA:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum starren Template {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Instanziierbarkeit {best['instantiation_ready']['bootstrap']:.2f}, "
        f"Erweiterung {best['extension_hooks']['operations']:.2f}, "
        f"Resilienz {best['resilience_margin']['stress']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Runtime-DNA-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['instantiation_ready']['bootstrap'] for item in summaries],
        width,
        label='Instanziierbarkeit',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['identity_coherence']['bootstrap'] for item in summaries],
        width,
        label='Identitaet',
        color='#59a14f',
    )
    axes[0, 1].set_title('Startfaehigkeit und Identitaet')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['extension_hooks']['operations'] for item in summaries],
        width,
        label='Erweiterung',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['runtime_overhead']['operations'] for item in summaries],
        width,
        label='Overhead',
        color='#e15759',
    )
    axes[0, 2].set_title('Hooks vs. Laufzeitkosten')
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
                item['runtime_operability']['operations'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Runtime-Kontexte')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Boot', 'Ops', 'Stress', 'Rec', 'Run'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['resilience_margin']['stress'] for item in summaries],
        width,
        label='Resilienz',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['runtime_operability']['operations'] for item in summaries],
        width,
        label='Operabilitaet',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Resilienz und Operabilitaet')
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
            f"- Delta zum starren Template: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Instanziierbarkeit: {best['instantiation_ready']['bootstrap']:.2f}\n"
            f"- Identitaet: {best['identity_coherence']['bootstrap']:.2f}\n"
            f"- Erweiterung: {best['extension_hooks']['operations']:.2f}\n"
            f"- Operabilitaet: {best['runtime_operability']['operations']:.2f}\n"
            f"- Resilienz: {best['resilience_margin']['stress']:.2f}\n"
            f"- Overhead: {best['runtime_overhead']['operations']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_runtime_dna.png', dpi=150)


if __name__ == '__main__':
    main()
