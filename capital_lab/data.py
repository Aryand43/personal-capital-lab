import pandas as pd
import vectorbt as vbt


def load_prices(tickers: list[str], start: str, end: str | None) -> pd.DataFrame:
    prices = vbt.YFData.download(tickers, start=start, end=end, missing_index="drop").get("Close")
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(tickers[0])
    return prices.dropna()
