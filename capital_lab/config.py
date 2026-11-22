from dataclasses import dataclass, field


@dataclass(frozen=True)
class BacktestConfig:
    universe: tuple[str, ...] = ("XLP", "XLV", "XLU", "XLK", "SMH")
    benchmark: str = "SPY"
    start: str = "2015-01-01"
    end: str | None = None
    initial_cash: float = 30_000.0
    fee_rate: float = 0.001
    trend_window: int = 200
    rebalance_rule: str = "MS"
    tags: dict[str, str] = field(default_factory=lambda: {
        "XLP": "defensive", "XLV": "defensive", "XLU": "defensive",
        "XLK": "ai_tech", "SMH": "ai_tech",
    })
