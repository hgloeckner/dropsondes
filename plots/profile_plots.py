# %%

import xarray as xr
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

lev3 = xr.open_dataset(
    "/Users/helene/Documents/Data/Dropsonde/dropsonde_data/products/Level_3_qc/PERCUSION_Level_3.zarr"
)
# %%

sal = lev3.where(lev3.aircraft_longitude > -40, drop=True)
bb = lev3.where(lev3.aircraft_longitude < -40, drop=True)

# %%

csal = "#960018"
cbb = "#0085db"
variables = ["theta", "rh", "u", "v"]


fig, axes = plt.subplots(ncols=len(variables), figsize=(6 * len(variables), 6))

for j, var in enumerate(variables):
    for i in range(max([sal.sonde.size, bb.sonde.size])):
        sonde = max([sal.sonde.size, bb.sonde.size]) - i - 1
        try:
            sal.sel(sonde=sonde)[var].plot(
                ax=axes[j], color=csal, alpha=0.05, y="altitude"
            )
        except IndexError:
            pass
        bb.sel(sonde=sonde)[var].plot(ax=axes[j], color=cbb, alpha=0.05, y="altitude")

    sal[var].mean("sonde").plot(ax=axes[j], color=csal, y="altitude", linewidth=5)
    bb[var].mean("sonde").plot(ax=axes[j], color=cbb, y="altitude", linewidth=5)

sns.despine(offset=10)

for ax in axes:
    ax.set_ylim(0, None)
sns.despine(offset={"left": 10})
line = Line2D([0], [0], label="Sal", alpha=0.5, color=csal)
line1 = Line2D([0], [0], label="Barbados", alpha=0.5, color=cbb)
axes[0].legend(handles=[line, line1])
fig.tight_layout()
fig.savefig("../images/profile_overview.png")

# %%
