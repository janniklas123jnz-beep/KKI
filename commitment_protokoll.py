"""
KKI Commitment-Protokoll: Kryptografische Verifikation von Kooperation
=======================================================================
Implementiert das Protokoll aus Sektion VIII:
- Phase 1: Commit (Hash der geplanten Aktion)
- Phase 2: Reveal (Aktion offenlegen)
- Phase 3: Verifikation (Manipulation erkennen)

Agenten können nicht mehr lügen, ohne entdeckt zu werden!
"""

import random
import hashlib
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Tuple

from kki_runtime import (
    apply_test_overrides,
    configure_matplotlib,
    initialize_runtime,
    save_and_maybe_show,
)

configure_matplotlib(plt)

# === KONFIGURATION ===
ANZAHL_AGENTEN = 50
ANZAHL_MANIPULATOREN = 8  # Agenten die versuchen zu betrügen
RUNDEN = 200
INTERAKTIONEN_PRO_RUNDE = 100
TEST_OVERRIDES = apply_test_overrides({
    'RUNDEN': RUNDEN,
    'INTERAKTIONEN_PRO_RUNDE': INTERAKTIONEN_PRO_RUNDE,
})
RUNDEN = TEST_OVERRIDES['RUNDEN']
INTERAKTIONEN_PRO_RUNDE = TEST_OVERRIDES['INTERAKTIONEN_PRO_RUNDE']
SEED = initialize_runtime(np)

PAYOFFS = {
    ('C', 'C'): 3,
    ('C', 'D'): 0,
    ('D', 'C'): 5,
    ('D', 'D'): 1,
}


@dataclass
class Commitment:
    """Ein kryptografisches Commitment."""
    hash_wert: str
    nonce: str
    aktion: Optional[str] = None  # Wird beim Reveal gesetzt
    
    @staticmethod
    def erstelle(aktion: str) -> 'Commitment':
        """Erstelle ein Commitment für eine Aktion."""
        nonce = hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]
        hash_wert = hashlib.sha256(f"{aktion}:{nonce}".encode()).hexdigest()
        return Commitment(hash_wert=hash_wert, nonce=nonce, aktion=None)
    
    def reveal(self, aktion: str) -> bool:
        """Offenbare die Aktion und prüfe Konsistenz."""
        erwarteter_hash = hashlib.sha256(f"{aktion}:{self.nonce}".encode()).hexdigest()
        self.aktion = aktion
        return erwarteter_hash == self.hash_wert
    
    def verifiziere(self, behauptete_aktion: str) -> bool:
        """Verifiziere ob die behauptete Aktion zum Commitment passt."""
        erwarteter_hash = hashlib.sha256(f"{behauptete_aktion}:{self.nonce}".encode()).hexdigest()
        return erwarteter_hash == self.hash_wert


