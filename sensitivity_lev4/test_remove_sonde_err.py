# %%
import configparser

import copy
import numpy as np
import pydropsonde.pipeline
import xarray as xr
import matplotlib.pyplot as plt
import seaborn as sns
from pydropsonde.processor import Gridded
import pydropsonde


from helper_products import iterate_circle
from helper_products import (
    iterate_Circle_method_over_dict_of_Circle_objects,
)
from xhistogram.xarray import histogram
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

config = configparser.ConfigParser()
config.read("../orcestra_drop.cfg")

# %%
root = "ipns://latest.orcestra-campaign.org/"
l3_ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
).rename({"interp_time": "bin_average_time"})

l3_ds = xr.open_dataset(
    "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/products/Level_3_qc/PERCUSION_Level_3.zarr"
)

gridded = Gridded(sondes={}, global_attrs={})
gridded.set_l3_ds(l3_ds)  # .where((l3_ds["p_qc"] == 0), drop=True))
gridded.get_circle_times_from_segmentation(
    "https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml"
)
gridded.alt_dim = "altitude"
gridded.sonde_dim = "sonde"
gridded.create_interim_l4()
gridded.add_autocorrelation(
    autocorr_dir="../dropsonde_data/", filename="autocorrelation.zarr"
)
gridded.add_distances()
gridded.add_weights()
# %%
# HALO-20240928a_8b0b, HALO-20240916a_719b


# %%
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
# good_circles = get_good(circles, thres=12)
# circles = keep_good(circles, good_circles)
circles_w = copy.deepcopy(circles)
# %%
iterate_Circle_method_over_dict_of_Circle_objects(
    circles_w, ["calc_remove_sonde_vals"], config=config
)
weights_ref = iterate_circle(circles=circles_w, config=config, int=True)
# %%
iterate_Circle_method_over_dict_of_Circle_objects(
    weights_ref,
    ["add_circle_id_variable", "add_remove_sonde_errors", "add_sign_change_qc"],
    config=config,
)

# %%


var = "omega"
err = xr.concat(
    [
        weights_ref[key].circle_ds[f"{var}_remove_sonde_qc"]
        for key in weights_ref.keys()
    ],
    dim="sonde",
)

# %%


err.name = var
binsize = 200
sig_om_err = err  # .where(original_values > 1)
bins_div = np.linspace(sig_om_err.min().values, sig_om_err.max().values, binsize)
fig, axes = plt.subplots(nrows=2, height_ratios=(0.3, 2), sharex=True, figsize=(6, 6.9))

hist = histogram(sig_om_err, sig_om_err.altitude, bins=[bins_div, binsize])
im = hist.where(hist != 0).plot(
    cmap="cmo.ice",
    vmin=0,
    vmax=100,
    ax=axes[1],
    add_colorbar=False,
    y="altitude_bin",
)
cbaxes = inset_axes(axes[1], width="3%", height="30%", loc=4)
fig.colorbar(
    im, cax=cbaxes, orientation="vertical", label="count", fraction=1, extend="max"
)

axes[1].set_ylabel("altitude / m")
axes[1].set_xlabel("omega error if sonde is removed / hPa hr-1")

sns.histplot(
    sig_om_err.to_dataframe()["omega"]
    .reset_index()
    .drop("altitude", axis=1)
    .drop("sonde", axis=1),
    bins=200,
    stat="probability",
    alpha=0.5,
    color="#00267f",
    kde=True,
    element="step",
    ax=axes[0],
)
axes[0].set_ylabel("")
sns.despine(offset={"left": 10})
fig.tight_layout()

fig.savefig("../images/omega_error_2d_good_circles.png")


# %%


changed_values = xr.concat(
    [
        (
            np.sign(
                weights_ref[key].circle_ds[f"{var}"]
                + weights_ref[key].circle_ds[f"{var}_remove_sonde_qc"]
            )
            == np.sign(weights_ref[key].circle_ds[f"{var}"])
        )
        for key in weights_ref.keys()
    ],
    dim="sonde",
)


# %%
same_sign_omega = np.abs(err.where(changed_values))
diff_sign_omega = np.abs(err.where(~changed_values))

# %%

plt_err = diff_sign_omega


fig, axes = plt.subplots(ncols=2, figsize=(12, 6))
for ax, plt_err in zip(axes, [same_sign_omega, diff_sign_omega]):
    plt_err.name = var
    bins_div = np.linspace(plt_err.min().values, plt_err.max().values, 100)

    hist = histogram(plt_err, plt_err.altitude, bins=[bins_div, 100])
    hist.where(hist != 0).plot(cmap="cmo.ice", ax=ax)
    print(plt_err.count())
print(err.count())

# %%

# %%
l4_ds = xr.open_dataset(
    "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/products/Level_4/Level_4.zarr"
)


# %%
# %%

# %%
nice_circles = [13, 23, 28, 31, 40, 43, 50, 56, 62, 75]
# nice_circles = l4_ds.circle.values

colors = sns.color_palette("bright", n_colors=len(nice_circles))
fig, axes = plt.subplots(ncols=2, figsize=(12, 6))
for i, circle in enumerate(nice_circles):
    c = colors[i]
    l4_ds.omega.sel(circle=circle).plot(
        y="altitude",
        ax=axes[0],
        color=c,
        label=l4_ds.sel(circle=circle).circle_id.values,
    )

    lower_err = l4_ds.omega.sel(circle=circle) - l4_ds.se_omega.sel(circle=circle)
    upper_err = l4_ds.omega.sel(circle=circle) + l4_ds.se_omega.sel(circle=circle)
    axes[0].fill_betweenx(
        y=l4_ds.altitude,
        x1=lower_err,
        x2=upper_err,
        color=c,
        alpha=0.2,
    )
    l4_ds.omega.sel(circle=circle).plot(label=circle, y="altitude", ax=axes[1], color=c)
    try:
        remove_sonde_err = weights_ref[
            str(l4_ds.sel(circle=circle).circle_id.values)
        ].circle_ds["omega_remove_sonde_qc"]
    except KeyError:
        print(str(l4_ds.sel(circle=circle).circle_id.values))
    else:
        lower_err = l4_ds.omega.sel(circle=circle) + remove_sonde_err.min("sonde")
        upper_err = l4_ds.omega.sel(circle=circle) + remove_sonde_err.max("sonde")
        axes[1].fill_betweenx(
            y=l4_ds.altitude,
            x1=lower_err,
            x2=upper_err,
            color=c,
            alpha=0.2,
        )

sns.despine(offset={"left": 10})
for ax in axes:
    ax.set_ylabel("")
    ax.set_title("")
    ax.set_xlabel("omega / hPa hr-1")
    ax.set_ylim(0, None)
axes[0].set_ylabel("altitude / m")
axes[0].set_title("regression standard error")
axes[1].set_title("remove sonde error")
axes[0].legend(fontsize="small")
fig.savefig("../images/different_error_meassures.pdf")
