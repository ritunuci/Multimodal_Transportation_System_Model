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


#### K-meanns clustering

# Load your dataset
# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/" \
#        "non_dominated_data_old_method _Copy.csv"
# df = pd.read_csv(file)
# df_pareto = df[:23]
# df_naive = df[23:]


# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/" \
#        "bayesian_journal_lemon_grove_150sobol_400itr/non_dom_including_sobol.csv"
# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_fs_4_to_6/" \
#        "suppliment_3/non_dom_with_suppliment.csv"
file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/lemon_grove_final_results/" \
       "non_dom_with_suppliment.csv"

# file_1 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/" \
#        "non_dominated_data_old_method _Copy.csv"
df_pareto = pd.read_csv(file)
df_pareto["Total subsidy ($)"] = -df_pareto["Total subsidy ($)"]
# df_pareto = df_pareto[df_pareto["Total subsidy ($)"]<=16000]
# Define decision variables
decision_vars = [
    "Transit Fare ($)",
    "Micro distance based fare ($/mile)",
    "Micro start fare ($)",
    "Fleet size",
    "Peak fare factor",
    "Micro to fixed factor",
    "FRT Headway (min)"
]

# ----------------------------------------------------------------------------------------------------------------------
#### K-meanns clustering (new method)
#TODO: The following commented out part is not being used

