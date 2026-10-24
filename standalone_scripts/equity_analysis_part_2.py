import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
# import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap
import matplotlib as mpl

# set your preferred default style
# mpl.rcParams.update({
#     "lines.linewidth": 2.8,     # default line thickness
#     "lines.markersize": 7,      # default marker size
#     "errorbar.capsize": 5,      # default cap size on errorbars
#     "axes.labelsize": 15,       # optional: larger axis labels
#     "axes.titlesize": 16,       # optional: larger titles
#     "xtick.labelsize": 13,      # optional: tick label size
#     "ytick.labelsize": 13,      # optional: tick label size
# })

# mpl.rcParams.update({
#     "lines.linewidth": 3,     # default line thickness
#     "lines.markersize": 9,      # default marker size
#     "errorbar.capsize": 7,      # default cap size on errorbars
#     "axes.labelsize": 17,       # optional: larger axis labels
#     "axes.titlesize": 18,       # optional: larger titles
#     "xtick.labelsize": 15,      # optional: tick label size
#     "ytick.labelsize": 15,      # optional: tick label size
# })

mpl.rcParams.update({
    "lines.linewidth": 5,     # default line thickness
    "lines.markersize": 9,      # default marker size
    "errorbar.capsize": 16,      # default cap size on errorbars
    "axes.labelsize": 17,       # optional: larger axis labels
    "axes.titlesize": 18,       # optional: larger titles
    "xtick.labelsize": 15,      # optional: tick label size
    "ytick.labelsize": 15,      # optional: tick label size
})

# non_dm_df = pd.read_csv("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/"
#                         "bayesian_journal_lemon_grove_fs_4_to_6/suppliment_3/"
#                         "non_dominated_data_equity_analysis_with_suppliment.csv")
non_dm_df = pd.read_csv("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/"
                        "bayesian_journal_lemon_grove_150sobol_400itr/non_dominated_data_equity_analysis.csv")

# ---------- shared binning from x ----------
# x_all = non_dm_df["Micro to fixed factor"].to_numpy()
# Or
x_all = non_dm_df["Peak fare factor"].to_numpy()

mx = np.isfinite(x_all)
xv = x_all[mx]
n = xv.size

# Freedman–Diaconis rule (capped to 4–8 bins for n=23)
iqr = np.subtract(*np.percentile(xv, [75, 25]))
bin_width = 2 * iqr / np.cbrt(n)
if not np.isfinite(bin_width) or bin_width <= 0:
    bin_width = (xv.max() - xv.min()) / 5  # fallback
num_bins = int(np.clip((xv.max() - xv.min()) / bin_width, 4, 8))
num_bins = max(4, min(8, num_bins))  # final safety
bins = np.linspace(xv.min(), xv.max(), num_bins + 1)
print(f'Optimal number of bins: {bins}')
# ---------- plot each quartile ----------
# quartiles = {
#     "Q1": "tot_mob_logsum_incr Q1",
#     "Q2": "tot_mob_logsum_incr Q2",
#     "Q3": "tot_mob_logsum_incr Q3",
#     "Q4": "tot_mob_logsum_incr Q4",
# }
# Or
quartiles = {
    "Q1": "Number of micro trips Q1",
    "Q2": "Number of micro trips Q2",
    "Q3": "Number of micro trips Q3",
    "Q4": "Number of micro trips Q4",
}

plt.figure(figsize=(10,8),dpi=160)

for label, ycol in quartiles.items():
    y_all = non_dm_df[ycol].to_numpy()
    m = np.isfinite(y_all) & np.isfinite(x_all)

    df = pd.DataFrame({"x": x_all[m], "y": y_all[m]})
    df["bin"] = pd.cut(df["x"], bins, include_lowest=True)

    summary = (
        df.groupby("bin", observed=True)
          .agg(x_mid=("x", "mean"),
               y_mean=("y", "mean"),
               y_std=("y", "std"),
               n=("y", "size"))
          .dropna(subset=["x_mid", "y_mean"])
    )

    # SE/CI; when n<2 std is NaN → treat as 0 so errorbar disappears
    summary["y_std"] = summary["y_std"].fillna(0)
    summary["y_se"] = summary["y_std"] / np.sqrt(summary["n"].clip(lower=1))
    ci95 = 1.96 * summary["y_se"]

    # one series per quartile; let matplotlib pick distinct colors
    plt.errorbar(summary["x_mid"], summary["y_mean"], yerr=ci95,
                 fmt="o-", capsize=3, lw=1.6, label=label)

# plt.xlabel("Micro to fixed factor", fontsize=20)
plt.xlabel("Peak fare factor", fontsize=20)
# plt.ylabel("Mobility logsum incr.", fontsize=20)
plt.ylabel("Number of micro trips", fontsize=20)
plt.tick_params(axis='both', labelsize=20)
plt.grid(True, linestyle="--", alpha=0.5)
# plt.legend(title="Income quartile", loc="best", frameon=True, fontsize=16, title_fontsize=16, markerscale=1.5)
plt.legend(title="Income quartile", loc="best", frameon=True, fontsize=13, title_fontsize=13, markerscale=1.0)
plt.tight_layout()
plt.savefig("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/"
            "bayesian_journal_lemon_grove_fs_4_to_6/suppliment_3/equity_plots/pff_trip.png", format="png", dpi=160,
            bbox_inches="tight")
plt.show()

