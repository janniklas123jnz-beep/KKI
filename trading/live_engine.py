"""
Leitstern Live-Trading Engine — Echte Kraken API.

SICHERHEIT: API-Keys NUR über Umgebungsvariablen!
  export KRAKEN_API_KEY="dein_key"
  export KRAKEN_API_SECRET="dein_secret"

Verwendung:
  from trading.live_engine import test_connection, get_balance, run_live_cycle
"""
from __future__ import annotations
import os
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Kraken API Basis
KRAKEN_API_URL = "https://api.kraken.com"
KRAKEN_API_VERSION = "0"

def _get_credentials() -> tuple[str, str]:
    """API-Keys aus Umgebungsvariablen lesen."""
    key = os.environ.get("KRAKEN_API_KEY", "")
    secret = os.environ.get("KRAKEN_API_SECRET", "")
    if not key or not secret:
        raise EnvironmentError(
            "❌ Kraken API-Keys nicht gefunden!\n"
            "Bitte setzen:\n"
            "  export KRAKEN_API_KEY='dein_key'\n"
            "  export KRAKEN_API_SECRET='dein_secret'"
        )
    return key, secret

def _kraken_signature(urlpath: str, data: dict, secret: str) -> str:
    """Kraken API Signatur berechnen."""
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    return base64.b64encode(mac.digest()).decode()

def _private_request(method: str, data: dict = None) -> dict:
    """Authentifizierter Kraken API-Request."""
    key, secret = _get_credentials()
    if data is None:
        data = {}
    data["nonce"] = str(int(time.time() * 1000))
    urlpath = f"/{KRAKEN_API_VERSION}/private/{method}"
    headers = {
        "API-Key": key,
        "API-Sign": _kraken_signature(urlpath, data, secret)
    }
    r = requests.post(
        f"{KRAKEN_API_URL}{urlpath}",
        headers=headers, data=data, timeout=15
    )
    r.raise_for_status()
    result = r.json()
    if result.get("error"):
        raise ValueError(f"Kraken API Fehler: {result['error']}")
    return result.get("result", {})

def _public_request(method: str, params: dict = None) -> dict:
    """Öffentlicher Kraken API-Request (kein Key nötig)."""
    r = requests.get(
        f"{KRAKEN_API_URL}/{KRAKEN_API_VERSION}/public/{method}",
        params=params or {}, timeout=10
    )
    r.raise_for_status()
    result = r.json()
    if result.get("error"):
        raise ValueError(f"Kraken API Fehler: {result['error']}")
    return result.get("result", {})

def test_connection() -> bool:
    """Verbindung testen — liest nur den Kontostand (kein Trade)."""
    print("🔌 Teste Kraken-Verbindung...")
    try:
        balance = _private_request("Balance")
        print("✅ Verbindung erfolgreich!")
        print("\n💰 Kontostand:")
        for asset, amount in balance.items():
            val = float(amount)
            if val > 0.0001:
                print(f"   {asset}: {val:.6f}")
        return True
    except EnvironmentError as e:
        print(e)
        return False
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        return False

def get_balance() -> dict[str, float]:
    """Aktuellen Kontostand abrufen."""
    raw = _private_request("Balance")
    return {asset: float(amount) for asset, amount in raw.items() if float(amount) > 0.0001}

def get_eur_balance() -> float:
    """EUR-Guthaben abrufen."""
    balance = get_balance()
    # Kraken nutzt ZEUR für Euro
    return balance.get("ZEUR", balance.get("EUR", 0.0))

def get_ticker_kraken(pair: str = "XBTEUR") -> dict:
    """Aktuellen Preis von Kraken holen."""
    result = _public_request("Ticker", {"pair": pair})
    ticker = list(result.values())[0]
    return {
        "pair": pair,
        "bid": float(ticker["b"][0]),
        "ask": float(ticker["a"][0]),
        "last": float(ticker["c"][0]),
        "volume_24h": float(ticker["v"][1])
    }

# Kraken Pair-Namen (unterscheiden sich von Binance!)
KRAKEN_PAIRS = {
    "BTCEUR": "XBTEUR",
    "ETHEUR": "ETHEUR",
    "SOLEUR": "SOLEUR",
    "ADAEUR": "ADAEUR",
    "DOTEUR": "DOTEUR",
}

