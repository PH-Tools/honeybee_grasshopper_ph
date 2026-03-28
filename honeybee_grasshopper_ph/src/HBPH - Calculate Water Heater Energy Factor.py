#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2025, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
Convert a Water-Heater 'UEF' value into an equivalent 'EF' value. 
-
The Uniform Energy Factor (UEF) and Energy Factor (EF) are both efficiency ratings for 
water heaters, but UEF is the newer standard that replaced EF to provide more accurate 
and representative efficiency measurements. 
-
This is required for certain types of water-heaters in WUFI-Passive. The calculator 
here follows the conversion factors found in: 
    'RESNET Energy Factor Conversion Equations based on Water Heater Type'
    https://www.resnet.us/wp-content/uploads/RESNET-EF-Calculator-2017.xlsx
-
EM March 6, 2025
    Args:

        _heater_type: (str) Input either - 
1-Elec. Resistance
2-Boiler (gas/oil)
3-Boiler (wood)
4-District Heating
5-Heat Pump (annual COP)
6-Heat Pump (monthly COP)
7-Heat Pump (inside)

        _use_type: (str) Input either - 
1-Consumer (ie: single-family home, etc.)
2-Instant
3-Commercial (ie: apartment building, etc.)

        _UEF: (float) The manufacturer's stated 'UEF' value for the water-heater.
            
    Returns:
        annual_energy_factor_: The 'EF' value calculated from the input 'UEF'
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
ghenv.Component.Name = "HBPH - Calculate Water Heater Energy Factor"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io.hvac import calc_water_heater_EF as gh_compo_io
    reload(gh_compo_io)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CalculateWaterHeaterEnergyFactor(
        IGH,
        _heater_type,
        _use_type,
        _UEF,
    )
annual_energy_factor_ = gh_compo_interface.run()