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

from helper_products import calc_products, remove_one, iterate_circle
from helper_products import get_good, keep_good


config = configparser.ConfigParser()
config.read("../orcestra_drop.cfg")

# %%
root = "ipns://latest.orcestra-campaign.org/"
l3_ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
).rename({"interp_time": "bin_average_time"})

gridded = Gridded(sondes={}, global_attrs={})
gridded.set_l3_ds(
    l3_ds
)  # .where((l3_ds["u_qc"] == 0) & (l3_ds["p_qc"] == 0), drop=True))
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

circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
good_circles = get_good(circles, thres=12)
circles = keep_good(circles, good_circles)
circles_play = copy.deepcopy(circles)

# %%
no_int_ref = iterate_circle(circles=circles_play, config=config, int=False)
int_ref = iterate_circle(circles=circles_play, config=config, int=True)
# %%

gridded.add_weights()
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
good_circles = get_good(circles, thres=12)
circles = keep_good(circles, good_circles)
circles_w = copy.deepcopy(circles)
weights_ref = iterate_circle(circles=circles_w, config=config, int=True)


# %%
result = {
    "int": {key: [] for key in circles.keys()},
    "no_int": {key: [] for key in circles.keys()},
    "weight": {key: [] for key in circles.keys()},
}
sonde_ids = range(13)

for gap_sonde in sonde_ids:
    try:
        gap_no_int = remove_one(
            circles=circles_play, config=config, gap_sonde=gap_sonde, int=False
        )
    except IndexError:
        pass
    else:
        gap_no_int = calc_products(gap_no_int, config)
        gap_int = remove_one(
            circles=circles_play, config=config, gap_sonde=gap_sonde, int=True
        )
        gap_int = calc_products(gap_int, config)
        gap_w = remove_one(
            circles=circles_w, config=config, gap_sonde=gap_sonde, int=True
        )
        gap_w = calc_products(gap_w, config)
        for key in gap_int.keys():
            result["int"][key].append(gap_int[key].circle_ds)
            result["no_int"][key].append(gap_no_int[key].circle_ds)
            result["weight"][key].append(gap_w[key].circle_ds)


# %%

var = "omega"
mean_err_c = {
    "int": {key: [] for key in circles.keys()},
    "no_int": {key: [] for key in circles.keys()},
    "weight": {key: [] for key in circles.keys()},
}
for key in circles.keys():
    cint_ref = int_ref[key].circle_ds
    cno_int_ref = no_int_ref[key].circle_ds
    cweight_ref = weights_ref[key].circle_ds
    for ds_int, ds_no_int, ds_weight in zip(
        result["int"][key], result["no_int"][key], result["weight"][key]
    ):
        mean_err_c["int"][key].append(
            (ds_int[var] - cint_ref[var]).mean("altitude").values
        )
        mean_err_c["no_int"][key].append(
            (ds_no_int[var] - cno_int_ref[var]).mean("altitude").values
        )

        mean_err_c["weight"][key].append(
            (ds_weight[var] - cweight_ref[var]).mean("altitude").values
        )
# %%
x_name = "weight"
y_name = "no_int"

colors = sns.color_palette("turbo", 22)
fig, ax = plt.subplots()
fig.suptitle("Remove one sonde")
for idx, key in enumerate(mean_err_c[x_name].keys()):
    print("int", key, np.mean(mean_err_c[x_name][key]))
    print("no_int", key, np.mean(mean_err_c[y_name][key]))
    ax.scatter(
        mean_err_c["int"][key],
        mean_err_c["no_int"][key],
        color=colors[idx],
        s=10,
        label=key,
    )
# ax.legend(loc=1, fontsize="small")
ax.set_xlabel(f"{x_name} mean error / hPa hr-1")
ax.set_ylabel(f"{y_name} mean error / hPa hr-1")
ax.axvline(0, color="gray", alpha=0.5, linestyle="-")
ax.axhline(0, color="gray", alpha=0.5, linestyle="-")
x = np.linspace(-4, 4)
ax.fill_betweenx(x, -x, x, color="lightgray", alpha=0.2)
sns.despine(offset=10)
fig.tight_layout()
fig.savefig("../images/remove_one_sonde.pdf")


# %%
x_name = "weight"
y_name = "no_int"
int_err = np.concat(list(mean_err_c[x_name].values()))
no_int_err = np.concat(list(mean_err_c[y_name].values()))

nbins = 75
bin_range = (-4, 4)


fig, ax = plt.subplots()

ax.hist(
    int_err,
    bins=nbins,
    histtype="bar",
    alpha=0.5,
    range=bin_range,
    label=x_name,
    color="#00267f",
)
ax.hist(
    no_int_err,
    bins=nbins,
    histtype="bar",
    alpha=0.5,
    label=y_name,
    range=bin_range,
    color="#ffc726",
)

ax.legend()
ax.set_xlabel("mean error / hPa hr-1")
ax.set_ylabel("count")
ax.axvline(0, color="gray", alpha=0.5, linestyle="-")

sns.despine(offset=10)
fig.savefig("../images/hist_remove_one_sonde.png")
# %%
key = "HALO-20240816a_8c12"
var = "omega"

no_int_ds = no_int_ref[key].circle_ds
int_ds = int_ref[key].circle_ds
weight_ds = weights_ref[key].circle_ds
fig, ax = plt.subplots()
fig.suptitle(key)
ax.scatter(no_int_ds[var], no_int_ds.altitude, s=10, label="no_int", c="#00267f")

ax.scatter(int_ds[var], int_ds.altitude, s=10, label="int", c="#ffc726")
ax.scatter(weight_ds[var], weight_ds.altitude, s=10, label="weight", c="#6d88bc")

ax.set_ylabel("gpsalt / m")
ax.set_xlabel("omega / hPa hr-1")
ax.legend()
sns.despine(offset=10)
fig.tight_layout()
fig.savefig("../images/example_remove_one_sonde.png")
