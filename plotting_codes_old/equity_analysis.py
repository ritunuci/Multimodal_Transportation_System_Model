import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
# import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

# # Load your dataset
# file = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/sub_mob_logsum_28th_May_25/" \
#        "non_dominated_data_old_method - Copy.csv"
# df = pd.read_csv(file)
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
# silhouette_scores = {}
# K_range = range(2, 11)
#
# for k in K_range:
#     kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
#     labels = kmeans.fit_predict(X_scaled)
#     score = silhouette_score(X_scaled, labels)
#     silhouette_scores[k] = score
#
# print(silhouette_scores)
# ----------------------------------------------------------------------------------------------------------------------
# file_1 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/" \
#          "indv_res/indiv_res_optimization_itr_0.csv"
#
# file_2 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/" \
#          "indv_res/indiv_res_optimization_itr_1.csv"
# file_3 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/bayesian_journal_lemon_grove/" \
#          "indv_res/indiv_res_optimization_itr_2.csv"
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
# plt.hist(x1, bins=bins, alpha=0.4, edgecolor='black', label='Itr 0')
# plt.hist(x2, bins=bins, alpha=0.5, edgecolor='black', label='Itr 1')
# plt.hist(x3, bins=bins, alpha=0.5, edgecolor='black', label='Itr 2')
# plt.xlabel('Trip Distance (miles)')
# plt.ylabel('Number of Passengers')
# plt.title('Distribution of Trip Distances')
# plt.grid(True, linestyle='--', alpha=0.6)
# plt.legend()
# plt.show()
# ----------------------------------------------------------------------------------------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

file_1 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/test_folder/indv_res/indiv_res_optimization_itr_4.csv"
file_2 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/test_folder/indv_res/indiv_res_optimization_itr_5.csv"
file_3 = "D:/Ritun/Siwei_Micro_Transit/Bayesian_Optimization/optimization_output/test_folder/indv_res/indiv_res_optimization_itr_6.csv"

df_1 = pd.read_csv(file_1)
df_2 = pd.read_csv(file_2)
df_3 = pd.read_csv(file_3)  # only if you intend to use it

# keep positive distances only
df_1 = df_1[df_1['dist_M (mi)'] > 0]
df_2 = df_2[df_2['dist_M (mi)'] > 0]
df_3 = df_3[df_3['dist_M (mi)'] > 0]

x1 = df_1['dist_M (mi)'].to_numpy()
x2 = df_2['dist_M (mi)'].to_numpy()
x3 = df_3['dist_M (mi)'].to_numpy()

# Common bin edges
xmin = np.nanmin([x1.min(), x2.min(), x3.min()])
xmax = np.nanmax([x1.max(), x2.max(), x3.max()])
bins = np.linspace(xmin, xmax, 31)  # 30 bins

# Histogram + KDE overlay
plt.figure(figsize=(8,5))

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
plt.fill_between(grid, y1, alpha=0.25)
plt.fill_between(grid, y2, alpha=0.25)
plt.fill_between(grid, y3, alpha=0.25)

# curves on top
plt.plot(grid, y1, linewidth=2, label='Iteration 0', zorder=3)
plt.plot(grid, y2, linewidth=2, label='Iteration 1', zorder=3)
plt.plot(grid, y3, linewidth=2, label='Iteration 2', zorder=3)

plt.xlabel('Trip Distance (miles)', fontsize=12)
plt.ylabel('Density', fontsize=12)
plt.tick_params(axis='both', labelsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()