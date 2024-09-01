# %%
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import sys
import os

sys.path.append("./")
sys.path.append("../")

import droputils.plot_utils as plot_utils  # noqa: E402


# %%

level_4_path = "/Users/helene/Documents/Data/Dropsonde/complete/dropsondes/Level_3/PERCUSION_Level_4.nc"

ds_lev4 = xr.open_dataset(level_4_path)
# %%
cmap_name = "Blues_d"
mean_iwv = ds_lev4.iwv.where(ds_lev4.iwv > 10, drop=True).mean(dim=["sonde_id"])
colors, norm = plot_utils.create_colormap_by_values(mean_iwv, cmap_name=cmap_name)
# %%
plt_var = "w_vel"

cmap = sns.color_palette(cmap_name, as_cmap=True)

fig, axes = plt.subplots(ncols=3, figsize=(18, 6))

for c_type, ax in zip(["south", "center", "north"], axes):
    ds_type = ds_lev4.sel(position=c_type)
    for flight_id in ds_type.flight_id.values:
        color = colors.sel(flight_id=flight_id, position=c_type).values
        ds_type.sel(flight_id=flight_id)[plt_var].plot(
            ax=ax, y="alt", label=flight_id, color=color
        )
    ax.set_title(f"circles {c_type}")
fig.tight_layout()
sns.despine(offset=10)
fig.subplots_adjust(bottom=0.15, top=0.9, left=0.05, right=0.9, wspace=0.15, hspace=0.3)
cb_ax = fig.add_axes([0.92, 0.08, 0.01, 0.8])
cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cb_ax)
cbar.ax.set_ylabel("IWV", rotation=-90, labelpad=15)
for ax in axes:
    ax.axvline(0, alpha=0.5, color="grey")
    # ax.set_xlim(-0.5, 0.5)
    # ax.set_xlim(-0.05, 0.05)

quicklook_path = os.path.dirname(level_4_path.replace("Level_3", "Quicklooks"))
os.makedirs(quicklook_path, exist_ok=True)
fig.savefig(f"{quicklook_path}/{plt_var}_by_iwv.png", dpi=200)
