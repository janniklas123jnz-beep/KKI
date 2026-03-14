"""
KKI Overlay-Modul-Studie
========================
Vergleicht verschiedene Modularisierungen gruppenspezifischer Zusatzfaehigkeiten
ueber einer gemeinsamen Bau-DNA und misst, welche Overlay-Pakete kompatibel
bleiben, ohne unerwuenschte Seiteneffekte in Koordination und Robustheit zu
erzeugen.
"""

from __future__ import annotations

import os
import random
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_dna_schema import get_named, schema_metrics, schema_profiles
from schwarm_gruppenidentitaet import modellkatalog, mittelwert
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


ROLE_KEYS = ['connector_share', 'sentinel_share', 'mediator_share', 'analyzer_share']


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_OVERLAY_MODULE_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 2)
        failure_round = min(rounds - 1, attack_round + 1)
    else:
        repetitions = int(os.getenv('KKI_OVERLAY_MODULE_REPETITIONS', '3'))
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
        'agent_count': int(os.getenv('KKI_OVERLAY_MODULE_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'stress_strength': float(os.getenv('KKI_OVERLAY_MODULE_STRESS_STRENGTH', '0.45')),
        'stress_sources': int(os.getenv('KKI_OVERLAY_MODULE_STRESS_SOURCES', '8')),
        'failure_duration': int(os.getenv('KKI_FAILURE_DURATION', '8')),
        'failure_fraction': float(os.getenv('KKI_OVERLAY_MODULE_FAILURE_FRACTION', '0.18')),
        'resync_strength': float(os.getenv('KKI_RESYNC_STRENGTH', '0.36')),
    }


def clamp01(value):
    return max(0.0, min(1.0, float(value)))


def normalize(value, minimum, maximum):
    if maximum <= minimum:
        return 0.0
    return clamp01((float(value) - minimum) / (maximum - minimum))


def kontexte():
    return [
        {'name': 'bootstrap', 'label': 'Bootstrap', 'scenario': 'consensus', 'bootstrap_mode': True},
        {'name': 'consensus', 'label': 'Konsens', 'scenario': 'consensus'},
        {
            'name': 'stress',
            'label': 'Manipulationsstress',
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


def add_scaled(config, key, delta, multiplier):
    current = config.get(key, 0)
    if isinstance(delta, int) and not isinstance(delta, bool):
        config[key] = int(round(int(current) + delta * multiplier))
        return
    config[key] = float(current) + float(delta) * multiplier


def module_catalog():
    return {
        'analysis': {
            'label': 'Analysemodul',
            'domains': ('learning', 'analysis'),
            'deltas': {
                'analyzer_share': 0.04,
                'generalist_share': -0.02,
                'analyzer_memory_window': 12,
                'analyzer_learning_multiplier': 0.08,
                'group_learning_rate': 0.015,
                'meta_priority_strength': 0.015,
            },
        },
        'bridge': {
            'label': 'Brueckenmodul',
            'domains': ('coordination', 'handoff'),
            'deltas': {
                'connector_share': 0.04,
                'mediator_share': 0.03,
                'generalist_share': -0.03,
                'connector_cross_group_learning_bonus': 0.06,
                'rewire_cross_group_bonus': 0.05,
                'resource_share_factor': 0.02,
            },
        },
        'shield': {
            'label': 'Schutzmodul',
            'domains': ('security', 'governance'),
            'deltas': {
                'sentinel_share': 0.05,
                'generalist_share': -0.03,
                'trust_shield_strength': 0.07,
                'meta_priority_strength': 0.03,
                'quarantine_compromise_threshold': -0.03,
                'quarantine_exposure_threshold': -0.03,
            },
        },
        'recovery': {
            'label': 'Recovery-Modul',
            'domains': ('recovery', 'coordination'),
            'deltas': {
                'mediator_share': 0.02,
                'generalist_share': -0.02,
                'group_learning_rate': 0.02,
                'resource_budget': 0.03,
                'resource_share_factor': 0.02,
                'resync_strength': 0.08,
            },
        },
    }


def overlay_profiles():
    return [
        {
            'name': 'core-contract',
            'label': 'Nur Bauvertrag',
            'selected_modules': [],
            'multiplier': 0.0,
            'style': 'core',
            'style_bias': {'integration': 0.44, 'isolation': 0.96, 'side_effect': 0.02, 'rollback': 0.16},
        },
        {
            'name': 'starres-bundle',
            'label': 'Starres Gesamtpaket',
            'selected_modules': ['analysis', 'bridge', 'shield', 'recovery'],
            'multiplier': 1.10,
            'style': 'monolith',
            'style_bias': {'integration': 0.62, 'isolation': 0.46, 'side_effect': 0.16, 'rollback': -0.06},
        },
        {
            'name': 'isolierte-module',
            'label': 'Isolierte Module',
            'selected_modules': ['analysis', 'bridge', 'shield', 'recovery'],
            'multiplier': 0.82,
            'style': 'isolated',
            'style_bias': {'integration': 0.52, 'isolation': 0.88, 'side_effect': 0.07, 'rollback': 0.10},
        },
        {
            'name': 'kompatible-overlays',
            'label': 'Kompatible Overlay-Module',
            'selected_modules': ['analysis', 'bridge', 'shield', 'recovery'],
            'multiplier': 0.88,
            'style': 'compatible',
            'style_bias': {'integration': 0.90, 'isolation': 0.80, 'side_effect': 0.04, 'rollback': 0.14},
        },
        {
            'name': 'adaptiver-stack',
            'label': 'Adaptiver Overlay-Stack',
            'selected_modules': ['analysis', 'bridge', 'shield', 'recovery'],
            'multiplier': 0.95,
            'style': 'adaptive',
            'style_bias': {'integration': 0.96, 'isolation': 0.72, 'side_effect': 0.07, 'rollback': 0.08},
        },
        {
            'name': 'invasive-overlays',
            'label': 'Invasive Overlays',
            'selected_modules': ['analysis', 'bridge', 'shield', 'recovery'],
            'multiplier': 1.32,
            'style': 'invasive',
            'style_bias': {'integration': 0.56, 'isolation': 0.34, 'side_effect': 0.25, 'rollback': -0.12},
        },
    ]


def normalize_role_shares(config, min_generalist=0.12):
    roles = [max(0.10, float(config.get(key, 0.0))) for key in ROLE_KEYS]
    max_specialists = 1.0 - min_generalist
    total = sum(roles)
    if total > max_specialists:
        scale = max_specialists / total
        roles = [value * scale for value in roles]
    for key, value in zip(ROLE_KEYS, roles):
        config[key] = value
    config['generalist_share'] = max(min_generalist, 1.0 - sum(roles))


def clamp_safe_ranges(config):
    config['resource_budget'] = min(0.76, max(0.60, float(config.get('resource_budget', 0.66))))
    config['resource_share_factor'] = min(0.30, max(0.20, float(config.get('resource_share_factor', 0.24))))
    config['cluster_budget_skew'] = min(0.28, max(0.16, float(config.get('cluster_budget_skew', 0.22))))
    config['group_learning_rate'] = min(0.20, max(0.12, float(config.get('group_learning_rate', 0.15))))
    config['meta_priority_strength'] = min(0.40, max(0.30, float(config.get('meta_priority_strength', 0.33))))
    config['trust_shield_strength'] = min(0.42, max(0.24, float(config.get('trust_shield_strength', 0.30))))
    config['rewire_cross_group_bonus'] = min(0.18, max(0.10, float(config.get('rewire_cross_group_bonus', 0.12))))
    config['connector_cross_group_learning_bonus'] = min(
        0.24, max(0.14, float(config.get('connector_cross_group_learning_bonus', 0.18)))
    )
    config['analyzer_memory_window'] = min(60, max(24, int(config.get('analyzer_memory_window', 42))))
    config['analyzer_learning_multiplier'] = min(
        1.36, max(1.18, float(config.get('analyzer_learning_multiplier', 1.24)))
    )
    config['quarantine_compromise_threshold'] = min(
        0.24, max(0.18, float(config.get('quarantine_compromise_threshold', 0.21)))
    )
    exposure = min(0.32, max(0.24, float(config.get('quarantine_exposure_threshold', 0.28))))
    config['quarantine_exposure_threshold'] = max(
        config['quarantine_compromise_threshold'] + 0.04,
        exposure,
    )


def build_profile(katalog, params, eintrag):
    base_contract = get_named(schema_profiles(katalog), 'balanced-contract')['config']
    config = dict(base_contract)
    modules = module_catalog()
    selected_modules = [modules[name] for name in eintrag['selected_modules']]

    key_overlap = Counter()
    for modul in selected_modules:
        for key, delta in modul['deltas'].items():
            add_scaled(config, key, delta, eintrag['multiplier'])
            key_overlap[key] += 1

    config.setdefault('resync_strength', params['resync_strength'])
    config.setdefault('failure_fraction', params['failure_fraction'])

    style = eintrag['style']
    if style == 'monolith':
        add_scaled(config, 'resource_budget', 0.05, 1.0)
        add_scaled(config, 'cluster_budget_skew', 0.10, 1.0)
        add_scaled(config, 'meta_priority_strength', 0.04, 1.0)
        add_scaled(config, 'generalist_share', -0.04, 1.0)
        add_scaled(config, 'rewire_cross_group_bonus', -0.02, 1.0)
    elif style == 'isolated':
        add_scaled(config, 'resource_share_factor', -0.03, 1.0)
        add_scaled(config, 'rewire_cross_group_bonus', -0.04, 1.0)
        add_scaled(config, 'meta_priority_strength', -0.02, 1.0)
        add_scaled(config, 'group_learning_rate', -0.01, 1.0)
    elif style == 'compatible':
        add_scaled(config, 'resource_budget', 0.02, 1.0)
        add_scaled(config, 'resource_share_factor', 0.02, 1.0)
        add_scaled(config, 'meta_priority_strength', 0.02, 1.0)
        add_scaled(config, 'rewire_cross_group_bonus', 0.02, 1.0)
        add_scaled(config, 'trust_shield_strength', 0.02, 1.0)
        clamp_safe_ranges(config)
    elif style == 'adaptive':
        add_scaled(config, 'resource_budget', 0.03, 1.0)
        add_scaled(config, 'resource_share_factor', 0.03, 1.0)
        add_scaled(config, 'group_learning_rate', 0.01, 1.0)
        add_scaled(config, 'meta_priority_strength', 0.03, 1.0)
        add_scaled(config, 'resync_strength', 0.05, 1.0)
        config['enable_role_switching'] = True
        config['role_switch_interval'] = min(8, int(config.get('role_switch_interval', 8)))
        config['role_switch_min_tenure'] = min(4, int(config.get('role_switch_min_tenure', 4)))
        config['meta_update_interval'] = 4
        clamp_safe_ranges(config)
    elif style == 'invasive':
        add_scaled(config, 'resource_budget', 0.10, 1.0)
        add_scaled(config, 'cluster_budget_skew', 0.14, 1.0)
        add_scaled(config, 'meta_priority_strength', 0.08, 1.0)
        add_scaled(config, 'group_learning_rate', 0.04, 1.0)
        add_scaled(config, 'generalist_share', -0.06, 1.0)
        add_scaled(config, 'analyzer_memory_window', 18, 1.0)
        add_scaled(config, 'analyzer_learning_multiplier', 0.10, 1.0)
        add_scaled(config, 'trust_shield_strength', 0.06, 1.0)

    normalize_role_shares(config, min_generalist=0.12 if style != 'invasive' else 0.08)
    config['failure_fraction'] = max(0.08, min(0.28, float(config.get('failure_fraction', params['failure_fraction']))))
    config['resync_strength'] = max(0.22, min(0.54, float(config.get('resync_strength', params['resync_strength']))))

    return config, key_overlap


def overlay_module_metrics(config, base_contract, eintrag, key_overlap):
    schema = schema_metrics(config)
    selected_count = len(eintrag['selected_modules'])
    module_surface = selected_count / max(1.0, float(len(module_catalog())))
    numeric_keys = sorted(
        {
            'resource_budget',
            'resource_share_factor',
            'cluster_budget_skew',
            'group_learning_rate',
            'meta_priority_strength',
            'trust_shield_strength',
            'rewire_cross_group_bonus',
            'connector_cross_group_learning_bonus',
            'analyzer_memory_window',
            'analyzer_learning_multiplier',
            'quarantine_compromise_threshold',
            'quarantine_exposure_threshold',
            'resync_strength',
            *ROLE_KEYS,
        }
    )
    deviations = []
    for key in numeric_keys:
        baseline = float(base_contract.get(key, config.get(key, 0.0)))
        current = float(config.get(key, baseline))
        deviations.append(abs(current - baseline) / max(0.05, abs(baseline)))
    module_intensity = mittelwert(deviations)

    overlap_total = sum(max(0, count - 1) for count in key_overlap.values())
    overlap_pressure = overlap_total / max(1.0, float(sum(key_overlap.values())))
    compatibility_score = clamp01(
        mittelwert(
            [
                schema['mandatory_coverage'],
                schema['invariant_compliance'],
                schema['extensibility'],
                1.0 - normalize(module_intensity, 0.18, 0.70),
                1.0 - eintrag['style_bias']['side_effect'],
            ]
        )
    )
    side_effect_risk = clamp01(
        0.38 * schema['contract_risk']
        + 0.24 * overlap_pressure
        + 0.20 * normalize(module_intensity, 0.20, 0.80)
        + 0.18 * eintrag['style_bias']['side_effect']
    )
    isolation_score = clamp01(
        eintrag['style_bias']['isolation'] - 0.24 * overlap_pressure - 0.10 * schema['overload_risk']
    )
    integration_score = clamp01(
        eintrag['style_bias']['integration']
        + 0.14 * normalize(config.get('resource_share_factor', 0.0), 0.18, 0.30)
        + 0.14 * normalize(config.get('rewire_cross_group_bonus', 0.0), 0.10, 0.18)
        + 0.12 * normalize(config.get('meta_priority_strength', 0.0), 0.28, 0.40)
        - 0.16 * side_effect_risk
    )
    rollback_safety = clamp01(
        mittelwert(
            [
                1.0 - schema['overload_risk'],
                schema['safety_margin'],
                schema['startup_readiness'],
                1.0 - side_effect_risk,
                0.5 + eintrag['style_bias']['rollback'],
            ]
        )
    )
    module_synergy = clamp01(
        mittelwert([module_surface, integration_score, schema['learning_capacity'], schema['safety_margin']])
        - 0.12 * overlap_pressure
    )

    return {
        'module_coverage': module_surface,
        'module_intensity': module_intensity,
        'compatibility_score': compatibility_score,
        'side_effect_risk': side_effect_risk,
        'isolation_score': isolation_score,
        'integration_score': integration_score,
        'rollback_safety': rollback_safety,
        'overlap_pressure': overlap_pressure,
        'module_synergy': module_synergy,
        **schema,
    }


def experiment_metrics(result):
    workflow = result['workflow_metrics']
    return {
        'completion_rate': workflow.get('completion_rate', 0.0),
        'resource_efficiency': workflow.get('resource_efficiency', 0.0),
        'meta_alignment_rate': workflow.get('meta_alignment_rate', 0.0),
        'skill_alignment_rate': workflow.get('skill_alignment_rate', 0.0),
        'handoff_rate': workflow.get('handoff_rate', 0.0),
        'resource_share_rate': workflow.get('resource_share_rate', 0.0),
        'bottleneck_relief_rate': workflow.get('bottleneck_relief_rate', 0.0),
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
    }


def run_context(seed, params, katalog, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    profile, key_overlap = build_profile(katalog, params, eintrag)
    base_contract = get_named(schema_profiles(katalog), 'balanced-contract')['config']
    config.update(profile)
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext.get('bootstrap_mode'):
        config['mission_switch_interval'] = 4
        config['workflow_stage_min_tenure'] = 1
        config['role_switch_interval'] = max(4, int(config.get('role_switch_interval', 4)))
        config['role_switch_min_tenure'] = min(
            max(2, int(config.get('role_switch_min_tenure', 2))),
            int(config['role_switch_interval']),
        )
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
    result['overlay_metrics'] = experiment_metrics(result)
    result['module_metrics'] = overlay_module_metrics(config, base_contract, eintrag, key_overlap)
    return result


def context_score(kontext_name, result, agent_count):
    metrics = result['overlay_metrics']
    module = result['module_metrics']
    base = metrics['consensus'] - metrics['polarization']
    recoveries = metrics['recovery_events_total'] / max(1.0, agent_count)
    failed_share = metrics['failed_agents_mean'] / max(1.0, agent_count)

    if kontext_name == 'bootstrap':
        return (
            metrics['completion_rate']
            + 0.12 * metrics['cross_group_cooperation']
            + 0.10 * metrics['meta_alignment_rate']
            + 0.12 * module['compatibility_score']
            + 0.12 * module['integration_score']
            + 0.10 * module['module_coverage']
            + 0.10 * module['startup_readiness']
            + 0.08 * module['rollback_safety']
            - 0.12 * module['side_effect_risk']
        )
    if kontext_name == 'consensus':
        return (
            metrics['consensus']
            + 0.18 * metrics['completion_rate']
            + 0.10 * metrics['resource_efficiency']
            + 0.10 * metrics['handoff_rate']
            + 0.12 * module['module_synergy']
            + 0.10 * module['compatibility_score']
            + 0.08 * module['integration_score']
            - 0.08 * module['side_effect_risk']
        )
    if kontext_name == 'stress':
        return (
            base
            + 0.16 * metrics['detection_rate']
            + 0.12 * metrics['trust_shield_mean']
            + 0.12 * module['safety_margin']
            + 0.10 * module['compatibility_score']
            + 0.08 * module['rollback_safety']
            - 0.14 * metrics['corruption_mean']
            - 0.10 * metrics['cluster_compromise_mean']
            - 0.12 * module['side_effect_risk']
        )
    return (
        base
        + 0.18 * metrics['sync_strength_mean']
        + 0.14 * recoveries
        + 0.14 * module['rollback_safety']
        + 0.10 * module['compatibility_score']
        + 0.10 * module['integration_score']
        - 0.12 * failed_share
        - 0.10 * metrics['cluster_compromise_mean']
        - 0.10 * module['side_effect_risk']
    )


def summarize_runs(runs, eintrag, context_list, agent_count):
    context_scores = {}
    metrics = {
        'completion_rate': {},
        'resource_efficiency': {},
        'handoff_rate': {},
        'detection_rate': {},
        'corruption_mean': {},
        'trust_shield_mean': {},
        'sync_strength_mean': {},
        'compatibility_score': {},
        'side_effect_risk': {},
        'module_coverage': {},
        'integration_score': {},
        'rollback_safety': {},
        'module_synergy': {},
    }

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name], agent_count) for run in runs])
        for metric_name in ['completion_rate', 'resource_efficiency', 'handoff_rate', 'detection_rate', 'corruption_mean', 'trust_shield_mean', 'sync_strength_mean']:
            metrics[metric_name][name] = mittelwert([run[name]['overlay_metrics'][metric_name] for run in runs])
        for metric_name in ['compatibility_score', 'side_effect_risk', 'module_coverage', 'integration_score', 'rollback_safety', 'module_synergy']:
            metrics[metric_name][name] = mittelwert([run[name]['module_metrics'][metric_name] for run in runs])

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
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
    eintraege = overlay_profiles()
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI OVERLAY-MODUL-STUDIE')
    print('=' * 84)
    print('Vergleicht, wie Zusatzfaehigkeiten als Overlay-Module ueber dem Bauvertrag')
    print('gekapselt werden koennen, ohne die gemeinsame DNA oder ihre Robustheit zu zerstoeren.\n')

    summaries = []
    for profil_index, eintrag in enumerate(eintraege):
        runs = []
        for repetition in range(params['repetitions']):
            repetition_seed = base_seed + profil_index * 100 + repetition
            run = {}
            for context_index, kontext in enumerate(context_list):
                run[kontext['name']] = run_context(
                    repetition_seed + context_index * 1000,
                    params,
                    katalog,
                    eintrag,
                    kontext,
                )
            runs.append(run)

        summary = summarize_runs(runs, eintrag, context_list, params['agent_count'])
        summaries.append(summary)
        print(
            f"{summary['label']:<28} Score={summary['combined_score']:+.3f} | "
            f"Kompat={summary['compatibility_score']['bootstrap']:.2f} | "
            f"Integration={summary['integration_score']['bootstrap']:.2f} | "
            f"Seiteneffekte={summary['side_effect_risk']['bootstrap']:.2f}"
        )

    best = max(summaries, key=lambda item: item['combined_score'])
    baseline = next(item for item in summaries if item['name'] == 'core-contract')

    print('\nBestes Overlay-Modulprofil:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zum reinen Bauvertrag {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Kompatibilitaet {best['compatibility_score']['bootstrap']:.2f}, "
        f"Integration {best['integration_score']['bootstrap']:.2f}, "
        f"Seiteneffekte {best['side_effect_risk']['bootstrap']:.2f}"
    )

    labels = [item['label'] for item in summaries]
    x = np.arange(len(labels))
    width = 0.35
    colors = ['#9aa0a6', '#f28e2b', '#4e79a7', '#59a14f', '#76b7b2', '#e15759']

    fig, axes = plt.subplots(2, 3, figsize=(19, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in summaries], color=colors)
    axes[0, 0].set_title('Kombinierter Overlay-Modul-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['compatibility_score']['bootstrap'] for item in summaries],
        width,
        label='Kompatibilitaet',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['side_effect_risk']['bootstrap'] for item in summaries],
        width,
        label='Seiteneffekte',
        color='#e15759',
    )
    axes[0, 1].set_title('Bauvertrag vs. Seiteneffekte')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['module_coverage']['bootstrap'] for item in summaries],
        width,
        label='Modulabdeckung',
        color='#76b7b2',
    )
    axes[0, 2].bar(
        x + width / 2,
        [item['integration_score']['bootstrap'] for item in summaries],
        width,
        label='Integration',
        color='#59a14f',
    )
    axes[0, 2].set_title('Overlay-Reichweite')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['context_scores']['bootstrap'],
                item['context_scores']['consensus'],
                item['context_scores']['stress'],
                item['context_scores']['recovery'],
                item['rollback_safety']['recovery'],
            ]
            for item in summaries
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Kontextprofil')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Boot', 'Kon', 'Stress', 'Rec', 'Rollback'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['detection_rate']['stress'] * 100.0 for item in summaries],
        width,
        label='Detektion (%)',
        color='#edc948',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['trust_shield_mean']['stress'] for item in summaries],
        width,
        label='Abschirmung',
        color='#b07aa1',
    )
    axes[1, 1].set_title('Stressabwehr')
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
            f"- Delta zum Bauvertrag: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Kompatibilitaet: {best['compatibility_score']['bootstrap']:.2f}\n"
            f"- Integration: {best['integration_score']['bootstrap']:.2f}\n"
            f"- Rollback-Sicherheit: {best['rollback_safety']['recovery']:.2f}\n"
            f"- Modulsynergie: {best['module_synergy']['consensus']:.2f}\n"
            f"- Stress-Detektion: {best['detection_rate']['stress']:.1%}\n"
            f"- Seiteneffekte: {best['side_effect_risk']['bootstrap']:.2f}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_overlay_module.png', dpi=150)


if __name__ == '__main__':
    main()
