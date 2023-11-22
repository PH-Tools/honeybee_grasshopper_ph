# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Names and meta-data for all the Honeybee-PH Grasshopper Components.
These are called when the component is instantiated within the Grasshopper canvas.
"""

RELEASE_VERSION = "Honeybee-PH v1.0.76"
CATEGORY = "HB-PH"
SUB_CATEGORIES = {
    0: "00 | Utils",
    1: "01 | Model",
    2: "02 | Shading",
    3: "03 | Write",
    4: "04 | PDF",
}
COMPONENT_PARAMS = {
    # -- Model
    "HBPH - Merge Rooms": {
        "NickName": "Merge HB Rooms",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Bldg Segment": {
        "NickName": "PH Bldg Segment",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Set Model Project Data": {
        "NickName": "Set Project Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Project Team Member": {
        "NickName": "Team Member",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Phius Certification": {
        "NickName": "Phius Cert.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PHI Certification": {
        "NickName": "PHI Cert.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Climate
    "HBPH - PH Site": {
        "NickName": "PH Site",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PH Location": {
        "NickName": "PH Location",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PH Climate Data": {
        "NickName": "PH Climate Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PH PHPP Climate": {
        "NickName": "PH PHPP Climate",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PH Climate Monthly Temps": {
        "NickName": "PH Monthly Temps",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PH Climate Monthly Radiation": {
        "NickName": "PH Monthly Radiation",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - PH Climate Peak Load": {
        "NickName": "PH Peak Load",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Site From Phius File": {
        "NickName": "Create Site from File",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Spaces
    "HBPH - Create Spaces": {
        "NickName": "PH Spaces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Space PH Ventilation": {
        "NickName": "Create Space PH Vent",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Vent. Schedule": {
        "NickName": "PH Vent. Sched.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Operation Period": {
        "NickName": "PH Op. Period",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Get FloorSegment Data": {
        "NickName": "Get Seg. Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Spaces": {
        "NickName": "Create PH Spaces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add Spaces": {
        "NickName": "Add PH Spaces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Ventilator": {
        "NickName": "PH Ventilator",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Spaces from HB-Rooms": {
        "NickName": "Create Spaces from Rooms",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- DHW
    "HBPH - Create SHW Tank": {
        "NickName": "Create SHW Tank",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create SHW Heater": {
        "NickName": "Create SHW Heater",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create SHW Pipe | Trunks": {
        "NickName": "Create Trunk Pipes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create SHW Pipe | Branches": {
        "NickName": "Create Branch Pipes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create SHW Pipe | Fixtures": {
        "NickName": "Create Fixture/Twig Pipes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create SHW Recirculation Pipes": {
        "NickName": "Create Recirc Pipes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create SHW System": {
        "NickName": "Create SHW Sys",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Apply SHW System": {
        "NickName": "Apply SHW Sys",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- HVAC
    "HBPH - Create Exhaust Ventilator": {
        "NickName": "Create Exhaust Ventilator",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add Exhaust Ventilator": {
        "NickName": "Create Exhaust Ventilator",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add Mech Systems": {
        "NickName": "Add Mech",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Ventilation System": {
        "NickName": "Create Vent",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Supportive Device": {
        "NickName": "Create Supportive Device",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Ventilation Duct": {
        "NickName": "Create Duct",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create PV System": {
        "NickName": "Create PV",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add Renewable Energy Devices": {
        "NickName": "Add Renewables",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add Mech Supportive Devices": {
        "NickName": "Add Supportive Devices",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Space Conditioning System": {
        "NickName": "Create Heating / Cooling",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Cooling Params": {
        "NickName": "Create Cooling Parameters",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    #  -- Elec Equipment
    "HBPH - Create PH Equipment": {
        "NickName": "Create PH Equipment",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add PH Equipment": {
        "NickName": "Add PH Equipment",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Programs
    "HBPH - Set Res Occupancy": {
        "NickName": "Set Res Occupancy",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Phius MF Res Calculator": {
        "NickName": "Phius MF Res Calc",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Phius Program Finder": {
        "NickName": "Phius Programs",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Conversion Factor": {
        "NickName": "Factor",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Windows
    "HBPH - Create PH Window Frame Element": {
        "NickName": "Create Frame Element",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create PH Window Frame": {
        "NickName": "Create Frame",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create PH Glazing": {
        "NickName": "Create Glazing",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create PH Window Construction": {
        "NickName": "Create PH Win Const",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create PH Glazing": {
        "NickName": "Create Glazing",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Set Window Install Depth": {
        "NickName": " Window Install Depth",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Calculate Phius Blind Transmittance": {
        "NickName": "Calc Phius Blind",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Window Types": {
        "NickName": "Create Win Types",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Window Geometry": {
        "NickName": "Create Geom",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Set Monthly Shade Factor": {
        "NickName": "Set Shade Factor",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Envelope
    "HBPH - Create SD Constructions": {
        "NickName": "Create SD Const.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Mixed HB-Material": {
        "NickName": "Create Mixed HB-Material",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Thermal Bridges": {
        "NickName": "Create Thermal Bridges",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Add Thermal Bridges to Rooms": {
        "NickName": "Add Thermal Bridges",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Set Spec Heat Capacity": {
        "NickName": "Set Spec Heat Cap.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Import Flixo Materials": {
        "NickName": "Import Flixo Mats.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Create Detailed Constructions": {
        "NickName": "Create Detailed Constructions",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Calc Air Layer HB Material": {
        "NickName": "Create Air Layer Mat",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Shading
    "HBPH - Create Building Shading": {
        "NickName": "Create Shading",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HBPH - Shading Factor Settings - LBT Rad": {
        "NickName": "Settings",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HBPH - Add Shading Dims": {
        "NickName": "Shading Dims",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HBPH - Add Shading Factors - LBT Rad": {
        "NickName": "Shading Factors",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    # -- Write Model
    "HBPH - Write to PHPP": {
        "NickName": "Write PHPP",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH - Write WUFI XML": {
        "NickName": "Write WUFI XML",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    # -- Export PDF
    "HBPH - Report Envelope Data": {
        "NickName": "Report Envelope",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Report Thermal Bridge Data": {
        "NickName": "Report TB",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Report Space Floor Segments": {
        "NickName": "Report Floor Segments",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Create Text Annotation": {
        "NickName": "Create Text Annotation",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Create PDF Geometry": {
        "NickName": "Create PDF Geometry",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Create Elevation PDF Geometry": {
        "NickName": "Report Elevations",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Export PDFs": {
        "NickName": "Export PDFs",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    # -- Foundations
    "HBPH - Add Foundations": {
        "NickName": "Add Foundations",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Create Foundation": {
        "NickName": "Create Foundation",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    # -- Utility
    "HBPH - Get Brep Subface Materials": {
        "NickName": "Get Subface Mats",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Create Custom Collection": {
        "NickName": "Create Collection",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Get From Custom Collection": {
        "NickName": "Get From Collection",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Sort Geom by Level": {
        "NickName": "Sort Geom by Level",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Sort HB Objects by Level": {
        "NickName": "Sort HB-Objs by Level",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Get Object Attributes": {
        "NickName": "Get Attributes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Set Object Attributes": {
        "NickName": "Set Attributes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Create Objects From CSV": {
        "NickName": "Create Objs from CSV",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH - Diagnose HB Rooms": {
        "NickName": "Diagnose HB Rooms",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    # -- Visualize
    "HBPH - Visualize Spaces": {
        "NickName": "Visualize HBPH Spaces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Visualize Window Frames": {
        "NickName": "Visualize Window Frames",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- Organize
    "HBPH - Organize Spaces": {
        "NickName": "Organize HBPH Spaces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- AirTable
    "HBPH - Airtable Download Table Data": {
        "NickName": "Download Table Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Airtable Create Material Layers": {
        "NickName": "Airtable Material Layers",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Airtable Create Constructions": {
        "NickName": "Airtable Opaque Constructions",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH - Airtable Create Window Constructions": {
        "NickName": "Airtable Window Constructions",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
}


class ComponentNameError(Exception):
    def __init__(self, _name, error):
        self.message = 'Error: Cannot get Component Params for: "{}"'.format(_name)
        print(error)
        super(ComponentNameError, self).__init__(self.message)


def set_component_params(ghenv, dev=False):
    # type (ghenv, Optional[str | bool]) -> bool
    """
    Sets the visible attributes of the Grasshopper Component (Name, Date, etc..)

    Arguments:
    __________
        * ghenv: The Grasshopper Component 'ghenv' variable.
        * dev: (str | bool) Default=False. If False, will use the RELEASE_VERSION value as the
            'message' shown on the bottom of the component in the Grasshopper scene.
            If a string is passed in, will use that for the 'message' shown instead.

    Returns:
    --------
        * None:
    """

    compo_name = ghenv.Component.Name
    try:
        sub_cat_num = COMPONENT_PARAMS.get(compo_name, {}).get("SubCategory", 1)
        sub_cat_name = SUB_CATEGORIES.get(sub_cat_num)
    except Exception as e:
        raise ComponentNameError(compo_name, e)

    # ------ Set the visible message
    if dev:
        msg = "DEV | {}".format(str(dev))
    else:
        msg = COMPONENT_PARAMS.get(compo_name, {}).get("Message")

    ghenv.Component.Message = msg

    # ------ Set the other stuff
    ghenv.Component.NickName = COMPONENT_PARAMS.get(compo_name, {}).get("NickName")
    ghenv.Component.Category = CATEGORY
    ghenv.Component.SubCategory = sub_cat_name
    ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application

    return dev
