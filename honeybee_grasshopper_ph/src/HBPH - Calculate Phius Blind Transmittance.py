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
Calculate an effective solar reduction factor for Phius WUFI-Passive Models. This 
calcualtor will output a solar transmittance and solar reflectance value which can 
be used in a Honeybee Energy "HB Shade Material" to create interior or exterior blinds.
The calculataion here follows the protocol described in the Phius Guidebook v3.1, Appenix N-8
-
If the shading reduction factor for a blind in the closed position is “_material_transmittance”, 
and “transmittance_efective_” is in the input in WUFI Passive then:

For exterior blinds use:
    Z eﬀective = 0.3 + 0.7 * z
    Example: If blinds allow 46% solar access (solar transmittance, Ts) when closed, 
    use that for "_material_transmittance", and "transmittance_efective_" turns out to be 62%.
    Z eﬀective = 0.3 + (0.7*0.46) = 0.622

For interior blinds use:
    Z eﬀective = 1- (1-z) * (1-0.6)
    Example: If blinds allow 46% solar access (solar transmittance, Ts) when closed, 
    use that for "_material_transmittance", and "transmittance_efective_" turns out to be 78%.
    Z eﬀective = 1 – (1-0.46) * (1-0.6) = 0.784

-
EM March 23, 2023
    Args:
        _material_transmittance: (float) A value from 0.0 to 1.0
        
        _inside: (bool) Default=True. Set to False if the blinds are mounted ouside.
        
    Returns:
        transmittance_effective_: The solar transmittance value. Input this result value 
            into the "_transmittance_" input on an "HB Shade Material" component.
        
        reflectance_effective_: The solar reflectance value. Input this result value 
            into the "_reflectance_" input on an "HB Shade Material" component.
"""
   
try:
    from honeybee_ph_utils import preview
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_utils:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_compo_io, gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


# -------------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Calculate Phius Blind Transmittance"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_rhino.gh_compo_io import win_calc_phius_blind as gh_compo_io
    reload(gh_compo_io)


# -------------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CalcPhiusShadeTransmittance(
        _material_transmittance,
        _inside,
    )
transmittance_effective_, reflectance_effective_ = gh_compo_interface.run()
