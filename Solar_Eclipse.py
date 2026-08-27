import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

ECLIPSE_DATES = [
    "2004-04-19", "2004-10-14", "2005-04-08", "2005-10-03",
    "2006-03-29", "2006-09-22", "2007-03-19", "2007-09-11",
    "2008-02-07", "2008-08-01", "2009-01-26", "2009-07-22",
    "2010-01-15", "2010-07-11", "2011-01-04", "2011-06-01",
    "2011-07-01", "2011-11-25", "2012-05-20", "2012-11-13",
    "2013-05-10", "2013-11-03", "2014-04-29", "2014-10-23",
    "2015-03-20", "2015-09-13", "2016-03-09", "2016-09-01",
    "2017-02-26", "2017-08-21", "2018-02-15", "2018-07-13",
    "2018-08-11", "2019-01-05", "2019-07-02", "2019-12-26",
    "2020-06-21", "2020-12-14", "2021-06-10", "2021-12-04",
    "2022-04-30", "2022-10-25", "2023-04-20", "2023-10-14",
    "2024-04-08", "2024-10-02", "2025-03-29", "2025-09-21"
]

df = yf.download("^GSPC", start="2004-01-01", end="2026-01-01")
df = (
    df["Close"]["^GSPC"].to_frame(name="SP500")
    if isinstance(df.columns, pd.MultiIndex)
    else df[["Close"]].rename(columns={"Close": "SP500"})
).dropna()

dates = df.index
prices = df["SP500"].values
n_days = len(df)
years = (dates[-1] - dates[0]).days / 365.25

MONTHLY_BUDGET = 100.0
ANNUAL_BUDGET = MONTHLY_BUDGET * 12

eclipse_dt = pd.to_datetime(ECLIPSE_DATES)
eclipse_days = df.index.get_indexer(eclipse_dt, method="nearest")
eclipse_days = sorted(list(set(eclipse_days)))


def run_dca_monthly():
    shares, cash, invested = 0.0, 0.0, 0.0
    portfolio_vals = np.zeros(n_days)

    for i in range(n_days):
        if i % 21 == 0:
            cash += MONTHLY_BUDGET
            invested += MONTHLY_BUDGET

        if cash > 0:
            shares += cash / prices[i]
            cash = 0.0

        portfolio_vals[i] = shares * prices[i]

    return portfolio_vals, invested


def run_eclipse_strategy():
    shares, cash, invested, buys = 0.0, 0.0, 0.0, 0
    portfolio_vals = np.zeros(n_days)
    daily_accrual = ANNUAL_BUDGET / 252

    for i in range(n_days):
        cash += daily_accrual
        invested += daily_accrual

        if i in eclipse_days and cash > 0:
            shares += cash / prices[i]
            cash = 0.0
            buys += 1

        portfolio_vals[i] = (shares * prices[i]) + cash

    return portfolio_vals, invested, buys


dca_vals, total_inv = run_dca_monthly()
eclipse_vals, _, eclipse_buys = run_eclipse_strategy()

results = {
    "Standard Monthly DCA": {"values": dca_vals, "buys": n_days // 21},
    "Solar Eclipse Strategy": {"values": eclipse_vals, "buys": eclipse_buys},
}

print("=" * 80)
print(
    f"{'Strategy':<25} | {'Invested':<10} | {'Final Value':<12} | {'Gain (%)':<9} | {'CAGR (%)':<9} | {'Buys':<5}"
)
print("=" * 80)

for name, res in results.items():
    final_val = res["values"][-1]
    gain_pct = ((final_val / total_inv) - 1) * 100
    cagr = (((final_val / total_inv) ** (1 / years)) - 1) * 100
    print(
        f"{name:<25} | ${total_inv:>9,.0f} | ${final_val:>10,.2f} | {gain_pct:>8.1f}% | {cagr:>8.2f}% | {res['buys']:>5}"
    )

print("=" * 80 + "\n")

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    dates,
    results["Standard Monthly DCA"]["values"],
    label="Standard Monthly DCA",
    color="black",
    linewidth=1.5,
)
ax.plot(
    dates,
    results["Solar Eclipse Strategy"]["values"],
    label="Solar Eclipse Strategy",
    color="darkorange",
    linewidth=1.8,
)

eclipse_prices_dates = dates[eclipse_days]
eclipse_portfolio_vals = results["Solar Eclipse Strategy"]["values"][
    eclipse_days
]
ax.scatter(
    eclipse_prices_dates,
    eclipse_portfolio_vals,
    color="red",
    s=25,
    label="Solar Eclipse Buy Event",
    zorder=5,
)

ax.set_title(
    "Solar Eclipse Investment Strategy vs Standard DCA ($100/Mo Normalized)"
)
ax.set_ylabel("Portfolio Value ($)")
ax.set_xlabel("Date")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()