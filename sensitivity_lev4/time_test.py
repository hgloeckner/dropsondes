# %%
import configparser

import pydropsonde.pipeline
import xarray as xr
from pydropsonde.processor import Gridded
import pydropsonde

from helper_products import pipeline_like_iter

from pydropsonde.helper.xarray_helper import write_ds, open_dataset

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
circles = pydropsonde.pipeline.create_and_populate_circle_object(gridded, None)

# %%
no_int_ref = pipeline_like_iter(circles=circles, config=config, int=False)
# %%


# %%

for val in no_int_ref.circles.values():
    ds = val.circle_ds
    print(ds.circle_time.values)
    write_ds(
        ds, "../dropsonde_data/", "test.zarr", object_dims=("sonde"), alt_dim="altitude"
    )
    ds = open_dataset("../dropsonde_data/test.zarr")
    print(ds["circle_time"].values)
    print(ds["sonde_time"].mean().values)
    break
