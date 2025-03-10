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
gridded.create_interim_l4()
gridded.add_autocorrelation(
    autocorr_dir="../dropsonde_data/", filename="autocorrelation.zarr"
)
gridded.add_distances()

# %%
ref_int = True

# %%
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
good_circles = get_good(circles, thres=12)
circles = keep_good(circles, good_circles)
circles_play = copy.deepcopy(circles)


no_int_ref = iterate_circle(circles=circles_play, config=config, int=ref_int)
# %%
gridded.add_weights()
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
good_circles = get_good(circles, thres=12)
circles = keep_good(circles, good_circles)
circles_w = copy.deepcopy(circles)
weights_ref = iterate_circle(circles=circles_w, config=config, int=True)


# %%


var = "omega"

gap_alts = [500]  # , 7000]
gap_depths = [30, 300, 1500]  # 30, 1500, 1000]
sonde_ids = np.arange(0, 13)
result = {
    "weight": {
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
            gap_alt, gap_depth, gap_sonde, circles_play, config, int=ref_int
        )
    except IndexError:
        pass
    else:
        gap_no_int = calc_products(gap_no_int, config)
        gap_w = remove_from_one(
            gap_alt, gap_depth, gap_sonde, circles_w, config, int=True
        )
        gap_w = calc_products(gap_w, config)
        for key in gap_w.keys():
            result["weight"][gap_alt][gap_depth][key].append(gap_w[key].circle_ds)
            result["no_int"][gap_alt][gap_depth][key].append(gap_no_int[key].circle_ds)


# %%
depths = [30, 100, 300]
alts = [500, 1000, 5000]
int_type = "weight"
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
        int_result = result[int_type][gap_alt][gap_depth]
        no_int_result = result["no_int"][gap_alt][gap_depth]
        for idx, key in enumerate(int_result.keys()):
            count = 0

            for ds_int, ds_no_int in zip(int_result[key], no_int_result[key]):
                if count == 0 and row == 0 and col == 0:
                    axes[col].scatter(
                        (ds_int[var] - weights_ref[key].circle_ds[var]).mean(alt),
                        (ds_no_int[var] - no_int_ref[key].circle_ds[var]).mean(alt),
                        color=colors[idx],
                        label=key,
                    )
                else:
                    axes[col].scatter(
                        (ds_int[var] - weights_ref[key].circle_ds[var]).mean(alt),
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


# %%
# %%
depths = [30, 300, 1500]
gap_alt = 500
int_type = "weight"
var = "omega"
x = np.linspace(-2.5, 2.5, 20)
alt = "altitude"

colors = sns.color_palette("turbo", n_colors=22)
fig, axes = plt.subplots(ncols=3, figsize=(18, 6), sharey=False)
fig.suptitle("Artificial gaps of different sizes at 500m")
for ax in axes:
    ax.fill_betweenx(x, -x, x, color="lightgray", alpha=0.2)
for col, gap_depth in enumerate(depths):
    int_result = result[int_type][gap_alt][gap_depth]
    no_int_result = result["no_int"][gap_alt][gap_depth]
    for idx, key in enumerate(int_result.keys()):
        count = 0

        for ds_int, ds_no_int in zip(int_result[key], no_int_result[key]):
            if count == 0 and col == 0:
                axes[col].scatter(
                    (ds_int[var] - weights_ref[key].circle_ds[var]).mean(alt),
                    (ds_no_int[var] - no_int_ref[key].circle_ds[var]).mean(alt),
                    color=colors[idx],
                    label=key,
                )
            else:
                axes[col].scatter(
                    (ds_int[var] - weights_ref[key].circle_ds[var]).mean(alt),
                    (ds_no_int[var] - no_int_ref[key].circle_ds[var]).mean(alt),
                    color=colors[idx],
                )

            count += 1
    axes[col].set_title(f"gap depth: {gap_depth}")
    axes[col].set_xlabel("omega (gap_weight_int - weight_int) mean over gpsalt")
# axes[0].legend()

limits = (-0.002, 0.002)  # (-0.1, 0.1)
axes[0].set_xlim(*limits)
axes[0].set_ylim(*limits)
limits = (-0.3, 0.3)  # (-1.3, 1.3)
axes[1].set_xlim(*limits)
axes[1].set_ylim(*limits)
limits = (-2.2, 2.2)
axes[2].set_xlim(*limits)
axes[2].set_ylim(*limits)


axes[2].set_ylabel("omega(gap_no_int - no_int) mean over gpsalt")
for ax in axes:
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)


sns.despine(offset=10)
# fig.savefig(f"../images/{var}_different_gaps_one_sonde.pdf")
# %%


fig, axes = plt.subplots(ncols=3, figsize=(18, 6), sharey=True, sharex=True)


for col, gap_depth in enumerate(depths):
    int_result = result[int_type][gap_alt][gap_depth]
    no_int_result = result["no_int"][gap_alt][gap_depth]

    for idx, key in enumerate(int_result.keys()):
        for ds_int, ds_no_int in zip(int_result[key], no_int_result[key]):
            axes[col].scatter(
                ds_int.omega - ds_no_int.omega,
                y=ds_int.altitude,
                color=colors[idx],
            )
            axes[col].set_title(f"gap depth: {gap_depth}")
for ax in axes:
    ax.set_xlabel("omega(int - weight int) / hPa hr-1")

axes[0].set_ylabel("altitude / m")
sns.despine(offset={"left": 10})
# %%
sns.set_palette("Paired")
key = "HALO-20240829a_d387"
ref = weights_ref[key].circle_ds
for i, weight in enumerate(result["weight"][500][300][key]):
    ref.sel(sonde=i).u.plot(y="altitude")
    weight.sel(sonde=i).u.plot(y="altitude")

plt.fill_between(
    x=np.linspace(-1, 6),
    y1=np.full(50, 500),
    y2=np.full(50, 800),
    color="gray",
    alpha=0.1,
)

plt.ylim(400, 900)

plt.xlim(-1, 6)
