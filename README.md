# personal-capital-lab

A paper-money backtest of simple ETF strategies, built with vectorbt. Starts with a pretend $30,000.

## Strategies

- **v1 Trend per ETF:** each month, hold only the ETFs priced above their 200-day average.
- **Momentum only:** once a year, put 60% of the money into the two ETFs that rose most over the past year.
- **v3 Core:** momentum, plus a crash guard on SPY with a 5% buffer, two-month confirmation, and a half sell.
- **Benchmarks:** hold all five ETFs, or hold SPY.

The ETFs are XLP, XLV, XLU, XLK and SMH. Every result is split into build years (2016–2021) and unseen years (2022 onward).

## Run

```bash
uv sync
uv run python run_backtest.py
```

## Layout

- `capital_lab/config.py`: settings
- `capital_lab/data.py`: price download
- `capital_lab/strategy.py`: trading rules
- `capital_lab/backtest.py`: simulation and metrics
- `run_backtest.py`: entry point

Educational only. Not investment advice.
