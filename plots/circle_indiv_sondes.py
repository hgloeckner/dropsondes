# %%
import sys
import os
import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append("./")
sys.path.append("../")
import droputils.data_utils as data_utils  # noqa: E402

# %%
flight_id = "20240906"  # sys.argv[1]
config_path = "/Users/helene/Documents/Orcestra/playground/run_complete_orcestra/complete_orcestra.cfg"  # sys.argv[2]
circle = "west"  # sys.arg[3]

config = data_utils.get_config(config_path)
l3_path = data_utils.get_l3_path(config, flight_id)

ds = xr.open_dataset(l3_path)
dict_ds_c = data_utils.get_circle_data(ds, flight_id)
# %%

plt_variables = ["theta", "rh", "u", "v"]
plt_units = ["K", "%", r"m s$^{-1}$", r"m s$^{-1}$"]
alt_var = "alt"

ds_c = dict_ds_c[circle]
ds_c = (
    ds_c.where(ds_c["ta"].isnull().sum(dim=alt_var) < 1300, drop=True)
    .where(ds_c["rh"].isnull().sum(dim=alt_var) < 1300, drop=True)
    .where(ds_c["p"].isnull().sum(dim=alt_var) < 1300, drop=True)
)

# %%
sns.set_palette("turbo", n_colors=12)
fig, axes = plt.subplots(ncols=len(plt_variables), figsize=(18, 6))
fig.suptitle(f"{flight_id} circle: {circle}")
for sonde_id in ds_c.sonde_id:
    ds_sonde = ds_c.sel(sonde_id=sonde_id)
    for ax, plt_var, unit in zip(axes, plt_variables, plt_units):
        ds_sonde[plt_var].plot(y=alt_var, ax=ax, label=sonde_id.values)
        ax.set_xlabel(f"{plt_var} / {unit}")
for ax in axes.flatten():
    ax.set_title("")
for ax in axes[2:]:
    ax.axvline(0, color="grey", alpha=0.5)
axes[1].set_xlim(0, 1)
axes[2].set_xlim(-30, 20)
axes[3].set_xlim(-20, 15)
axes[0].legend()
sns.despine(offset=10)
fig.tight_layout()


quicklook_path = os.path.dirname(l3_path.replace("Level_3", "Quicklooks"))
os.makedirs(quicklook_path, exist_ok=True)
fig.savefig(f"{quicklook_path}/{flight_id}_{circle}_profiles.png", dpi=80)
