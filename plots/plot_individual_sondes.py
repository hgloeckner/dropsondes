# %%
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import numpy as np
from datetime import date
import os

# %%
folder = "complete"

l3_path = f"/Users/helene/Documents/Data/Dropsonde/{folder}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.nc"


ds = xr.open_dataset(l3_path)

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
print(ds_flight.sonde_id.values)
# %%
refs = ["234140488", "233460722", "234150017"]
olds = ["213430255", "213430256", "213431458"]
labels = ["south", "center", "north"]


plt_variables = ["rh", "u", "v"]
plt_units = ["%", r"m s$^{-1}$", r"m s$^{-1}$"]
alt_var = "alt"


# %%
sns.set_palette("Paired", n_colors=12)
fig, axes = plt.subplots(ncols=len(plt_variables), figsize=(18, 6))
fig.suptitle("compare ref and 2021 sondes")
for old, ref, label in zip(olds, refs, labels):
    ds_old = ds.sel(sonde_id=old)
    ds_ref = ds.sel(sonde_id=ref)
    for ax, plt_var, unit in zip(axes, plt_variables, plt_units):
        ds_old[plt_var].plot(y=alt_var, ax=ax, label=f"{label} - 2021")
        ds_ref[plt_var].plot(y=alt_var, ax=ax, label=f"{label} - ref")

        ax.set_xlabel(f"{plt_var} / {unit}")
for ax in axes.flatten():
    ax.set_title("")
for ax in axes[1:]:
    ax.axvline(0, color="grey", alpha=0.5)
# axes[1].set_xlim(0, 1)
# axes[2].set_xlim(-30, 20)
# axes[3].set_xlim(-20, 15)
axes[0].legend()
sns.despine(offset=10)
fig.tight_layout()


quicklook_path = os.path.dirname(l3_path.replace("Level_3", "Quicklooks"))
os.makedirs(quicklook_path, exist_ok=True)
fig.savefig(f"{quicklook_path}/ref_2021_profiles.png", dpi=80)
