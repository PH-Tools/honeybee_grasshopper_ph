# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Brep Subface Materials."""

try:
    from typing import Dict, List, Tuple, Any
except ImportError:
    pass #IronPython 2.7

try:
    from Grasshopper import DataTree # type: ignore
    from Grasshopper.Kernel.Data import GH_Path # type: ignore
    from System import Object # type: ignore
except:
    pass #  outside Rhino / Grasshopper

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))


class GHCompo_GetSubFaceMaterials(object):

    def __init__(self, _IGH, _brep_guids, *args, **kwargs):
        # type: (gh_io.IGH, List, List, Dict) -> None
        self.IGH = _IGH
        self.brep_guids = _brep_guids

    def get_brep_face_data(self, _brep_guid):
        # type: (Any, Any) -> Tuple[List, List]
        geo_ = []
        names_ = []
        brep = self.IGH.rs.coercebrep(_brep_guid)
        for face in brep.Faces:
            # -- Add the face geometry to the output set
            geo_.append(face)

            # -- Get the BrepFace's Material Name and add to the output
            compo_index = self.IGH.Rhino.Geometry.ComponentIndex(
                    self.IGH.Rhino.Geometry.ComponentIndexType.BrepFace,
                    face.FaceIndex
                )
            brep_obj = self.IGH.Rhino.RhinoDoc.ActiveDoc.Objects.FindId(_brep_guid)
            mat_name = self.IGH.Rhino.DocObjects.RhinoObject.GetMaterial(brep_obj, compo_index).Name
            names_.append(mat_name)

        return geo_, names_

    def run(self):
        subface_geo_ = DataTree[Object]()
        mat_names_ = DataTree[Object]()

        with self.IGH.context_rh_doc():
            for i, brep_guid in enumerate(self.brep_guids):
                faces, mats = self.get_brep_face_data(brep_guid)
                subface_geo_.AddRange(faces, GH_Path(i))
                mat_names_.AddRange(mats, GH_Path(i))
                
        return subface_geo_, mat_names_