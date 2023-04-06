# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Create Building Shading."""

try:
    from typing import List, Tuple, Optional, Collection
except ImportError:
    pass # IronPython 2.7

try:
    import Rhino.Geometry as rg # type: ignore
except ImportError:
    pass

try:
    from honeybee import room, aperture
except ImportError as e:
    raise ImportError('\nFailed to import honeybee:\n\t{}'.format(e))

try:
    from ladybug_rhino.fromgeometry import from_face3d
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from ladybug_geometry.geometry3d import Face3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from honeybee_ph.properties.aperture import AperturePhProperties
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph:\n\t{}'.format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

def create_punched_geometry(_hb_rooms):
    # type: (Collection[room.Room]) -> List[rg.Brep]
    """Return a list of all of the 'punched' surfaces from the HB-Model."""

    envelope_surfaces_punched = []
    for hb_room in _hb_rooms:
        for face in hb_room.faces:
            rh_geom = from_face3d(face.punched_geometry)  # type: Optional[rg.Brep]

            if rh_geom:
                rh_geom.SetUserString('display_name', face.display_name)
                envelope_surfaces_punched.append(rh_geom)

    return envelope_surfaces_punched


def create_inset_aperture_surface(_aperture):
    # type: (aperture.Aperture) -> Optional[rg.Brep]
    """Return Rhino.Geometry.Brep of an aperture's face, inset."""
    ap_prop_ph = _aperture.properties.ph # type: AperturePhProperties
    inset_face = from_face3d(
        _aperture.geometry.move(
            _aperture.geometry.normal.reverse() * ap_prop_ph.install_depth
        )
    )  # type: Optional[rg.Brep]

    if inset_face:
        inset_face.SetUserString('display_name', _aperture.display_name)

    return inset_face


def create_inset_aperture_surfaces(_hb_rooms):
    # type: (Collection[room.Room]) -> List[rg.Brep]
    """Return a list of aperture Rhino.Geometry.Brep surfaces, inset."""

    inset_window_surfaces = []
    for room in _hb_rooms:
        for face in room.faces:
            for aperture in face.apertures:
                inset_window_surfaces.append(create_inset_aperture_surface(aperture))
    return inset_window_surfaces


def create_window_reveal(_hb_aperture):
    # type: (aperture.Aperture) -> List[rg.Brep]
    """Return a list of the Aperture 'reveal' surfaces."""
    ap_prop_ph = _hb_aperture.properties.ph # type: AperturePhProperties
    extrusion_vector = _hb_aperture.normal.reverse(
    ) * ap_prop_ph.install_depth
    return [
        from_face3d(Face3D.from_extrusion(seg, extrusion_vector))
        for seg in _hb_aperture.geometry.boundary_segments
        if extrusion_vector.magnitude != 0 
    ]


def create_window_reveals(_hb_rooms):
    # type: (Collection[room.Room]) -> List[rg.Brep]
    """Return a list of all the aperture 'reveals' in the Honeybee-Model"""

    reveals = []
    for room in _hb_rooms:
        for face in room.faces:
            for aperture in face.apertures:
                reveals.extend(create_window_reveal(aperture))
    return reveals


class GHCompo_CreateBuildingShading(object):
    def __init__(self, _IGH, _hb_rooms):
        # type: (gh_io.IGH, List[room.Room]) -> None
        self.IGH = _IGH
        self.hb_rooms = _hb_rooms

    def run(self):
        # type: () -> Tuple[List[rg.Brep], List[rg.Brep], List[room.Room]]

        shading_surfaces_ = []
        shading_surfaces_.extend(create_punched_geometry(self.hb_rooms))
        shading_surfaces_.extend(create_window_reveals(self.hb_rooms))

        window_surfaces_ = create_inset_aperture_surfaces(self.hb_rooms)
        hb_rooms_ = self.hb_rooms

        return (window_surfaces_, shading_surfaces_, hb_rooms_)