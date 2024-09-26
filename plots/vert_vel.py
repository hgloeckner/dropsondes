# %%
import xarray as xr
import os
import matplotlib.pyplot as plt
import seaborn as sns

# %%
folder = "complete"

l4_path = (
    f"/Users/helene/Documents/Data/Dropsonde/{folder}/products/HALO/dropsondes/Level_4/"
)

ds_lev4 = xr.open_dataset(
    os.path.join(l4_path, "PERCUSION_Level_4.zarr"), engine="zarr"
)
# %%


def assign_island(lon):
    if lon > -40:
        return "SAL"
    else:
        return "BB"


island = ds_lev4.aircraft_longitude.to_series().apply(assign_island)
circle_island = ds_lev4.circle_lon.to_series().apply(assign_island)
ds_island = xr.DataArray(island, dims="sonde_id", name="island")
c_island = xr.DataArray(circle_island, dims="circle_id", name="c_island")
ds = ds_lev4.assign_coords(island=ds_island, c_island=c_island).sortby("launch_time")
# %%
ds_outlier = ["20240829_center", "20240818_center"]
# %%
ds_omega = ds.omega.interpolate_na(dim="alt")

fig, ax = plt.subplots()

ds_omega.where(ds_omega.c_island == "SAL").mean("circle_id").plot(
    y="alt", label="SAL mean", color="#FF6F00"
)

ds_out = (
    ds_omega.where(ds_omega.c_island == "SAL")
    .median("circle_id")
    .plot(y="alt", label="SAL median", color="#FF6F00", linestyle="--")
)

ds_omega.where(ds_omega.c_island == "BB").mean("circle_id").plot(
    y="alt", label="BB mean", color="#33691E"
)
ds_out = (
    ds_omega.where(ds_omega.c_island == "BB")
    .median("circle_id")
    .plot(y="alt", label="BB median", color="#33691E", linestyle="--")
)
ax.set_ylabel("altitude / m")

sns.despine(offset=10)
ax.legend()
fig.tight_layout()

# %%
quicklook_path = "/Users/helene/Documents/Data/Dropsonde/orcestra_plots"

fig.savefig(f"{quicklook_path}/omega.png", transparent=True)
