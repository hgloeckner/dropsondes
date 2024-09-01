# %%

import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import sys
import os
import numpy as np

sys.path.append("./")
sys.path.append("../")

import droputils.plot_utils as plot_utils  # noqa: E402

# %%

# %%
l4_path = "/Users/helene/Documents/Data/Dropsonde/complete/dropsondes/Level_3/PERCUSION_Level_4.nc"
ds_lev4 = xr.open_dataset(l4_path)

# %%

cmap_name = "Blues"
mean_iwv = ds_lev4.iwv.where(ds_lev4.iwv > 10, drop=True).mean(dim=["sonde_id"])
colors, norm = plot_utils.create_colormap_by_values(mean_iwv, cmap_name=cmap_name)
# %%
sonde_dim = "sonde_id"
alt_var = "alt"
all_int = []
for flight_id in ds_lev4.flight_id:
    all_pos = []
    for position in ds_lev4.position:
        ds_sonde = ds_lev4.sel(flight_id=flight_id, position=position)
        omega = ds_sonde.omega.where(~np.isnan(ds_sonde.omega), drop=True).swap_dims(
            {alt_var: "p"}
        )
        if omega.sizes["p"] > 0:
            int_omega = omega.integrate(coord="p")
            all_pos.append(int_omega.copy())

    all_int.append(xr.concat(all_pos, dim="position"))
ds_int_omega = xr.concat(all_int, dim="flight_id")


# %%
cmap = sns.color_palette(cmap_name, as_cmap=True)

fig, ax = plt.subplots(figsize=(10, 6))

for c_type in ["south", "center", "north"]:
    ds_type = ds_int_omega.sel(position=c_type)
    for flight_id in ds_type.flight_id.values:
        color = colors.sel(flight_id=flight_id, position=c_type).values
        ax.scatter(
            x=ds_type.flight_id,
            y=ds_type.values,
            color=color,
        )

    ax.set_ylabel("integrated omega (with $p$)")
fig.tight_layout()
sns.despine(offset=10)
fig.subplots_adjust(bottom=0.1, top=0.95, left=0.1, right=0.9, wspace=0.15, hspace=0.3)
cb_ax = fig.add_axes([0.92, 0.08, 0.01, 0.8])
cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cb_ax)
cbar.ax.set_ylabel("IWV", rotation=-90, labelpad=15)

quicklook_path = os.path.dirname(l4_path.replace("Level_3", "Quicklooks"))
os.makedirs(quicklook_path, exist_ok=True)
fig.savefig(f"{quicklook_path}/{flight_id}_integrated_omega.png", dpi=200)


# %%
