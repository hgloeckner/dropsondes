# %%
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import numpy as np


# %%

root = "ipfs://QmYfaiyryTLJYuju27cys7FXenBpEdh3FWV47Sa49BCHs5"
ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
)


# %%

gordon = ds.where(
    (ds.sonde_time > np.datetime64("2024-09-11"))
    & (ds.sonde_time < np.datetime64("2024-09-21")),
    drop=True,
)
non_gordon = ds.where(
    (ds.sonde_time < np.datetime64("2024-09-11"))
    | (ds.sonde_time > np.datetime64("2024-09-21")),
    drop=True,
)

# %% wind direction

ds_sfc = non_gordon.sel(altitude=slice(0, 50)).mean("altitude")

# ds_sfc = ds_sfc.where((ds_sfc.sonde_time < np.datetime64("2024-09-28")) | (ds_sfc.sonde_time > np.datetime64("2024-09-29")), drop=True)

plt.style.use("./beach.mplstyle")
lon_min, lon_max, lat_min, lat_max = -65, -15, 0, 23  # -15
cmap = "twilight_shifted"

fig, ax = plt.subplots(
    figsize=(10.5, 6), subplot_kw=dict(projection=ccrs.PlateCarree())
)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.25)
gl.top_labels = False
gl.right_labels = False
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor="black", facecolor="lightgrey")

ax.set_title("Surface wind direction")

p = ax.scatter(
    ds_sfc.lon.values, ds_sfc.lat.values, c=ds_sfc.w_dir, cmap=cmap, vmin=0, vmax=360
)

ax1 = fig.add_axes((0.88, 0.2, 0.1, 0.1), projection="polar")

azimuths = np.arange(0, 361, 1)
zeniths = np.arange(40, 70, 1)
values = azimuths * np.ones((30, 361))
ax1.pcolormesh(azimuths * np.pi / 180.0, zeniths, values, cmap=cmap)
ax1.set_yticklabels("")
ax1.set_theta_zero_location("N")
ax1.set_theta_direction(-1)
ax1.set_xticks(np.deg2rad([0, 45, 90, 135, 180, 225, 270, 315]))
ax1.set_xticklabels(["N", "", "E", "", "S", "", "W", ""])
ax1.tick_params(axis="x", which="major", pad=-1)
ax1.grid(False)

fig.tight_layout()
fig.savefig("../images/no_gordon_w_dir.png", dpi=300)

# %%
ds_iwv = non_gordon.iwv

plt.style.use("./beach.mplstyle")
lon_min, lon_max, lat_min, lat_max = -65, -15, 0, 23
cmap = "BrBG"  # "cmo.tarn"

fig, ax = plt.subplots(
    figsize=(10.5, 6), subplot_kw=dict(projection=ccrs.PlateCarree())
)
gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.25)
gl.top_labels = False
gl.right_labels = False
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor="black", facecolor="lightgrey")

ax.set_title("Integrated water vapor")

p = ax.scatter(
    ds_iwv.aircraft_longitude.values,
    ds_iwv.aircraft_latitude.values,
    c=ds_iwv,
    cmap=cmap,
    vmin=25,
    vmax=71,
)

cax = fig.add_axes((0.92, 0.15, 0.02, 0.3))
cb = fig.colorbar(p, cax=cax, ticks=[30, 48, 55, 70], extend="max")


fig.tight_layout()
fig.savefig("../images/non_gordon_map_iwv.png", dpi=300)

# %%
