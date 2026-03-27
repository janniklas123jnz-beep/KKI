"""Marktdaten-Modul — holt echte Crypto-Preise von Binance public API."""
from __future__ import annotations
import requests
import time
from dataclasses import dataclass, field
from typing import Optional

BINANCE_BASE = "https://api.binance.com/api/v3"

@dataclass
class Candle:
    symbol: str
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass 
class Ticker:
    symbol: str
    price: float
    change_24h: float
    volume_24h: float

def get_price(symbol: str = "BTCUSDT") -> float:
    """Aktuellen Preis eines Symbols holen."""
    try:
        r = requests.get(f"{BINANCE_BASE}/ticker/price", params={"symbol": symbol}, timeout=10)
        r.raise_for_status()
        return float(r.json()["price"])
    except Exception as e:
        print(f"⚠️ Preisfehler für {symbol}: {e}")
        return 0.0

def get_ticker(symbol: str = "BTCUSDT") -> Optional[Ticker]:
    """24h Ticker-Daten holen."""
    try:
        r = requests.get(f"{BINANCE_BASE}/ticker/24hr", params={"symbol": symbol}, timeout=10)
        r.raise_for_status()
        d = r.json()
        return Ticker(
            symbol=symbol,
            price=float(d["lastPrice"]),
            change_24h=float(d["priceChangePercent"]),
            volume_24h=float(d["quoteVolume"])
        )
    except Exception as e:
        print(f"⚠️ Ticker-Fehler für {symbol}: {e}")
        return None

def get_klines(symbol: str = "BTCUSDT", interval: str = "1h", limit: int = 50) -> list[Candle]:
    """Historische Kerzen holen (z.B. 1h, 4h, 1d)."""
    try:
        r = requests.get(f"{BINANCE_BASE}/klines", 
                        params={"symbol": symbol, "interval": interval, "limit": limit}, 
                        timeout=10)
        r.raise_for_status()
        return [Candle(
            symbol=symbol,
            open_time=int(c[0]),
            open=float(c[1]),
            high=float(c[2]),
            low=float(c[3]),
            close=float(c[4]),
            volume=float(c[5])
        ) for c in r.json()]
    except Exception as e:
        print(f"⚠️ Klines-Fehler für {symbol}: {e}")
        return []

def get_top_symbols(quote: str = "USDT", limit: int = 10) -> list[str]:
    """Top-Symbole nach Volumen."""
    try:
        r = requests.get(f"{BINANCE_BASE}/ticker/24hr", timeout=10)
        r.raise_for_status()
        tickers = [t for t in r.json() if t["symbol"].endswith(quote) and float(t["quoteVolume"]) > 0]
        tickers.sort(key=lambda x: float(x["quoteVolume"]), reverse=True)
        return [t["symbol"] for t in tickers[:limit]]
    except Exception as e:
        print(f"⚠️ Top-Symbole-Fehler: {e}")
        return ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
