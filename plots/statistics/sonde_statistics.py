# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import xarray as xr
import cartopy.crs as ccrs
import os
import sys

sys.path.append("../")
sys.path.append("../../")
import droputils.data_utils as data_utils  # noqa: E402

# %%
root = "ipns://latest.orcestra-campaign.org"
ds_lev3 = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
# %%
root = "~/Documents/Data/Dropsonde/complete/"
ds_lev3 = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr",
    engine="zarr",
)
# %%

# %%

sonde_op = {
    pd.Timestamp("2024-08-11").date(): "Helene",
    pd.Timestamp("2024-08-13").date(): "Theresa",
    pd.Timestamp("2024-08-16").date(): "Helene",
    pd.Timestamp("2024-08-18").date(): "Theresa",
    pd.Timestamp("2024-08-21").date(): "Helene",
    pd.Timestamp("2024-08-22").date(): "Nina",
    pd.Timestamp("2024-08-25").date(): "Theresa",
    pd.Timestamp("2024-08-27").date(): "Helene",
    pd.Timestamp("2024-08-29").date(): "Nina",
    pd.Timestamp("2024-08-31").date(): "Theresa",
    pd.Timestamp("2024-09-03").date(): "Nina",
    pd.Timestamp("2024-09-06").date(): "Bjorn",
    pd.Timestamp("2024-09-07").date(): "Helene",
    pd.Timestamp("2024-09-09").date(): "Theresa",
    pd.Timestamp("2024-09-12").date(): "Jakob",
    pd.Timestamp("2024-09-14").date(): "Theresa",
    pd.Timestamp("2024-09-16").date(): "Nina",
    pd.Timestamp("2024-09-19").date(): "Helene",
    pd.Timestamp("2024-09-21").date(): "Nina",
    pd.Timestamp("2024-09-23").date(): "Helene",
    pd.Timestamp("2024-09-24").date(): "Marius",
    pd.Timestamp("2024-09-26").date(): "Nina",
    pd.Timestamp("2024-09-28").date(): "Allison",
}

colors = {
    "Allison": "#782F40",
    "Bjorn": "#006C66",
    "Helene": "#C6D325",
    "Jakob": "#ee1d23",
    "Marius": "#00b1ea",
    "Nina": "#00a1d7",
    "Theresa": "#EF7C00",
}

"""
statistics I want:
- lowest 100m winds: done
- drop altitude: done
- descend time
- nb sondes/ flight
- iwv distribution
"""

# %% add names to flights
ds = ds_lev3.sortby("launch_time")
ds = data_utils.add_island(ds)
ds = data_utils.add_operator(ds, sonde_op)
# %%
# %% lower wind
mean_wind = ds_lev3.w_spd.sel(alt=slice(0, 100)).mean("alt")
fall_duration = ds.interp_time.max(dim="alt", skipna=True) - ds.interp_time.where(
    ds.interp_time > np.datetime64("2000-01-01T00:00:00.000000000")
).min(dim="alt", skipna=True)
fall_duration = fall_duration.where(fall_duration > 500 * 10 ^ 9)
ds = ds.assign(low_wind=mean_wind, fall_duration=fall_duration)

# %%
pd_df_sd = ds.drop_dims("alt").to_dataframe()
# %%
save_path = "/Users/helene/Documents/Data/Dropsonde/orcestra_plots/"
# %%

plt_var = "low_wind"
xlabel = "wind speed avg 0-100m / ms-1"

fig, ax = plt.subplots(figsize=(18, 6))
sns.despine(fig)


sns.histplot(
    pd_df_sd,
    x=plt_var,
    hue="iwv",
    multiple="stack",
    palette="cmo.ice",
    bins=75,
    legend=False,
    edgecolor=None,
    cbar_kws=dict(
        vmin=40,
        vmax=60,
    ),
)
ax.axvspan(0, 3, alpha=0.2, color="gray")
ax.text(0.5, 25, "doldrums", color="gray")
ax.set_xlabel(xlabel)
mean = pd_df_sd[plt_var].mean()
fig.tight_layout()
fig.savefig(os.path.join(save_path, f"hist_{plt_var}"), transparent=True)