class Agent:
    """Agent mit Commitment-Protokoll Support."""
    
    def __init__(self, id: int, ist_manipulator: bool = False):
        self.id = id
        self.name = f"M{id}" if ist_manipulator else f"A{id}"
        self.ist_manipulator = ist_manipulator
        self.kooperations_neigung = 0.5
        self.intelligenz = 1.0
        self.reputation = 0.5
        
        # Manipulation-Tracking
        self.manipulations_versuche = 0
        self.erwischt_count = 0
        self.erfolgreiche_manipulationen = 0  # Sollte bei Commitment-Protokoll 0 sein!
        
        # Vertrauens-Netzwerk
        self.vertrauen = defaultdict(lambda: 0.5)  # Partner-ID -> Vertrauenswert
        self.interaktions_history = defaultdict(list)
        
        # Tracking
        self.intelligenz_history = [1.0]
        self.reputation_history = [0.5]
        self.erwischt_history = [0]
    
    def plane_aktion(self, partner_vertrauen: float) -> Tuple[str, Commitment]:
        """
        Phase 1: Plane Aktion und erstelle Commitment.
        Manipulatoren planen manchmal zu betrügen.
        """
        # Basis-Entscheidung
        if random.random() < self.kooperations_neigung:
            geplante_aktion = 'C'
        else:
            geplante_aktion = 'D'
        
        # Manipulatoren könnten versuchen zu betrügen
        self.will_manipulieren = False
        if self.ist_manipulator and random.random() < 0.3:  # 30% Manipulationsversuch
            self.will_manipulieren = True
            self.manipulations_versuche += 1
        
        # Erstelle Commitment für die ECHTE geplante Aktion
        commitment = Commitment.erstelle(geplante_aktion)
        return geplante_aktion, commitment
    
    def fuehre_aus_und_reveal(self, geplante_aktion: str, commitment: Commitment, 
                               partner_aktion_sichtbar: bool = False) -> Tuple[str, bool]:
        """
        Phase 2: Führe Aktion aus und offenbare.
        Manipulatoren könnten versuchen, eine andere Aktion zu behaupten.
        """
        tatsaechliche_aktion = geplante_aktion
        
        # Manipulator versucht zu betrügen?
        if self.will_manipulieren:
            # Versuche die "bessere" Aktion zu behaupten
            if geplante_aktion == 'C':
                behauptete_aktion = 'D'  # Behaupte Defektion um auszunutzen
            else:
                behauptete_aktion = 'C'  # Behaupte Kooperation um Reputation zu behalten
            
            # ABER: Das Commitment-Protokoll macht das unmöglich!
            ist_konsistent = commitment.verifiziere(behauptete_aktion)
            
            if not ist_konsistent:
                # ERWISCHT! Manipulation fehlgeschlagen
                self.erwischt_count += 1
                return geplante_aktion, False  # Muss echte Aktion verwenden, wurde erwischt
            else:
                # Theoretisch unmöglich bei korrektem Protokoll
                self.erfolgreiche_manipulationen += 1
                return behauptete_aktion, True
        
        return tatsaechliche_aktion, True
    
    def lerne(self, meine_aktion: str, partner_aktion: str, partner_id: int,
              partner_intelligenz: float, ich_wurde_erwischt: bool, partner_wurde_erwischt: bool):
        """Lerne aus der Interaktion mit Commitment-Konsequenzen."""
        
        self.interaktions_history[partner_id].append(partner_aktion)
        
        # Erwischt werden hat SCHWERE Konsequenzen
        if ich_wurde_erwischt:
            self.intelligenz *= 0.85  # Massiver Intelligenz-Verlust!
            self.reputation -= 0.15
            self.kooperations_neigung += 0.02  # Lerne, nicht zu manipulieren
        
        # Partner erwischt = Vertrauen in Partner sinkt
        if partner_wurde_erwischt:
            self.vertrauen[partner_id] *= 0.5
        
        # Normale Lernregeln
        if not ich_wurde_erwischt:
            if meine_aktion == 'C' and partner_aktion == 'C':
                synergie = 1.0 + (partner_intelligenz * 0.003)
                self.intelligenz *= 1.003 * synergie
                self.kooperations_neigung += 0.004
                self.reputation += 0.01
                self.vertrauen[partner_id] += 0.02
                
            elif meine_aktion == 'C' and partner_aktion == 'D':
                self.kooperations_neigung -= 0.002
                self.vertrauen[partner_id] -= 0.05
                
            elif meine_aktion == 'D' and partner_aktion == 'C':
                self.intelligenz *= 0.997
                self.reputation -= 0.015
                
            elif meine_aktion == 'D' and partner_aktion == 'D':
                self.intelligenz *= 0.99
                self.kooperations_neigung += 0.003
        
        # Grenzen
        self.kooperations_neigung = max(0.05, min(0.95, self.kooperations_neigung))
        self.intelligenz = max(0.1, min(6.0, self.intelligenz))
        self.reputation = max(0.0, min(1.0, self.reputation))
        self.vertrauen[partner_id] = max(0.0, min(1.0, self.vertrauen[partner_id]))
    
    def runde_beenden(self):
        self.intelligenz_history.append(self.intelligenz)
        self.reputation_history.append(self.reputation)
        self.erwischt_history.append(self.erwischt_count)


