# %%
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import sys
import os
import numpy as np
import pandas as pd

sys.path.append("./")
sys.path.append("../")


# %%

# %%
l4_path = "/Users/helene/Documents/Data/Dropsonde/complete/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.nc"
ds_lev4 = xr.open_dataset(l4_path)
# %%


# Define a custom order for the positions
custom_order = ["south", "center", "north", "west"]  # Example custom order

# Convert the dataset to a DataFrame for easier manipulation
df = (
    (-ds_lev4["div"])
    .sel(position=["south", "north", "center", "west"])
    .to_dataframe()
    .reset_index()
)
# Sort the DataFrame based on the custom order of positions
df["position"] = pd.Categorical(df["position"], categories=custom_order, ordered=True)
df = df.sort_values("position")

pivot_df = df.pivot_table(index="alt", columns=["flight_id", "position"], values="div")

# Create the heatmap plot
fig, ax = plt.subplots(ncols=1, figsize=(18, 6))
sns.heatmap(pivot_df, cmap="cmo.balance_r", center=0)


# Set minor ticks for positions
minor_ticks = np.arange(len(pivot_df.columns)) + 0.5
ax.set_xticks(minor_ticks, minor=True)
ax.set_xticklabels([f"{pos}" for id, pos in pivot_df.columns], minor=True, rotation=90)

# Set major ticks for ids
unique_ids = sorted(set(id for id, pos in pivot_df.columns))
major_ticks = [
    np.mean([i for i, (id, pos) in enumerate(pivot_df.columns) if id == unique_id])
    + 0.5
    for unique_id in unique_ids
]
ax.set_xticks(major_ticks)
ax.set_xticklabels(unique_ids, rotation=0, fontsize=12, fontweight="bold")

# Customize the appearance of the ticks
ax.tick_params(axis="x", which="major", pad=15)
ax.tick_params(axis="x", which="minor", length=5, width=1)

# Reduce the number of y-ticks to show only every fifth tick
y_ticks = np.arange(0, len(pivot_df.index), 200)
ax.set_yticks(y_ticks)
ax.set_yticklabels(pivot_df.index[y_ticks])
ax.invert_yaxis()
"""
for i in range(1, len(unique_ids)):
    pos = minor_ticks[i * len(pivot_df.columns.levels[1])]
    ax.axvline(pos, color="black", linestyle="--", linewidth=1)
"""

# Adjust the plot to make room for the labels
plt.xlabel("")
plt.ylabel("height")
plt.title("Convergence (blue); Divergence (red)")

plt.tight_layout()

quicklook_path = os.path.dirname(l4_path.replace("Level_4", "Quicklooks"))
os.makedirs(quicklook_path, exist_ok=True)
fig.savefig(f"{quicklook_path}/divergence.png", dpi=200)
