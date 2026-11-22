import pandas as pd

from capital_lab import backtest, strategy
from capital_lab.config import BacktestConfig
from capital_lab.data import load_prices


def build_plans(prices: pd.DataFrame, config: BacktestConfig) -> dict[str, strategy.Plan]:
    known = prices.shift(1)
    etfs, market = known[list(config.universe)], known[config.benchmark]
    return {
        "v1 Trend per ETF": strategy.trend_per_etf(etfs, market, config),
        "v2a Crash switch": strategy.crash_switch(etfs, market, config),
        "v2b Momentum tilt": strategy.momentum(etfs, market, config),
        "v2 Core (both)": strategy.core_v2(etfs, market, config),
        "Hold all 5 ETFs": strategy.hold(etfs),
        f"Hold {config.benchmark}": strategy.hold(known[[config.benchmark]]),
    }


def periods(index: pd.DatetimeIndex, config: BacktestConfig) -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
    start, end = index[config.warmup], index[-1]
    split = index[index >= config.split_date][0]
    return {
        "Full period": (start, end),
        "Build years (train)": (start, index[index < split][-1]),
        "Unseen years (test)": (split, end),
    }


def main(config: BacktestConfig = BacktestConfig()) -> None:
    prices = load_prices([*config.universe, config.benchmark], config.start, config.end)
    plans = build_plans(prices, config)
    for label, (start, end) in periods(prices.index, config).items():
        portfolios = {name: backtest.run(prices, backtest.orders_for(plan, start, end), config) for name, plan in plans.items()}
        print(f"\n{label}: {start.date()} to {end.date()} | Starting cash: ${config.initial_cash:,.0f}")
        print(backtest.summarize(portfolios).to_string())


if __name__ == "__main__":
    main()
