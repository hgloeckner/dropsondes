# %%
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import numpy as np
import os

# %%

root = "ipns://latest.orcestra-campaign.org"


ds_lev4 = xr.open_zarr(
    f"{root}/products/HALO/dropsondes/Level_4/PERCUSION_Level_4.zarr"
)
flight_ids = np.unique(ds_lev4.flight_id.values)[1:]
ds_lev3 = xr.open_zarr(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr"
)
flight_ids = np.unique(ds_lev4.flight_id.values)[1:]
# %%

local_root = "/Users/helene/Documents/Data/Dropsonde/complete"
lev1_example = xr.open_dataset(
    f"{local_root}/products/HALO/dropsondes/Level_1/HALO-20240914a/D20240914_130224QC.nc"
)
# %%
save_path = "/Users/helene/Documents/Data/Dropsonde/orcestra_plots/"

# %%


fig, ax = plt.subplots()
fig.suptitle("Level_1")

ax.scatter(lev1_example.rh, lev1_example.alt, label="dim: altitude")
ax.scatter(lev1_example.rh, lev1_example.gpsalt, label="dim: gps-altitude")
ax.set_ylabel("height / m")
ax.set_xlabel("RH / 1")
sns.despine(offset=10)
ax.legend()
fig.tight_layout()

fig.savefig(os.path.join(save_path, "lev1_both"))  # , transparent=True)