# %%

plt_var = "iwv"
xlabel = "integrated water vapor / kgm-3"

fig, ax = plt.subplots(figsize=(18, 6))
sns.despine(fig)


sns.histplot(
    pd_df_sd,
    x=plt_var,
    hue="iwv",
    multiple="stack",
    palette="cmo.ice",
    bins=75,
    legend=False,
    edgecolor=None,
)
ax.axvspan(0, 3, alpha=0.2, color="gray")
ax.text(0.5, 28, "doldrums", color="gray")
ax.set_xlabel(xlabel)
mean = pd_df_sd[plt_var].mean()
fig.tight_layout()
fig.savefig(os.path.join(save_path, f"hist_{plt_var}"), transparent=True)
# %%

plt_var = "aircraft_msl_altitude"
xlabel = "aircraft altitude / m"

fig, ax = plt.subplots(figsize=(18, 6))
sns.despine(fig)


sns.histplot(
    pd_df_sd, x=plt_var, hue="operator", multiple="stack", palette=colors, bins=75
)
ax.set_xlabel(xlabel)
mean = pd_df_sd[plt_var].mean()
ax.axvline(mean, color="grey")
ax.text(mean + 10, 185, np.round(mean, 2), color="gray")
fig.tight_layout()
fig.savefig(os.path.join(save_path, f"hist_{plt_var}"))

# %%

pd_df_sd["fall_duration"] = pd_df_sd["fall_duration"].dt.total_seconds()
# %% this seems odd

plt_var = "fall_duration"
xlabel = "duration of fall / min"
fig, ax = plt.subplots(figsize=(18, 6))
sns.despine(fig)


sns.histplot(
    pd_df_sd, x=plt_var, hue="operator", multiple="stack", palette=colors, bins=75
)

ax.set_xlim(500, 1010)
xticks = ax.get_xticks()
new_label_min = (xticks // 60).astype(int)
new_label_sec = (xticks % 60).astype(int)
new_label = [f"{min}:{sec}" for min, sec in zip(new_label_min, new_label_sec)]
ax.set_xticks(xticks, new_label)
fig.tight_layout()
fig.savefig(os.path.join(save_path, f"hist_{plt_var}"))
# %%


root = "ipns://latest.orcestra-campaign.org"
ds_lev4 = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr",
    engine="zarr",
)
# %%

lon_min, lon_max, lat_min, lat_max = -60, -15, 0, 20

fig, ax = plt.subplots(figsize=(14, 8), subplot_kw={"projection": ccrs.PlateCarree()})

ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
ax.coastlines(alpha=1.0)
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False, alpha=0.25)

im = ax.scatter(
    ds_lev3.aircraft_longitude,
    ds_lev3.aircraft_latitude,
    c=ds_lev3.w_dir.sel(alt=slice(0, 100)).mean("alt"),
    cmap="twilight_shifted",
)

fig.colorbar(im, fraction=0.015, aspect=30)
fig.tight_layout()
fig.savefig(os.path.join(save_path, "wind_dir"), transparent=True)

# %% iwv sal vs barbados

plt_var = "iwv"
xlabel = "integrated water vapor / kgm-3"
fig, ax = plt.subplots(figsize=(18, 6))
sns.despine(fig)


sns.histplot(
    pd_df_sd,
    x=plt_var,
    hue="low_wind",
    palette="cmo.speed",  # {"SAL": "#FF6F00", "BB": "#1B5E20"},
    bins=75,
    multiple="stack",
    legend=False,
    edgecolor=None,
)
fig.tight_layout()

ax.set_xlim(30, None)
fig.savefig(os.path.join(save_path, f"{plt_var}"), transparent=True)
