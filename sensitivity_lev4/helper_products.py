import copy
import configparser
from pydropsonde.pipeline import iterate_Circle_method_over_dict_of_Circle_objects


def calc_products(circles, config):
    products = [
        "add_density",
        "apply_fit2d",
        "remove_invalid",
        "add_divergence",
        "add_vorticity",
        "add_omega",
        # "add_wvel",
        # "add_regression_stderr",
    ]
    iterate_Circle_method_over_dict_of_Circle_objects(circles, products, config=config)
    return circles


def get_xy_circles(circles, config):
    get_xy = [
        "get_xy_coords_for_circles",
        "broadcast_ds",
    ]
    iterate_Circle_method_over_dict_of_Circle_objects(circles, get_xy, config=config)
    return circles


def interp_na(circles, interpolate, config, w=False, max_gap=1500):
    if interpolate:
        try:
            config.add_section("circles.Circle.interpolate_na")
        except configparser.DuplicateSectionError:
            pass
        config.set("circles.Circle.interpolate_na", "max_gap", str(max_gap))
        if w:
            print("calculated with weight")
            try:
                config.add_section("circles.Circle.add_weights")
            except configparser.DuplicateSectionError:
                pass
            config.set("circles.Circle.interpolate_na", "max_gap", str(15000))
            path = "/Users/helene/Documents/Orcestra/dropsonde/dropsonde_data/autocorrelation.zarr"
            config.set("circles.Circle.add_weights", "path", path)
            config.set("circles.Circle.add_weights", "method", "autocorrelation")
            get_xy = [
                "add_distances",
                "add_weights",
                "interpolate_na",
            ]

        else:
            config.set("circles.Circle.interpolate_na", "max_gap", str(max_gap))
            get_xy = [
                "interpolate_na",
            ]
        iterate_Circle_method_over_dict_of_Circle_objects(
            circles, get_xy, config=config
        )
    return circles


def get_good(circles, thres=12):
    good_circles = []
    for name, circle in circles.items():
        ds = circle.circle_ds
        good_sondes = ds.where((ds["u_qc"] == 0) & (ds["p_qc"] == 0), drop=True).sizes[
            "sonde"
        ]

        if good_sondes >= thres:
            good_circles.append(name)
            print(name, good_sondes)
    return good_circles


def keep_good(circles, good_circles):
    for key in list(circles.keys()):
        if key not in good_circles:
            circles.pop(key)
        else:
            print(key)
    return circles


def iterate_circle(circles, config, int=False, w=None):
    circles_play = copy.deepcopy(circles)
    get_xy_circles(circles_play, config)
    interp_na(circles=circles_play, interpolate=int, config=config, w=w)
    calc_products(circles_play, config)
    return circles_play
