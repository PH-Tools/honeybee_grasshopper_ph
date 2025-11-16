# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to run the OpenPH Calculation from a specified HBJSON file.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file).
    * [1] (str): The path to the HBJSON file to read in.
    * [2] (str): The path to the output folder.
"""

from collections import namedtuple
import os
from pathlib import Path
import sys

from openph.from_HBJSON import create_phpp
from openph.to_table import TableDisplayManager, TableNames, TableGroup
from openph_demand.to_table import DemandTableNames

from PHX.from_HBJSON import create_project, read_HBJSON_file


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot locate the specified file:'{path}'"
        super().__init__(self.msg)


Filepaths = namedtuple("Filepaths", ["output", "hbjson"])


def resolve_paths(_args: list[str]) -> Filepaths:
    """Get out the file input path.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * (Filepaths): The Filepaths object.
    """

    assert len(_args) == 3, "Error: Incorrect number of arguments."

    # -----------------------------------------------------------------------------------
    # -- The output folder location to save the script results to.
    output_folder = Path(_args[1])
    if not output_folder.exists():
        os.mkdir(output_folder)

    # -----------------------------------------------------------------------------------
    # -- The EnergyPlus HBJSON input file.
    results_hbjson_file = Path(_args[2])
    if not results_hbjson_file.exists():
        raise InputFileError(results_hbjson_file)

    return Filepaths(output_folder, results_hbjson_file)


def main(output_folder: Path, source_file_path: Path) -> None:
    OUTPUT_DIR = output_folder / "out"
    if not OUTPUT_DIR.exists():
        os.mkdir(OUTPUT_DIR)

    # -- Read in an existing HB_JSON and re-build the HB Objects
    # -------------------------------------------------------------------------
    print(f"Reading in the HBJSON file: {source_file_path}")
    hb_json_dict = read_HBJSON_file.read_hb_json_from_file(source_file_path)
    hb_model = read_HBJSON_file.convert_hbjson_dict_to_hb_model(hb_json_dict)

    # -- Generate the PhxProject from the HB-Model
    # -------------------------------------------------------------------------
    phx_project = create_project.convert_hb_model_to_PhxProject(
        hb_model, _group_components=True
    )

    # -- Build the PHPP Model
    # -------------------------------------------------------------------------
    for phx_variant in phx_project.variants:
        ph_energy_phpp = create_phpp.from_phx_variant(phx_variant)

        # ---------------------------------------------------------------------
        display = TableDisplayManager(ph_energy_phpp)
        print(f"\nAvailable table views: {display.available_tables}\n")
        
        # ---------------------------------------------------------------------
        # Group 1.1: Climate Tables (Core)
        # ---------------------------------------------------------------------
        climate_group = display.create_group(
            [
                TableNames.CLIMATE_ANNUAL,
                TableNames.CLIMATE_PEAK_LOAD,
            ]
        )
        climate_group.render(format="html", output_path=OUTPUT_DIR / "climate.html")

        # ---------------------------------------------------------------------
        # Group 1.2: Ventilation Tables (Core)
        # ---------------------------------------------------------------------
        ventilation_group = display.create_group(
            [
                TableNames.ROOMS_VENTILATION_PROPERTIES,
                TableNames.ROOMS_VENTILATION_SCHEDULE,
                TableNames.VENTILATION_DUCT_INPUTS,
                TableNames.VENTILATION_DUCT_RESULTS,
                TableNames.VENTILATION_DUCT_ITERATIVE_SOLVER,
                TableNames.VENTILATION_DUCT_NUSSELT_NUMBER,
            ]
        )
        ventilation_group.render(format="html", output_path=OUTPUT_DIR / "ventilation.html")

        # ---------------------------------------------------------------------
        # Group 1.3: Areas Tables (Core)
        # ---------------------------------------------------------------------
        areas_group = display.create_group(
            [
                TableNames.AREAS_SUMMARY,
                TableNames.AREAS_OPAQUE_SURFACE_ATTRIBUTES,
                TableNames.AREAS_OPAQUE_SURFACE_HEAT_GAIN,
                TableNames.AREAS_APERTURE_SURFACES,
                TableNames.AREAS_APERTURE_HEAT_GAIN,
                TableNames.AREAS_SOLAR_REDUCTION_WINTER,
                TableNames.AREAS_SOLAR_REDUCTION_SUMMER,
            ]
        )
        areas_group.render(format="html", output_path=OUTPUT_DIR / "areas.html")

        # ---------------------------------------------------------------------
        # Group 2.1: Energy-Demand | Ground
        # ---------------------------------------------------------------------
        demand_group = display.create_group(
            [
                DemandTableNames.GROUND,
            ]
        )
        demand_group.render(format="html", output_path=OUTPUT_DIR / "ground.html")

        # ---------------------------------------------------------------------
        # Group 2.2: Energy-Demand | Cooling and Heating
        # ---------------------------------------------------------------------
        demand_group = display.create_group(
            [
                DemandTableNames.COOLING_DEMAND,
                DemandTableNames.COOLING_DEMAND_PEAK_MONTH,
                DemandTableNames.HEATING_DEMAND,
            ]
        )
        demand_group.render(format="html", output_path=OUTPUT_DIR / "energy_demand.html")


        # ---------------------------------------------------------------------
        # Group 2.3: Energy-Demand | Cooling Detail Tables
        # ---------------------------------------------------------------------
        cooling_detail_tables = []

        for orientation in ["north", "east", "south", "west"]:
            opaque_rad = display.get_table(
                DemandTableNames.SUMMER_OPAQUE_SURFACE_RADIATION,
                phpp=ph_energy_phpp,
                orientation=orientation,
            )
            cooling_detail_tables.append(opaque_rad)

        for orientation in ["north", "east", "south", "west"]:
            window_rad = display.get_table(
                DemandTableNames.SUMMER_WINDOW_SURFACE_RADIATION,
                phpp=ph_energy_phpp,
                orientation=orientation,
            )
            cooling_detail_tables.append(window_rad)

        window_total = display.get_table(DemandTableNames.SUMMER_WINDOW_TOTAL_RADIATION, phpp=ph_energy_phpp)
        window_total = display.get_table(DemandTableNames.SUMMER_OPAQUE_SURFACE_HEAT_GAINS, phpp=ph_energy_phpp)
        cooling_detail_tables.append(window_total)

        cooling_detail_group = TableGroup(cooling_detail_tables)
        cooling_detail_group.render(format="html", output_path=OUTPUT_DIR / "summer_radiation.html")



if __name__ == "__main__":
    file_paths = resolve_paths(sys.argv)
    result = main(file_paths.output, file_paths.hbjson)
