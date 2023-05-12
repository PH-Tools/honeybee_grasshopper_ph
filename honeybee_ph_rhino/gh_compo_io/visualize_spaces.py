# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Visualize Spaces."""

try:
    from typing import Tuple, List, Any
except ImportError:
    pass  # IronPython 2.7

try:
    from System import Object  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except:
    pass  # Outside Rhino

try:
    from ladybug_rhino.fromgeometry import from_face3d
except:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_ph.space import Space
except:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_VisualizeSpaces(object):
    """Transform HBPH Spaces into Rhino geometry which can be visualized."""

    def __init__(self, _IGH, _spaces, *args, **kwargs):
        # type: (gh_io.IGH, List[Space], Any, Any) -> None
        self.IGH = _IGH
        self.spaces = _spaces

    def run(self):
        # type: () -> Tuple[DataTree[List], DataTree[List]]
        space_floor_segments_ = DataTree[Object]()
        space_volumes_ = DataTree[Object]()

        if not self.spaces:
            return (space_floor_segments_, space_volumes_)

        # -- Get the Floor Segment geometry as Rhino surfaces
        for i, space in enumerate(self.spaces):
            for k, segment_group in enumerate(space.floor_segment_surfaces):
                space_floor_segments_.AddRange(
                    [from_face3d(face) for face in segment_group], GH_Path(i, k)
                )

            for j, volume in enumerate(space.volumes):
                space_volumes_.Add(
                    self.IGH.ghc.BrepJoin(
                        [from_face3d(face) for face in volume.geometry]
                    ).breps,
                    GH_Path(i, j),
                )

        return (space_floor_segments_, space_volumes_)
