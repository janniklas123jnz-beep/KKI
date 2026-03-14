"""
KKI Gruppenbildungs-Studie
==========================
Untersucht, ob aus starken Beziehungen, Rollen und Faehigkeitsmustern
emergente Proto-Gruppen und stabile Funktionsgruppen entstehen.
"""

from __future__ import annotations

import os
import random
from collections import Counter, defaultdict

import matplotlib.pyplot as plt
import numpy as np

from kki_runtime import DEFAULT_SEED, configure_matplotlib, is_test_mode, save_and_maybe_show
from schwarm_interaktionsmodelle import base_config as interaction_base_config
from schwarm_interaktionsmodelle import profile as interaction_profiles
from schwarm_polarisierung import (
    DEFAULT_AGENT_COUNT,
    DEFAULT_CONNECTIONS_PER_AGENT,
    DEFAULT_INTERACTIONS_PER_ROUND,
    DEFAULT_ROUNDS,
    run_polarization_experiment,
)


def studienparameter():
    if is_test_mode():
        repetitions = int(os.getenv('KKI_GROUP_FORMATION_REPETITIONS', '2'))
        rounds = min(DEFAULT_ROUNDS, int(os.getenv('KKI_TEST_ROUNDS', '6')))
        interactions = min(DEFAULT_INTERACTIONS_PER_ROUND, int(os.getenv('KKI_TEST_INTERACTIONS', '8')))
        attack_round = min(max(2, int(os.getenv('KKI_TEST_INVASION_ROUND', '3'))), rounds - 1)
    else:
        repetitions = int(os.getenv('KKI_GROUP_FORMATION_REPETITIONS', '3'))
        rounds = DEFAULT_ROUNDS
        interactions = DEFAULT_INTERACTIONS_PER_ROUND
        attack_round = int(os.getenv('KKI_INJECTION_ATTACK_ROUND', '90'))

    return {
        'repetitions': repetitions,
        'rounds': rounds,
        'interactions': interactions,
        'attack_round': attack_round,
        'agent_count': int(os.getenv('KKI_GROUP_FORMATION_AGENT_COUNT', str(DEFAULT_AGENT_COUNT))),
        'degree': int(os.getenv('KKI_NETWORK_DEGREE', str(DEFAULT_CONNECTIONS_PER_AGENT))),
        'bond_history_threshold': int(os.getenv('KKI_GROUP_BOND_HISTORY_THRESHOLD', '18')),
        'bond_trust_threshold': float(os.getenv('KKI_GROUP_BOND_TRUST_THRESHOLD', '0.76')),
        'proto_group_min_size': int(os.getenv('KKI_PROTO_GROUP_MIN_SIZE', '4')),
        'functional_group_min_size': int(os.getenv('KKI_FUNCTIONAL_GROUP_MIN_SIZE', '5')),
        'functional_alignment_threshold': float(os.getenv('KKI_FUNCTIONAL_ALIGNMENT_THRESHOLD', '0.60')),
        'group_opinion_distance_threshold': float(os.getenv('KKI_GROUP_OPINION_DISTANCE_THRESHOLD', '0.18')),
        'top_relationships_per_agent': int(os.getenv('KKI_GROUP_TOP_RELATIONSHIPS', '3')),
        'stress_strength': float(os.getenv('KKI_GROUP_FORMATION_STRESS_STRENGTH', '0.40')),
        'stress_sources': int(os.getenv('KKI_GROUP_FORMATION_STRESS_SOURCES', '6')),
    }


def mittelwert(values):
    return float(np.mean(values)) if values else 0.0


def modellkatalog(params):
    return {item['name']: item for item in interaction_profiles(params)}


