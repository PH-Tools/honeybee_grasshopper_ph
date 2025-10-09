# -*- coding: utf-8 -*-
# Type stubs for System (IronPython/CLR)

from typing import Any

# System.Object in CLR/.NET is the base class for all objects,
# equivalent to Python's 'object'. We alias it to 'object' so that
# any type is assignable to Object (making it work like 'Any' in practice).
# This allows DataTree[Object] to accept any type.
Object = object

# For backwards compatibility and CLR method signatures,
# we can also define the class with its methods:
class _ObjectMethods:
    """
    Represents the base class for all .NET objects.
    This is the CLR System.Object type used in IronPython.

    Note: In type annotations, System.Object is aliased to Python's 'object'
    so it accepts any type (covariant behavior).
    """

    def GetType(self) -> type:
        """Gets the Type of the current instance."""
        ...

    def ToString(self) -> str:
        """Returns a string that represents the current object."""
        ...

    def Equals(self, obj: object) -> bool:
        """Determines whether the specified object is equal to the current object."""
        ...

    def GetHashCode(self) -> int:
        """Serves as the default hash function."""
        ...
