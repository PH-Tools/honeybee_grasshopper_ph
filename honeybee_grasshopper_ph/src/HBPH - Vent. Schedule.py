#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
#
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
#
# Copyright (c) 2022, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com>
# Honeybee-PH is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# Honeybee-PH is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License
# see <https://github.com/PH-Tools/honeybee_ph/blob/main/LICENSE>.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
Create a new Honeybee-Energy ScheduleRuleset for the fresh-air ventilation system 
operation using 'Passive House' style inputs. These inputs will be used to create an 
equivalent constant-value fresh air ventilation operation scheduled which can then be
used to control the Honeybee-Energy fresh air ventilation. Note that the values here
will also be stored and used as detailed inputs into  WUFI-Passive or PHPP upon export.
-
EM October 2, 2022
    Args:
        _name_: Optional name for the Ventilation Schedule
        
        operating_day_per_week_: (default=7) Value for the number of days/week to run
            at the specified flowrates.
        operating_weeks_per_year_: (default=52) Value for the number of weeks/year to 
            run at the specified flowrates.
        
        _op_period_high: Enter an Operation-Period decribing the high-speed period.
        _op_period_standard: Enter an Operation-Period decribing the normal-speed period.
        _op_period_basic: Enter an Operation-Period decribing the low-speed period.
        _op_period_minimum: Enter an Operation-Period decribing the minimum-speed period.
    
    Returns:
        ventilation_sch_: The HB-Ventilation Schedule which can be applied to HB Rooms
"""


import ghpythonlib.components as ghc
import Grasshopper as gh
import Rhino as rh
import rhinoscriptsyntax as rs
import scriptcontext as sc

try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_utils:\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\t{}".format(e))

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_

reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Vent. Schedule"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_compo_io)
    reload(gh_io)
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH(ghdoc, ghenv, sc, rh, rs, ghc, gh)


# -------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateVentSched(
    IGH,
    _name_,
    operating_days_per_week_,
    operating_weeks_per_year_,
    _op_period_high,
    _op_period_standard,
    _op_period_basic,
    _op_period_minimum,
)
ventilation_sch_ = gh_compo_interface.run()

# ------------------------------------------------------------------------------
if ventilation_sch_:
    preview.object_preview(ventilation_sch_.properties.ph)