# # exact column names (case-sensitive)
# col_subsidy = "Total subsidy ($)"
# col_logsum = "Total mob. Logsum increase with micro"
#
# # produce a list of [subsidy, logsum] for each row
# list_2 = df_pareto[[col_subsidy, col_logsum]].values.tolist()
# X = np.array(list_2, dtype=float)
#
# # 2) Drop rows with NaNs/Infs (just in case)
# mask = np.isfinite(X).all(axis=1)
# X = X[mask]
#
# # 3) Scale features so different magnitudes don't dominate
# scaler = StandardScaler()
# X_scaled = scaler.fit_transform(X)
#
# # --- Determine optimal k using silhouette scores ---
# sil_scores = []
# K_range = range(2, 10)  # Try cluster counts between 2 and 9 (you can change this)
#
# for k in K_range:
#     km = KMeans(n_clusters=k, n_init=50, random_state=23)
#     labels = km.fit_predict(X_scaled)
#     score = silhouette_score(X_scaled, labels)
#     sil_scores.append(score)
#     print(f"k = {k}, silhouette score = {score:.4f}")
#
# # Plot silhouette scores
# plt.figure(figsize=(8, 5),dpi=150)
# plt.plot(K_range, sil_scores, marker='o')
# plt.title("Silhouette Score vs Number of Clusters", fontsize=15)
# plt.xlabel("Number of Clusters (k)", fontsize=13)
# plt.ylabel("Silhouette Score", fontsize=13)
# plt.grid(True)
# plt.show()
#
# # Select k that maximizes silhouette score
# best_k = K_range[np.argmax(sil_scores)]
# print(f"Optimal number of clusters (k): {best_k}")
#
# # 4) K-means on scaled data
# k = best_k
# # k = 3
# km = KMeans(n_clusters=k, n_init=50, random_state=23)
# labels = km.fit_predict(X_scaled)
#
# # 5) Centers back on original scale
# centers_orig = scaler.inverse_transform(km.cluster_centers_)
#
# # 6) Build clusters dict: {idx: {'center': center, 'points': [array([...]), ...]}}
# clusters = {}
# for idx in range(k):
#     points_idx = np.where(labels == idx)[0]
#     clusters[idx] = {
#         'center': centers_orig[idx],
#         'points': X[points_idx].tolist()
#     }
#
#
# def distance(p1,p2):
#     return np.sqrt(np.sum((p1-p2)**2))
#
#
# def assign_clusters(X, clusters):
#     for idx in range(X.shape[0]):
#         dist = []
#
#         curr_x = X[idx]
#
#         for i in range(k):
#             dis = distance(curr_x, clusters[i]['center'])
#             dist.append(dis)
#         curr_cluster = np.argmin(dist)
#         clusters[curr_cluster]['points'].append(curr_x)
#     return clusters
#
#
# def update_clusters(X, clusters):
#     for i in range(k):
#         points = np.array(clusters[i]['points'])
#         if points.shape[0] > 0:
#             new_center = points.mean(axis=0)
#             clusters[i]['center'] = new_center
#
#             clusters[i]['points'] = []
#     return clusters
#
#
# def pred_cluster(X, clusters):
#     pred = []
#     for i in range(X.shape[0]):
#         dist = []
#         for j in range(k):
#             dist.append(distance(X[i],clusters[j]['center']))
#         pred.append(np.argmin(dist))
#     return pred
#
# clusters = assign_clusters(X, clusters)
# clusters = update_clusters(X, clusters)
# pred = pred_cluster(X, clusters)
#
#
# from matplotlib.colors import ListedColormap
# from matplotlib.lines import Line2D
#
# # Bright, high-contrast colors (0→red, 1→bright green, 2→vivid blue)
# cmap = ListedColormap(["#FF6F00",  # bright red
#                        "#00C853",  # bright green (Material A700)
#                        "#2979FF",   # vivid blue
#                        "#FF69B4"])  # hot pink
#
# plt.figure(figsize=(10, 7), dpi=150)
#
# sc = plt.scatter(
#     X[:, 0], X[:, 1],
#     c=pred, s=80, edgecolor="black", linewidth=0.8,
#     cmap=cmap, vmin=-0.5, vmax=2.5  # for 3 clusters: 0..2
# )
#
# # Centroids
# for i in clusters:
#     cx, cy = clusters[i]['center']
#     plt.scatter(cx, cy, marker='^', c='black', s=130,
#                 edgecolor="black", linewidth=0.8, zorder=3)
#
# plt.xlabel("Total Subsidy ($)", fontsize=17)
# plt.ylabel("Total mob. Logsum increase with micro", fontsize=17)
# plt.tick_params(labelsize=17)
# plt.grid(True)
#
# # Legend that matches the colors exactly
# handles = [
#     Line2D([0], [0], marker='o', linestyle='',
#            markerfacecolor=cmap(i), markeredgecolor='black',
#            markeredgewidth=0.8, markersize=9, label=f'Cluster {i}')
#     for i in range(2)
# ]
# handles.append(
#     Line2D([0], [0], marker='^', linestyle='',
#            markerfacecolor='black', markeredgecolor='black',
#            markeredgewidth=0.8, markersize=9, label='Centroid')
# )
#
# plt.legend(handles=handles, title='Clusters',
#            loc='upper left', bbox_to_anchor=(1.02, 1),
#            borderaxespad=0., frameon=True)
#
# plt.tight_layout()
# plt.show()
##########################################################
# TODO: This part is being used for K-means clustering calculation
col_subsidy = "Total subsidy ($)"
col_logsum = "Total mob. Logsum increase with micro"

# produce a list of [subsidy, logsum] for each row
list_2 = df_pareto[[col_subsidy, col_logsum]].values.tolist()
X = np.array(list_2, dtype=float)

# 2) Drop rows with NaNs/Infs (just in case)
mask = np.isfinite(X).all(axis=1)
X = X[mask]

# 3) Scale features so different magnitudes don't dominate
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Determine optimal k using silhouette scores ---
sil_scores = []
K_range = range(2, 10)  # Try cluster counts between 2 and 9 (you can change this)

for k in K_range:
    km = KMeans(n_clusters=k, n_init=50, random_state=23)
    labels = km.fit_predict(X_scaled)
    score = silhouette_score(X_scaled, labels)
    sil_scores.append(score)
    print(f"k = {k}, silhouette score = {score:.4f}")

# Plot silhouette scores
plt.figure(figsize=(8, 5),dpi=150)
plt.plot(K_range, sil_scores, marker='o')
plt.title("Silhouette Score vs Number of Clusters", fontsize=15)
plt.xlabel("Number of Clusters (k)", fontsize=13)
plt.ylabel("Silhouette Score", fontsize=13)
plt.grid(True)
plt.show()

