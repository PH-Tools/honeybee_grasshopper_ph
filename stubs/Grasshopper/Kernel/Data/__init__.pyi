# -*- coding: utf-8 -*-
# Type stubs for Grasshopper.Kernel.Data
# Based on: https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_Kernel_Data_GH_Path.htm

from typing import List, Optional, Tuple, overload

class GH_Path:
    """
    Describes the path in structure space of a data item or a list of items.
    A path consists of a series of integers, each one of which represents an index in a branch structure.
    """

    # Constructors
    @overload
    def __init__(self) -> None:
        """Default constructor, creates a path with zero elements."""
        ...

    @overload
    def __init__(self, other: "GH_Path") -> None:
        """Creates an exact copy of another path."""
        ...

    @overload
    def __init__(self, index: int) -> None:
        """Creates a new path with a single element."""
        ...

    @overload
    def __init__(self, indices: List[int]) -> None:
        """Creates a new path from a series of elements."""
        ...
    # Properties
    @property
    def Indices(self) -> List[int]:
        """Gets or sets the entire index space; the path that identifies an element in structure space.
        You should not change the index space when the path is used inside a structure since it will
        invalidate the sort order. If you don't know what you're doing, for Pete's sake don't touch this."""
        ...

    @Indices.setter
    def Indices(self, value: List[int]) -> None: ...
    @property
    def Length(self) -> int:
        """Returns the number of dimensions in the path."""
        ...

    @property
    def Valid(self) -> bool:
        """Gets whether this path is valid. Invalid paths either have no elements or negative elements."""
        ...
    # Methods
    def AppendElement(self, index: int) -> "GH_Path":
        """Create a new path by appending a new index value to this path."""
        ...

    def Compare(self, x: "GH_Path", y: "GH_Path") -> int:
        """Compare two paths. This function determines the Sorting behaviour of paths."""
        ...

    def CompareTo(self, other: "GH_Path") -> int:
        """Compare this path to another path. This function determines the Sorting behaviour of paths."""
        ...

    def CullElement(self) -> "GH_Path":
        """Removes the last index value from the path. If the path is already empty, nothing will happen."""
        ...

    def CullFirstElement(self) -> "GH_Path":
        """Removes the first index value from the path. If the path is already empty, nothing will happen."""
        ...

    def Format(self, format_provider: str, separator: str) -> str:
        """Format a path."""
        ...

    @staticmethod
    def FromString(s: str) -> bool:
        """Try to deserialize a GH_Path from a String."""
        ...

    def GetHashCode(self) -> int:
        """Specialized Hash code pattern."""
        ...

    @overload
    def Increment(self, index: int) -> "GH_Path":
        """Increment a specific index in this path by one."""
        ...

    @overload
    def Increment(self, index: int, offset: int) -> "GH_Path":
        """Increment a specific index in this path by a specific offset."""
        ...

    def IsAncestor(self, potential_ancestor: "GH_Path", additional_generations: int) -> Tuple[bool, int]:
        """Test another path to see if it is an ancestor of this path.
        For a path to be considered an ancestor, it must share the initial dimensions."""
        ...

    @overload
    def IsCoincident(self, other: "GH_Path") -> bool:
        """Test to see if this path is coincident with another path."""
        ...

    @overload
    def IsCoincident(self, indices: List[int]) -> bool:
        """Test to see if this path is coincident with set of integers."""
        ...

    def PrependElement(self, index: int) -> "GH_Path":
        """Create a new path by prepending a new index value to this path."""
        ...

    @staticmethod
    def SplitPathLikeString(s: str) -> Tuple[bool, List[str], str]:
        """Try to split up a path-like formatted string "{A;B;C}(i)" into component parts."""
        ...

    @overload
    def ToString(self) -> str:
        """Concatenates the indices in the path."""
        ...

    @overload
    def ToString(self, includeBrackets: bool) -> str:
        """Concatenates the indices in the path."""
        ...
    # Operators
    def __eq__(self, other: object) -> bool:
        """Equality operator."""
        ...

    def __ne__(self, other: object) -> bool:
        """Inequality operator."""
        ...

    def __lt__(self, other: "GH_Path") -> bool:
        """Less than operator."""
        ...

    def __gt__(self, other: "GH_Path") -> bool:
        """Greater than operator."""
        ...
