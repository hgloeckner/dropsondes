# %%
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import glob
import moist_thermodynamics.constants as mtc
import moist_thermodynamics.functions as mtf
import moist_thermodynamics.saturation_vapor_pressures as svp

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

# %%

# %% plot iwv histograms to check if they are plausible/similar
fig, ax = plt.subplots()

sns.histplot(new_l3.iwv, ax=ax, bins=30, binrange=(25, 85), label="new")
sns.histplot(old_l3.iwv, ax=ax, bins=30, binrange=(25, 85), label="old")
ax.legend()
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
# %%

assert ~np.any(np.isnan(new_l3.launch_lat))
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
old_l4.p.plot()

plt.show()
new_l4.p.plot()

# %%
# %%
l2 = xr.open_dataset(
    "~/Documents/Data/Dropsonde/dropsonde_data/products/Level_2/HALO-20240811a/PERCUSION_c723db9f_Level_2.zarr",
    engine="zarr",
)
old_l4.sel(sonde=1).rh.plot(label="old l4")
new_l4.sel(sonde=1).rh.plot(label="new l4")
sid = new_l4.sel(sonde=1).sonde_id.values
new_l3.where(new_l3.sonde_id == sid, drop=True).rh.plot(label="new l3")
old_l3.where(old_l3.sonde_id == sid, drop=True).rh.plot(label="old l3")
plt.plot(l2.gpsalt, l2.rh, marker="P", markersize=2, color="k")

plt.legend()
# %%

# %%
fig, ax = plt.subplots()
ax.plot(
    old_l4.sel(sonde=1).rh,
    old_l4.sel(sonde=1).p,
    label="old l4",
    color="C0",
    linestyle="",
    markersize=2,
)
ax.plot(
    new_l4.sel(sonde=1).rh,
    new_l4.sel(sonde=1).p,
    label="new l4",
    color="C1",
    linestyle="",
    markersize=2,
)
ax.plot(
    new_l3.where(new_l3.sonde_id == sid, drop=True).rh,
    new_l3.where(new_l3.sonde_id == sid, drop=True).p,
    label="new l3",
    color="C1",
    linestyle="",
    marker="x",
    markersize=1,
)
ax.plot(
    old_l3.where(old_l3.sonde_id == sid, drop=True).rh,
    old_l3.where(old_l3.sonde_id == sid, drop=True).p,
    label="old l3",
    marker="x",
    color="C0",
    linestyle="",
    markersize=1,
)
ax.plot(l2.rh, l2.p, label="l2", marker="P", markersize=1, color="C2")
# ax.legend()
ax.invert_yaxis()
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

# %%

empty_p_id = new_l3.where(np.all(np.isnan(new_l3.p), axis=1), drop=True).sonde_id.values
# %%

for sid in list(set(empty_p_id) & set(new_l4.sonde_id.values)):
    print(sid)
    new_l3.where(new_l3.sonde_id == sid, drop=True).p.plot(
        label="new l3", marker="o", markersize=2
    )
    new_l4.where(new_l4.sonde_id == sid, drop=True).p.plot(
        label="new l4", marker="x", markersize=2
    )
    old_l3.where(old_l3.sonde_id == sid, drop=True).p.plot(
        label="old l3", marker="o", markersize=2
    )
    old_l4.where(old_l4.sonde_id == sid, drop=True).p.plot(
        label="old l4", marker="x", markersize=2
    )
    plt.legend()
# %%
(
    old_l4.swap_dims({"sonde": "sonde_id"}).p
    - new_l4.swap_dims({"sonde": "sonde_id"}).p
).swap_dims({"sonde_id": "sonde"}).plot()

# %%
l2 = xr.open_dataset(
    "ipfs://QmNTyD2chhgg4w8bh9SZNSLBma9Hj7qcDKxKLmJMWJVVS9", engine="zarr"
)
# %%

ds = l2.isel(time=slice(300, 305))
xr.where(np.isnan(ds.alt), np.nan, 1).plot(linestyle="", marker="o", markersize=5)

