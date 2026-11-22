from capital_lab import backtest, strategy
from capital_lab.config import BacktestConfig
from capital_lab.data import load_prices


def main(config: BacktestConfig = BacktestConfig()) -> None:
    universe = list(config.universe)
    prices = load_prices([*universe, config.benchmark], config.start, config.end)
    start = prices.index[config.trend_window]
    etfs, bench = prices[universe], prices[[config.benchmark]]

    portfolios = {
        "Trend strategy": backtest.run(etfs.loc[start:], strategy.target_weights(etfs, config.trend_window, config.rebalance_rule), config),
        "Hold all ETFs": backtest.run(etfs.loc[start:], strategy.buy_and_hold_weights(etfs.loc[start:]), config),
        f"Hold {config.benchmark}": backtest.run(bench.loc[start:], strategy.buy_and_hold_weights(bench.loc[start:]), config),
    }
    print(f"Period: {start.date()} to {prices.index[-1].date()} | Starting cash: ${config.initial_cash:,.0f}\n")
    print(backtest.summarize(portfolios).to_string())


if __name__ == "__main__":
    main()
