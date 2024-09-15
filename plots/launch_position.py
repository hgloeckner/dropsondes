# %%

import numpy as np
import xarray as xr
from datetime import date
import matplotlib.pyplot as plt

# %%

# %%

level_3_path = "/Users/helene/Documents/Data/Dropsonde/complete/dropsondes/Level_3/PERCUSION_Level_3.nc"


ds = xr.open_dataset(level_3_path)
# %%
flight_id = 20240907
ds_flight = (
    ds.where(
        ds["launch_time"] > np.datetime64(date.fromisoformat(str(flight_id))),
        drop=True,
    )
    .where(
        ds["launch_time"] < np.datetime64(date.fromisoformat(str(flight_id + 1))),
        drop=True,
    )
    .swap_dims({"sonde_id": "launch_time"})
    .sortby("launch_time")
)

# %%


fig, ax = plt.subplots(figsize=(18, 6))
ax.plot(
    ds_flight["launch_time"].values,
    ds_flight.lat.mean(dim="alt").values,
    marker="o",
)
plt.xticks(rotation=45, ha="right")
