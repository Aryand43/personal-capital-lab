from dataclasses import dataclass


@dataclass(frozen=True)
class Guard:
    buffer: float = 0.0
    confirm_months: int = 1
    off_exposure: float = 0.0


@dataclass(frozen=True)
class BacktestConfig:
    universe: tuple[str, ...] = ("XLP", "XLV", "XLU", "XLK", "SMH")
    benchmark: str = "SPY"
    start: str = "2015-01-01"
    end: str | None = None
    split_date: str = "2022-01-01"
    initial_cash: float = 30_000.0
    fee_rate: float = 0.001
    trend_window: int = 200
    momentum_lookback: int = 252
    top_n: int = 2
    top_share: float = 0.6
    guard: Guard = Guard(buffer=0.05, confirm_months=2, off_exposure=0.5)

    @property
    def warmup(self) -> int:
        return max(self.trend_window, self.momentum_lookback) + 1
