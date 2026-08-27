import matplotlib.pyplot as plt
import numpy as np
import yfinance as yf

tickers = ["^GSPC", "^VIX", "^VIX3M"]
df = yf.download(tickers, start="2004-01-01", end="2026-01-01")["Close"].dropna()

df["Ratio"] = df["^VIX"] / df["^VIX3M"]
df["SP500"] = df["^GSPC"]

MONTHLY_CONTRIBUTION = 100.0
thresholds = [1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07]

dates = df.index
prices = df["SP500"].values
ratios = df["Ratio"].values
n_days = len(df)
months = dates.month
years = (dates[-1] - dates[0]).days / 365.25


def run_backtest(threshold=None):
    shares, cash, invested, trade_count = 0.0, 0.0, 0.0, 0
    portfolio_vals = np.zeros(n_days)
    current_month = None

    for i in range(n_days):
        if months[i] != current_month:
            current_month = months[i]
            cash += MONTHLY_CONTRIBUTION
            invested += MONTHLY_CONTRIBUTION

        if threshold is None:
            shares += cash / prices[i]
            cash = 0.0
        elif ratios[i] > threshold and cash > 0:
            shares += cash / prices[i]
            cash = 0.0
            trade_count += 1

        portfolio_vals[i] = (shares * prices[i]) + cash

    return portfolio_vals, invested, trade_count


dca_vals, total_invested, _ = run_backtest(threshold=None)
results = {"Standard DCA": {"values": dca_vals, "trades": n_days // 21}}

for thresh in thresholds:
    vals, _, trades = run_backtest(threshold=thresh)
    results[f"Ratio > {thresh:.2f}"] = {"values": vals, "trades": trades}

print("=" * 80)
print(
    f"{'Strategy':<20} | {'Final Value':<14} | {'Gain (%)':<10} | {'CAGR (%)':<10} | {'Triggers':<8}"
)
print("=" * 80)

sorted_results = sorted(
    results.items(), key=lambda x: x[1]["values"][-1], reverse=True
)

for name, res in sorted_results:
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
    linewidth=2.5,
    zorder=10,
)

colors = plt.cm.plasma(np.linspace(0, 0.85, len(thresholds)))
for idx, thresh in enumerate(thresholds):
    label = f"Ratio > {thresh:.2f}"
    ax.plot(
        dates,
        results[label]["values"],
        label=label,
        color=colors[idx],
        linewidth=1.2,
        alpha=0.85,
    )

ax.set_title("VIX Term Structure Inversion Thresholds vs Standard DCA (2004 - Present)")
ax.set_ylabel("Portfolio Value ($)")
ax.set_xlabel("Date")
ax.legend(loc="upper left")
ax.grid(True, linestyle="--", alpha=0.5)

plt.tight_layout()
plt.show()