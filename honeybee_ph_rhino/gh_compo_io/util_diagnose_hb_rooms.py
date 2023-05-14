# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Diagnose HB Rooms."""

try:
    from typing import Any, Tuple
except ImportError:
    pass  # IronPython 2.7

try:  # import the core honeybee dependencies
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.typing import clean_and_id_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:  # import the ladybug_rhino dependencies
    from ladybug_rhino.config import tolerance, angle_tolerance
    from ladybug_rhino.grasshopper import document_counter
    from ladybug_rhino.fromgeometry import from_linesegment3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from System import Object  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_DiagnoseBadHBRoomGeometry(object):
    def __init__(self, _IGH, _faces, _radius, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[Face], float, Any, Any) -> None
        self.IGH = _IGH
        self.faces = _faces
        self.radius = _radius

    def run(self):
        # type: () -> Tuple[DataTree[Object], DataTree[Object], DataTree[Object]
        error_rooms_ = DataTree[Object]()
        error_rooms_non_manifold_edges_ = DataTree[Object]()
        error_rooms_naked_edges_ = DataTree[Object]()

        for i, faces in enumerate(self.faces.Branches):
            # duplicate the input objects to avoid editing them
            dup_faces = [face.duplicate() for face in faces]

            # generate a default name
            display_name = "Room_{}".format(document_counter("room_count"))
            name = clean_and_id_string(display_name)

            # create the Room
            room = Room(name, dup_faces, tolerance, angle_tolerance)

            # check that the Room geometry is closed.
            if room.check_solid(tolerance, angle_tolerance, False) != "":
                self.IGH.warning(
                    "Input _faces do not form a closed volume.\n"
                    "Room volume must be closed to access most honeybee features.\n"
                    "Preview the output Room to see the holes in your model."
                )
                error_rooms_.AddRange(dup_faces, GH_Path(i))
                error_rooms_non_manifold_edges_.AddRange(
                    [
                        self.IGH.ghc.Pipe(from_linesegment3d(l), self.radius, 0)
                        for l in room.geometry.non_manifold_edges
                    ],
                    GH_Path(i),
                )
                error_rooms_naked_edges_.AddRange(
                    [
                        self.IGH.ghc.Pipe(from_linesegment3d(l), self.radius, 0)
                        for l in room.geometry.naked_edges
                    ],
                    GH_Path(i),
                )

        return error_rooms_, error_rooms_non_manifold_edges_, error_rooms_naked_edges_