def place_market_order(pair: str, side: str, volume: float,
                       dry_run: bool = True) -> Optional[dict]:
    """
    Market-Order platzieren.

    WICHTIG: dry_run=True by default — erst testen, dann live!
    pair: z.B. "XBTEUR", "ETHEUR"
    side: "buy" oder "sell"
    volume: Menge in der Basis-Währung (z.B. BTC-Menge)
    """
    if dry_run:
        print(f"🔬 DRY-RUN (kein echter Trade): {side.upper()} {volume:.8f} {pair}")
        return {"dry_run": True, "side": side, "pair": pair, "volume": volume}

    print(f"🚀 ECHTER TRADE: {side.upper()} {volume:.8f} {pair}")
    data = {
        "pair": pair,
        "type": side,
        "ordertype": "market",
        "volume": str(volume),
    }
    result = _private_request("AddOrder", data)
    print(f"✅ Order platziert: {result}")
    return result

def run_live_cycle(max_trade_eur: float = 2.0, dry_run: bool = True) -> dict:
    """
    Einen Live-Trading-Zyklus ausführen.

    dry_run=True: Zeigt was getan würde, handelt aber nicht
    dry_run=False: Echter Trade! (erst nach Paper-Trading Erfolg!)
    max_trade_eur: Maximaler Betrag pro Trade in EUR
    """
    print(f"\n{'🔬 DRY-RUN' if dry_run else '🚀 LIVE'} — Leitstern Live-Zyklus")
    print(f"   Max. Trade: {max_trade_eur:.2f}€")
    print("=" * 50)

    # Kontostand
    try:
        eur_balance = get_eur_balance()
        print(f"💶 EUR-Guthaben: {eur_balance:.2f}€")
    except Exception as e:
        print(f"⚠️ Kontostand-Fehler: {e}")
        return {}

    if eur_balance < 0.5:
        print("⚠️ Zu wenig EUR-Guthaben für einen Trade.")
        return {"status": "insufficient_balance"}

    # Signale (von unserem Paper-Trading System)
    from .strategy import scan_opportunities, Signal
    from .market_data import get_price

    # Kraken-Preise für Signalberechnung
    scan_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]  # Binance für Signale
    signals = scan_opportunities(scan_symbols)

    print("\n📊 Signale:")
    for sig in signals:
        emoji = "🟢" if sig.signal == Signal.BUY else "🔴"
        print(f"   {emoji} {sig.symbol}: {sig.signal.value} ({sig.confidence:.0%}) — {sig.reason}")

    if not signals:
        print("   ⚪ Keine starken Signale — HOLD")
        return {"status": "hold"}

    best = signals[0]
    if best.signal != Signal.BUY:
        print(f"\n⚪ Kein Kauf-Signal — {best.signal.value}")
        return {"status": "no_buy_signal"}

    # Binance→Kraken Pair-Mapping
    pair_map = {"BTCUSDT": "XBTEUR", "ETHUSDT": "ETHEUR", "SOLUSDT": "SOLEUR"}
    kraken_pair = pair_map.get(best.symbol, "XBTEUR")

    # Preis von Kraken
    try:
        ticker = get_ticker_kraken(kraken_pair)
        price = ticker["ask"]
    except Exception:
        price = get_price(best.symbol)  # Fallback Binance-Preis

    # Position-Größe
    trade_eur = min(eur_balance * 0.3, max_trade_eur)
    volume = trade_eur / price

    print(f"\n🎯 Bestes Signal: {best.symbol} → {kraken_pair}")
    print(f"   Preis: {price:.4f}€")
    print(f"   Kaufbetrag: {trade_eur:.2f}€")
    print(f"   Menge: {volume:.8f}")

    order = place_market_order(kraken_pair, "buy", volume, dry_run=dry_run)
    return {"status": "order_placed", "order": order, "pair": kraken_pair,
            "trade_eur": trade_eur, "dry_run": dry_run}


def status_live() -> None:
    """Zeigt Live-Portfolio-Status von Kraken."""
    print("\n🌟 LEITSTERN LIVE-PORTFOLIO (Kraken)")
    print("=" * 50)
    try:
        balance = get_balance()
        total_eur = balance.get("ZEUR", 0.0)

        for asset, amount in balance.items():
            if asset == "ZEUR":
                print(f"   💶 EUR:  {amount:.2f}€")
            else:
                try:
                    # Versuche Kraken-Ticker
                    pair = f"{asset}EUR"
                    t = get_ticker_kraken(pair)
                    value_eur = amount * t["last"]
                    print(f"   🪙 {asset}: {amount:.8f} ≈ {value_eur:.2f}€")
                    total_eur += value_eur
                except Exception:
                    print(f"   🪙 {asset}: {amount:.8f}")

        print(f"   {'─'*30}")
        print(f"   💼 Gesamt: ~{total_eur:.2f}€")
    except Exception as e:
        print(f"   ❌ Fehler: {e}")
