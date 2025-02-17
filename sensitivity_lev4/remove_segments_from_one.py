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
import itertools

from helper_products import calc_products, remove_from_one, iterate_circle
from helper_products import get_good, keep_good


config = configparser.ConfigParser()
config.read("../orcestra_drop.cfg")

# %%
root = "ipns://latest.orcestra-campaign.org/"
l3_ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
).rename({"interp_time": "bin_average_time"})

gridded = Gridded(sondes={}, global_attrs={})
gridded.set_l3_ds(l3_ds.where((l3_ds["u_qc"] == 0) & (l3_ds["p_qc"] == 0), drop=True))
gridded.get_circle_times_from_segmentation(
    "https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml"
)
gridded.alt_dim = "altitude"
gridded.sonde_dim = "sonde"
# %%
# %%
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles

good_circles = get_good(circles, thres=12)


circles = keep_good(circles, good_circles)
circles_play = copy.deepcopy(circles)

# %%
no_int_ref = iterate_circle(circles=circles_play, config=config, int=False)
int_ref = iterate_circle(circles=circles_play, config=config, int=True)


# %%


var = "omega"

gap_alts = [500, 1000, 5000]  # , 7000]
gap_depths = [30, 100, 300]  # , 1000]
sonde_ids = np.arange(0, 13)
result = {
    "int": {
        gap_alt: {
            gap_depth: {key: [] for key in circles.keys()} for gap_depth in gap_depths
        }
        for gap_alt in gap_alts
    },
    "no_int": {
        gap_alt: {
            gap_depth: {key: [] for key in circles.keys()} for gap_depth in gap_depths
        }
        for gap_alt in gap_alts
    },
}
for params in itertools.product(gap_alts, gap_depths, sonde_ids):
    print(params)
    gap_alt, gap_depth, gap_sonde = params
    try:
        gap_no_int = remove_from_one(
            gap_alt, gap_depth, gap_sonde, circles_play, config, int=False
        )
    except IndexError:
        pass
    else:
        gap_no_int = calc_products(gap_no_int, config)
        gap_int = remove_from_one(
            gap_alt, gap_depth, gap_sonde, circles_play, config, int=True
        )
        gap_int = calc_products(gap_int, config)
        for key in gap_int.keys():
            result["int"][gap_alt][gap_depth][key].append(gap_int[key].circle_ds)
            result["no_int"][gap_alt][gap_depth][key].append(gap_no_int[key].circle_ds)

# %%
depths = [30, 100, 300]
alts = [500, 1000, 5000]
int_type = "int"
var = "omega"
x = np.linspace(-1, 1, 20)
alt = "altitude"

colors = sns.color_palette("turbo", n_colors=22)
fig = plt.figure(figsize=(18, 18), constrained_layout=True)
fig.suptitle("difference to reference for different gap sizes and heights")
subfigs = fig.subfigures(nrows=3, ncols=1)
for row, (gap_depth, subfig) in enumerate(zip(depths, subfigs)):
    subfig.suptitle(f"gap_depth: {gap_depth}m")
    axes = subfig.subplots(nrows=1, ncols=3)
    for ax in axes:
        ax.fill_betweenx(x, -x, x, color="lightgray", alpha=0.2)
    for col, gap_alt in enumerate(alts):
        int_result = result["int"][gap_alt][gap_depth]
        no_int_result = result["no_int"][gap_alt][gap_depth]
        for idx, key in enumerate(int_result.keys()):
            count = 0

            for ds_int, ds_no_int in zip(int_result[key], no_int_result[key]):
                if count == 0 and row == 0 and col == 0:
                    axes[col].scatter(
                        (ds_int[var] - int_ref[key].circle_ds[var]).mean(alt),
                        (ds_no_int[var] - no_int_ref[key].circle_ds[var]).mean(alt),
                        color=colors[idx],
                        label=key,
                    )
                else:
                    axes[col].scatter(
                        (ds_int[var] - int_ref[key].circle_ds[var]).mean(alt),
                        (ds_no_int[var] - no_int_ref[key].circle_ds[var]).mean(alt),
                        color=colors[idx],
                    )

                count += 1

# .legend(loc="upper left", fontsize="x-small" )

for ax, alt in zip(subfigs[0].axes, alts):
    ax.set_title(f"gap_alt: {alt}m")
    ax.legend()
    limits = (-0.1, 0.1)
    ax.set_xlim(*limits)
    ax.set_ylim(*limits)

for ax in subfigs[1].axes:
    limits = (-0.3, 0.3)
    ax.set_xlim(*limits)
    ax.set_ylim(*limits)

for ax in subfigs[-1].axes:
    ax.set_xlabel("omega(gap_int - int) mean over gpsalt")
    limits = (-0.7, 0.9)
    ax.set_xlim(*limits)
    ax.set_ylim(*limits)

for ax in fig.axes[::3]:
    ax.set_ylabel("omega(gap_no_int - no_int) mean over gpsalt")
for ax in fig.axes:
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)


sns.despine(offset=10)
fig.savefig(f"../images/{var}_different_gaps_one_sonde.pdf")
