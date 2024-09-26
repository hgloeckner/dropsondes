# %%
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import sys
import numpy as np

sys.path.append("./")
sys.path.append("../")


# %%

# %%
l4_path = "/Users/helene/Documents/Data/Dropsonde/complete/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr"
ds_lev4 = xr.open_dataset(l4_path, engine="zarr")
# %%

ds = ds_lev4.sortby("circle_id")

# %%

df = (
    ds["div"].to_pandas()
    #    .reset_index()
)
# %%
new_index = df.index.str.split("_", expand=True)
df.set_index(new_index, inplace=True)
# %%

df_pivot = df.stack().reset_index()

# %%
pivot_df = df_pivot.pivot_table(index="alt", columns=["level_0", "level_1"], values=0)

# %%
fig, ax = plt.subplots(ncols=1, figsize=(24, 6))
im = sns.heatmap(pivot_df, cmap="cmo.balance", ax=ax, center=0)


xticks = ax.get_xticks()
borders = [(xticks[i] + xticks[i + 1]) / 2 for i in range(len(xticks) - 1)]

unique_ids = sorted(set(date for date, name in pivot_df.columns))
major_ticks = [
    np.mean([i for i, (date, name) in enumerate(pivot_df.columns) if date == unique_id])
    + 0.5
    for unique_id in unique_ids
]
labels = ["\n" * (i % 2) + unique_id for i, unique_id in enumerate(unique_ids)]
ax.set_xticks(major_ticks, labels=labels, rotation=0, fontsize=12, fontweight="bold")
ax.set_ylabel("")

ax.invert_yaxis()
y_ticks = np.arange(0, len(df.columns), 150)
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_ticks)
ax.set_ylabel("altitude / m")

border_pos = [
    [i for i, (date, name) in enumerate(pivot_df.columns) if date == unique_id][0]
    for unique_id in unique_ids
]
for border in border_pos:
    ax.axvline(border, color="black")
fig.tight_layout()

# %%
quicklook_path = "/Users/helene/Documents/Data/Dropsonde/orcestra_plots"

fig.savefig(f"{quicklook_path}/divergence.png", transparent=True)
