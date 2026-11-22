import pandas as pd
import vectorbt as vbt

from capital_lab.config import BacktestConfig

vbt.settings.returns["year_freq"] = "252 days"


def run(prices: pd.DataFrame, weights: pd.DataFrame, config: BacktestConfig) -> vbt.Portfolio:
    return vbt.Portfolio.from_orders(
        close=prices,
        size=weights,
        size_type="targetpercent",
        group_by=True,
        cash_sharing=True,
        call_seq="auto",
        fees=config.fee_rate,
        init_cash=config.initial_cash,
        freq="1D",
    )


def summarize(portfolios: dict[str, vbt.Portfolio]) -> pd.DataFrame:
    metrics = {
        "Final value ($)": lambda pf: pf.final_value(),
        "Total return (%)": lambda pf: pf.total_return() * 100,
        "Yearly return (%)": lambda pf: pf.annualized_return() * 100,
        "Worst drop (%)": lambda pf: pf.max_drawdown() * 100,
        "Sharpe ratio": lambda pf: pf.sharpe_ratio(),
        "Trades": lambda pf: pf.trades.count(),
    }
    table = pd.DataFrame({name: {m: f(pf) for m, f in metrics.items()} for name, pf in portfolios.items()})
    return table.round(2)
