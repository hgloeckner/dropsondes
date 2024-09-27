import configparser
import os
from datetime import datetime, date, time
import numpy as np
import xarray as xr
import pandas as pd

import droputils.rough_segments as segments


def get_config(config_file="../orcestra_drop.cfg"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def get_l3_path(config, flight_id="20240811", platform="HALO"):
    """
    get l3 filename for a flight from config file
    """
    l3_file = os.path.join(
        config["processor.Gridded.get_l3_dir"]["l3_dir"],
        config["processor.Gridded.get_l3_filename"]["l3_filename"],
    )
    return l3_file


def get_circle_data(ds, flight_id="20240811"):
    """
    get a dictionary of circle data for one flight
    """
    flight_date = date.fromisoformat(flight_id)
    circles = {
        circle: {
            "start_time": np.datetime64(
                datetime.combine(
                    flight_date, time.fromisoformat(segments.starts[flight_id][circle])
                )
            ),
            "end_time": np.datetime64(
                datetime.combine(
                    flight_date, time.fromisoformat(segments.ends[flight_id][circle])
                )
            ),
        }
        for circle in segments.starts[flight_id].keys()
    }
    ds_c = {}
    for circle in list(circles.keys()):
        try:
            ds_c[circle] = ds.where(
                ds["launch_time"] > circles[circle]["start_time"],
                drop=True,
            ).where(
                ds["launch_time"] < circles[circle]["end_time"],
                drop=True,
            )
        except ValueError:
            print(f"No sondes for circle {circle}. It is omitted")

    return ds_c


def get_circle_mean(ds, variable):
    flights = []
    for flight in np.unique(ds.flight):
        grouped_mean = (
            ds.where(ds.flight == flight, drop=True).groupby("c_name").mean()[variable]
        )
        mean_data = xr.DataArray(grouped_mean, dims=["c_name"]).expand_dims(
            dim={"flight": [flight]}
        )

        flights.append(mean_data.copy())
    return xr.concat(flights, dim="flight")


def add_operator(ds, sonde_op):
    def assign_operator(time):
        date = pd.Timestamp(time).date()
        return sonde_op[date]

    df = ds.launch_time.to_series()
    df = df.apply(assign_operator)
    return ds.assign_coords(operator=xr.DataArray(df, name="operator"))


def add_island(ds):
    def assign_island(lon):
        if lon > -40:
            return "SAL"
        else:
            return "BB"

    df = ds.aircraft_longitude.to_series()
    df = df.apply(assign_island)
    return ds.assign_coords(island=xr.DataArray(df, name="island"))