def simulation():
    """Simulation mit Commitment-Protokoll."""
    
    # Erstelle Agenten
    alle_ids = list(range(ANZAHL_AGENTEN))
    random.shuffle(alle_ids)
    manipulator_ids = set(alle_ids[:ANZAHL_MANIPULATOREN])
    
    agenten = []
    for i in range(ANZAHL_AGENTEN):
        ist_manipulator = i in manipulator_ids
        agent = Agent(i, ist_manipulator)
        agenten.append(agent)
    
    agenten_dict = {a.id: a for a in agenten}
    
    print("=" * 75)
    print("KKI COMMITMENT-PROTOKOLL: KRYPTOGRAFISCHE KOOPERATIONS-VERIFIKATION")
    print("=" * 75)
    print(f"\nAgenten: {ANZAHL_AGENTEN} (davon {ANZAHL_MANIPULATOREN} Manipulatoren)")
    print(f"Runden: {RUNDEN}")
    print(f"\nDas Protokoll macht Manipulation UNMÖGLICH - Manipulatoren werden IMMER erwischt!")
    print("\nSimulation läuft...\n")
    
    # Tracking
    schwarm_phi_history = []
    normale_phi_history = []
    manipulator_phi_history = []
    erwischt_pro_runde = []
    manipulations_versuche_total = []
    
    for runde in range(1, RUNDEN + 1):
        runden_erwischt = 0
        
        for _ in range(INTERAKTIONEN_PRO_RUNDE):
            # Wähle zwei Agenten
            a1, a2 = random.sample(agenten, 2)
            
            # === COMMITMENT-PROTOKOLL ===
            
            # Phase 1: Beide planen und committen
            aktion1_geplant, commitment1 = a1.plane_aktion(a1.vertrauen[a2.id])
            aktion2_geplant, commitment2 = a2.plane_aktion(a2.vertrauen[a1.id])
            
            # Phase 2: Beide revealn (Manipulatoren könnten versuchen zu betrügen)
            aktion1_final, a1_ok = a1.fuehre_aus_und_reveal(aktion1_geplant, commitment1)
            aktion2_final, a2_ok = a2.fuehre_aus_und_reveal(aktion2_geplant, commitment2)
            
            a1_erwischt = not a1_ok
            a2_erwischt = not a2_ok
            
            if a1_erwischt:
                runden_erwischt += 1
            if a2_erwischt:
                runden_erwischt += 1
            
            # Phase 3: Lernen mit Konsequenzen
            a1.lerne(aktion1_final, aktion2_final, a2.id, a2.intelligenz, a1_erwischt, a2_erwischt)
            a2.lerne(aktion2_final, aktion1_final, a1.id, a1.intelligenz, a2_erwischt, a1_erwischt)
        
        # Runde beenden
        for agent in agenten:
            agent.runde_beenden()
        
        # Statistiken
        normale = [a for a in agenten if not a.ist_manipulator]
        manipulatoren = [a for a in agenten if a.ist_manipulator]
        
        schwarm_phi = np.mean([a.intelligenz for a in agenten])
        normale_phi = np.mean([a.intelligenz for a in normale])
        manipulator_phi = np.mean([a.intelligenz for a in manipulatoren])
        
        schwarm_phi_history.append(schwarm_phi)
        normale_phi_history.append(normale_phi)
        manipulator_phi_history.append(manipulator_phi)
        erwischt_pro_runde.append(runden_erwischt)
        
        total_versuche = sum(a.manipulations_versuche for a in manipulatoren)
        manipulations_versuche_total.append(total_versuche)
        
        if runde % 40 == 0:
            total_erwischt = sum(a.erwischt_count for a in manipulatoren)
            print(f"Runde {runde:3d}: Schwarm-Φ={schwarm_phi:.2f}, "
                  f"Normale={normale_phi:.2f}, Manipulatoren={manipulator_phi:.2f}, "
                  f"Erwischt={total_erwischt}")
    
    # === ERGEBNISSE ===
    print("\n" + "=" * 75)
    print("FINALE ERGEBNISSE: COMMITMENT-PROTOKOLL ANALYSE")
    print("=" * 75)
    
    normale = [a for a in agenten if not a.ist_manipulator]
    manipulatoren = [a for a in agenten if a.ist_manipulator]
    
    total_versuche = sum(a.manipulations_versuche for a in manipulatoren)
    total_erwischt = sum(a.erwischt_count for a in manipulatoren)
    total_erfolg = sum(a.erfolgreiche_manipulationen for a in manipulatoren)
    
    print(f"\n{'=== MANIPULATIONS-STATISTIK ==='}")
    print(f"Manipulationsversuche gesamt:     {total_versuche}")
    print(f"Davon ERWISCHT:                   {total_erwischt} ({total_erwischt/max(1,total_versuche)*100:.1f}%)")
    print(f"Erfolgreiche Manipulationen:      {total_erfolg}")
    
    if total_erfolg == 0:
        print(f"\n🔐 COMMITMENT-PROTOKOLL 100% EFFEKTIV!")
        print(f"   Keine einzige Manipulation war erfolgreich!")
    
    print(f"\n{'=== INTELLIGENZ-VERGLEICH ==='}")
    avg_normale = np.mean([a.intelligenz for a in normale])
    avg_manip = np.mean([a.intelligenz for a in manipulatoren])
    
    print(f"{'Gruppe':<25} {'Anzahl':>10} {'Ø Intelligenz':>15} {'Ø Reputation':>15}")
    print("-" * 70)
    print(f"{'Normale Agenten':<25} {len(normale):>10} {avg_normale:>15.2f} "
          f"{np.mean([a.reputation for a in normale]):>15.2f}")
    print(f"{'Manipulatoren':<25} {len(manipulatoren):>10} {avg_manip:>15.2f} "
          f"{np.mean([a.reputation for a in manipulatoren]):>15.2f}")
    print(f"\nDifferenz Intelligenz: {avg_normale - avg_manip:.2f}")
    
    # Top & Bottom
    sortiert = sorted(agenten, key=lambda a: a.intelligenz, reverse=True)
    
    print(f"\n{'=== TOP 5 AGENTEN ==='}")
    for agent in sortiert[:5]:
        typ = "MANIPULATOR" if agent.ist_manipulator else "Normal"
        print(f"  {agent.name}: Φ={agent.intelligenz:.2f}, Rep={agent.reputation:.2f}, Typ={typ}")
    
    print(f"\n{'=== BOTTOM 5 AGENTEN ==='}")
    for agent in sortiert[-5:]:
        typ = "MANIPULATOR" if agent.ist_manipulator else "Normal"
        erwischt = agent.erwischt_count
        print(f"  {agent.name}: Φ={agent.intelligenz:.2f}, Rep={agent.reputation:.2f}, "
              f"Typ={typ}, Erwischt={erwischt}x")
    
    # Analyse: Sind alle Manipulatoren unten?
    bottom_10 = sortiert[-10:]
    manip_in_bottom = sum(1 for a in bottom_10 if a.ist_manipulator)
    print(f"\nManiputoren in Bottom 10: {manip_in_bottom}/{ANZAHL_MANIPULATOREN}")
    
    if avg_normale > avg_manip * 1.5 and total_erfolg == 0:
        print("\n🐝🔐 VOLLSTÄNDIGER ERFOLG!")
        print("    Das Commitment-Protokoll hat ALLE Manipulationen verhindert")
        print("    UND Manipulatoren wurden durch Erwischt-Werden marginalisiert!")
    
    # === VISUALISIERUNG ===
    fig = plt.figure(figsize=(18, 12))
    
    ax1 = fig.add_subplot(2, 3, 1)
    ax2 = fig.add_subplot(2, 3, 2)
    ax3 = fig.add_subplot(2, 3, 3)
    ax4 = fig.add_subplot(2, 3, 4)
    ax5 = fig.add_subplot(2, 3, 5)
    ax6 = fig.add_subplot(2, 3, 6)
    
    fig.suptitle('KKI Commitment-Protokoll: Kryptografische Manipulations-Verhinderung', 
                 fontsize=14, fontweight='bold')
    
    runden_x = list(range(RUNDEN + 1))
    
    # --- Graph 1: Intelligenz-Verläufe ---
    ax1.set_title('Individuelle Intelligenz')
    ax1.set_ylabel('Intelligenz (Φ)')
    ax1.set_xlabel('Runde')
    
    for agent in agenten:
        color = '#E74C3C' if agent.ist_manipulator else '#3498DB'
        alpha = 0.7 if agent.ist_manipulator else 0.25
        linewidth = 1.5 if agent.ist_manipulator else 0.5
        linestyle = '--' if agent.ist_manipulator else '-'
        ax1.plot(runden_x, agent.intelligenz_history, 
                color=color, alpha=alpha, linewidth=linewidth, linestyle=linestyle)
    
    ax1.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax1.grid(True, alpha=0.3)
    
    # --- Graph 2: Gruppen-Vergleich ---
    ax2.set_title('Intelligenz: Normale vs. Manipulatoren')
    ax2.set_ylabel('Ø Intelligenz')
    ax2.set_xlabel('Runde')
    
    ax2.plot(range(1, RUNDEN + 1), normale_phi_history, color='#3498DB', 
             linewidth=2.5, label='Normale')
    ax2.plot(range(1, RUNDEN + 1), manipulator_phi_history, color='#E74C3C', 
             linewidth=2.5, linestyle='--', label='Manipulatoren')
    ax2.fill_between(range(1, RUNDEN + 1), normale_phi_history, manipulator_phi_history,
                     alpha=0.2, color='#2ECC71')
    
    ax2.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # --- Graph 3: Erwischt pro Runde ---
    ax3.set_title('Manipulationen ERWISCHT pro Runde')
    ax3.set_ylabel('Anzahl Erwischt')
    ax3.set_xlabel('Runde')
    
    ax3.bar(range(1, RUNDEN + 1), erwischt_pro_runde, color='#E74C3C', alpha=0.6)
    ax3.set_xlim(0, RUNDEN)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # --- Graph 4: Kumulative Erwischt ---
    ax4.set_title('Kumulative Manipulations-Entdeckungen')
    ax4.set_ylabel('Gesamt Erwischt')
    ax4.set_xlabel('Runde')
    
    kumulativ = np.cumsum(erwischt_pro_runde)
    ax4.fill_between(range(1, RUNDEN + 1), kumulativ, alpha=0.3, color='#9B59B6')
    ax4.plot(range(1, RUNDEN + 1), kumulativ, color='#8E44AD', linewidth=2)
    ax4.grid(True, alpha=0.3)
    
    # --- Graph 5: Scatter Finale Position ---
    ax5.set_title('Finale Position: Intelligenz vs. Reputation')
    ax5.set_xlabel('Reputation')
    ax5.set_ylabel('Intelligenz')
    
    for agent in agenten:
        color = '#E74C3C' if agent.ist_manipulator else '#3498DB'
        marker = 'X' if agent.ist_manipulator else 'o'
        size = 100 + agent.erwischt_count * 30 if agent.ist_manipulator else 40
        ax5.scatter(agent.reputation, agent.intelligenz, c=color, marker=marker, 
                   s=size, alpha=0.7, edgecolors='black' if agent.ist_manipulator else 'none')
    
    ax5.axhline(y=1.0, color='gray', linestyle=':', alpha=0.3)
    ax5.axvline(x=0.5, color='gray', linestyle=':', alpha=0.3)
    ax5.grid(True, alpha=0.3)
    
    # --- Graph 6: Protokoll-Effektivität ---
    ax6.set_title('Commitment-Protokoll Effektivität')
    
    kategorien = ['Manipulations-\nVersuche', 'ERWISCHT\n(verhindert)', 'Erfolgreich\n(durchgekommen)']
    werte = [total_versuche, total_erwischt, total_erfolg]
    farben = ['#F39C12', '#27AE60', '#E74C3C']
    
    bars = ax6.bar(kategorien, werte, color=farben, edgecolor='black', linewidth=2)
    
    for bar, wert in zip(bars, werte):
        ax6.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{wert}', ha='center', va='bottom', fontweight='bold', fontsize=14)
    
    ax6.set_ylabel('Anzahl')
    ax6.grid(True, alpha=0.3, axis='y')
    
    # Erfolgsrate
    if total_versuche > 0:
        erfolgsrate = (1 - total_erfolg / total_versuche) * 100
        ax6.text(0.5, 0.95, f'Protokoll-Effektivität: {erfolgsrate:.1f}%', 
                transform=ax6.transAxes, ha='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='#2ECC71', alpha=0.8))
    
    plt.tight_layout()
    save_and_maybe_show(plt, 'kki_commitment_protokoll.png', dpi=150)


if __name__ == "__main__":
    simulation()
