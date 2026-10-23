import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import matplotlib.patheffects as pe
import os
from matplotlib.cm import ScalarMappable


# Load your file
# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/" \
#        "bayesian_journal_lemon_grove_150sobol_400itr/non_dom_including_sobol.csv"
# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_fs_4_to_6" \
#        "/suppliment_3/non_dom_with_suppliment.csv"


file = "D:/Ritun/Siwei_Micro_Transit_R1/Bayesian_Optimization/optimization_output/lemon_grove_final_results/" \
       "non_dom_with_suppliment.csv"
file_1 = "D:/Ritun/Siwei_Micro_Transit_R1/Bayesian_Optimization/optimization_output/New folder/bayesian_journal_lemon_grove/" \
       "non_dominated_data_old_method _Copy.csv"
df_pareto = pd.read_csv(file)
df_pareto["Total subsidy ($)"] = -df_pareto["Total subsidy ($)"]
df_file_1 = pd.read_csv(file_1)
df_naive = df_file_1[23:]
# ----------------------------------------------------------------------------------------------------------------------
### Pareto front plotting
plt.figure(figsize=(10, 8), dpi=160)
plt.scatter(
    df_pareto["Total subsidy ($)"],                          # X-axis
    df_pareto["Total mob. Logsum increase with micro"],
    color='purple',                                      # Y-axis
    s=70,
    alpha=1.0,
    label='Pareto',
)
plt.scatter(
    df_naive["Total subsidy ($)"],                          # X-axis
    df_naive["Total mob. Logsum increase with micro"],
    color='green',                                      # Y-axis
    s=70,
    alpha=1.0,
    label='Naive',
)

# Set labels and title
plt.xlabel("Total Subsidy ($)", fontsize=17)
plt.ylabel("Total Mobility Logsum Increase with Micro", fontsize=17)
plt.tick_params(labelsize=17)
plt.legend(title="Design type", fontsize=15)

# Display
plt.grid(True)
plt.tight_layout()
# plt.savefig("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/"
#             "lemon_grove_final_results/neive_fig.png", format="png", dpi=160,
#             bbox_inches="tight")
plt.show()
#############################################################################################
# # Make grid sit behind points
# plt.grid(True, zorder=0, linestyle='--', alpha=0.4)
#
# # Plot: use larger s, solid alpha, dark edge, and a halo
# p1 = plt.scatter(
#     df_pareto["Total subsidy ($)"],
#     df_pareto["Total mob. Logsum increase with micro"],
#     label='Pareto',            # <- for legend
#     color='#7D3C98',           # saturated purple
#     s=90,                      # a bit larger
#     alpha=0.95,
#     edgecolors='black',
#     linewidths=0.9,
#     zorder=3
# )
# p1.set_path_effects([pe.withStroke(linewidth=1.6, foreground='white')])
#
# p2 = plt.scatter(
#     df_naive["Total subsidy ($)"],
#     df_naive["Total mob. Logsum increase with micro"],
#     label='Naive',             # <- for legend
#     color='#1874D1',           # saturated blue
#     s=90,
#     alpha=0.95,
#     edgecolors='black',
#     linewidths=0.9,
#     zorder=3
# )
# p2.set_path_effects([pe.withStroke(linewidth=1.6, foreground='white')])
#
# # Labels
# plt.xlabel("Total Subsidy ($)", fontsize=17)
# plt.ylabel("Total Mobility Logsum Increase with Micro", fontsize=17)
# plt.tick_params(labelsize=15)
#
# # Legend box that stands out
# plt.legend(
#     title="Scenario",
#     loc='best',
#     frameon=True,
#     fancybox=True,
#     framealpha=0.95,
#     edgecolor='0.2',
#     markerscale=1.1
# )
#
# plt.tight_layout()
# plt.show()
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
##Parallel axis plot

# Define decision variables and objective to color by
decision_vars = [
    "Transit Fare ($)",
    "Micro distance based fare ($/mile)",
    "Micro start fare ($)",
    "Fleet size",
    "Peak fare factor",
    "Micro to fixed factor",
    "FRT Headway (min)"
]

decision_vars_1 = [
    "Transit\nFare ($)",
    "Micro dist.\nbased fare ($/mi)",
    "Micro start\nfare ($)",
    "Fleet size",
    "Peak\nfare factor",
    "Micro to\nfixed factor",
    "FRT\nHeadway (min)"
]

color_by = "transit_mode_share (%)"  # Here insert the exact column name for the csv file
color_by_1 = "Transit mode share (%)"     # Here insert the name you want to see on the color bar

# Extract raw values (no normalization)
decision_df = df_pareto[decision_vars].copy()
decision_df["FRT Headway (min)"] = numpy.log1p(decision_df["FRT Headway (min)"])
color_values = df_pareto[color_by].values

# Normalize color scale for colormap
norm = plt.Normalize(color_values.min(), color_values.max())
colors = cm.viridis(norm(color_values))

# Create figure and axis
fig, ax = plt.subplots(figsize=(13, 5), dpi=115)

# Plot each line on the axis, colored by normalized logsum
for i, row in decision_df.iterrows():
    ax.plot(decision_vars, row.values, color=colors[i], alpha=0.9)

# Add colorbar to this axis
sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.ax.tick_params(labelsize=15)
cbar.set_label(color_by_1, fontsize=15)

# More granular y-axis
y_min = decision_df.min().min()
y_max = decision_df.max().max()
step_size = (y_max - y_min) / 14  # Increase this denominator for finer ticks

