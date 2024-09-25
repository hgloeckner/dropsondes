# %%
import matplotlib.pyplot as plt
import xarray as xr
import seaborn as sns
import sys
import os

sys.path.append("./")
sys.path.append("../")

import droputils.rough_segments as segments  # noqa: E402
import droputils.data_utils as data_utils  # noqa: E402
import droputils.circle_products as circle_products  # noqa: E402


# %%
folder = "complete"

level_3_path = f"/Users/helene/Documents/Data/Dropsonde/{folder}/products/HALO/dropsondes/Level_3/PERCUSION_Level_3.zarr"


ds_lev3 = xr.open_dataset(level_3_path, engine="zarr")

flight_ids = list(segments.starts.keys())


# %%
# gives reasonable results
all_data = []
for flight_id in flight_ids:
    print(flight_id)
    dict_ds_c = data_utils.get_circle_data(ds_lev3, flight_id)
    c_names = list(dict_ds_c.keys())
    flight_c = []
    for c_name in c_names:
        circle = dict_ds_c[c_name]

        circle = circle_products.get_xy_coords_for_circles(circle, position=c_name)
        circle = circle_products.apply_fit2d(circle)
        circle = circle_products.get_div_and_vor(circle)
        circle = circle_products.get_density(circle)
        circle = circle_products.get_vertical_velocity(circle)
        circle = circle_products.get_omega(circle)
        circle = circle_products.add_circle_vars(
            circle, c_name=c_name, flight_id=flight_id
        )
        circle = circle_products.add_circle_dimensions(
            circle, c_name=c_name, flight_id=flight_id
        )
        flight_c.append(circle.copy())
        print(circle.coords)

    all_data.append(
        circle_products.merge_concat_circles(
            flight_c, dim1="circle_id", dim2="sonde_id"
        )
    )

ds = circle_products.merge_concat_circles(all_data, dim1="circle_id", dim2="sonde_id")


l4_path = os.path.dirname(level_3_path.replace("Level_3", "Level_4"))
# %%
ds.to_zarr(os.path.join(l4_path, "PERCUSION_Level_4.zarr"))

# %%
ds.to_netcdf(os.path.join(l4_path, "PERCUSION_Level_4.nc"))
# %%

# %%
ds = xr.open_dataset(os.path.join(l4_path, "PERCUSION_Level_4.nc"))
# %%
c_types = ["south", "center", "north"]
# c_types = ["west"]


sns.set_palette("turbo", n_colors=len(flight_ids))
fig, axes = plt.subplots(ncols=3, figsize=(18, 6))


for c_type, ax in zip(c_types, axes):
    ds_type = ds.sel(position=[val for val in ds.position.values if c_type in val])
    for flight_id in ds_type.flight_id.values:
        for pos in ds_type.position.values:
            ds_type.sel(flight_id=flight_id, position=pos).w_vel.plot(
                ax=ax, y="alt", label=flight_id
            )
    ax.set_title(f"circles {c_type}")


sns.despine(offset=10)
for ax in axes.flatten():
    ax.axvline(0, alpha=0.5, color="grey")
    ax.legend()
    # ax.set_xlim(-0.6, 0.2)

# %%
