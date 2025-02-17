# %%
import matplotlib.pyplot as plt
import seaborn as sns
import xhistogram.xarray as xh
import xarray as xr
import numpy as np

# %%

root = "ipfs://QmQgxdRzcsGsf2Whp5A4fa5x7vYHYHNwjUEgPJdzzTgz5U"
ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3_qc/PERCUSION_Level_3.zarr", engine="zarr"
)
# %%
colors = ["#a3b4d8", "#00267f", "#6d88bc", "#ffc726"]

nb_bins = 50
variables = ["u", "rh", "p", "ta"]
bins_fullness = np.linspace(0, 1, nb_bins)
bins_count = np.linspace(0, 210, nb_bins)
bins_extend = np.linspace(0, 15000, nb_bins)
var = variables[0]

fig, axes = plt.subplots(ncols=3, figsize=(18, 6))
for var, color in zip(variables, colors):
    h_fullness = xh.histogram(
        ds[var + "_profile_sparsity_fraction"], bins=[bins_fullness]
    )
    ds[var + "_profile_sparsity_fraction"].plot.hist(
        ax=axes[0], color=color, label=var, histtype="step", bins=bins_fullness
    )
    ds[var + "_near_surface_count"].plot.hist(
        bins=bins_count, histtype="step", color=color, ax=axes[1], label=var
    )
    ext = ds[var + "_profile_extent_max"]
    ext.name = "extent"
    h_extend = xh.histogram(ext, bins=[bins_extend])
    ds[var + "_profile_extent_max"].plot.hist(
        ax=axes[2], color=color, label=var, histtype="step", bins=bins_extend
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
fig.savefig(
    "../images/qc_distribution.png",
)
