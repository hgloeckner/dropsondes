# %%
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# %%

old_cid = "latest.orcestra-campaign.org"
new_cid = "QmNywDWEPwZhrKzibE2Wgn8RU16VDgxakPtFFqzFAxMUPn"
old_l3 = xr.open_dataset(
    f"ipns://{old_cid}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
old_l4 = xr.open_dataset(
    f"ipns://{old_cid}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)
new_l3 = xr.open_dataset(
    "~/Documents/Data/Dropsonde/dropsonde_data/products/Level_3/PERCUSION_Level_3.zarr",
    # f"ipfs://{new_cid}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
new_l4 = xr.open_dataset(
    # f"ipfs://{new_cid}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    "~/Documents/Data/Dropsonde/dropsonde_data/products/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)

# %% plot iwv histograms to check if they are plausible/similar
fig, ax = plt.subplots()

sns.histplot(new_l3.iwv, ax=ax, bins=30, label="new")
sns.histplot(old_l3.iwv, ax=ax, bins=30, label="old")

# %% check that l4 and l3 are identical wherever l4 is not interpolated
for sonde in new_l4.sonde_id.values:
    assert not np.any(
        np.abs(
            (
                new_l4.swap_dims({"sonde": "sonde_id"}).u.sel(sonde_id=sonde)
                - new_l3.swap_dims({"sonde": "sonde_id"}).u.sel(sonde_id=sonde)
            )
        )
        > 0
    )
    assert not np.any(
        np.abs(
            (
                new_l4.swap_dims({"sonde": "sonde_id"}).rh.sel(sonde_id=sonde)
                - new_l3.swap_dims({"sonde": "sonde_id"}).rh.sel(sonde_id=sonde)
            )
        )
        > 0
    )
# %% check that l4 is interpolated and l3 is not
fig, ax = plt.subplots()
new_l3.ta.sel(altitude=slice(0, 1000)).plot()
plt.show()
new_l4.ta.sel(altitude=slice(0, 1000)).plot()

# %% check that l4 and l3 are not extrapolated at high altitudes
fig, ax = plt.subplots()
new_l3.ta.sel(altitude=slice(13000, None)).plot()
plt.show()
new_l4.ta.sel(altitude=slice(13000, None)).plot()
# %%
fig, ax = plt.subplots()
new_l4.omega.mean(dim="circle").plot(
    ax=ax, label="new", y="altitude", linestyle="", marker="o", markersize=2
)
ax.fill_betweenx(
    new_l4.altitude,
    new_l4.omega.quantile(0.25, dim="circle"),
    new_l4.omega.quantile(0.75, dim="circle"),
    alpha=0.3,
)

old_l4.omega.mean(dim="circle").plot(
    ax=ax, label="old", y="altitude", linestyle="", marker="o", markersize=2
)
ax.fill_betweenx(
    old_l4.altitude,
    old_l4.omega.quantile(0.25, dim="circle"),
    old_l4.omega.quantile(0.75, dim="circle"),
    alpha=0.3,
)
ax.legend()
