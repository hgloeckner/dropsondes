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

from helper_products import calc_products, remove_from_all, iterate_circle
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
results = dict({"gap": {}, "gap_int": {}})
for gap_length in [3, 10, 30]:
    circles_gap = remove_from_all(gap_length, circles_play, config, False)
    calc_products(circles_gap, config)
    circles_gap_int = remove_from_all(gap_length, circles_play, config, True)
    calc_products(circles_gap_int, config)
    results["gap"][gap_length] = circles_gap
    results["gap_int"][gap_length] = circles_gap_int

# %%
ref_dict = circles
var = "omega"
alt = "altitude"
factor = 1
sns.set_palette("turbo", n_colors=14)

lengths = [3, 10, 30]
fig = plt.figure(constrained_layout=True, figsize=(18, 6 * len(lengths)))
subfigs = fig.subfigures(nrows=len(lengths), ncols=1)
for row, subfig in enumerate(subfigs):
    gap_length = lengths[row]
    subfig.suptitle(f"gap size: {gap_length * 10}m")
    circles_gap = results["gap"][gap_length]
    circles_gap_int = results["gap_int"][gap_length]
    axes = subfig.subplots(nrows=1, ncols=2)

    for key in circles_play:
        plt_var = (
            circles_gap[key].circle_ds[var].where(circles_gap[key].circle_ds[var] != 0)
            - no_int_ref[key].circle_ds[var]
        )  # / ref_dict[key].circle_ds[var]
        axes[0].scatter(plt_var, ref_dict[key].circle_ds[alt], s=2)
        plt_var = (
            circles_gap_int[key]
            .circle_ds[var]
            .where(circles_gap_int[key].circle_ds[var] != 0)
            - int_ref[key].circle_ds[var]
        )  # / ref_dict[key].circle_ds[var]
        axes[1].scatter(plt_var, ref_dict[key].circle_ds[alt], s=2, label=key)

    for ax in axes.flatten():
        ax.set_xlim(-7 * factor, 7 * factor)  # -7e-5
    axes[0].set_title("no interpolation")
    axes[1].set_title("interpolation")
    axes[0].set_ylabel("gpsaltitude / m")
    axes[1].legend()
axes[0].set_xlabel(
    r"$\Delta$ {} / {} (gap_no-int - no-int)".format(
        var, circles_gap[key].circle_ds[var].attrs["units"]
    )
)
axes[1].set_xlabel(
    r"$\Delta$ {} / {} (gap_int - int)".format(
        var, circles_gap[key].circle_ds[var].attrs["units"]
    )
)
sns.despine(offset=10)
# fig.tight_layout()
fig.savefig(f"../images/{var}_different_gaps.png")
# %%

lengths = [3, 10, 30]

colors = ["#303F9F", "#42A5F5", "#E65100", "#FBC02D"]

gap_length = 3
# key = "HALO-20240829a_d387"
key = "HALO-20240816a_8c12"
# key = "HALO-20240827a_6c6b"
# key = "HALO-20240921a_a71f"
circles_gap = results["gap"][gap_length]
circles_gap_int = results["gap_int"][gap_length]
var = "omega"
factor = 1  #
sns.set_palette(colors)
fig, axes = plt.subplots(ncols=len(lengths), figsize=(6 * len(lengths), 6))
fig.suptitle(f"{key}")
for ax, gap_length in zip(axes, lengths):
    circles_gap = results["gap"][gap_length]
    circles_gap_int = results["gap_int"][gap_length]
    ax.scatter(
        no_int_ref[key].circle_ds[var],
        no_int_ref[key].circle_ds[alt],
        s=2,
        label="no interpolation",
    )
    ax.scatter(
        int_ref[key].circle_ds[var],
        int_ref[key].circle_ds[alt],
        s=2,
        label="interpolation",
    )
    ax.scatter(
        circles_gap[key].circle_ds[var],
        circles_gap[key].circle_ds[alt],
        s=2,
        label="gap, no interpolation",
    )
    ax.scatter(
        circles_gap_int[key].circle_ds[var],
        circles_gap_int[key].circle_ds[alt],
        s=2,
        label="gap, interpolation",
    )
    ax.set_xlabel(f"{var} / {int_ref[key].circle_ds[var].attrs['units']}")
    ax.set_title(f"gap size: {gap_length * 10}m")
    ax.set_xlim(-10 * factor, 10 * factor)
axes[-1].legend()
axes[0].set_ylabel("gpsaltitude / m")
cnormal = circles[key].circle_ds
for i in cnormal.sonde.values:
    val_array = np.where(np.isnan(cnormal.sel(sonde=i).u), 1, np.nan)
    axes[0].scatter(
        10 * factor + 0.5 * factor * val_array * (-i - 1),
        cnormal[alt],
        color="black",
        alpha=0.8,
        s=0.1,
    )

sns.despine(offset=10)
fig.tight_layout()
fig.savefig(f"../images/omega_gap_int_{key}.pdf")


# %%

depths = [3, 10, 30]
var = "omega"

colors = sns.color_palette("turbo", n_colors=22)
fig, axes = plt.subplots(figsize=(18, 6), ncols=3)
for col, (depth, ax) in enumerate(zip(depths, axes)):
    ax.set_title(f"gap_depth: {depth * 10}m")
    int_result = results["gap_int"][depth]
    no_int_result = results["gap"][depth]
    for idx, key in enumerate(int_result.keys()):
        count = 0
        ds_int = int_result[key].circle_ds
        ds_no_int = no_int_result[key].circle_ds
        if count == 0 and col == 0:
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

ax = axes[0]

limits = (-2, 2)
ax.set_xlim(*limits)
ax.set_ylim(*limits)
ax.set_xlabel("omega(gap_int - int) mean over gpsalt")
# ax.legend()

ax = axes[1]
ax.set_xlabel("omega(gap_int - int) mean over gpsalt")
ax.set_xlim(*limits)
ax.set_ylim(*limits)

ax = axes[2]
ax.set_xlabel("omega(gap_int - int) mean over gpsalt")
ax.set_xlim(*limits)
ax.set_ylim(*limits)

axes[0].set_ylabel("omega(gap_no_int - no_int) mean over gpsalt")
for ax in fig.axes:
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)

sns.despine(offset=10)
fig.savefig(f"../images/{var}_different_gaps_all_sondes.pdf")

# %%
