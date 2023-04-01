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
Create a new custom "Collection" of items. This collection works just like
a normal python 'Dictionary' and allows for item set and get using the typical
square bracket notation (ie: collection["my_key"] = my_value, etc.)

If provided, the collection will use the "_key_name" as the dictionary "key",
for all items and if left blank will use the items 'id()' as the key
-
EM April 1, 2023
    Args:
        _name: (str) An optional display_name for the collection.
        
        _key_name: (str): Default='id(item)'. Provide the name of the item's 
            'key' atribute you would like to use when storing the item
            to a dictionary. Be sure all items have this attribute.
            
        _items: (Collection) An iterable collection of items you would 
            like to add to the new CustomCollection object.
            
    Returns:
        collection_: The new CustomCollection object with the items stored
            according to their 'key' (or 'id' by default).
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_compo_io, gh_io

# ------------------------------------------------------------------------------
import honeybee_ph_rhino._component_info_
reload(honeybee_ph_rhino._component_info_)
ghenv.Component.Name = "HBPH - Create Custom Collection"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import util_create_collection as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateCustomCollection(
    IGH,
    _name,
    _key_name,
    _items,
    )
collection_ = gh_compo_interface.run()