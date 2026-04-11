#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2026, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
Settings for the building-segment's Summer Ventilation. These are OPTIONAL extra attributes which 
can be used to set things like window ventilation (daytime and nighttime) as well as supplamental 
extract ventilation. Note that for Phius Certified projects, unless you are building a 'Passive' 
cooling building (one with NO active cooling systems) you should not assign these values and instead
should just leave Summer-Ventilation in WUFI set to automatic.
-
EM April 11, 2026

    Args:
        _ventilation_system_ach: The air-change-rate (ACH) of the primary ventilation system (ERV/HRV)
            in SUMMER. This is usually the same as winter. If NONE is set, this will default to match 
            the winter ventilation air-change-rate.

        _ventilation_system_summer_bypass_model: Input either -
"1-None"
"2-Auto TemperatureDifference"
"3-Auto Humidity Difference"
"4-Always" (Default)

        _daytime_extract_system_ach: [Optional, default=0.0] extra air-change-rate (ACH) provided by a
            dedicated supplemental extract-air ventilation system in the building segment during summer. 

        _daytime_extract_system_fan_power_wh_m3: [Optional, default=0.0] If a supplamental extract ventilation
            system is used, provide the fan-power (Wh/m3)

        _daytime_window_ach: [Optional, default=0.0] extra air-change-rate (ACH) provided by the windows 
            in the building segment during summer. 

        _nighttime_extract_system_ach: [Optional, default=0.0] extra air-change-rate (ACH) provided by a
            dedicated supplemental extract-air ventilation system in the building segment during summer. 

        _nighttime_extract_system_fan_power_wh_m3: [Optional, default=0.0] If a supplamental extract ventilation
            system is used, provide the fan-power (Wh/m3)

        _nighttime_extract_system_heat_fraction: [Optional, default=0.0] Fraction released as heat into the building.

        _nighttime_extract_system_control: Input either - 
"1-Temperature Controlled" (Default)
"2-Humidity Controlled"

        _nighttime_window_ach: [Optional, default=0.0] extra air-change-rate (ACH) provided by the windows 
            in the building segment during summer. 

        _nighttime_minimum_indoor_temp_C: [Optional, default=22.0 C] Minimum allowable temperature inside the building segment.
            
    Returns:
        summer_ventilation_: ....
"""
import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh


try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


#-------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Summer Ventilation"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import summer_ventilation as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

#-------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
# -- Create the new Summer-Ventilation
summer_ventilation_ = gh_compo_io.GHCompo_CreateSummerVentilation(
    IGH,
    _ventilation_system_ach,
    _ventilation_system_summer_bypass_model,
    _daytime_extract_system_ach,
    _daytime_extract_system_fan_power_wh_m3,
    _daytime_window_ach,
    _nighttime_extract_system_ach,
    _nighttime_extract_system_fan_power_wh_m3, 
    _nighttime_extract_system_heat_fraction,
    _nighttime_extract_system_control,
    _nighttime_window_ach,
    _nighttime_minimum_indoor_temp_C,
).run()

# -------------------------------------------------------------------------------
preview.object_preview(summer_ventilation_)