xr.where(np.isnan(ds.gpsalt), np.nan, 1).plot(linestyle="", marker="o", markersize=2)
# %%

l1 = xr.open_dataset(
    "~/Documents/Data/Dropsonde/dropsonde_data/products/Level_1/HALO-20240821a/D20240821_143942QC.nc"
)
# %%
ds = l1.isel(time=slice(300, 305))
xr.where(np.isnan(ds.alt), np.nan, 1).plot(linestyle="", marker="o", markersize=5)

xr.where(np.isnan(ds.gpsalt), np.nan, 1).plot(linestyle="", marker="o", markersize=2)

# %%

files = glob.glob(
    "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/products/Level_2/**/*.zarr",
)


l2 = xr.open_dataset(files[5], engine="zarr")

# %%

# %%
l2res = []

for file in files:
    l2 = xr.open_dataset(file)
    if l2.sonde_qc.values == 0:
        l2 = l2.assign(
            q=mtf.relative_humidity_to_specific_humidity(
                l2.rh, l2.p, l2.ta, es=svp.liq_wagner_pruss
            )
        )
        ds = l2[["q", "gpsalt", "ta", "p"]].dropna(dim="time", how="any")
        Rd = mtc.Rv
        hydro = np.diff(
            mtf.pressure_altitude(
                ds.p.values,
                ds.ta.values,
                qv=ds.q.values,
            )
        )
        dz = ds.gpsalt.diff(dim="time")
        l2res.append((dz - hydro))
# %%

# %%
l3res = []
for sonde in new_l3.sonde:
    l3ds = new_l3.sel(sonde=sonde)
    if l3ds.sonde_qc.values == 0:
        l3ds = l3ds.assign(
            q=mtf.relative_humidity_to_specific_humidity(
                l3ds.rh, l3ds.p, l3ds.ta, es=svp.liq_wagner_pruss
            )
        )
        ds = l3ds[["q", "altitude", "ta", "p"]].dropna(dim="altitude", how="any")
        hydro = np.diff(
            mtf.pressure_altitude(
                ds.p.values,
                ds.ta.values,
                qv=ds.q.values,
            )
        )
        dz = ds.altitude.diff(dim="altitude")
        l3res.append((dz - hydro))

# %%
l3old_res = []
for sonde in old_l3.sonde:
    l3ds = old_l3.sel(sonde=sonde)
    if l3ds.sonde_qc.values == 0:
        l3ds = l3ds.assign(
            q=mtf.relative_humidity_to_specific_humidity(
                l3ds.rh, l3ds.p, l3ds.ta, es=svp.liq_wagner_pruss
            )
        )
        ds = l3ds[["q", "altitude", "ta", "p"]].dropna(dim="altitude", how="any")
        hydro = np.diff(
            mtf.pressure_altitude(
                ds.p.values,
                ds.ta.values,
                qv=ds.q.values,
            )
        )
        dz = ds.altitude.diff(dim="altitude")
        l3old_res.append((dz - hydro))
# %%
"""
sns.histplot(
    df,
    bins=300,
    binrange=(-10, 10)
)
"""
sns.histplot(
    np.concatenate(l3res),
    bins=300,
    binrange=(-5, 5),
    stat="probability",
    label="L3 Beach: median {:.2f} m".format(np.nanmedian(np.concatenate(l3res))),
)
sns.histplot(
    np.concatenate(l2res),
    bins=300,
    binrange=(-5, 5),
    stat="probability",
    label="L2 Beach: median {:.2f} m".format(np.nanmedian(np.concatenate(l2res))),
)
sns.histplot(
    np.concatenate(l3old_res),
    bins=300,
    binrange=(-5, 5),
    stat="probability",
    label="L3 Beach old: median {:.2f} m".format(
        np.nanmedian(np.concatenate(l3old_res))
    ),
)
plt.legend()
plt.savefig("/Users/helene/Downloads/height.png")
# %%
