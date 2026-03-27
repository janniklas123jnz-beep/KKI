"""Risikomanagement — Stop-Loss, Position Sizing."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class RiskConfig:
    max_position_pct: float = 0.35    # Max 35% des Portfolios pro Trade
    stop_loss_pct: float = 0.05       # 5% Stop-Loss
    take_profit_pct: float = 0.15     # 15% Take-Profit
    max_open_positions: int = 3       # Max 3 offene Positionen

DEFAULT_RISK = RiskConfig()

def position_size(portfolio_value: float, confidence: float,
                  suggested_pct: float, config: RiskConfig = DEFAULT_RISK) -> float:
    """Optimale Positionsgröße berechnen."""
    base_size = portfolio_value * min(suggested_pct, config.max_position_pct)
    adjusted = base_size * confidence
    return round(adjusted, 2)

def check_stop_loss(avg_price: float, current_price: float,
                    config: RiskConfig = DEFAULT_RISK) -> bool:
    return (avg_price - current_price) / avg_price >= config.stop_loss_pct

def check_take_profit(avg_price: float, current_price: float,
                      config: RiskConfig = DEFAULT_RISK) -> bool:
    return (current_price - avg_price) / avg_price >= config.take_profit_pct
