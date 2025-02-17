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

from helper_products import get_good, keep_good


config = configparser.ConfigParser()
config.read("../orcestra_drop.cfg")

# %%
root = "ipns://latest.orcestra-campaign.org/"
l3_ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
)

gridded = Gridded(sondes={}, global_attrs={})
gridded.set_l3_ds(l3_ds.where((l3_ds["u_qc"] == 0) & (l3_ds["p_qc"] == 0), drop=True))
gridded.get_circle_times_from_segmentation(
    "https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml"
)
gridded.alt_dim = "altitude"
gridded.sonde_dim = "sonde"

# %%
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None)

good_circles = get_good(circles, thres=12)


circles = keep_good(circles, good_circles)
circles_play = copy.deepcopy(circles)


# %%


def get_gap_sizes(ds, variable):
    res = []
    for sonde_id in ds.sonde:
        res.append(
            ds.sel(sonde=sonde_id)
            .dropna(dim="altitude", subset=[variable])
            .altitude.diff(dim="altitude")
            - 10
        )
    return res


# %%
ds_p = xr.concat(get_gap_sizes(l3_ds, "p"), dim="sonde")
ds_u = xr.concat(get_gap_sizes(l3_ds, "u"), dim="sonde")
ds_rh = xr.concat(get_gap_sizes(l3_ds, "rh"), dim="sonde")
ds_ta = xr.concat(get_gap_sizes(l3_ds, "ta"), dim="sonde")

# %%

colors = ["#00E3DB", "#ffc726", "#00267f"]
bins = np.concat([np.linspace(0, 1000, 50), np.linspace(1000, 10000, 50)])
fig, ax = plt.subplots(figsize=(6, 6))
for c, ds, var in zip(colors, [ds_p, ds_u, ds_rh], ["p", "u", "rh"]):
    bins = 100
    if var == "u":
        bins = 500
    ds.plot.hist(ax=ax, bins=bins, histtype="bar", color=c, alpha=0.5, label=var)

ax.set_ylim(0, 20)
#
ax.set_xlim(0, 4000)
ax.set_xlabel("gap size / m")
ax.set_ylabel("count")
ax.set_yticks(np.arange(0, 21, 2))
ax.legend()
sns.despine(offset=10)
fig.savefig("../images/gap_size_hist.pdf")
