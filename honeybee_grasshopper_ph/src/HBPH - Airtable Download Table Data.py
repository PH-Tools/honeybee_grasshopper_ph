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
Use this to download data from an AirTable database and Table. Note that you will need to 
have a Personal Access Token setup with the right scope (permissions) for the database and 
table that you are trying to get the data from. To setup tokens, you can go to your AirTable 
account and navigate to the "Developers" section https://airtable.com/create/tokens
-
This component will return a lists of generic Python 'record' objects which will have only 
the standard AirTable "id", "createdTime", and "fields" attributes. All of the actual record data will be 
stored in the "fields" dictionary and will use the AirTable column names as keys.
- 
Note that since AirTable limits the data download to 100 records per request, this component will 
make multiple requests until all the data of the table has been downloaded. 
-
EM June 19, 2023
    Args:
        _access_token: (str) The AirTable Personal Access Token 
            needed for accessing the base/table data.
            
        _base_id_number: (str) The AirTable 'base' ID number for 
            the database you are trying to access. This number can be found
            in the url. For instance in an example AirTable URL like this
https://airtable.com/app2huKgwyKrnMRbp/tblaqehqmP6xfOPUP/viwpz3Fm16Fq8X38i?blocks=hide
--------------------^^^^^^^^^^^^^^^^^
            the "base-id" is the first part with the "app" prefix

        _table_id_number: (str) The AirTable Table ID number for 
            the database you are trying to access. This number can be found
            in the url. For instance in an example AirTable URL like this
https://airtable.com/app2huKgwyKrnMRbp/tblaqehqmP6xfOPUP/viwpz3Fm16Fq8X38i?blocks=hide
--------------------------------------------^^^^^^^^^^^^^^^^^
            the "table-id" is the second part with the "tbl" prefix
            
        _download: (bool) Set True to download the data from the 
            specified database and table.
            
    Returns:
        
        records_: (List) All the records downloaded from the specified database and 
            table returned as generic Python objects with the id and fields.
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
ghenv.Component.Name = "HBPH - Airtable Download Table Data"
DEV = honeybee_ph_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_rhino.gh_compo_io import airtable_download_data as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AirTableDownloadTableData(
    IGH,
    _access_token,
    _base_id_number, 
    _table_id_number,
    _download,
    )
records_ = gh_compo_interface.run()