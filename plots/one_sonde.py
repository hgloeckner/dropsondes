# %%

import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams["lines.linewidth"] = 3
mpl.rcParams.update({"font.size": 14})


# %%
root = "ipns://latest.orcestra-campaign.org/"
ds = xr.open_dataset(
    f"{root}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr", engine="zarr"
)

# %%
one_sonde = ds.isel(sonde_id=10).load()
# %%
ta_c = "#FF8F00"
rh_c = "#0277BD"
fig, axes = plt.subplots(ncols=2, figsize=(13, 6))
ax1 = axes[0]
ax2 = ax1.twiny()

(one_sonde.rh * 100).plot(y="gpsalt", ax=ax1, c=rh_c)
one_sonde.ta.plot(y="gpsalt", ax=ax2, c=ta_c)

ax1.set_ylabel("gps-altitude / m")
ax1.set_xlabel("relative humidity / %", c=rh_c)
ax2.set_xlabel("air temperature / K", c=ta_c)

for ax, c in zip([ax1, ax2], [rh_c, ta_c]):
    ax.set_title("")

    ax.xaxis.label.set_color(c)
    ax.tick_params(axis="x", colors=c)

ax2.spines["bottom"].set_color(rh_c)
ax2.spines["top"].set_color(ta_c)

wspd_c = "#00695C"
wdir_c = "#AD1457"

ax3 = axes[1]
ax4 = ax3.twiny()
one_sonde.w_dir.plot(y="gpsalt", ax=ax3, c=wdir_c)
one_sonde.w_spd.plot(y="gpsalt", ax=ax4, c=wspd_c)

ax3.set_ylabel("")
ax3.set_xlabel("wind direction / degree", c=wdir_c)
ax4.set_xlabel("wind speed / m s-1", c=wspd_c)

ax4.spines["bottom"].set_color(wdir_c)
ax4.spines["top"].set_color(wspd_c)

for ax, c in zip([ax1, ax2, ax3, ax4], [rh_c, ta_c, wdir_c, wspd_c]):
    ax.set_title("")

    ax.xaxis.label.set_color(c)
    ax.tick_params(axis="x", colors=c)

sns.despine(offset=10)
fig.tight_layout()
fig.savefig("../images/one_sonde.pdf")