def profile():
    return [
        {'name': 'homogen', 'label': 'Homogen', 'source_model': 'homogen'},
        {
            'name': 'beziehungsnetz',
            'label': 'Beziehungsnetz',
            'source_model': 'memory-enhanced',
            'overrides': {
                'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
                'analyzer_learning_multiplier': 1.26,
                'mediator_share': 0.22,
                'analyzer_share': 0.26,
                'enable_role_switching': False,
                'rewire_min_interactions': 5,
                'rewire_removal_probability': 0.18,
            },
        },
        {
            'name': 'proto-gruppen',
            'label': 'Proto-Gruppen',
            'source_model': 'adaptive-hybrid',
            'overrides': {
                'generalist_share': 0.10,
                'connector_share': 0.18,
                'sentinel_share': 0.18,
                'mediator_share': 0.24,
                'analyzer_share': 0.30,
                'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
                'analyzer_learning_multiplier': 1.24,
                'mediator_partner_bias': 0.88,
                'mediator_partner_distance': 0.36,
                'rewire_min_interactions': 5,
                'rewire_removal_probability': 0.18,
                'rewire_addition_probability': 0.78,
                'enable_role_switching': False,
            },
        },
        {
            'name': 'funktionsgruppen',
            'label': 'Funktionsgruppen',
            'source_model': 'adaptive-hybrid',
            'overrides': {
                'generalist_share': 0.08,
                'connector_share': 0.18,
                'sentinel_share': 0.20,
                'mediator_share': 0.24,
                'analyzer_share': 0.30,
                'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
                'analyzer_learning_multiplier': 1.28,
                'mediator_partner_bias': 0.90,
                'mediator_partner_distance': 0.38,
                'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.03,
                'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.05,
                'rewire_min_interactions': 5,
                'rewire_removal_probability': 0.16,
                'rewire_addition_probability': 0.80,
            },
        },
        {
            'name': 'resiliente-funktionsgruppen',
            'label': 'Resiliente Funktionsgruppen',
            'source_model': 'adaptive-hybrid',
            'overrides': {
                'generalist_share': 0.08,
                'connector_share': 0.16,
                'sentinel_share': 0.24,
                'mediator_share': 0.22,
                'analyzer_share': 0.30,
                'analyzer_memory_window': int(os.getenv('KKI_RELATIONSHIP_MEMORY_WINDOW', '42')),
                'analyzer_learning_multiplier': 1.30,
                'mediator_partner_bias': 0.88,
                'mediator_partner_distance': 0.36,
                'group_learning_rate': float(os.getenv('KKI_GROUP_LEARNING_RATE', '0.12')) + 0.04,
                'meta_priority_strength': float(os.getenv('KKI_META_PRIORITY_STRENGTH', '0.28')) + 0.07,
                'rewire_min_interactions': 5,
                'rewire_removal_probability': 0.14,
                'rewire_addition_probability': 0.80,
            },
        },
    ]


def kontexte():
    return [
        {'name': 'polarization', 'label': 'Polarisierung', 'scenario': 'polarization', 'enable_prompt_injection': False},
        {'name': 'consensus', 'label': 'Konsens', 'scenario': 'consensus', 'enable_prompt_injection': False},
        {'name': 'stress', 'label': 'Manipulationsstress', 'scenario': 'polarization', 'enable_prompt_injection': True},
    ]


def build_overrides(katalog, eintrag):
    basis = dict(katalog[eintrag['source_model']])
    overrides = {key: value for key, value in basis.items() if key not in {'name', 'label'}}
    overrides.update(eintrag.get('overrides', {}))
    return overrides


def components(graph):
    remaining = set(graph)
    result = []
    while remaining:
        start = remaining.pop()
        stack = [start]
        component = {start}
        while stack:
            node = stack.pop()
            for neighbor in graph[node]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        result.append(component)
    return result


