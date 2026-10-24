import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.ticker import MultipleLocator, AutoMinorLocator


# Load your file
file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/sub_mob_logsum_28th_May_25/" \
       "non_dominated_data_old_method - Copy.csv"
df = pd.read_csv(file)

# ----------------------------------------------------------------------------------------------------------------------
### Pareto front plotting

plt.figure(figsize=(10, 6))
plt.scatter(
    df["Total subsidy ($)"],                          # X-axis
    df["Total mob. Logsum increase with micro"],
    color='purple',                                      # Y-axis
    s=70,
    alpha=1.0
)

# Set labels and title
plt.xlabel("Total Subsidy ($)", fontsize=17)
plt.ylabel("Total Mobility Logsum Increase with Micro", fontsize=17)
plt.tick_params(labelsize=17)

# Display
plt.grid(True)
plt.tight_layout()
plt.show()

# ----------------------------------------------------------------------------------------------------------------------
### Parallel axis plot

# # Define decision variables and objective to color by
# decision_vars = [
#     "Transit Fare ($)",
#     "Micro distance based fare ($/mile)",
#     "Micro start fare ($)",
#     "Fleet size",
#     "Peak fare factor",
#     "Micro to fixed factor"
# ]
#
# decision_vars_1 = [
#     "Transit Fare ($)",
#     "Micro dist.\nbased fare ($/mile)",
#     "Micro start fare ($)",
#     "Fleet size",
#     "Peak fare factor",
#     "Micro to\nfixed factor"
# ]
#
# color_by = "Total subsidy ($)"
# color_by_1 = "Total subsidy ($)"
#
# # Extract raw values (no normalization)
# decision_df = df[decision_vars].copy()
# color_values = df[color_by].values
#
# # Normalize color scale for colormap
# norm = plt.Normalize(color_values.min(), color_values.max())
# colors = cm.viridis(norm(color_values))
#
# # Create figure and axis
# fig, ax = plt.subplots(figsize=(15, 6))
#
# # Plot each line on the axis, colored by normalized logsum
# for i, row in decision_df.iterrows():
#     ax.plot(decision_vars, row.values, color=colors[i], alpha=0.9)
#
# # Add colorbar to this axis
# sm = plt.cm.ScalarMappable(cmap="viridis", norm=norm)
# sm.set_array([])
# cbar = fig.colorbar(sm, ax=ax)
# cbar.ax.tick_params(labelsize=17)
# cbar.set_label(color_by_1, fontsize=17)
#
# # More granular y-axis
# y_min = decision_df.min().min()
# y_max = decision_df.max().max()
# step_size = (y_max - y_min) / 14  # Increase this denominator for finer ticks
#
# ax.set_ylim(y_min, y_max)
# ax.yaxis.set_major_locator(MultipleLocator(step_size))
# ax.yaxis.set_minor_locator(AutoMinorLocator(2))  # Optional: finer minor ticks
#
# # Final formatting
# ax.set_ylabel("Value in Actual Units", size=17)
# ax.tick_params(axis='y', labelsize=15)
# ax.set_xticks(range(len(decision_vars)))
# ax.set_xticklabels(decision_vars_1, rotation=0, size=17)
# ax.grid(True, which='both', linestyle='--', linewidth=0.7)
# plt.tight_layout()
# plt.show()

# ----------------------------------------------------------------------------------------------------------------------
# ### K-means clustering plotting
#
# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
# from sklearn.preprocessing import StandardScaler
# from sklearn.cluster import KMeans
#
# # Load your dataset
# df = pd.read_csv("non_dominated_data_old_method.csv")
#
# # Define decision variables
# decision_vars = [
#     "Transit Fare ($)",
#     "Micro distance based fare ($/mile)",
#     "Micro start fare ($)",
#     "Fleet size",
#     "Peak fare factor",
#     "Micro to fixed factor"
# ]
#
# # Standardize
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(df[decision_vars])
#
# # KMeans clustering
# kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
# df['cluster'] = kmeans.fit_predict(X_scaled)
#
# # Visualization
# plt.figure(figsize=(10, 7))
# sns.scatterplot(
#     data=df,
#     x="Total subsidy ($)",
#     y="Total mob. Logsum increase with micro",
#     hue="cluster",
#     palette="Set2",
#     s=80,
#     edgecolor="k"
# )
#
# plt.xlabel("Total Subsidy ($)", fontsize=14)
# plt.ylabel("Mobility Logsum Increase", fontsize=14)
# plt.title("Policy Clustering Based on Decision Variables", fontsize=16)
# plt.legend(title="Cluster", fontsize=12)
# plt.grid(True)
# plt.tight_layout()
# plt.show()
#
# # Summary stats
# cluster_summary = df.groupby('cluster')[decision_vars].mean()
# print(cluster_summary)
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

