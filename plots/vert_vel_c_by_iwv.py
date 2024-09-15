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

level_4_path = "/Users/helene/Documents/Data/Dropsonde/complete/dropsondes/Level_4/PERCUSION_Level_4.nc"

ds_lev4 = xr.open_dataset(level_4_path)
level_3_path = "/Users/helene/Documents/Data/Dropsonde/complete/dropsondes/Level_3/PERCUSION_Level_3.nc"
# complete/dropsondes/Level_3

ds_lev3 = xr.open_dataset(level_3_path)
# %%
cmap_name = "Blues_d"
mean_iwv = ds_lev4.iwv.where(ds_lev4.iwv > 10, drop=True).mean(dim=["sonde_id"])
colors, norm = plot_utils.create_colormap_by_values(mean_iwv, cmap_name=cmap_name)

# %%
plt_var = "omega"
unit = "Pa/s"

mode = "compare_type"
save_name = f"{plt_var}_by_iwv_{mode}.png"

quantiles = [0, 0.33, 0.66, 1]

cmap = sns.color_palette(cmap_name, as_cmap=True)

fig, axes = plt.subplots(ncols=3, nrows=3, figsize=(18, 18), sharey=True, sharex="col")

for j, position in enumerate(["south", "center", "north"]):
    ds_pos = ds_lev4.sel(position=position)
    if mode == "compare_all":
        ds_iwv_quantile = ds_lev4.iwv.mean("sonde_id").quantile(quantiles)
    elif mode == "compare_type":
        ds_iwv_quantile = ds_pos.iwv.mean("sonde_id").quantile(quantiles)

    ds_iwv_quantile_values = ds_iwv_quantile.values
    ds_iwv_quantile_values[-1] = ds_iwv_quantile_values[-1] + 0.01
    ds_iwv_quantile = xr.DataArray(
        ds_iwv_quantile_values, dims=ds_iwv_quantile.dims, coords=ds_iwv_quantile.coords
    )

    for qu in range(3):
        ax = axes[qu]
        ds_iwv_quant = (
            ds_pos[plt_var]
            .where(
                ds_pos.iwv.mean("sonde_id")
                > ds_iwv_quantile.isel(quantile=qu, drop=True).values - 0.001
            )
            .where(
                ds_pos.iwv.mean("sonde_id")
                < ds_iwv_quantile.isel(quantile=qu + 1, drop=True).values
            )
            .dropna("alt", how="all")
            .dropna("flight_id", how="all")
        )

        for flight_id in ds_iwv_quant.flight_id:
            color = colors.sel(flight_id=flight_id, position=position).values
            plt_ds = ds_iwv_quant.sel(flight_id=flight_id)
            plt_ds.plot(
                ax=axes[qu, j],
                y="alt",
                label=f"{flight_id.values}",
                color=color,
            )


fig.tight_layout()
fig.suptitle(f"iwv {mode}", fontsize=14)


sns.despine(offset=10)
fig.subplots_adjust(
    bottom=0.05, top=0.95, left=0.05, right=0.9, wspace=0.15, hspace=0.3
)


cb_ax = fig.add_axes([0.92, 0.17, 0.01, 0.7])
cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cb_ax)
cbar.ax.set_ylabel("IWV", rotation=-90, labelpad=15)

for ax in axes.flatten():
    ax.axvline(0, alpha=0.5, color="grey")
    """
    if plt_var =='w_vel':
        ax.set_xlim(-0.05, 0.05)
    if plt_var =='omega':
        ax.set_xlim(-0.5, 0.5)
    """
    ax.set_title("")
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.legend()

for ax, moist in zip(axes[:, 1], ["dry", "medium", "moist"]):
    ax.text(0, 14000, moist, ha="center")

for ax, pos in zip(axes[0, :], ["south", "center", "north"]):
    ax.set_title(f"{pos} circles", pad=15)
for ax in axes[:, 0]:
    ax.set_ylabel(
        f'{ds_lev3.alt.attrs['standard_name']} / {ds_lev3.alt.attrs['units']}'
    )
for ax in axes[2, :]:
    ax.set_xlabel(f"{plt_var} / {unit}")

quicklook_path = os.path.dirname(level_4_path.replace("Level_4", "Quicklooks"))
os.makedirs(quicklook_path, exist_ok=True)
fig.savefig(f"{quicklook_path}/{save_name}", dpi=200)
