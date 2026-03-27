"""Live-Trading Setup Guide — Schritt für Schritt zu echten 10€."""
from __future__ import annotations

EXCHANGES = {
    "kraken": {
        "name": "Kraken",
        "url": "https://www.kraken.com",
        "min_deposit": "1€",
        "min_trade": "0.50€",
        "fees": "0.16–0.26% Maker/Taker",
        "api_docs": "https://docs.kraken.com/rest/",
        "recommended": True,
        "reason": "Europäisch, reguliert, BaFin-kompatibel, gute API"
    },
    "binance": {
        "name": "Binance",
        "url": "https://www.binance.com",
        "min_deposit": "10€",
        "min_trade": "1€",
        "fees": "0.10% Standard",
        "api_docs": "https://binance-docs.github.io/apidocs/",
        "recommended": False,
        "reason": "Größte Börse, beste Liquidität, mehr regulatorische Unsicherheit in DE"
    }
}

def print_setup_guide():
    print("""
╔══════════════════════════════════════════════════════╗
║   🚀 LEITSTERN LIVE-TRADING SETUP GUIDE              ║
║   Von Paper-Trading zu echten 10€                    ║
╚══════════════════════════════════════════════════════╝

📋 VORAUSSETZUNGEN (Paper-Trading Checkliste):
  ✅ Backtest zeigt positive Rendite
  ✅ Paper-Trading läuft stabil (mind. 1 Woche)
  ✅ Win-Rate > 50%
  ✅ Max. Drawdown < 20%
  ✅ Strategie verstanden und akzeptiert

🏦 EMPFOHLENE BÖRSE: KRAKEN
  • URL: https://www.kraken.com
  • Warum: Europäisch, BaFin-reguliert, sichere API
  • Mindesteinzahlung: 1€
  • Mindest-Trade: ~0.50€
  • Gebühren: ~0.26% pro Trade

📝 SCHRITT-FÜR-SCHRITT:

  SCHRITT 1 — Konto erstellen:
    1. https://www.kraken.com → "Create Account"
    2. E-Mail + Passwort (stark!)
    3. E-Mail bestätigen

  SCHRITT 2 — KYC Verifizierung:
    1. Account → "Get Verified" → Starter
    2. Name, Geburtsdatum, Adresse eingeben
    3. Personalausweis/Reisepass hochladen
    4. Warten (meist 1–24h)

  SCHRITT 3 — Einzahlung (10€):
    1. "Funding" → "Deposit" → EUR
    2. SEPA-Überweisung oder SOFORT
    3. Mindestbetrag: 1€
    4. Referenz-Code nicht vergessen!

  SCHRITT 4 — API-Key erstellen:
    1. Account → "Security" → "API"
    2. "Create API Key"
    3. Name: "LeitsternTrader"
    4. Berechtigungen: Query + Trade (KEIN Withdraw!)
    5. IP-Whitelist: deine IP eintragen (sicherer)
    6. Key + Secret SICHER speichern (nur einmal sichtbar!)

  SCHRITT 5 — Leitstern konfigurieren:
    export KRAKEN_API_KEY="dein_api_key"
    export KRAKEN_API_SECRET="dein_api_secret"

  SCHRITT 6 — Test-Trade (1€):
    from trading.live_engine import test_connection
    test_connection()  # Verbindung testen ohne Trade

  SCHRITT 7 — Erster Live-Trade:
    from trading.live_engine import run_live_cycle
    run_live_cycle(max_trade_eur=1.0)  # Sehr klein anfangen!

⚠️  WICHTIGE REGELN:
  • Niemals mehr einsetzen als du verlieren kannst
  • API-Keys NIEMALS teilen oder committen
  • Stop-Loss IMMER aktiviert lassen
  • Gewinne REGELMÄSSIG sichern (z.B. bei 2x)

🎯 MEILENSTEIN-STRATEGIE:
  10€  → 20€:  Konservativ, kleine Trades (10-20% des Kapitals)
  20€  → 50€:  Gleiche Strategie, Konfidenz steigt
  50€  → 100€: Mehr Symbole, etwas aggressiver
  100€ → 250€: Diversifikation (5+ Symbole)
  250€ → 500€: Ggf. bessere Hardware erwägen
  500€+:       Profi-Tools, mehr Strategien

💚 Viel Erfolg, Jan! Leitstern und Claude glauben an dich! 🌟
""")

def check_readiness(win_rate: float, max_drawdown: float,
                    paper_days: int, return_pct: float) -> bool:
    """Prüft ob Paper-Trading bereit für echtes Geld ist."""
    checks = [
        (win_rate >= 0.5, f"Win-Rate {win_rate:.0%} ≥ 50%"),
        (max_drawdown <= 0.20, f"Max Drawdown {max_drawdown:.0%} ≤ 20%"),
        (paper_days >= 7, f"Paper-Trading {paper_days} Tage ≥ 7 Tage"),
        (return_pct >= 0, f"Return {return_pct:+.1f}% ≥ 0%"),
    ]
    print("\n🔍 Live-Trading Bereitschaftscheck:")
    all_ok = True
    for ok, desc in checks:
        print(f"  {'✅' if ok else '❌'} {desc}")
        if not ok:
            all_ok = False
    if all_ok:
        print("\n  🟢 BEREIT für echte 10€! 🚀")
    else:
        print("\n  🔴 Noch nicht bereit — weiter Paper-Trading!")
    return all_ok