# Select k that maximizes silhouette score
best_k = K_range[np.argmax(sil_scores)]
print(f"Optimal number of clusters (k): {best_k}")

# 4) K-means on scaled data
# k = best_k
k = 3
km = KMeans(n_clusters=k, n_init=50, random_state=23)
labels = km.fit_predict(X_scaled)

# 5) Centers back on original scale
centers_orig = scaler.inverse_transform(km.cluster_centers_)

# 6) Build clusters dict: {idx: {'center': center, 'points': [array([...]), ...]}}
clusters = {}
for idx in range(k):
    points_idx = np.where(labels == idx)[0]
    clusters[idx] = {
        'center': centers_orig[idx],
        'points': X[points_idx].tolist()
    }


def distance(p1,p2):
    return np.sqrt(np.sum((p1-p2)**2))


def assign_clusters(X, clusters):
    for idx in range(X.shape[0]):
        dist = []

        curr_x = X[idx]

        for i in range(k):
            dis = distance(curr_x, clusters[i]['center'])
            dist.append(dis)
        curr_cluster = np.argmin(dist)
        clusters[curr_cluster]['points'].append(curr_x)
    return clusters


def update_clusters(X, clusters):
    for i in range(k):
        points = np.array(clusters[i]['points'])
        if points.shape[0] > 0:
            new_center = points.mean(axis=0)
            clusters[i]['center'] = new_center

            clusters[i]['points'] = []
    return clusters


def pred_cluster(X, clusters):
    pred = []
    for i in range(X.shape[0]):
        dist = []
        for j in range(k):
            dist.append(distance(X[i],clusters[j]['center']))
        pred.append(np.argmin(dist))
    return pred

clusters = assign_clusters(X, clusters)
clusters = update_clusters(X, clusters)
pred = pred_cluster(X, clusters)


from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D

# Bright, high-contrast colors (0→red, 1→bright green, 2→vivid blue)
# cmap = ListedColormap(["#FF6F00",  # bright red
#                        "#00C853",  # bright green (Material A700)
#                        "#2979FF",
#                        "#FF69B4"])  # Blue      #TODO: To have more clusters, add more colors

# cmap = ListedColormap(["#FF6F00",  # bright red
#                        "#00C853",  # bright green (Material A700)
#                        "#2979FF"])  # Blue      #TODO: To have more clusters, add more colors

cmap = ListedColormap(["#2979FF",
                       "#FF6F00",
                       "#00C853"])

# cmap = ListedColormap(["#1f77b4",
#                        "#ff7f0e",
#                        "#2ca02c"])

plt.figure(figsize=(10, 7), dpi=150)

sc = plt.scatter(
    X[:, 0], X[:, 1],
    c=pred, s=80, edgecolor="black", linewidth=0.8,
    cmap=cmap, vmin=-0.5, vmax=k-0.5
)

# Centroids
for i in clusters:
    cx, cy = clusters[i]['center']
    plt.scatter(cx, cy, marker='^', c='black', s=130,
                edgecolor="black", linewidth=0.8, zorder=3)

plt.xlabel("Total Subsidy ($)", fontsize=17)
plt.ylabel("Total mob. Logsum increase with micro", fontsize=17)
plt.tick_params(labelsize=17)
plt.grid(True)

# Legend that matches the colors exactly
handles = [
    Line2D([0], [0], marker='o', linestyle='',
           markerfacecolor=cmap(i), markeredgecolor='black',
           markeredgewidth=0.8, markersize=9, label=f'Cluster {i}')
    for i in range(k)
]
handles.append(
    Line2D([0], [0], marker='^', linestyle='',
           markerfacecolor='black', markeredgecolor='black',
           markeredgewidth=0.8, markersize=9, label='Centroid')
)

plt.legend(handles=handles, title='Legend',
           loc='upper left', bbox_to_anchor=(1.02, 1),
           borderaxespad=0., frameon=True)

