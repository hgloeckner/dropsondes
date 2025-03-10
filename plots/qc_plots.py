# %%
import matplotlib.pyplot as plt
import seaborn as sns
import xarray as xr
import numpy as np

# %%

root = "ipfs://QmQgxdRzcsGsf2Whp5A4fa5x7vYHYHNwjUEgPJdzzTgz5U"
ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3_qc/PERCUSION_Level_3.zarr", engine="zarr"
)

# %%
ds = xr.open_dataset(
    "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/products/Level_3_qc/PERCUSION_Level_3.zarr"
)
# %%
colors = ["#a3b4d8", "#00267f", "#ffc726"]

nb_bins = 50
variables = ["u", "rh", "ta"]
bins_fullness = np.linspace(0, 1, nb_bins)
bins_count = np.linspace(0, 210, nb_bins)
bins_extend = np.linspace(0, 15000, nb_bins)
var = variables[0]

fig, axes = plt.subplots(ncols=3, figsize=(9, 3))
for var, color in zip(variables, colors):
    sns.histplot(
        ds[var + "_profile_sparsity_fraction"],
        bins=100,
        stat="probability",
        alpha=0.5,
        label=var,
        color=color,
        kde=True,
        element="step",
        ax=axes[0],
    )

    sns.histplot(
        ds[var + "_near_surface_count"],
        bins=100,
        stat="probability",
        alpha=0.5,
        label=var,
        color=color,
        kde=True,
        element="step",
        ax=axes[1],
    )
    sns.histplot(
        ds[var + "_profile_extent_max"],
        bins=100,
        stat="probability",
        alpha=0.5,
        binrange=(0, 15000),
        label=var,
        color=color,
        # kde=True,
        element="step",
        ax=axes[2],
    )


ax = axes[0]
ax.set_xlabel("Profile Sparsity Fraction")
ax.set_ylabel("Number of Sondes")
# ax.set_xlim(0.5, 1)
ax.legend()
ax.axvline(0.2, color="gray", alpha=0.5)
ax = axes[1]
ax.set_ylabel("")
ax.set_xlabel("Number of Near-Surface Measurements")
ax.axvline(50, color="gray", alpha=0.5)
ax.legend()
ax = axes[2]
ax.set_ylabel("")
ax.set_xlabel("Profile Extent / m")
ax.legend()
ax.axvline(8000, color="gray", alpha=0.5)
# ax.set_xlim(0, 0.5)
sns.despine(offset=10)
fig.tight_layout()
fig.savefig(
    "../images/qc_distribution.pdf",
)
