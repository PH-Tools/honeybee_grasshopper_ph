# Adding More Grasshopper Stubs

If you need type support for additional Grasshopper types, follow this guide.

## Step 1: Find the API Documentation

Visit: https://developer.rhino3d.com/api/grasshopper/

Search for the class you need (e.g., `GH_Structure`, `GH_Component`, etc.)

## Step 2: Determine the Namespace

From the API docs, note the namespace. For example:

- `Grasshopper.DataTree<T>` → `Grasshopper/__init__.pyi`
- `Grasshopper.Kernel.Data.GH_Path` → `Grasshopper/Kernel/Data/__init__.pyi`
- `Grasshopper.Kernel.IGH_DataAccess` → `Grasshopper/Kernel/__init__.pyi`

## Step 3: Create the Stub File

Match the namespace structure:

```
stubs/
└── Grasshopper/
    ├── __init__.pyi              ← For Grasshopper.ClassName
    └── Kernel/
        ├── __init__.pyi          ← For Grasshopper.Kernel.ClassName
        └── Data/
            └── __init__.pyi      ← For Grasshopper.Kernel.Data.ClassName
```

## Step 4: Write the Stub

### Template for a Simple Class

```python
# -*- coding: utf-8 -*-
# Type stubs for Grasshopper.Kernel.Data.GH_Structure
# Based on: [URL to API docs]

from typing import TypeVar, Generic, List, overload

T = TypeVar('T')

class GH_Structure(Generic[T]):
    """Class description from API docs."""

    # Constructors
    def __init__(self) -> None:
        """Constructor description."""
        ...

    # Properties
    @property
    def PropertyName(self) -> int:
        """Property description."""
        ...

    @PropertyName.setter
    def PropertyName(self, value: int) -> None:
        ...

    # Methods
    def MethodName(self, param: str) -> bool:
        """Method description."""
        ...

    @overload
    def OverloadedMethod(self, x: int) -> None:
        """First overload."""
        ...

    @overload
    def OverloadedMethod(self, x: str) -> None:
        """Second overload."""
        ...
```

### Template for a Generic Class

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class GenericClass(Generic[T]):
    def __init__(self) -> None: ...

    def Add(self, item: T) -> None: ...

    def Get(self, index: int) -> T: ...
```

## Step 5: Common Type Mappings

Map C#/.NET types to Python types:

| C# / .NET Type     | Python Stub Type  |
| ------------------ | ----------------- |
| `void`             | `None`            |
| `string`           | `str`             |
| `int`, `Int32`     | `int`             |
| `double`, `Double` | `float`           |
| `bool`, `Boolean`  | `bool`            |
| `List<T>`          | `List[T]`         |
| `IEnumerable<T>`   | `Iterable[T]`     |
| `Dictionary<K,V>`  | `Dict[K, V]`      |
| `object`           | `object` or `Any` |
| `T[]` (array)      | `List[T]`         |
| `out T`            | Return as `Tuple` |

## Step 6: Handle Overloaded Methods

If a C# method has multiple signatures:

```python
from typing import overload

class MyClass:
    @overload
    def Method(self, x: int) -> None: ...

    @overload
    def Method(self, x: str, y: bool) -> None: ...
```

## Step 7: Handle Optional Parameters

```python
def Method(self, required: str, optional: int = ...) -> None:
    """The '= ...' indicates optional parameter."""
    ...
```

## Example: Adding IGH_DataAccess

Let's say you want to add `IGH_DataAccess` for better component input/output handling:

```python
# File: stubs/Grasshopper/Kernel/__init__.pyi
# -*- coding: utf-8 -*-

from typing import Any, List, TypeVar

T = TypeVar('T')

class IGH_DataAccess:
    """Interface for accessing component parameters."""

    def GetData(self, index: int, data: T) -> bool:
        """Gets data from input parameter."""
        ...

    def GetDataList(self, index: int, data: List[T]) -> bool:
        """Gets list of data from input parameter."""
        ...

    def SetData(self, index: int, data: Any) -> None:
        """Sets data to output parameter."""
        ...

    def SetDataList(self, index: int, data: List[Any]) -> None:
        """Sets list to output parameter."""
        ...
```

## Common Grasshopper Types You Might Need

### High Priority

- `IGH_DataAccess` - Component I/O
- `GH_Structure<T>` - Advanced tree structure
- `IGH_Goo` - Grasshopper data wrapper
- `GH_Component` - Base component class

### Medium Priority

- `GH_Document` - Document access
- `GH_ComponentAttributes` - UI attributes
- `IGH_Param` - Parameter interface

### Lower Priority

- Various component types
- UI elements
- Advanced geometry types

## Testing Your Stubs

1. **Create a test file**:

```python
from Grasshopper.Kernel import IGH_DataAccess

def test():
    # type: (IGH_DataAccess) -> None
    # Try using your new stubs
    pass
```

2. **Check for errors**:

   - Red squiggles indicate syntax errors
   - Hover to see if autocomplete works
   - Use "Go to Definition" (F12)

3. **Restart Language Server**:
   - Cmd+Shift+P → "Python: Restart Language Server"

## Troubleshooting

### Stub not recognized

- Check the file is in the correct namespace folder
- Ensure `__init__.pyi` exists in all parent folders
- Restart VS Code language server

### Import errors in stub file

- Use `from typing import ...` for type hints
- Don't import actual Grasshopper modules in stubs
- Use string literals for forward references: `'ClassName'`

### Wrong autocomplete

- Check the method signature matches the API
- Verify generic types are properly declared
- Look for typos in class/method names

## Resources

- **Grasshopper API**: https://developer.rhino3d.com/api/grasshopper/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html
- **PEP 484**: https://www.python.org/dev/peps/pep-0484/
- **Stub Files (PEP 484)**: https://www.python.org/dev/peps/pep-0484/#stub-files

## Contributing

If you create useful stubs:

1. Test them thoroughly
2. Add documentation
3. Consider sharing with the community
4. Keep them updated with API changes
