# %%
import xarray as xr
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

    all_data.append(
        circle_products.merge_concat_circles(
            flight_c, dim1="circle_id", dim2="sonde_id"
        )
    )


ds = circle_products.merge_concat_circles(all_data, dim1="circle_id", dim2="sonde_id")


l4_path = os.path.dirname(level_3_path.replace("Level_3", "Level_4"))
# %%
ds.to_zarr(os.path.join(l4_path, "PERCUSION_Level_4.zarr"), mode="w")

# %%
ds.to_netcdf(os.path.join(l4_path, "PERCUSION_Level_4.nc"))

# %%
