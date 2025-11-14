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
from openph.to_table import TableDisplayManager, TableNames

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
        # Group 1: Climate Tables (Core)
        # ---------------------------------------------------------------------
        climate_group = display.create_group(
            [
                TableNames.CLIMATE_ANNUAL,
                TableNames.CLIMATE_PEAK_LOAD,
                TableNames.CLIMATE_RADIATION_FACTORS,
            ]
        )
        climate_group.render(format="txt", output_path=OUTPUT_DIR / "climates.txt")
        climate_group.render(format="html", output_path=OUTPUT_DIR / "climate.html")

if __name__ == "__main__":
    file_paths = resolve_paths(sys.argv)
    result = main(file_paths.output, file_paths.hbjson)
