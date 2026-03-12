"""
KKI Proof-of-Concept: Zwei Agenten lernen Kooperation
======================================================
Dieses Skript demonstriert die Grundidee aus Sektion VIII:
Agenten, die kooperieren, erhalten höhere "Intelligenz-Punkte".
"""

import random

# === KONFIGURATION ===
RUNDEN = 100
LERNRATE = 0.1

# Payoff-Matrix (Gefangenendilemma)
# (meine_aktion, andere_aktion) -> mein_payoff
PAYOFFS = {
    ('C', 'C'): 3,  # Beide kooperieren: gut für beide
    ('C', 'D'): 0,  # Ich kooperiere, anderer defektiert: schlecht für mich
    ('D', 'C'): 5,  # Ich defektiere, anderer kooperiert: kurzfristig super
    ('D', 'D'): 1,  # Beide defektieren: schlecht für beide
}


class Agent:
    """Ein einfacher lernender Agent."""
    
    def __init__(self, name):
        self.name = name
        self.kooperations_neigung = 0.5  # Start: 50% Kooperation
        self.intelligenz = 1.0  # Startwert
        self.punkte_history = []
    
    def waehle_aktion(self):
        """Wähle C (Kooperation) oder D (Defektion)."""
        if random.random() < self.kooperations_neigung:
            return 'C'
        return 'D'
    
    def lerne(self, meine_aktion, andere_aktion, payoff):
        """Passe Kooperationsneigung basierend auf Erfahrung an."""
        # Kernidee: Intelligenz hängt von Kooperation ab!
        if meine_aktion == 'C' and andere_aktion == 'C':
            # Gegenseitige Kooperation erhöht Intelligenz
            self.intelligenz *= 1.02
            self.kooperations_neigung += LERNRATE * 0.1
        elif meine_aktion == 'D':
            # Defektion reduziert Intelligenz (der Kern unserer Theorie!)
            self.intelligenz *= 0.98
            
        # Begrenze Werte
        self.kooperations_neigung = max(0.1, min(0.9, self.kooperations_neigung))
        
        # Speichere für Analyse
        self.punkte_history.append(payoff * self.intelligenz)


def simulation():
    """Führe die Simulation durch."""
    agent_a = Agent("Alpha")
    agent_b = Agent("Beta")
    
    print("=== KKI Kooperations-Simulation ===\n")
    print(f"{'Runde':>6} | {'Alpha':>8} | {'Beta':>8} | {'A-Intell':>8} | {'B-Intell':>8}")
    print("-" * 50)
    
    for runde in range(1, RUNDEN + 1):
        # Beide wählen gleichzeitig
        aktion_a = agent_a.waehle_aktion()
        aktion_b = agent_b.waehle_aktion()
        
        # Payoffs berechnen
        payoff_a = PAYOFFS[(aktion_a, aktion_b)]
        payoff_b = PAYOFFS[(aktion_b, aktion_a)]
        
        # Lernen
        agent_a.lerne(aktion_a, aktion_b, payoff_a)
        agent_b.lerne(aktion_b, aktion_a, payoff_b)
        
        # Ausgabe alle 10 Runden
        if runde % 10 == 0:
            print(f"{runde:>6} | {aktion_a:>8} | {aktion_b:>8} | "
                  f"{agent_a.intelligenz:>8.2f} | {agent_b.intelligenz:>8.2f}")
    
    print("\n=== ERGEBNIS ===")
    print(f"Alpha: Kooperationsneigung = {agent_a.kooperations_neigung:.1%}, "
          f"Finale Intelligenz = {agent_a.intelligenz:.2f}")
    print(f"Beta:  Kooperationsneigung = {agent_b.kooperations_neigung:.1%}, "
          f"Finale Intelligenz = {agent_b.intelligenz:.2f}")
    
    if agent_a.intelligenz > 1.0 and agent_b.intelligenz > 1.0:
        print("\n✓ Kooperation hat sich durchgesetzt!")
        print("  → Die Agenten haben 'gelernt', dass Kooperation ihre Intelligenz erhöht.")
    else:
        print("\n✗ Defektion hat dominiert - Intelligenz ist kollabiert.")


if __name__ == "__main__":
    simulation()
