"""Leitstern Trading Strategien — basierend auf KKI-Wissen."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from .market_data import Candle, get_klines, get_ticker

class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

@dataclass
class TradeSignal:
    symbol: str
    signal: Signal
    confidence: float      # 0.0 – 1.0
    reason: str
    suggested_size_pct: float = 0.3   # Anteil des Portfolios

def _sma(candles: list[Candle], period: int) -> float:
    if len(candles) < period:
        return 0.0
    return sum(c.close for c in candles[-period:]) / period

def _rsi(candles: list[Candle], period: int = 14) -> float:
    if len(candles) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(-period, 0):
        diff = candles[i].close - candles[i-1].close
        (gains if diff > 0 else losses).append(abs(diff))
    avg_gain = sum(gains) / period if gains else 0
    avg_loss = sum(losses) / period if losses else 1e-10
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def momentum_strategy(symbol: str = "BTCUSDT") -> TradeSignal:
    """Einfache SMA-Crossover + RSI Strategie."""
    candles = get_klines(symbol, interval="1h", limit=50)
    if len(candles) < 26:
        return TradeSignal(symbol=symbol, signal=Signal.HOLD, confidence=0.0, reason="Nicht genug Daten")

    sma_fast = _sma(candles, 7)
    sma_slow = _sma(candles, 21)
    rsi = _rsi(candles, 14)
    price = candles[-1].close
    ticker = get_ticker(symbol)
    change_24h = ticker.change_24h if ticker else 0.0

    reasons = []
    buy_score = 0.0
    sell_score = 0.0

    # SMA Crossover
    if sma_fast > sma_slow * 1.001:
        buy_score += 0.35
        reasons.append(f"SMA7({sma_fast:.0f}) > SMA21({sma_slow:.0f}) ↑")
    elif sma_fast < sma_slow * 0.999:
        sell_score += 0.35
        reasons.append(f"SMA7({sma_fast:.0f}) < SMA21({sma_slow:.0f}) ↓")

    # RSI
    if rsi < 35:
        buy_score += 0.35
        reasons.append(f"RSI {rsi:.1f} — überverkauft 🟢")
    elif rsi > 65:
        sell_score += 0.35
        reasons.append(f"RSI {rsi:.1f} — überkauft 🔴")
    else:
        reasons.append(f"RSI {rsi:.1f} — neutral")

    # 24h Momentum
    if change_24h > 3.0:
        buy_score += 0.3
        reasons.append(f"24h +{change_24h:.1f}% — Aufwärtstrend")
    elif change_24h < -3.0:
        sell_score += 0.3
        reasons.append(f"24h {change_24h:.1f}% — Abwärtstrend")

    reason_str = " | ".join(reasons)

    if buy_score > 0.5 and buy_score > sell_score:
        return TradeSignal(symbol=symbol, signal=Signal.BUY, confidence=min(buy_score, 1.0),
                          reason=reason_str, suggested_size_pct=0.3)
    elif sell_score > 0.5 and sell_score > buy_score:
        return TradeSignal(symbol=symbol, signal=Signal.SELL, confidence=min(sell_score, 1.0),
                          reason=reason_str, suggested_size_pct=1.0)
    else:
        return TradeSignal(symbol=symbol, signal=Signal.HOLD, confidence=0.5,
                          reason=reason_str)

def scan_opportunities(symbols: list[str] = None) -> list[TradeSignal]:
    """Mehrere Symbole scannen."""
    if symbols is None:
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "ADAUSDT"]
    signals = []
    for sym in symbols:
        sig = momentum_strategy(sym)
        if sig.signal != Signal.HOLD:
            signals.append(sig)
    signals.sort(key=lambda s: s.confidence, reverse=True)
    return signals
