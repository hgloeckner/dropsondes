# %%
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import eurec4a


# %%

l4_path = "/Users/helene/Documents/Data/Dropsonde/dropsondes/products/Level_4/PERCUSION_Level_4.zarr"
ds_lev4 = xr.open_dataset(l4_path, engine="zarr")


def get_nb_circles_per_flight(ds):
    circle_idx = np.insert(ds.sondes_per_circle.cumsum(dim="circle").values, 0, 0)[:-1]

    return ds.flight_id.isel(sonde=circle_idx).rename({"sonde": "circle"})


# %%
circle_flights = get_nb_circles_per_flight(ds_lev4)


plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots(figsize=(24, 6))
im = (ds_lev4.div).plot(
    cmap="coolwarm",
    ax=ax,
    y="altitude",
    center=0,
    vmin=-3e-5,
    vmax=3e-5,
    add_colorbar=False,
)
fig.subplots_adjust(right=0.93)
cax = fig.add_axes([0.95, 0.15, 0.01, 0.7])
fig.colorbar(im, cax=cax, label="divergence / s-1", extend="both")
nb_circ = 0
xpos = [-0.5]
for flight in np.unique(circle_flights):
    nb_circ += list(circle_flights).count(flight)
    # ax.axvline(nb_circ - 0.5, color="black")
    xpos.append(nb_circ - 0.5)

xtickpos = [(xpos[i] + xpos[i + 1]) / 2 for i in range(len(xpos) - 1)]
xlabels = (
    [
        "\n" * (i % 2) + f"{flight}".split("-")[1].split("a")[0]
        for i, flight in enumerate(np.unique(circle_flights)[:11])
    ]
    + [""]
    + [
        "\n" * ((i + 1) % 2) + f"{flight}".split("-")[1].split("a")[0]
        for i, flight in enumerate(np.unique(circle_flights)[12:])
    ]
)
ax.set_xticks(xtickpos, labels=xlabels)
ax.set_xlabel("")
ax.set_ylabel("Altitude / m")

ax1 = ax.twiny()
ax1.set_xticks([xtickpos[11]], labels=["Transfer 20240906"])
ax1.set_xlim(ax.get_xlim())
# ax.set_ylim(0, 2500)

fig.savefig("../images/divergence.png", transparent=True, bbox_inches="tight")

# %%
# %% div lowest 2500 m
circle_flights = get_nb_circles_per_flight(ds_lev4)


plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots(figsize=(24, 6))
im = (
    (ds_lev4.div)
    .sel(circle=slice(None, 43))
    .plot(
        cmap="coolwarm",
        ax=ax,
        y="altitude",
        center=0,
        vmin=-3e-5,
        vmax=3e-5,
        add_colorbar=False,
    )
)
fig.subplots_adjust(right=0.93)
cax = fig.add_axes([0.95, 0.15, 0.01, 0.7])
fig.colorbar(im, cax=cax, label="divergence / s-1", extend="both")
nb_circ = 0
ax.set_xlabel("")
ax.set_ylabel("Altitude / m")

ax.set_ylim(0, 2500)

fig.savefig("../images/divergence_east_low.png", bbox_inches="tight")
# %%
# %% div to mean lowest 2500 m
circle_flights = get_nb_circles_per_flight(ds_lev4)

cat = eurec4a.get_intake_catalog()
joanne = cat.dropsondes.JOANNE.level4.to_dask()


plt.style.use("./beach.mplstyle")
fig, ax = plt.subplots(figsize=(24, 6))
im = (joanne.D).plot(
    cmap="coolwarm",
    ax=ax,
    y="alt",
    center=0,
    vmin=-3e-5,
    vmax=3e-5,
    add_colorbar=False,
)
fig.subplots_adjust(right=0.93)
cax = fig.add_axes([0.95, 0.15, 0.01, 0.7])
fig.colorbar(im, cax=cax, label="divergence / s-1", extend="both")
ax.set_xlabel("")
ax.set_ylabel("Altitude / m")

ax.set_ylim(0, 2500)

fig.savefig("../images/divergence_joanne_low.png", bbox_inches="tight")
