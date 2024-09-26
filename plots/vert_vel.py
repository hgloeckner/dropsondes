# %%
import xarray as xr
import sys
import os

sys.path.append("./")
sys.path.append("../")


# %%
folder = "complete"

l4_path = (
    f"/Users/helene/Documents/Data/Dropsonde/{folder}/products/HALO/dropsondes/Level_4/"
)

ds = xr.open_dataset(os.path.join(l4_path, "PERCUSION_Level_4.zarr"), engine="zarr")
# %%
