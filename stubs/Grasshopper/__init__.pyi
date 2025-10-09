# -*- coding: utf-8 -*-
# Type stubs for Grasshopper DataTree
# Based on: https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_DataTree_1.htm

from typing import Callable, Generic, Iterable, List, TypeVar, overload

from Grasshopper.Kernel.Data import GH_Path

T = TypeVar("T")

class DataTree(Generic[T]):
    """
    Implements basic Grasshopper Data Tree functionality in an easy-to-use class.
    This class is used primarily in Scripting components.
    """

    # Constructors
    @overload
    def __init__(self) -> None:
        """Default constructor, create an empty data tree."""
        ...

    @overload
    def __init__(self, other: "DataTree[T]") -> None:
        """Create a shallow duplicate of another data tree.
        This means it will create a new tree that contains the same items."""
        ...

    @overload
    def __init__(self, data: Iterable[T], path: GH_Path) -> None:
        """Create a tree with a single branch"""
        ...
    # Properties
    @property
    def BranchCount(self) -> int:
        """Gets the number of branches defined in this tree."""
        ...

    @property
    def Branches(self) -> List[List[T]]:
        """Gets a list of all the data-arrays in this tree"""
        ...

    @property
    def DataCount(self) -> int:
        """Gets the total number of data items (including nulls) stored in all branches."""
        ...

    @property
    def Item(self) -> T:
        """Gets or set the data item at the specified path and index."""
        ...

    @Item.setter
    def Item(self, value: T) -> None: ...
    @property
    def Paths(self) -> List[GH_Path]:
        """Gets a list of all the branch paths in this tree."""
        ...

    @property
    def TopologyDescription(self) -> str:
        """Gets a description of the topology of the tree. Useful for debugging purposes."""
        ...
    # Methods
    @overload
    def Add(self, item: T) -> None:
        """Add (append) a data item to the last branch in the tree.
        If no branches exist yet, a new one will be created with [path = {0}]"""
        ...

    @overload
    def Add(self, item: T, path: GH_Path) -> None:
        """Add (append) a data item to the specified branch in the tree.
        If the branch doesn't exist yet, it will be created."""
        ...

    @overload
    def AddRange(self, items: Iterable[T]) -> None:
        """Add (append) a list of data items to the last branch in the tree.
        If no branch exists yet, a new one will be created."""
        ...

    @overload
    def AddRange(self, items: Iterable[T], path: GH_Path) -> None:
        """Add (append) a list of data items to the specified branch in the tree.
        If the branch doesn't exist yet, it will be created."""
        ...

    def AllData(self) -> List[T]:
        """Collects all data in the tree in a single list. Does not alter the topology of this tree."""
        ...

    @overload
    def Branch(self, path: GH_Path) -> List[T]:
        """Gets the list of data which belongs to a given Branch path."""
        ...

    @overload
    def Branch(self, index: int) -> List[T]:
        """Gets the list of data which belongs to the branch path at the given index."""
        ...

    @overload
    def Branch(self, indices: List[int]) -> List[T]:
        """Gets the list of data which belongs to a given Branch path."""
        ...

    def Clear(self) -> None:
        """Clears the entire tree."""
        ...

    def ClearData(self) -> None:
        """Removes all data from all branches without affecting the tree topology."""
        ...

    @overload
    def EnsurePath(self, path: GH_Path) -> List[T]:
        """Create a new branch with the specified path if it doesn't already exists."""
        ...

    @overload
    def EnsurePath(self, indices: List[int]) -> List[T]:
        """Create a new branch with the specified path if it doesn't already exists."""
        ...

    def Flatten(self) -> None:
        """Flattens the entire tree into a single path."""
        ...

    @overload
    def Graft(self, includeEmptyBranches: bool) -> None:
        """Graft all paths in this tree.
        "Grafting" means appending a new branch for every item in an existing branch."""
        ...

    @overload
    def Graft(self, path: GH_Path, includeEmptyBranches: bool) -> None:
        """Graft a single path in the tree.
        "Grafting" means appending a new branch for every item in an existing branch."""
        ...

    def Insert(self, item: T, path: GH_Path, index: int) -> None:
        """Insert a data item to the specified branch in the tree.
        If the branch doesn't exist yet, it will be created."""
        ...

    def ItemExists(self, path: GH_Path, index: int) -> bool:
        """Test if the specified path + item index are defined inside the tree."""
        ...

    def MergeTree(self, other: "DataTree[T]") -> None:
        """Merges two trees together. Data inside similar branches will be merged into single lists
        and unique paths will be appended. The other tree will not be altered,
        so beware that data is now shared among both trees."""
        ...

    def Path(self, index: int) -> GH_Path:
        """Gets the data path at the specified index."""
        ...

    @overload
    def PathExists(self, path: GH_Path) -> bool:
        """Test if the specified path is already defined inside the tree."""
        ...

    @overload
    def PathExists(self, indices: List[int]) -> bool:
        """Test if the specified path is already defined inside the tree."""
        ...

    @overload
    def RemovePath(self, path: GH_Path) -> None:
        """Removes a path and all associated data from the structure.
        If the path doesn't exist, nothing will happen."""
        ...

    @overload
    def RemovePath(self, indices: List[int]) -> None:
        """Removes a path and all associated data from the structure.
        If the path doesn't exist, nothing will happen."""
        ...

    @overload
    def RenumberPaths(self) -> None:
        """Renumber all paths in this data tree, using a single incrementing path index."""
        ...

    @overload
    def RenumberPaths(self, format: str) -> None:
        """Renumber all paths in this data tree, using a single incrementing path index."""
        ...

    def SimplifyPaths(self) -> None:
        """Simplify the branches in this tree by removing all identical path entries.
        The length of the shortest path will be indicative of the similarity search depth.
        If this tree only contains a single branch, the branch wil be simplified to its last index."""
        ...

    def ToString(self) -> str:
        """Creates a brief description of the tree."""
        ...

    def TrimExcess(self) -> None:
        """Trims the excess allocated memory in all branches"""
        ...
