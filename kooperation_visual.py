"""
KKI Proof-of-Concept: Kooperation mit Visualisierung
=====================================================
Erweiterte Version mit matplotlib-Graphen
"""

import random
import matplotlib.pyplot as plt

# === KONFIGURATION ===
RUNDEN = 100
LERNRATE = 0.1

# Payoff-Matrix (Gefangenendilemma)
PAYOFFS = {
    ('C', 'C'): 3,  # Beide kooperieren
    ('C', 'D'): 0,  # Ich kooperiere, anderer defektiert
    ('D', 'C'): 5,  # Ich defektiere, anderer kooperiert
    ('D', 'D'): 1,  # Beide defektieren
}


class Agent:
    """Ein einfacher lernender Agent."""
    
    def __init__(self, name, farbe):
        self.name = name
        self.farbe = farbe  # Für den Graphen
        self.kooperations_neigung = 0.5
        self.intelligenz = 1.0
        # History für Visualisierung
        self.intelligenz_history = [1.0]
        self.kooperation_history = [0.5]
    
    def waehle_aktion(self):
        """Wähle C (Kooperation) oder D (Defektion)."""
        if random.random() < self.kooperations_neigung:
            return 'C'
        return 'D'
    
    def lerne(self, meine_aktion, andere_aktion, payoff):
        """Passe Verhalten basierend auf Erfahrung an."""
        if meine_aktion == 'C' and andere_aktion == 'C':
            self.intelligenz *= 1.02
            self.kooperations_neigung += LERNRATE * 0.1
        elif meine_aktion == 'D':
            self.intelligenz *= 0.98
            
        self.kooperations_neigung = max(0.1, min(0.9, self.kooperations_neigung))
        
        # Speichere für Graph
        self.intelligenz_history.append(self.intelligenz)
        self.kooperation_history.append(self.kooperations_neigung)


def simulation():
    """Führe Simulation durch und zeige Graphen."""
    agent_a = Agent("Alpha", "#E74C3C")  # Rot
    agent_b = Agent("Beta", "#3498DB")   # Blau
    
    aktionen_history = []  # Für Hintergrundfarben
    
    print("=== KKI Kooperations-Simulation ===\n")
    
    for runde in range(1, RUNDEN + 1):
        aktion_a = agent_a.waehle_aktion()
        aktion_b = agent_b.waehle_aktion()
        
        # Speichere Aktionen für Visualisierung
        if aktion_a == 'C' and aktion_b == 'C':
            aktionen_history.append('CC')  # Beide kooperieren
        elif aktion_a == 'D' and aktion_b == 'D':
            aktionen_history.append('DD')  # Beide defektieren
        else:
            aktionen_history.append('CD')  # Gemischt
        
        payoff_a = PAYOFFS[(aktion_a, aktion_b)]
        payoff_b = PAYOFFS[(aktion_b, aktion_a)]
        
        agent_a.lerne(aktion_a, aktion_b, payoff_a)
        agent_b.lerne(aktion_b, aktion_a, payoff_b)
    
    # === VISUALISIERUNG ===
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    fig.suptitle('KKI: Emergenz von Kooperation durch Intelligenz-Kopplung', 
                 fontsize=14, fontweight='bold')
    
    runden = list(range(RUNDEN + 1))
    
    # --- Graph 1: Intelligenz über Zeit ---
    ax1.set_ylabel('Intelligenz (Φ)', fontsize=11)
    ax1.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5, label='Startwert')
    
    # Hintergrund: Grün wenn CC, Rot wenn DD, Gelb wenn gemischt
    for i, aktion in enumerate(aktionen_history):
        if aktion == 'CC':
            ax1.axvspan(i, i+1, alpha=0.15, color='green')
        elif aktion == 'DD':
            ax1.axvspan(i, i+1, alpha=0.15, color='red')
    
    ax1.plot(runden, agent_a.intelligenz_history, 
             color=agent_a.farbe, linewidth=2, label=f'{agent_a.name}')
    ax1.plot(runden, agent_b.intelligenz_history, 
             color=agent_b.farbe, linewidth=2, label=f'{agent_b.name}')
    
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0.5, max(agent_a.intelligenz, agent_b.intelligenz) * 1.1)
    
    # --- Graph 2: Kooperationsneigung über Zeit ---
    ax2.set_xlabel('Runde', fontsize=11)
    ax2.set_ylabel('Kooperationsneigung', fontsize=11)
    ax2.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Startwert')
    
    ax2.plot(runden, agent_a.kooperation_history, 
             color=agent_a.farbe, linewidth=2, label=f'{agent_a.name}')
    ax2.plot(runden, agent_b.kooperation_history, 
             color=agent_b.farbe, linewidth=2, label=f'{agent_b.name}')
    
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 1)
    
    # Beschriftung
    ax2.text(RUNDEN * 0.7, 0.15, 
             f'Finale Intelligenz:\n{agent_a.name}: {agent_a.intelligenz:.2f}\n{agent_b.name}: {agent_b.intelligenz:.2f}',
             fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Speichern und anzeigen
    plt.savefig('kki_kooperation_graph.png', dpi=150)
    print("Graph gespeichert: kki_kooperation_graph.png")
    plt.show()
    
    # Ergebnis
    print(f"\n=== ERGEBNIS ===")
    print(f"Alpha: Kooperationsneigung = {agent_a.kooperations_neigung:.1%}, "
          f"Finale Intelligenz = {agent_a.intelligenz:.2f}")
    print(f"Beta:  Kooperationsneigung = {agent_b.kooperations_neigung:.1%}, "
          f"Finale Intelligenz = {agent_b.intelligenz:.2f}")


if __name__ == "__main__":
    simulation()