def gruppenmetriken(agenten, params):
    agenten_dict = {agent.id: agent for agent in agenten}
    graph = {agent.id: set() for agent in agenten}
    bond_history_threshold = params['bond_history_threshold']
    bond_trust_threshold = params['bond_trust_threshold']
    top_relationships = max(1, params['top_relationships_per_agent'])

    candidate_scores = defaultdict(dict)
    candidate_trust = {}
    internal_trust_values = []
    external_trust_values = []

    for agent in agenten:
        for partner_id, history in agent.interaktions_history.items():
            if partner_id not in agenten_dict or agent.id >= partner_id:
                continue
            partner = agenten_dict[partner_id]
            partner_history = partner.interaktions_history.get(agent.id, [])
            mean_history_len = 0.5 * (len(history) + len(partner_history))
            mutual_trust = 0.5 * (
                agent.berechne_partner_reputation(partner_id)
                + partner.berechne_partner_reputation(agent.id)
            )
            opinion_distance = abs(agent.meinung - partner.meinung)
            if (
                mean_history_len >= bond_history_threshold
                and mutual_trust >= bond_trust_threshold
                and opinion_distance <= params['group_opinion_distance_threshold']
            ):
                score = mutual_trust - 0.35 * opinion_distance + 0.02 * mean_history_len / max(1, params['rounds'])
                candidate_scores[agent.id][partner_id] = score
                candidate_scores[partner_id][agent.id] = score
                candidate_trust[(min(agent.id, partner_id), max(agent.id, partner_id))] = mutual_trust

    top_neighbors = {
        agent_id: {
            partner_id
            for partner_id, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_relationships]
        }
        for agent_id, scores in candidate_scores.items()
    }

    strong_edge_count = 0
    for agent_id, partners in top_neighbors.items():
        for partner_id in partners:
            if agent_id < partner_id and agent_id in top_neighbors.get(partner_id, set()):
                graph[agent_id].add(partner_id)
                graph[partner_id].add(agent_id)
                strong_edge_count += 1

    group_components = [comp for comp in components(graph) if len(comp) >= params['proto_group_min_size']]
    functional_groups = []
    dominant_clusters = []
    dominant_skills = []

    for comp in group_components:
        members = [agenten_dict[aid] for aid in comp]
        cluster_counts = Counter(agent.capability_cluster for agent in members)
        skill_counts = Counter(agent.emergent_skill for agent in members)
        dominant_cluster, dominant_cluster_size = cluster_counts.most_common(1)[0]
        dominant_skill, dominant_skill_size = skill_counts.most_common(1)[0]
        cluster_alignment = dominant_cluster_size / len(members)
        skill_alignment = dominant_skill_size / len(members)
        alignment = min(cluster_alignment, skill_alignment)
        if (
            len(comp) >= params['functional_group_min_size']
            and alignment >= params['functional_alignment_threshold']
        ):
            functional_groups.append(comp)
            dominant_clusters.append(dominant_cluster)
            dominant_skills.append(dominant_skill)

    group_members = set().union(*group_components) if group_components else set()
    functional_members = set().union(*functional_groups) if functional_groups else set()

    for agent in agenten:
        for neighbor_id in graph[agent.id]:
            if agent.id >= neighbor_id:
                continue
            neighbor = agenten_dict[neighbor_id]
            trust = candidate_trust[(agent.id, neighbor_id)]
            same_proto_group = any(agent.id in comp and neighbor_id in comp for comp in group_components)
            if same_proto_group:
                internal_trust_values.append(trust)
            else:
                external_trust_values.append(trust)

    proto_group_share = len(group_members) / max(1, len(agenten))
    functional_group_share = len(functional_members) / max(1, len(agenten))
    return {
        'proto_group_count': len(group_components),
        'functional_group_count': len(functional_groups),
        'proto_group_share': proto_group_share,
        'functional_group_share': functional_group_share,
        'largest_group_share': max((len(comp) for comp in group_components), default=0) / max(1, len(agenten)),
        'strong_edge_rate': strong_edge_count / max(1, sum(len(agent.nachbarn) for agent in agenten) / 2),
        'internal_trust_mean': mittelwert(internal_trust_values),
        'external_trust_mean': mittelwert(external_trust_values),
        'group_separation': max(0.0, mittelwert(internal_trust_values) - mittelwert(external_trust_values)),
        'dominant_cluster_diversity': len(set(dominant_clusters)),
        'dominant_skill_diversity': len(set(dominant_skills)),
        'mean_component_size': mittelwert([len(comp) for comp in group_components]),
        'mean_functional_alignment': mittelwert(
            [
                max(
                    Counter(agenten_dict[aid].capability_cluster for aid in comp).most_common(1)[0][1] / len(comp),
                    Counter(agenten_dict[aid].emergent_skill for aid in comp).most_common(1)[0][1] / len(comp),
                )
                for comp in functional_groups
            ]
        ),
    }


def run_context(seed, params, katalog, eintrag, kontext):
    random.seed(seed)
    np.random.seed(seed)
    config = interaction_base_config(params, kontext['scenario'])
    config.update(build_overrides(katalog, eintrag))
    config['agent_count'] = params['agent_count']
    config['rounds'] = params['rounds']
    config['interactions_per_round'] = params['interactions']
    config['connections_per_agent'] = params['degree']
    config['rewire_target_degree'] = params['degree']

    if kontext['enable_prompt_injection']:
        config['enable_prompt_injection'] = True
        config['injection_attack_round'] = params['attack_round']
        config['injection_strength'] = params['stress_strength']
        config['injection_source_count'] = params['stress_sources']
    else:
        config['enable_prompt_injection'] = False

    result = run_polarization_experiment(config, make_plot=False, print_summary=False)
    result['group_metrics'] = gruppenmetriken(result['agents'], params)
    return result