plt.tight_layout()
plt.savefig("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/"
            "lemon_grove_final_results/policy_cluster_new.png", format="png", dpi=160,
            bbox_inches="tight")
plt.show()
# # ------------------------------------------------------------------------------------
### For calculating the most representative points in the clusters from K-means clustering
orig_row_idx = np.flatnonzero(mask)  # positions in original df that survived the mask

rep_rows = []
for c in range(km.n_clusters):
    # indices for points in cluster c
    idxs = np.where(labels == c)[0]
    # distances in scaled space to the centroid of cluster c
    dists = np.linalg.norm(X_scaled[idxs] - km.cluster_centers_[c], axis=1)
    # representative (medoid) index within X
    rep_local = idxs[np.argmin(dists)]
    rep_point_orig = X[rep_local]  # [subsidy, logsum] on original scale
    rep_df_idx = orig_row_idx[rep_local]  # row index in df_pareto

    rep_rows.append({
        "cluster": c,
        "df_index": int(rep_df_idx),
        "Total subsidy ($)": float(rep_point_orig[0]),
        "Total mob. Logsum increase with micro": float(rep_point_orig[1])
    })

# Pretty print as a small DataFrame
rep_df = pd.DataFrame(rep_rows).sort_values("cluster").reset_index(drop=True)
print("Most representative point (medoid) per cluster:")
print(rep_df.to_string(index=False))
# ----------------------------------------------------------------------------------------------------------------------
#### Microtrasit trip length distribution by histogram
# rep_batch_nums = [23,42,89]
#
# file_1 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[0]}.csv'
#
# file_2 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[1]}.csv'
# file_3 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[2]}.csv'
#
# df_1 = pd.read_csv(file_1)
# df_2 = pd.read_csv(file_2)
# df_3 = pd.read_csv(file_3)
#
# df_1=df_1[df_1['dist_M (mi)']>0]
# df_2=df_2[df_2['dist_M (mi)']>0]
# df_3=df_3[df_3['dist_M (mi)']>0]
#
# x1 = df_1["dist_M (mi)"].values
# x2 = df_2["dist_M (mi)"].values
# x3 = df_3["dist_M (mi)"].values
#
# # Common bins across both datasets
# xmin = np.nanmin([x1.min(), x2.min(), x3.min()])
# xmax = np.nanmax([x1.max(), x2.max(), x3.max()])
# bins = np.linspace(xmin, xmax, 31)
#
# plt.figure(figsize=(8,5))
# plt.hist(x1, bins=bins, alpha=0.4, edgecolor='black', label=f'Itr {rep_batch_nums[0]}')
# plt.hist(x2, bins=bins, alpha=0.5, edgecolor='black', label=f'Itr {rep_batch_nums[1]}')
# plt.hist(x3, bins=bins, alpha=0.5, edgecolor='black', label=f'Itr {rep_batch_nums[2]}')
# plt.xlabel('Trip Distance (miles)')
# plt.ylabel('Number of Passengers')
# plt.title('Distribution of Trip Distances')
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.legend()
# plt.show()
# ----------------------------------------------------------------------------------------------------------------------
### Microtrasit trip length distribution by kernel density

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# rep_batch_nums = [23,42,89]
# rep_batch_nums = [23,60]
# rep_batch_nums = [431,778,596]      # Cluster 0, 1, and 2 # cluster numbers from fs_4_to_6 suppliment_2
# rep_batch_nums = [337,153,540]          # cluster numbers fron 150 sobol 400 itr
rep_batch_nums = [337,596,153]
# rep_batch_nums = [431,596,778]

if rep_batch_nums[0]<=150:
    file_1 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/indv_res/indiv_res_training_itr_{int(rep_batch_nums[0])}.csv'
elif rep_batch_nums[0]>150 and rep_batch_nums[0]<=550:
    file_1 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/indv_res/indiv_res_optimization_itr_{int(rep_batch_nums[0])-150}.csv'
