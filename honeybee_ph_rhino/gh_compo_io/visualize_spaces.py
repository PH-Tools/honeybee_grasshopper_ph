# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Visualize Spaces."""

from uuid import uuid4

try:
    from typing import Any, List, Optional, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from Rhino.Geometry import Brep  # type: ignore
    from System import Object  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.fromgeometry import from_face3d, from_face3d_to_wireframe, from_face3ds_to_colored_mesh
    from ladybug_rhino.fromobjects import legend_objects
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee.colorobj import ColorFace
    from honeybee.face import Face, Face3D
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.space import Space
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))


class TempFace(Face):
    """A temporary subclass of Honeybee.face.Face so that we can add custom attributes

    This is required since the base Face class using __slots__
    """

    def __init__(self, geometry):
        super(TempFace, self).__init__(str(uuid4()), geometry)


class GHCompo_VisualizeSpaces(object):
    """Transform HBPH Spaces into Rhino geometry which can be visualized."""

    def __init__(self, _IGH, _spaces, _attribute, *args, **kwargs):
        # type: (gh_io.IGH, List[Space], Optional[str], Any, Any) -> None
        self.IGH = _IGH
        self.spaces = _spaces
        self.attribute = _attribute

    def get_floor_segment_faces_as_datatree(self):
        # type: () -> DataTree[List[Face3D]]
        """Return a DataTree of the space floor-segment LBT-faces. One Space per branch."""
        space_floor_segments_ = DataTree[Object]()
        for i, space in enumerate(self.spaces):
            for j, floor_segment_surface in enumerate(space.floor_segment_surfaces):
                space_floor_segments_.AddRange(floor_segment_surface, GH_Path(i, j))
        return space_floor_segments_

    def get_space_volume_faces_as_datatree(self):
        # type: () -> DataTree[List[Face3D]]
        """Return a DataTree of the space volume LBT-faces. One Space per branch."""
        space_volume_faces_ = DataTree[Object]()
        for i, space in enumerate(self.spaces):
            for j, volume in enumerate(space.volumes):
                space_volume_faces_.AddRange(volume.geometry, GH_Path(i, j))
        return space_volume_faces_

    def convert_to_rhino_surfaces(self, _data_tree):
        # type: (DataTree[List[Face3D]]) -> DataTree[List[Brep]]
        """Return a DataTree of the space LBT-faces as Rhino surfaces. One Space per branch."""
        output_tree_ = DataTree[Object]()
        for i, branch in enumerate(_data_tree.Branches):
            for lbt_face in branch:
                output_tree_.Add(from_face3d(lbt_face), GH_Path(i))
        return output_tree_

    def get_floor_segment_surfaces_as_HB_Faces(self):
        # type: () -> List[TempFace]
        """Return a flat list of all the floor-segments as 'TempFace' objects."""
        hb_faces_ = []
        for space in self.spaces:
            for floor_segment in space.floor_segments:
                if not floor_segment.geometry:
                    continue

                # -- Create the new Face, and store the attributes from the space/floor-segment
                # -- so that they can be accessed later by the visualization component.
                hb_face = TempFace(floor_segment.geometry)
                setattr(hb_face, "display_name", space.full_name)
                setattr(hb_face, "weighting_factor", floor_segment.weighting_factor)
                setattr(hb_face, "weighted_floor_area", floor_segment.weighted_floor_area)
                setattr(hb_face, "floor_area", floor_segment.floor_area)
                hb_faces_.append(hb_face)
        return hb_faces_

    def run(self):
        # type: () -> Tuple[DataTree[List], DataTree[List], Optional[List], Optional[List], Optional[Tuple]]
        # -------------------------------------------------------------------------------
        space_floor_segments_faces_ = DataTree[Object]()
        space_volume_faces_ = DataTree[Object]()

        if not self.spaces:
            return (space_floor_segments_faces_, space_volume_faces_, None, None, None)

        # -------------------------------------------------------------------------------
        # -- If there is NO attribute input, just return the LBT-Faces as Rhino-surfaces
        if not self.attribute:
            # -- Get the LBT-Face geometry as organized DataTrees
            space_floor_segments_faces_ = self.get_floor_segment_faces_as_datatree()
            space_volume_faces_ = self.get_space_volume_faces_as_datatree()

            return (
                self.convert_to_rhino_surfaces(space_floor_segments_faces_),
                self.convert_to_rhino_surfaces(space_volume_faces_),
                None,
                None,
                None,
            )

        # -------------------------------------------------------------------------------
        # -- If there is an attribute input, return Rhino-Meshes colored by the attribute value
        # -- Create the ColorFace visualization object
        floor_segment_faces = self.get_floor_segment_surfaces_as_HB_Faces()
        color_obj = ColorFace(floor_segment_faces, self.attribute)
        graphic = color_obj.graphic_container
        values = color_obj.attributes_original
        flat_geo = color_obj.flat_geometry

        # -------------------------------------------------------------------------------
        # -- Output the visualization geometry
        mesh = [from_face3ds_to_colored_mesh([fc], col) for fc, col in zip(flat_geo, graphic.value_colors)]
        wire_frame = []
        for face in color_obj.flat_faces:
            wire_frame.extend(from_face3d_to_wireframe(face.geometry))
        legend = legend_objects(graphic.legend)

        return (mesh, space_volume_faces_, wire_frame, legend, values)
