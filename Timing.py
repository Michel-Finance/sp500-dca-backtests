import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

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

frequencies = {
    "Bi-weekly (10 days)": {
        "days": 10,
        "amount": ANNUAL_BUDGET / (252 / 10),
    },
    "Monthly (21 days)": {
        "days": 21,
        "amount": MONTHLY_BUDGET,
    },
    "Every 2 Months (42 days)": {
        "days": 42,
        "amount": MONTHLY_BUDGET * 2,
    },
    "Quarterly (63 days)": {
        "days": 63,
        "amount": MONTHLY_BUDGET * 3,
    },
    "Semi-Annually (126 days)": {
        "days": 126,
        "amount": MONTHLY_BUDGET * 6,
    },
    "Yearly (252 days)": {
        "days": 252,
        "amount": MONTHLY_BUDGET * 12,
    },
}


def run_dca(freq_days, contribution_amount):
    shares, cash, invested = 0.0, 0.0, 0.0
    portfolio_vals = np.zeros(n_days)

    for i in range(n_days):
        if i % freq_days == 0:
            cash += contribution_amount
            invested += contribution_amount

        if cash > 0:
            shares += cash / prices[i]
            cash = 0.0

        portfolio_vals[i] = shares * prices[i]

    return portfolio_vals, invested


results = {}

for label, params in frequencies.items():
    vals, total_inv = run_dca(params["days"], params["amount"])
    results[label] = {
        "values": vals,
        "invested": total_inv,
        "contribution_size": params["amount"],
    }

sorted_results = sorted(
    results.items(), key=lambda x: x[1]["values"][-1], reverse=True
)

for name, res in sorted_results:
    final_val = res["values"][-1]
    invested = res["invested"]
    gain_pct = ((final_val / invested) - 1) * 100
    cagr = (((final_val / invested) ** (1 / years)) - 1) * 100
    deposit_str = f"${res['contribution_size']:.2f}"
    print(
        f"{name:<25} | {deposit_str:>15} | ${invested:>9,.0f} | ${final_val:>10,.2f} | {gain_pct:>8.1f}% | {cagr:>8.2f}%"
    )

fig, ax = plt.subplots(figsize=(12, 6))

colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(frequencies)))

for idx, (name, res) in enumerate(sorted_results):
    ax.plot(
        dates,
        res["values"],
        label=name,
        color=colors[idx],
        linewidth=1.8 if idx == 0 else 1.2,
    )

ax.set_title("DCA Frequency Comparison ($100/Month Savings Rate)")
ax.set_ylabel("Portfolio Value ($)")
ax.set_xlabel("Date")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
