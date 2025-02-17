# %%

import seaborn as sns
import matplotlib.pyplot as plt
import xarray as xr
from pydropsonde.helper.xarray_helper import write_ds
import numpy as np

# %%
root = "ipns://latest.orcestra-campaign.org/"
l3_ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
)


def get_autocorr_np(da, tau, alt_dim="altitude"):
    vals = (da - da.mean(alt_dim)).values
    gh = vals[:, :-tau] * vals[:, tau:]
    axis = 1
    c0 = vals**2
    return (np.nansum(gh, axis=axis) / np.count_nonzero(~np.isnan(gh), axis=axis)) / (
        np.nansum(c0, axis=axis) / np.count_nonzero(~np.isnan(c0), axis=axis)
    )


def get_autocorr_xr(ds, alt_dim="altitude", maxalt=10000, variables=["u", "v"]):
    taus = ds[alt_dim].where(ds[alt_dim] < maxalt, drop=True).values[1:] / 10
    autocorr = {alt_dim: {"dims": (alt_dim), "data": taus * 10}}

    for var in variables:
        autocorr[f"autocorr_{var}"] = {
            "dims": (alt_dim),
        }
        res = [get_autocorr_np(ds[var], int(tau)) for tau in taus]
        autocorr[f"autocorr_{var}"]["data"] = [np.nanmean(corr) for corr in res]
        autocorr[f"std_autocorr_{var}"] = {
            "dims": (alt_dim),
            "data": [np.nanstd(corr) for corr in res],
        }
    return xr.Dataset.from_dict(autocorr)


ds = get_autocorr_xr(l3_ds, variables=["u", "v", "p", "theta", "q"])


path = "/Users/helene/Documents/Orcestra/dropsonde/dropsonde_data/"
write_ds(
    ds,
    dir=path,
    filename="autocorrelation.zarr",
    alt_dim="altitude",
)
# %%
path = "/Users/helene/Documents/Orcestra/dropsonde/dropsonde_data/"
autocorr = xr.open_dataset(f"{path}autocorrelation.zarr")

vars = ["u", "v", "p", "q", "theta"]
colors = sns.color_palette("turbo", n_colors=5)

fig, ax = plt.subplots(figsize=(12, 6))
for idx, var in enumerate(vars):
    da = ds[f"autocorr_{var}"]
    std = ds[f"std_autocorr_{var}"]
    da.plot(label=var, color=colors[idx], zorder=3)
    ax.fill_between(
        da.altitude.values,
        da.values - std.values,
        da.values + std.values,
        color=colors[idx],
        alpha=0.2,
        zorder=1,
    )
ax.legend()
ax.axhline(0, color="gray", linestyle=":", zorder=2)
ax.set_xlabel("alt diff / m")
ax.set_xlim(0, 5000)
ax.set_ylim(-0.5, 1.1)
sns.despine(offset=10)
fig.savefig("../images/autocorrelation.png")
