# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Clean Input Breps."""

try:
    from typing import Any, Tuple, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import Brep  # type: ignore
except:
    pass  # Outside Rhino

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


class GHCompo_CleanInputBreps(object):
    def __init__(self, _IGH, _breps, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[Brep], *Any, **Any) -> None
        self.IGH = _IGH
        self.breps = _breps

    def get_clean_face(self, face):
        # type: (Any) -> Tuple[Any, Optional[Any]]
        """Get a clean face from a Rhino Brep. If the input face as a U or V count > 2, will convert to a trimmed surface."""
        
        point, weights, greville, u_count, v_count = self.IGH.ghc.SurfacePoints(face)
        if u_count > 2 or v_count > 2:
            msg = (
                "An input Face has u_count={} and "
                "v_count={}. Converting. See 'bad_faces_' "
                "output to visualize these problem faces.".format(u_count, v_count)
            )
            self.IGH.warning(msg)

            bad_face = face
            face = self.IGH.ghc.BoundarySurfaces(
                self.IGH.ghc.JoinCurves(
                    self.IGH.ghc.DeconstructBrep(face).edges, 
                    True
                )
            )
            return face, bad_face
        return face, None

    def get_clean_brep(self, brep):
        # type: (Any) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]
        """Get a clean brep from a Rhino Brep. If the input brep is not closed, will try to join the faces."""

        good_brep_faces = []
        bad_brep_faces = []

        # -- Build up all the Brep Faces. Fix any faces if needed.
        for face in self.IGH.ghc.DeconstructBrep(brep).faces:
            good_face, bad_face = self.get_clean_face(face)
            good_brep_faces.append(good_face)
            if bad_face:
                bad_brep_faces.append(bad_face)
                
        brep_, brep_is_closed = self.IGH.ghc.BrepJoin(good_brep_faces)
        
        if not brep_is_closed:
            msg = (
                "Error: Brep '{}' is not closed."
                "Check the 'bad_breps_' to visualize.".format(brep)
            )
            self.IGH.error(msg)
            return None, brep_, bad_brep_faces

        return brep_, None, bad_brep_faces
        

    def run(self):
        # type: () -> Tuple[DataTree[Optional[Brep]], DataTree[Optional[Brep]], DataTree[Optional[Brep]]]
        good_breps_ = DataTree[Object]() 
        bad_breps_ = DataTree[Object]() 
        bad_faces_ = DataTree[Object]() 

        for i, branch in enumerate(self.breps.Branches):
            for k, brep in enumerate(branch):
                if not brep:
                    continue

                good_brep, bad_brep, bad_faces = self.get_clean_brep(brep)
                good_breps_.Add(good_brep, GH_Path(i, k))
                bad_breps_.Add(bad_brep, GH_Path(i, k))
                bad_faces_.AddRange(bad_faces, GH_Path(i, k))
 
        return good_breps_, bad_breps_, bad_faces_