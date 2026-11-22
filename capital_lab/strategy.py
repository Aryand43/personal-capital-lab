import numpy as np
import pandas as pd


def rebalance_dates(index: pd.DatetimeIndex, rule: str) -> pd.DatetimeIndex:
    return pd.Series(index, index=index).resample(rule).first().dropna().pipe(pd.DatetimeIndex)


def trend_filter(prices: pd.DataFrame, window: int) -> pd.DataFrame:
    return prices > prices.rolling(window).mean()


def equal_weight(signals: pd.DataFrame) -> pd.DataFrame:
    counts = signals.sum(axis=1).replace(0, np.nan)
    return signals.div(counts, axis=0).fillna(0.0)


def target_weights(prices: pd.DataFrame, window: int, rule: str) -> pd.DataFrame:
    weights = equal_weight(trend_filter(prices, window)).iloc[window:]
    schedule = rebalance_dates(weights.index, rule)
    return weights.where(pd.DataFrame(True, index=schedule, columns=weights.columns).reindex(weights.index, fill_value=False))


def buy_and_hold_weights(prices: pd.DataFrame) -> pd.DataFrame:
    weights = pd.DataFrame(np.nan, index=prices.index, columns=prices.columns)
    weights.iloc[0] = 1.0 / prices.shape[1]
    return weights
