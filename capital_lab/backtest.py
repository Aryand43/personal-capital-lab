import pandas as pd
import vectorbt as vbt

from capital_lab.config import BacktestConfig
from capital_lab.strategy import Plan

vbt.settings.returns["year_freq"] = "252 days"


def orders_for(plan: Plan, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    targets = plan.targets.loc[start:end]
    due = plan.schedule.loc[start:end].astype(bool)
    orders = targets.where(pd.concat({column: due for column in targets.columns}, axis=1))
    orders.iloc[0] = targets.iloc[0]
    return orders


def run(prices: pd.DataFrame, orders: pd.DataFrame, config: BacktestConfig) -> vbt.Portfolio:
    return vbt.Portfolio.from_orders(
        close=prices.loc[orders.index, orders.columns],
        size=orders,
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
        "Yearly return (%)": lambda pf: pf.annualized_return() * 100,
        "Worst drop (%)": lambda pf: pf.max_drawdown() * 100,
        "Sharpe ratio": lambda pf: pf.sharpe_ratio(),
        "Trades": lambda pf: pf.trades.count(),
    }
    table = pd.DataFrame({name: {m: f(pf) for m, f in metrics.items()} for name, pf in portfolios.items()})
    return table.T.round(2)
