# %%
import xarray as xr
import os
import matplotlib.pyplot as plt
import seaborn as sns

# %%
folder = "dropsondes"

l4_path = f"/Users/helene/Documents/Data/Dropsonde/{folder}/products/Level_4/"
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
ds_island = xr.DataArray(island, dims="sonde", name="island")
c_island = xr.DataArray(circle_island, dims="circle", name="c_island")
ds = ds_lev4.assign_coords(island=ds_island, c_island=c_island)
# %%
ds_omega = ds.omega
plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots()

ds_omega.where(ds_omega.c_island == "SAL").mean("circle").plot(
    y="altitude", label="East Atlantic mean", color="C0"
)

ds_out = (
    ds_omega.where(ds_omega.c_island == "SAL")
    .median("circle")
    .plot(y="altitude", label="East Atlantic median", linestyle="--", color="C0")
)

ds_omega.where(ds_omega.c_island == "BB").mean("circle").plot(
    y="altitude", label="West Atlantic mean", color="C1"
)
ds_out = (
    ds_omega.where(ds_omega.c_island == "BB")
    .median("circle")
    .plot(y="altitude", label="West Atlantic median", linestyle="--", color="C1")
)
ax.set_ylabel("altitude / m")
ax.set_xlabel("omega / hPa hr-1")

ax.axvline(0, color="gray", alpha=0.2)
sns.despine(offset={"left": 10})
ax.legend()
ax.set_ylim(-5, 13500)
fig.tight_layout()


quicklook_path = "/Users/helene/Documents/Data/Dropsonde/orcestra_plots"

fig.savefig(f"{quicklook_path}/omega.png", transparent=True)
# %% positive vs negative

ds_omega_day = ds_omega * 24
integrated_omega = ds_omega_day.mean("altitude")


# %%

unit = "hPa day-1"


fig, axes = plt.subplots(ncols=2, figsize=(12, 6), sharex=True)

ds_plt = ds_omega_day.where(integrated_omega < 0, drop=True)
bottom_heavy = ds_plt.where(
    ds_plt.sel(altitude=slice(5000, 10000)).min(dim="altitude")
    - ds_plt.sel(altitude=slice(0, 2500)).min(dim="altitude")
    > 0.1 * ds_plt.std(dim="altitude")
)
top_heavy = ds_plt.where(
    (ds_plt.sel(altitude=slice(5000, 10000)).min(dim="altitude") < 0)
    & (ds_plt.sel(altitude=slice(0, 2500)).mean(dim="altitude") > 0)
)
sim = ds_plt.where(
    (
        ds_plt.sel(altitude=slice(5000, 10000)).min(dim="altitude")
        - ds_plt.sel(altitude=slice(0, 2500)).min(dim="altitude")
        < 0.1 * ds_plt.std(dim="altitude")
    )
    & (ds_plt.sel(altitude=slice(0, 2500)).mean(dim="altitude") < 0)
)

ax = axes[0]

im = ds_plt.mean("circle").plot(y="altitude", ax=ax, label="mean omega < 0", color="C1")
for i in ds_plt.circle:
    ds_plt.sel(circle=i).plot(y="altitude", ax=ax, color="C1", alpha=0.1)


im = top_heavy.mean("circle").plot(
    y="altitude",
    ax=ax,
    label="top heavy",
    color="C2",
    linestyle="-",
)

im = bottom_heavy.mean("circle").plot(
    y="altitude",
    ax=ax,
    label="bottom heavy",
    color="C3",
    linestyle="-",
)

im = sim.mean("circle").plot(
    y="altitude", ax=ax, label="similar top and bottom", color="C0", linestyle="-"
)

ax = axes[1]
im = top_heavy.median("circle").plot(
    y="altitude",
    ax=ax,
    label="top heavy",
    color="C2",
    linestyle="-",
)

im = bottom_heavy.median("circle").plot(
    y="altitude",
    ax=ax,
    label="bottom heavy",
    color="C3",
    linestyle="-",
)

im = sim.median("circle").plot(
    y="altitude", ax=ax, label="similar top and bottom", color="C0", linestyle="-"
)
im = (
    ds_plt.where(integrated_omega < 0)
    .median("circle")
    .plot(y="altitude", ax=ax, label="all omega < 0", color="C1")
)

ax.legend(loc=2)
for ax in axes:
    ax.axvline(0, color="gray", alpha=0.2)
    ax.set_xlabel(f"omega / {unit}")
    ax.set_ylabel("")
    ax.set_ylim(0, 13500)
    ax.set_xlim(-350, 150)
sns.despine(offset={"left": 10})

axes[0].set_ylabel("altitude / m ")
axes[0].set_title("mean")
axes[1].set_title("median")

fig.tight_layout()

fig.savefig("../images/mean_omegas.png")

print(top_heavy.sel(altitude=5000).count().values)
print(bottom_heavy.sel(altitude=5000).count().values)
print(sim.sel(altitude=5000).count().values)
# %%
fig, axes = plt.subplots(ncols=2, figsize=(12, 6), sharex=True)

ds_plt = ds_omega_day.where(integrated_omega > 0, drop=True)
ax = axes[0]
for i in ds_plt.circle:
    ds_plt.sel(circle=i).plot(y="altitude", ax=ax, color="C1", alpha=0.1)

im = ds_plt.mean("circle").plot(y="altitude", ax=ax, label="mean omega > 0", color="C1")
ax.set_xlim(-150, 350)
