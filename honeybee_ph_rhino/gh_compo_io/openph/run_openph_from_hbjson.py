# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Run OpenPH with HBJSON File."""

import os

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io.gh_io import IGH
    from ph_gh_component_io.run_subprocess import process_stderr, process_stdout, run_subprocess
except ImportError as e:
    raise ImportError("\nFailed to import from ph_gh_component_io:\n\t{}".format(e))


class GHCompo_RunOpenPhFromHBJSON(object):
    """GHCompo Interface: HBPH - Run OpenPH with HBJSON File."""

    def __init__(self, _IGH, _output_folder, _hbjson_file, _calc, *args, **kwargs):
        # type: (IGH, str | None, str | None, bool, list, dict) -> None
        self.IGH = _IGH
        self._output_folder = _output_folder
        self.hbjson_file = _hbjson_file
        self.calc = _calc

    @property
    def ready(self):
        # type: () -> bool
        return self.hbjson_file is not None and self.calc is True

    @property
    def py3_script_file(self):
        # type: () -> str
        """The path to the Python3 Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_rhino",
            "scripts",
            "run_openph_with_hbjson_file.py",
        )

    @property
    def output_folder(self):
        # type: () -> str | None
        if self._output_folder:
            return self._output_folder
        else:
            if self.hbjson_file:
                return os.path.dirname(self.hbjson_file)
            else:
                return None

    def run(self):
        # type: () -> str | None
        if not self.ready:
            return None

        print("running OpenPH with HBJSON file: {}".format(self.hbjson_file))
        print("self.py3_script_file={}".format(self.py3_script_file))

        # -- Run as a Subprocess
        commands = [
            hb_folders.python_exe_path,  # ----- The python3-interpreter to use (LBT py3.10)
            self.py3_script_file,  # ----------- The python3-script to run
            self.output_folder,  # ------------- The save folder to use
            self.hbjson_file,  # --------------- The HBJSON file to use
        ]
        stdout, stderr = run_subprocess(commands)
        process_stderr(self.IGH, stderr)
        return process_stdout(self.IGH, stdout)
