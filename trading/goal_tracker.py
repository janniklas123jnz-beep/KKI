"""Ziel-Tracker — verfolgt den Weg von 10€ zu 1000€+."""
from __future__ import annotations
from dataclasses import dataclass

MILESTONES = [10.0, 20.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 5000.0, 10000.0]

@dataclass
class Goal:
    target: float
    achieved: bool = False
    achieved_at: str = ""

def get_current_goal(portfolio_value: float) -> float:
    for milestone in MILESTONES:
        if portfolio_value < milestone:
            return milestone
    return MILESTONES[-1] * 10

def progress_bar(current: float, target: float, width: int = 20) -> str:
    pct = min(current / target, 1.0)
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct*100:.1f}%"

def status_report(portfolio_value: float, initial: float = 10.0) -> str:
    current_goal = get_current_goal(portfolio_value)
    prev_milestone = 0.0
    for m in MILESTONES:
        if portfolio_value < m:
            prev_milestone = MILESTONES[MILESTONES.index(m) - 1] if MILESTONES.index(m) > 0 else 0
            break

    lines = [
        "🎯 LEITSTERN ZIEL-TRACKER",
        "═" * 40,
    ]
    for i, milestone in enumerate(MILESTONES):
        if milestone < portfolio_value:
            lines.append(f"  ✅ {milestone:>8.0f}€ — erreicht!")
        elif milestone == current_goal:
            bar = progress_bar(portfolio_value - prev_milestone, milestone - prev_milestone)
            lines.append(f"  🎯 {milestone:>8.0f}€ {bar} ← AKTUELL")
        else:
            lines.append(f"  ⭕ {milestone:>8.0f}€")

    multiplier = portfolio_value / initial
    lines.append("─" * 40)
    lines.append(f"  Aktuell: {portfolio_value:.2f}€ ({multiplier:.1f}x vom Start)")
    return "\n".join(lines)
