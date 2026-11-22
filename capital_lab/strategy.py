from typing import NamedTuple

import numpy as np
import pandas as pd

from capital_lab.config import BacktestConfig


class Plan(NamedTuple):
    targets: pd.DataFrame
    schedule: pd.Series


def calendar_schedule(index: pd.DatetimeIndex, rule: str) -> pd.Series:
    firsts = pd.Series(index, index=index).resample(rule).first().dropna()
    return pd.Series(index.isin(firsts), index=index)


def never(index: pd.DatetimeIndex) -> pd.Series:
    return pd.Series(False, index=index)


def above_average(prices: pd.DataFrame | pd.Series, window: int) -> pd.DataFrame | pd.Series:
    return (prices > prices.rolling(window).mean()).astype(float)


def equal_weight(signals: pd.DataFrame) -> pd.DataFrame:
    counts = signals.sum(axis=1).replace(0, np.nan)
    return signals.div(counts, axis=0).fillna(0.0)


def momentum_tilt(prices: pd.DataFrame, lookback: int, top_n: int, top_share: float) -> pd.DataFrame:
    leaders = prices.pct_change(lookback).rank(axis=1, ascending=False) <= top_n
    rest = (1 - top_share) / (prices.shape[1] - top_n)
    return leaders.astype(float) * (top_share / top_n - rest) + rest


def checked_monthly(signal: pd.Series) -> tuple[pd.Series, pd.Series]:
    monthly = calendar_schedule(signal.index, "MS")
    seen = signal.where(monthly).ffill()
    flips = monthly & seen.ne(seen.shift())
    return seen, flips


def hold(known: pd.DataFrame) -> Plan:
    targets = pd.DataFrame(1.0 / known.shape[1], index=known.index, columns=known.columns)
    return Plan(targets, never(known.index))


def trend_per_etf(known: pd.DataFrame, _: pd.Series, config: BacktestConfig) -> Plan:
    targets = equal_weight(above_average(known, config.trend_window))
    return Plan(targets, calendar_schedule(known.index, "MS"))


def crash_switch(known: pd.DataFrame, market: pd.Series, config: BacktestConfig) -> Plan:
    risk_on, flips = checked_monthly(above_average(market, config.trend_window))
    targets = hold(known).targets.mul(risk_on, axis=0)
    return Plan(targets, calendar_schedule(known.index, "YS") | flips)


def momentum(known: pd.DataFrame, _: pd.Series, config: BacktestConfig) -> Plan:
    targets = momentum_tilt(known, config.momentum_lookback, config.top_n, config.top_share)
    return Plan(targets, calendar_schedule(known.index, "YS"))


def core_v2(known: pd.DataFrame, market: pd.Series, config: BacktestConfig) -> Plan:
    risk_on, flips = checked_monthly(above_average(market, config.trend_window))
    targets = momentum(known, market, config).targets.mul(risk_on, axis=0)
    return Plan(targets, calendar_schedule(known.index, "YS") | flips)