def context_score(kontext_name, result):
    workflow = result['workflow_metrics']
    groups = result['group_metrics']
    base = result['final_consensus_score'] - result['final_polarization_index']
    proto_share = groups['proto_group_share']
    functional_share = groups['functional_group_share']
    separation = groups['group_separation']
    cluster_diversity = min(1.0, groups['dominant_cluster_diversity'] / 3.0)
    skill_diversity = min(1.0, groups['dominant_skill_diversity'] / 3.0)
    group_count_signal = min(1.0, groups['proto_group_count'] / 4.0)
    anti_monolith = 1.0 - groups['largest_group_share']
    strong_edge_rate = groups['strong_edge_rate']
    detection = workflow.get('misinformation_detection_rate', 0.0)
    corruption = workflow.get('misinformation_corruption_mean', 0.0)

    if kontext_name == 'polarization':
        return (
            base
            + 0.14 * proto_share
            + 0.18 * functional_share
            + 0.14 * separation
            + 0.08 * cluster_diversity
            + 0.10 * group_count_signal
            + 0.08 * anti_monolith
        )
    if kontext_name == 'consensus':
        return (
            result['final_consensus_score']
            + 0.12 * proto_share
            + 0.16 * functional_share
            + 0.10 * strong_edge_rate
            + 0.08 * skill_diversity
            + 0.06 * anti_monolith
        )
    return (
        base
        + 0.14 * functional_share
        + 0.10 * separation
        + 0.08 * detection
        - 0.10 * corruption
        + 0.06 * cluster_diversity
        + 0.06 * anti_monolith
    )


def summarize_runs(runs, eintrag, context_list):
    context_scores = {}
    proto_shares = {}
    functional_shares = {}
    separations = {}
    cluster_diversities = {}
    skill_diversities = {}
    stress_detection = {}
    stress_corruption = {}

    for kontext in context_list:
        name = kontext['name']
        context_scores[name] = mittelwert([context_score(name, run[name]) for run in runs])
        proto_shares[name] = mittelwert([run[name]['group_metrics']['proto_group_share'] for run in runs])
        functional_shares[name] = mittelwert([run[name]['group_metrics']['functional_group_share'] for run in runs])
        separations[name] = mittelwert([run[name]['group_metrics']['group_separation'] for run in runs])
        cluster_diversities[name] = mittelwert(
            [run[name]['group_metrics']['dominant_cluster_diversity'] for run in runs]
        )
        skill_diversities[name] = mittelwert(
            [run[name]['group_metrics']['dominant_skill_diversity'] for run in runs]
        )
        stress_detection[name] = mittelwert(
            [run[name]['workflow_metrics'].get('misinformation_detection_rate', 0.0) for run in runs]
        )
        stress_corruption[name] = mittelwert(
            [run[name]['workflow_metrics'].get('misinformation_corruption_mean', 0.0) for run in runs]
        )

    return {
        'name': eintrag['name'],
        'label': eintrag['label'],
        'combined_score': mittelwert(
            [sum(context_score(kontext['name'], run[kontext['name']]) for kontext in context_list) for run in runs]
        ),
        'context_scores': context_scores,
        'proto_shares': proto_shares,
        'functional_shares': functional_shares,
        'separations': separations,
        'cluster_diversities': cluster_diversities,
        'skill_diversities': skill_diversities,
        'stress_detection': stress_detection,
        'stress_corruption': stress_corruption,
    }