else:
    file_1 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_fs_4_to_6/indv_res/indiv_res_optimization_itr_{int(rep_batch_nums[0])-550}.csv'


if rep_batch_nums[1]<=150:
    file_2 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/indv_res/indiv_res_training_itr_{int(rep_batch_nums[1])}.csv'
elif rep_batch_nums[1]>150 and rep_batch_nums[1]<=550:
    file_2 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/indv_res/indiv_res_optimization_itr_{int(rep_batch_nums[1])-150}.csv'
else:
    file_2 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_fs_4_to_6/indv_res/indiv_res_optimization_itr_{int(rep_batch_nums[1])-550}.csv'


if rep_batch_nums[2]<=150:
    file_3 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/indv_res/indiv_res_training_itr_{int(rep_batch_nums[2])}.csv'
elif rep_batch_nums[2]>150 and rep_batch_nums[2]<=550:
    file_3 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/indv_res/indiv_res_optimization_itr_{int(rep_batch_nums[2])-150}.csv'
else:
    file_3 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_fs_4_to_6/indv_res/indiv_res_optimization_itr_{int(rep_batch_nums[2])-550}.csv'



# file_1 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[0]}.csv'
#
# file_2 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[1]}.csv'
# file_3 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove_150sobol_400itr/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[2]}.csv'

df_1 = pd.read_csv(file_1)
df_2 = pd.read_csv(file_2)
df_3 = pd.read_csv(file_3)  # only if you intend to use it

# keep positive travel times only
df_1 = df_1[df_1['tt_M (s)'] > 0]
df_2 = df_2[df_2['tt_M (s)'] > 0]
df_3 = df_3[df_3['tt_M (s)'] > 0]

x1 = df_1['dist_M (mi)'].to_numpy()
x2 = df_2['dist_M (mi)'].to_numpy()
x3 = df_3['dist_M (mi)'].to_numpy()

# Common bin edges
xmin = np.nanmin([x1.min(), x2.min(), x3.min()])
xmax = np.nanmax([x1.max(), x2.max(), x3.max()])
# xmin = np.nanmin([x1.min(), x2.min()])
# xmax = np.nanmax([x1.max(), x2.max()])
bins = np.linspace(xmin, xmax, 10)  # 30 bins

# Histogram + KDE overlay
plt.figure(figsize=(8,5),dpi=150)

# # normalized histograms for fair shape comparison
# plt.hist(x1, bins=bins, density=True, alpha=0.4, edgecolor='black', label='Group 1')
# plt.hist(x2, bins=bins, density=True, alpha=0.4, edgecolor='black', label='Group 2')

# KDE curves on a smooth grid
grid = np.linspace(xmin, xmax, 400)
kde1 = gaussian_kde(x1)
kde2 = gaussian_kde(x2)
kde3 = gaussian_kde(x3)
y1 = kde1(grid)
y2 = kde2(grid)
y3 = kde3(grid)

# shaded areas
# plt.fill_between(grid, y1, alpha=0.25, color='orange')
# plt.fill_between(grid, y2, alpha=0.25, color='green')
# plt.fill_between(grid, y3, alpha=0.25, color='cyan')

# plt.fill_between(grid, y1, alpha=0.25, color='#1f77b4')
# plt.fill_between(grid, y2, alpha=0.25, color='#ff7f0e')
# plt.fill_between(grid, y3, alpha=0.25, color='#2ca02c')
#
# # curves on top
# plt.plot(grid, y1, linewidth=2, label=f'Cluster 0', zorder=3, color='#1f77b4')
# plt.plot(grid, y2, linewidth=2, label=f'Cluster 1', zorder=3, color='#ff7f0e')
# plt.plot(grid, y3, linewidth=2, label=f'Cluster 2', zorder=3, color='#2ca02c')

plt.fill_between(grid, y1, alpha=0.25, color='#1f77b4')
plt.fill_between(grid, y2, alpha=0.25, color='#ff7f0e')
plt.fill_between(grid, y3, alpha=0.25, color='#2ca02c')

