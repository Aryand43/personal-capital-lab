from typing import NamedTuple

import numpy as np
import pandas as pd

from capital_lab.config import BacktestConfig, Guard


class Plan(NamedTuple):
    targets: pd.DataFrame
    schedule: pd.Series


def calendar_schedule(index: pd.DatetimeIndex, rule: str) -> pd.Series:
    firsts = pd.Series(index, index=index).resample(rule).first().dropna()
    return pd.Series(index.isin(firsts), index=index)


def never(index: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(False, index=index)


def above_average(prices: pd.DataFrame, window: int) -> pd.DataFrame:
    return (prices > prices.rolling(window).mean()).astype(float)


def equal_weight(signals: pd.DataFrame) -> pd.DataFrame:
    counts = signals.sum(axis=1).replace(0, np.nan)
    return signals.div(counts, axis=0).fillna(0.0)


def momentum_tilt(prices: pd.DataFrame, lookback: int, top_n: int, top_share: float) -> pd.DataFrame:
    leaders = prices.pct_change(lookback).rank(axis=1, ascending=False) <= top_n
    rest = (1 - top_share) / (prices.shape[1] - top_n)
    return leaders.astype(float) * (top_share / top_n - rest) + rest


def guarded_exposure(market: pd.Series, window: int, guard: Guard) -> tuple[pd.Series, pd.Series]:
    monthly = calendar_schedule(market.index, "MS")
    price, average = market[monthly], market.rolling(window).mean()[monthly]
    exposure, streak, decisions = 1.0, 0, []
    for now, avg in zip(price, average):
        streak = streak + 1 if now < avg * (1 - guard.buffer) else 0
        if exposure == 1.0 and streak >= guard.confirm_months:
            exposure = guard.off_exposure
        elif exposure < 1.0 and now > avg:
            exposure = 1.0
        decisions.append(exposure)
    seen = pd.Series(decisions, index=price.index).reindex(market.index).ffill()
    return seen, monthly & seen.ne(seen.shift())


def hold(known: pd.DataFrame) -> Plan:
    targets = pd.DataFrame(1.0 / known.shape[1], index=known.index, columns=known.columns)
    return Plan(targets, never(known.index))


def trend_per_etf(known: pd.DataFrame, config: BacktestConfig) -> Plan:
    targets = equal_weight(above_average(known, config.trend_window))
    return Plan(targets, calendar_schedule(known.index, "MS"))


def momentum(known: pd.DataFrame, config: BacktestConfig) -> Plan:
    targets = momentum_tilt(known, config.momentum_lookback, config.top_n, config.top_share)
    return Plan(targets, calendar_schedule(known.index, "YS"))


def guarded_momentum(known: pd.DataFrame, market: pd.Series, config: BacktestConfig, guard: Guard) -> Plan:
    exposure, flips = guarded_exposure(market, config.trend_window, guard)
    targets = momentum(known, config).targets.mul(exposure, axis=0)
    return Plan(targets, calendar_schedule(known.index, "YS") | flips)