def main():
    configure_matplotlib(plt)
    params = studienparameter()
    katalog = modellkatalog(params)
    eintraege = profile()
    context_list = kontexte()
    base_seed = int(os.getenv('KKI_SEED', str(DEFAULT_SEED)))

    print('=' * 84)
    print('KKI GRUPPENBILDUNGS-STUDIE')
    print('=' * 84)
    print('Untersucht, wann aus starken Beziehungsgraphen emergente Proto-Gruppen und')
    print('stabile Funktionsgruppen ohne feste Vorabzuweisung entstehen.\n')

    zusammenfassungen = []
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

        summary = summarize_runs(runs, eintrag, context_list)
        zusammenfassungen.append(summary)
        print(
            f"{summary['label']:<30} Score={summary['combined_score']:+.3f} | "
            f"Proto={summary['proto_shares']['polarization']:.1%} | "
            f"Funktional={summary['functional_shares']['polarization']:.1%} | "
            f"Stress-Detektion={summary['stress_detection']['stress']:.1%}"
        )

    best = max(zusammenfassungen, key=lambda item: item['combined_score'])
    baseline = next(item for item in zusammenfassungen if item['name'] == 'homogen')

    print('\nBeste Gruppenarchitektur:', best['label'])
    print(
        f"Score {best['combined_score']:+.3f} | "
        f"Delta zur Homogenitaet {best['combined_score'] - baseline['combined_score']:+.3f}"
    )
    print(
        f"Proto-Gruppen {best['proto_shares']['polarization']:.1%}, "
        f"Funktionsgruppen {best['functional_shares']['polarization']:.1%}, "
        f"Gruppenseparation {best['separations']['polarization']:.2f}"
    )

    labels = [item['label'] for item in zusammenfassungen]
    x = np.arange(len(labels))
    colors = ['#9aa0a6', '#4e79a7', '#f28e2b', '#59a14f', '#e15759']
    width = 0.35

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    axes[0, 0].bar(x, [item['combined_score'] for item in zusammenfassungen], color=colors)
    axes[0, 0].set_title('Kombinierter Gruppen-Score')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(labels, rotation=18)
    axes[0, 0].grid(True, axis='y', alpha=0.3)

    axes[0, 1].bar(
        x - width / 2,
        [item['proto_shares']['polarization'] * 100.0 for item in zusammenfassungen],
        width,
        label='Proto-Gruppen (%)',
        color='#4e79a7',
    )
    axes[0, 1].bar(
        x + width / 2,
        [item['functional_shares']['polarization'] * 100.0 for item in zusammenfassungen],
        width,
        label='Funktionsgruppen (%)',
        color='#59a14f',
    )
    axes[0, 1].set_title('Gruppenbildung unter Polarisierung')
    axes[0, 1].set_xticks(x)
    axes[0, 1].set_xticklabels(labels, rotation=18)
    axes[0, 1].legend()
    axes[0, 1].grid(True, axis='y', alpha=0.3)

    axes[0, 2].bar(
        x - width / 2,
        [item['stress_detection']['stress'] * 100.0 for item in zusammenfassungen],
        width,
        label='Detektion (%)',
        color='#f28e2b',
    )
    axes[0, 2].bar(
        x + width / 2,
        [(1.0 - item['stress_corruption']['stress']) * 100.0 for item in zusammenfassungen],
        width,
        label='Integritaet (%)',
        color='#76b7b2',
    )
    axes[0, 2].set_title('Stressrobustheit')
    axes[0, 2].set_xticks(x)
    axes[0, 2].set_xticklabels(labels, rotation=18)
    axes[0, 2].legend()
    axes[0, 2].grid(True, axis='y', alpha=0.3)

    heatmap_data = np.array(
        [
            [
                item['proto_shares']['polarization'],
                item['functional_shares']['polarization'],
                item['separations']['polarization'],
                item['cluster_diversities']['consensus'],
                item['skill_diversities']['consensus'],
            ]
            for item in zusammenfassungen
        ],
        dtype=float,
    )
    heatmap = axes[1, 0].imshow(heatmap_data, cmap='viridis', aspect='auto')
    axes[1, 0].set_title('Gruppenmetriken')
    axes[1, 0].set_xticks([0, 1, 2, 3, 4])
    axes[1, 0].set_xticklabels(['Proto', 'Funktion', 'Sep', 'Cluster', 'Skill'])
    axes[1, 0].set_yticks(range(len(labels)))
    axes[1, 0].set_yticklabels(labels)
    for row in range(heatmap_data.shape[0]):
        for col in range(heatmap_data.shape[1]):
            axes[1, 0].text(col, row, f'{heatmap_data[row, col]:.2f}', ha='center', va='center', fontsize=8)
    fig.colorbar(heatmap, ax=axes[1, 0], fraction=0.046, pad=0.04)

    axes[1, 1].bar(
        x - width / 2,
        [item['context_scores']['consensus'] for item in zusammenfassungen],
        width,
        label='Konsens',
        color='#59a14f',
    )
    axes[1, 1].bar(
        x + width / 2,
        [item['context_scores']['stress'] for item in zusammenfassungen],
        width,
        label='Stress',
        color='#e15759',
    )
    axes[1, 1].set_title('Kontextvergleich')
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
            f"- Beste Architektur: {best['label']}\n"
            f"- Delta zur Homogenitaet: {best['combined_score'] - baseline['combined_score']:+.3f}\n"
            f"- Proto-Gruppen: {best['proto_shares']['polarization']:.1%}\n"
            f"- Funktionsgruppen: {best['functional_shares']['polarization']:.1%}\n"
            f"- Separation: {best['separations']['polarization']:.2f}\n"
            f"- Cluster-Diversitaet: {best['cluster_diversities']['consensus']:.2f}\n"
            f"- Skill-Diversitaet: {best['skill_diversities']['consensus']:.2f}\n"
            f"- Stress-Detektion: {best['stress_detection']['stress']:.1%}"
        ),
        va='top',
        fontsize=10,
    )

    fig.tight_layout()
    save_and_maybe_show(plt, 'kki_gruppenbildung.png', dpi=150)


if __name__ == '__main__':
    main()