# curves on top
plt.plot(grid, y1, linewidth=2, label=f'Cluster 0', zorder=3, color='#1f77b4')
plt.plot(grid, y2, linewidth=2, label=f'Cluster 1', zorder=3, color='#ff7f0e')
plt.plot(grid, y3, linewidth=2, label=f'Cluster 2', zorder=3, color='#2ca02c')

plt.xlabel('Trip Distance (miles)', fontsize=12)
plt.ylabel('Density', fontsize=12)
plt.tick_params(axis='both', labelsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig("D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/"
            "lemon_grove_final_results/trip_len_dist_2_clusters_lg.png", format="png", dpi=160,
            bbox_inches="tight")
plt.show()

# ----------------------------------------------------------------------------------------------------------------------
#TODO: This part is not being used for income quartile analysis anymore. Please check equity_analysis_part_2.py

# #### For income quartile analysis
#
# rep_batch_nums = [60,23]
#
# file_1 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[0]}.csv'
#
# file_2 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/' \
#          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[1]}.csv'
# # file_3 = f'D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/' \
# #          f'indv_res/indiv_res_optimization_itr_{rep_batch_nums[2]}.csv'
#
# df_1 = pd.read_csv(file_1)
# df_2 = pd.read_csv(file_2)
# # df_3 = pd.read_csv(file_3)  # only if you intend to use it
#
# # keep positive distances only
# df_1 = df_1[df_1['dist (mi)'] > 0]
# df_2 = df_2[df_2['dist (mi)'] > 0]
# # df_3 = df_3[df_3['dist (mi)'] > 0]
#
#
# def income_quartile_summary(
#     df,
#     income_col='income (USD)',
#     dist_M='dist_M (mi)',
#     dist_C='dist_C (mi)',
#     cost_col='out_of_pock_cost ($)',
#     mob_log_sum='mob_logsum_increased_with_micro'
# ):
#     d = df[[income_col, dist_M, dist_C, cost_col, mob_log_sum]].dropna(subset=[income_col, cost_col]).copy()
#
#     # 1) Build quartiles without labels so we can read interval bounds (handles duplicates='drop')
#     quartile_cats = pd.qcut(d[income_col], 4, labels=None, duplicates='drop')  # categorical of intervals
#     intervals = quartile_cats.cat.categories
#     n_q = len(intervals)
#     labels = [f"Q{i+1}" for i in range(n_q)]
#
#     # Map interval categories to Q1..Qk
#     d['income_quartile'] = pd.Categorical.from_codes(quartile_cats.cat.codes, labels, ordered=True)
#
#     # A small table of the edges that define each quartile
#     quartile_edges = pd.DataFrame({
#         'income_quartile': labels,
#         'lower_bound': [iv.left for iv in intervals],
#         'upper_bound': [iv.right for iv in intervals],
#         'closed': [intervals.closed] * n_q  # usually 'right'
#     })
#
#     # Also useful to see the raw quantiles:
#     raw_quantiles = d[income_col].quantile([0.00, 0.25, 0.50, 0.75, 1.00]).rename('value').reset_index()
#     raw_quantiles.rename(columns={'index': 'quantile'}, inplace=True)
#
#     # 2) Grouped summaries
#     g = d.groupby('income_quartile', observed=True)
#
#     nz_M = (
#         g[dist_M]
#         .apply(lambda s: (s > 0).sum())
#         .rename('Number of micro trips')
#         .reset_index()
#     )
#
#     nz_C = (
#         g[dist_C]
#         .apply(lambda s: (s > 0).sum())
#         .rename('Number of car trips')
#         .reset_index()
#     )
#
#     mean_cost = (
#         g[cost_col]
#         .mean()
#         .rename('Mean out_of_pocket_cost')
#         .reset_index()
#     )
#
#     tot_mob_logsum_incr = (
#         g[mob_log_sum]
#         .sum()
#         .rename('tot_mob_logsum_incr')
#         .reset_index()
#     )
#
#     summary = (
#         nz_M.merge(nz_C, on='income_quartile')
#             .merge(mean_cost, on='income_quartile')
#             .merge(tot_mob_logsum_incr, on='income_quartile')
#             .sort_values('income_quartile')
#             .reset_index(drop=True)
#     )
#
#     # Print the quartile-defining income values
#     print("\nIncome quartile edges:")
#     for q, lo, hi in zip(quartile_edges['income_quartile'], quartile_edges['lower_bound'], quartile_edges['upper_bound']):
#         print(f"  {q}: [{lo:.2f}, {hi:.2f}]")
#
#     return nz_M, nz_C, mean_cost, summary, quartile_edges, raw_quantiles
#
# nz_M0, nz_C0, mean_cost0, summary0, quartile_edges0, raw_quantiles0 = income_quartile_summary(df_1)
# print("\nSummary by income quartile file 0:")
# print(summary0)
#
# nz_M1, nz_C1, mean_cost1, summary1, quartile_edges1, raw_quantiles1 = income_quartile_summary(df_2)
# print("\nSummary by income quartile file 1:")
# print(summary1)
#
# # nz_M2, nz_C2, mean_cost2, summary2, quartile_edges2, raw_quantiles2 = income_quartile_summary(df_3)
# # print("\nSummary by income quartile file 2:")
# # print(summary2)
#
#
# def plot_summaries_grid(summary_list, titles):
#     # summary columns expected:
#     # ['income_quartile','Number of micro trips','Number of car trips',
#     #  'Mean out_of_pocket_cost','tot_mob_logsum_incr']
#     quartiles = ['Q1', 'Q2', 'Q3', 'Q4']
#     nrows = len(summary_list)
#     fig, axes = plt.subplots(nrows=nrows, ncols=3, figsize=(14, 4 * nrows), constrained_layout=True, dpi=150)
#
#     if nrows == 1:
#         axes = np.array([axes])  # unify indexing
#
#     for r, (summary, title) in enumerate(zip(summary_list, titles)):
#         s = summary.copy()
#         # ensure quartile order
#         s['income_quartile'] = pd.Categorical(s['income_quartile'], categories=quartiles, ordered=True)
#         s = s.sort_values('income_quartile')
#
#         x = np.arange(len(s))
#         # ---- (1) counts: grouped bars
#         ax = axes[r, 0]
#         w = 0.35
#         ax.bar(x - w / 2, s['Number of micro trips'].values, width=w, label='Micro')
#         ax.bar(x + w / 2, s['Number of car trips'].values, width=w, label='Car')
#         ax.set_xticks(x);
#         ax.set_xticklabels(s['income_quartile'].astype(str))
#         ax.set_title(f"{title}", fontsize = 15)
#         ax.set_ylabel("Trips count", fontsize=15)
#         ax.tick_params(axis='both', labelsize=15)
#         ax.set_yscale('log')
#         ax.legend()
#
#         # ---- (2) mean cost
#         ax = axes[r, 1]
#         ax.bar(x, s['Mean out_of_pocket_cost'].values)
#         ax.set_xticks(x);
#         ax.set_xticklabels(s['income_quartile'].astype(str))
#         ax.set_title(f"{title}", fontsize = 15)
#         ax.set_ylabel("Mean out-of-pocket \n cost (USD)", fontsize=15)
#         ax.tick_params(axis='both', labelsize=15)
#
#         # ---- (3) total mobility logsum increase
#         ax = axes[r, 2]
#         ax.bar(x, s['tot_mob_logsum_incr'].values)
#         ax.set_xticks(x);
#         ax.set_xticklabels(s['income_quartile'].astype(str))
#         ax.set_title(f"{title}", fontsize = 15)
#         ax.set_ylabel("Total mobility \n logsum increase", fontsize=15)
#         ax.tick_params(axis='both', labelsize=15)
#         # Optional if one bar is much larger: uncomment to see small bars too
#         ax.set_yscale('log')
#
#     plt.show()
#
# plot_summaries_grid([summary0, summary1], ["Cluster 0", "Cluster 1"])