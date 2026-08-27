# sp500-dca-backtests
Does *when* you buy the S&P 500 matter, compared to just investing on a fixed schedule (DCA)? Four small backtests on real market data (2004–2026, $100/month simulated contributions).

## Tests

1. **1_05.py**  Buy only when the VIX/VIX3M ratio signals market stress (> 1.05), instead of monthly.
2. **DCA_vs_triggers.py**  Same signal, swept across 7 thresholds (1.01 to 1.07).
3. **Timing.py**  Same $100/month budget, different contribution frequencies (bi-weekly to yearly).
4. **Solar_Eclipse.py** Buy only on solar eclipse dates, as a deliberately meaningless control signal.

## Result

Every variant lands within a fraction of a percentage point of standard monthly DCA in final CAGR including the solar eclipse control. Timing the entry doesn't seem to matter much; staying invested does.

## Data

Prices pulled via yfinance: S&P 500 (^GSPC), VIX (^VIX), VIX3M (^VIX3M).

## Requirements

Run this to install what you need:

pip install yfinance pandas numpy matplotlib
