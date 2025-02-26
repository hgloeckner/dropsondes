# %%
import configparser

import copy
import pydropsonde.pipeline
import xarray as xr
from pydropsonde.processor import Gridded
import pydropsonde

from helper_products import iterate_circle


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
)  # (l3_ds.where((l3_ds["u_qc"] == 0) & (l3_ds["p_qc"] == 0), drop=True))
gridded.get_circle_times_from_segmentation(
    "https://orcestra-campaign.github.io/flight_segmentation/all_flights.yaml"
)
gridded.alt_dim = "altitude"
gridded.sonde_dim = "sonde"


# %%
gridded.create_interim_l4()

gridded.add_autocorrelation(
    autocorr_dir="../dropsonde_data/", filename="autocorrelation.zarr"
)
gridded.add_distances()
gridded.add_weights()

# %%
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
# good_circles = get_good(circles, thres=12)
# circles = keep_good(circles, good_circles)
circles_play = copy.deepcopy(circles)
# %%
gridded.interim_l4_ds = gridded.interim_l4_ds.drop_vars(
    [f"{var}_weights" for var in ["u", "v", "p", "theta", "q", "rh", "ta"]],
    errors="ignore",
)
# gridded.add_weights(method="no_weights")
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
circles_play = copy.deepcopy(circles)

no_weights_ref = iterate_circle(circles=circles_play, config=config, int=True)

# %%
gridded.interim_l4_ds = gridded.interim_l4_ds.drop_vars(
    [f"{var}_weights" for var in ["u", "v", "p", "theta", "q", "rh", "ta"]],
    errors="ignore",
)
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles
circles_play = copy.deepcopy(circles)

no_no_weights_ref = iterate_circle(circles=circles_play, config=config, int=True)

# %%
gridded.interim_l4_ds = gridded.interim_l4_ds.drop_vars(
    [f"{var}_weights" for var in ["u", "v", "p", "theta", "q", "rh", "ta"]],
    errors="ignore",
)
gridded.add_weights(method="autocorrelation")

circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles

circles_play = copy.deepcopy(circles)

weights_ref = iterate_circle(circles=circles_play, config=config, int=True)
# %%

circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None).circles

circles_play = copy.deepcopy(circles)

no_int_ref = iterate_circle(circles=circles_play, config=config, int=False)