ax.set_ylim(y_min, y_max)
ax.yaxis.set_major_locator(MultipleLocator(step_size))
ax.yaxis.set_minor_locator(AutoMinorLocator(2))  # Optional: finer minor ticks

# Final formatting
ax.set_ylabel("Value in Actual Units", size=15)
ax.tick_params(axis='y', labelsize=15)
ax.set_xticks(range(len(decision_vars)))
ax.set_xticklabels(decision_vars_1, rotation=0, size=15)
ax.grid(True, which='both', linestyle='--', linewidth=0.7)
# ax.grid(True)
plt.tight_layout()
plt.show()
# ----------------------------------------------------------------------------------------------------------------------
# TODO: From this point onwards the code is for backup only and are not used
# ----------------------------------------------------------------------------------------------------------------------
# decision_vars = [
#     "Transit Fare ($)",
#     "Micro distance based fare ($/mile)",
#     "Micro start fare ($)",
#     "Fleet size",
#     "Peak fare factor",
#     "Micro to fixed factor"
# ]
# # Panel labels
# panel_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']
# # Create a grid of subplots (3 rows, 2 columns)
# fig, axs = plt.subplots(3, 2, figsize=(15, 14))
# axs = axs.flatten()
# # Generate scatter plot for each decision variable
# for i, (var, label) in enumerate(zip(decision_vars, panel_labels)):
#     scatter = axs[i].scatter(
#         df["Total subsidy ($)"],
#         df["Total mob. Logsum increase with micro"],
#         c=df[var],
#         cmap="viridis",
#         alpha=0.9
#     )
#
#     axs[i].set_xlabel("Total Subsidy ($)", fontsize=16)
#     axs[i].set_ylabel("Mobility Logsum Increase", fontsize=16)
#     axs[i].tick_params(axis='both', labelsize=14)
#
#     axs[i].grid(True)
#
#     # Add subplot label below x-axis
#     axs[i].annotate(
#         label,
#         xy=(0.5, -0.25),
#         xycoords='axes fraction',
#         fontsize=16,
#         ha='center',
#         va='center'
#     )
#
#     # Add colorbar with larger fonts
#     cbar = fig.colorbar(scatter, ax=axs[i])
#     cbar.set_label(var, fontsize=16)
#     cbar.ax.tick_params(labelsize=14)
# # Adjust layout
# plt.tight_layout()
# plt.show()
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# plt.figure(figsize=(10, 6))
# scatter = plt.scatter(
#     df["Total subsidy ($)"],                          # X-axis
#     df["Total mob. Logsum increase with micro"],      # Y-axis
#     c=df["transit_mode_share (%)"],                   # Color
#     cmap="plasma",
#     s=50,
#     alpha=0.9
# )
#
# # Set labels and title
# plt.xlabel("Total Subsidy ($)", size=14)
# plt.ylabel("Total Mobility Logsum Increase with Micro", size=14)
# plt.tick_params(axis='x', labelsize=14)
# plt.tick_params(axis='y', labelsize=14)
# # plt.title("Pareto Frontier Colored by Transit Mode Share (%)")
#
# # Add colorbar
# cbar = plt.colorbar(scatter)
# cbar.ax.tick_params(labelsize=14)
# cbar.set_label("Transit Mode Share (%)", size=14)
#
# # Display
# plt.grid(True)
# plt.tight_layout()
# plt.show()

# ---------------------------------------------------------------------------------------------------------------------------------------------------
# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/sub_mob_logsum_28th_May_25/non_dominated_data_old_method.csv"
# # file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/Ax_25_cents_6_var_27th_Oct/optimization_result_new_method.csv"
# df = pd.read_csv(file)
# --------------------

# Define decision variables and objectives
# decision_vars = [
#     "Transit Fare ($)",
#     "Micro distance based fare ($/mile)",
#     "Micro start fare ($)",
#     "Fleet size",
#     "Peak fare factor",
#     "Micro to fixed factor"
# ]
#
# objectives = [
#     "Total mob. Logsum increase with micro",
#     "Total subsidy ($)"
# ]
#
# # Normalize decision variables
# scaler = MinMaxScaler()
# decision_data = scaler.fit_transform(df[decision_vars])
# decision_df_norm = pd.DataFrame(decision_data, columns=decision_vars)
#
# # Add back objectives for coloring and filtering
# decision_df_norm["Logsum"] = df["Total mob. Logsum increase with micro"]
# decision_df_norm["Subsidy"] = df["Total subsidy ($)"]
#
# # -------------------------------
# # 1. Run clustering on decision variables
# kmeans = KMeans(n_clusters=3, random_state=42)
# decision_df_norm["Cluster"] = kmeans.fit_predict(decision_data).astype(str)
#
# # -------------------------------
# # 2. Highlight high-logsum, low-subsidy solutions
# high_logsum_thresh = df["Total mob. Logsum increase with micro"].quantile(0.75)
# low_subsidy_thresh = df["Total subsidy ($)"].quantile(0.25)
# highlight_mask = (
#     (df["Total mob. Logsum increase with micro"] >= high_logsum_thresh) &
#     (df["Total subsidy ($)"] <= low_subsidy_thresh)
# )
# highlight_df = decision_df_norm[highlight_mask].copy()
# highlight_df["Cluster"] = "Highlight"
#
# # -------------------------------
# # 3. Combine all for plotting
# plot_df = pd.concat([decision_df_norm, highlight_df])
#
# # -------------------------------
# --------------------
# --------------------
# --------------------
# Create scatter plot

