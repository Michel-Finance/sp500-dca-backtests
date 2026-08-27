import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf

tickers = ["^GSPC", "^VIX", "^VIX3M"]
df = yf.download(tickers, start="2004-01-01", end="2026-01-01")["Close"].dropna()

df["Ratio"] = df["^VIX"] / df["^VIX3M"]
df["SP500"] = df["^GSPC"]

MONTHLY_CONTRIBUTION = 100.0

dates = df.index
prices = df["SP500"].values
ratios = df["Ratio"].values
n_days = len(df)
months = dates.month
years = (dates[-1] - dates[0]).days / 365.25


def run_dca():
    shares, cash, invested = 0.0, 0.0, 0.0
    portfolio_vals = np.zeros(n_days)
    current_month = None

    for i in range(n_days):
        if months[i] != current_month:
            current_month = months[i]
            cash += MONTHLY_CONTRIBUTION
            invested += MONTHLY_CONTRIBUTION

        shares += cash / prices[i]
        cash = 0.0
        portfolio_vals[i] = (shares * prices[i]) + cash

    return portfolio_vals, invested


def run_vix_105_strategy():
    shares, cash, invested, trade_count = 0.0, 0.0, 0.0, 0
    portfolio_vals = np.zeros(n_days)
    current_month = None

    for i in range(n_days):
        if months[i] != current_month:
            current_month = months[i]
            cash += MONTHLY_CONTRIBUTION
            invested += MONTHLY_CONTRIBUTION

        if ratios[i] > 1.05 and cash > 0:
            shares += cash / prices[i]
            cash = 0.0
            trade_count += 1

        portfolio_vals[i] = (shares * prices[i]) + cash

    return portfolio_vals, trade_count


dca_vals, total_invested = run_dca()
vix_vals, vix_trades = run_vix_105_strategy()

results = {
    "Standard DCA": {"values": dca_vals, "trades": n_days // 21},
    "VIX Ratio > 1.05": {"values": vix_vals, "trades": vix_trades},
}

print("=" * 80)
print(
    f"{'Strategy':<20} | {'Final Value':<14} | {'Gain (%)':<10} | {'CAGR (%)':<10} | {'Triggers':<8}"
)
print("=" * 80)

for name, res in results.items():
    final_val = res["values"][-1]
    gain_pct = ((final_val / total_invested) - 1) * 100
    cagr = (((final_val / total_invested) ** (1 / years)) - 1) * 100
    print(
        f"{name:<20} | ${final_val:>12,.2f} | {gain_pct:>8.1f}% | {cagr:>8.2f}% | {res['trades']:>8}"
    )

print("=" * 80)
print(f"Total Capital Invested: ${total_invested:,.2f}\n")

fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    dates,
    results["Standard DCA"]["values"],
    label="Standard DCA",
    color="black",
    linewidth=2.0,
)

ax.plot(
    dates,
    results["VIX Ratio > 1.05"]["values"],
    label="VIX Ratio > 1.05",
    color="crimson",
    linewidth=1.8,
)

ax.set_title("VIX Term Structure Inversion (Ratio > 1.05) vs Standard DCA")
ax.set_ylabel("Portfolio Value ($)")
ax.set_xlabel("Date")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()
