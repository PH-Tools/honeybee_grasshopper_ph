# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""TextAnnotations class used for writing to PDF."""

try:
    from typing import Optional, Union, Any, List, TypeVar
    T = TypeVar("T")
except ImportError:
    pass  # IronPython 2.7

try:
    from System.Drawing import Color # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Rhino.Geometry import TextJustification, Point3d, Plane, Transform # type: ignore
    from Rhino.DocObjects.DimensionStyle import MaskFrame # type: ignore
    from Grasshopper import DataTree # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError('{}\nFailed to import honeybee_ph_rhino'.format(e))

try:
    from honeybee_ph_utils.input_tools import clean_get, clean_tree_get
except ImportError as e:
    raise ImportError('{}\nFailed to import honeybee_ph_utils'.format(e))

class RHTextJustify(ghio_validators.Validated):
    """Validator for Integer user-input conversion into Rhino.Geometry.TextJustification Enum."""

    def validate(self, name, new_value, old_value):
        if new_value is None:
            return old_value

        if isinstance(new_value, TextJustification):
            return new_value

        # if it's an integer input, convert to a TextJustification
        mapping = {
            0: TextJustification.BottomLeft, 1: TextJustification.BottomCenter,
            2: TextJustification.BottomRight, 3: TextJustification.MiddleLeft,
            4: TextJustification.MiddleCenter, 5: TextJustification.MiddleRight,
            6: TextJustification.TopLeft, 7: TextJustification.TopCenter,
            8: TextJustification.TopRight
        }

        try:
            return mapping[int(new_value)]
        except KeyError as e:
            msg = "Error: Key {} is not a valid Text Justification?".format(new_value)
            raise KeyError("{}\n{}".format(e, msg))


class TextAnnotation(object):
    """Dataclass for Layout-Page Labels."""
    justification = RHTextJustify('justification')

    def __init__(self, _IGH, _text, _size, _location, _format="{}", _justification=3,
                 _mask_draw=False, _mask_color=None, _mask_offset=0.02,
                 _mask_frame=None, _mask_draw_frame=False, _align_to_layout_view=False):
        # type: (gh_io.IGH, str, float, Union[Point3d, Plane], str, int, bool, Optional[Color], float, Optional[MaskFrame], bool, bool) -> None
        self.IGH = _IGH
        self._text = _text
        self.text_size = _size
        self._location = _location
        self.format = _format
        self.justification = _justification
        self.mask_draw = _mask_draw
        self.mask_color = _mask_color or Color.FromArgb(50, 0, 0, 0)
        self.mask_offset = _mask_offset
        self.mask_frame = _mask_frame or MaskFrame.RectFrame
        self.mask_draw_frame = _mask_draw_frame
        self.align_to_layout_view = _align_to_layout_view

    @property
    def anchor_point(self):
        # type: () -> Point3d
        """Return the 3D anchor point for the Text Annotation"""

        if isinstance(self._location, Plane):
            return self._location.Origin
        elif isinstance(self._location, Point3d):
            return self._location
        else:
            raise ValueError("Location input must be a Point3d or Plane? Got: {}".format(type(self._location)))

    @property
    def plane(self):
        # type: () -> Plane
        """Return the 3D Plane for the Text Annotation."""

        if isinstance(self._location, Plane):
            return self._location
        elif isinstance(self._location, Point3d):
            default_normal = self.IGH.Rhino.Geometry.Vector3d(0, 0, 1)  # Assumes Top View
            default_plane = self.IGH.Rhino.Geometry.Plane(
                origin=self._location, normal=default_normal
            )
            return default_plane
        else:
            raise ValueError("Location input must be a Point3d or Plane? Got: {}".format(type(self._location)))

    @property
    def text(self):
        fmt = "{}".format(self.format)
        try:
            return fmt.format(self._text)
        except ValueError:
            try:
                return fmt.format(float(self._text))
            except Exception:
                return self._text

    def transform(self, _transform):
        # type: (Transform) -> TextAnnotation
        """Applies a Rhino-Transform to a TextAnnotation object. Returns a copy of the TextAnnotation.

        Arguments:
        ----------
            * _transform (Transform): The Rhino Transform to apply to the TextAnnotation.

        Returns:
        --------
            * (TextAnnotation): The new TextAnnotation with the transform applied.
        """

        if not _transform:
            return self
        
        new_obj = self.duplicate()
        try:
            new_obj._location = self.IGH.ghc.Transform(new_obj._location, _transform)
        except Exception as e:
            raise Exception(e)

        return new_obj

    def duplicate(self):
        # type: () -> TextAnnotation
        return self.__copy__()

    def __copy__(self):
        # type: () -> TextAnnotation
        return TextAnnotation(
            self.IGH,
            self._text,
            self.text_size,
            self._location,
            self.format,
            self.justification,
            self.mask_draw,
            self.mask_color,
            self.mask_offset,
            self.mask_frame,
            self.mask_draw_frame,
        )

    def _truncate(self, txt):
        # type: (str) -> str
        limit = 20
        if len(txt) > limit:
            return "{}...".format(txt.replace("\n", "")[:limit])
        else:
            return txt

    def __str__(self):
        return '{}(text={}, text_size={}, anchor_point={}, format={}, justification={})'.format(
            self.__class__.__name__, self._truncate(self.text), self.text_size, self.anchor_point, self._truncate(self.format), self.justification)

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_CreateTextAnnotations(object):

    default_size = 0.25
    default_format = "{}"
    default_justification = 4 # 4=Middle-Center

    def __init__(self, _IGH, _text, _size, _location, _format, _justification, *args, **kwargs):
        # type: (gh_io.IGH, DataTree, DataTree, DataTree, DataTree, DataTree, *Any, **Any) -> None
        self.IGH = _IGH
        self.text = _text
        self.size = _size
        self.location = _location
        self.format = _format
        self.justification = _justification
            
    def run(self):
        # type: () -> DataTree[TextAnnotation]
        text_annotations_ = self.IGH.DataTree(TextAnnotation)
        for i, branch in enumerate(self.text.Branches):
            # -- Get the right tree branch
            size_branch = clean_tree_get(self.size, i, _default=[self.default_size])
            loc_branch = clean_tree_get(self.location, i, _default=[Point3d(0,0,0)])
            format_branch = clean_tree_get(self.format, i, _default=[self.default_format])
            justify_branch = clean_tree_get(self.justification, i, _default=[self.default_justification]) 
            
            for k, txt in enumerate(branch):
                # -- Get the right data from the tree branch
                size = clean_get(list(size_branch), k, 0.25) or 0.25
                location = clean_get(list(loc_branch), k)
                format = clean_get(list(format_branch), k) or self.default_format
                justification = clean_get(list(justify_branch), k) or self.default_justification

                # -- Build the TextAnnotation
                new_label = TextAnnotation(self.IGH, txt, size, location, format, justification)
                text_annotations_.Add(new_label, self.IGH.GH_Path(i))

        return text_annotations_