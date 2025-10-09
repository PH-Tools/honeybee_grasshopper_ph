# Grasshopper Type Stubs

This directory contains custom type stub files (`.pyi`) for Grasshopper and IronPython/CLR types that are missing or incomplete in the `Grasshopper-stubs` package.

## What's Included

### `Grasshopper/__init__.pyi`

- **DataTree[T]**: Complete type definitions for Grasshopper's DataTree class
  - All constructors, properties, and methods
  - Generic type support for proper type checking
  - Based on the official API: https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_DataTree_1.htm

### `Grasshopper/Kernel/Data/__init__.pyi`

- **GH_Path**: Enhanced type definitions for path objects used with DataTrees
  - All constructors, properties, methods, and operators
  - Based on the official API: https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_Kernel_Data_GH_Path.htm

### `System/__init__.pyi`

- **Object**: Base .NET CLR Object type for IronPython

## How to Use

These stubs are automatically recognized by VS Code's Pylance language server through the workspace settings:

```json
{
  "python.analysis.stubPath": "./stubs"
}
```

## Benefits

With these stubs, you get:

1. **Full IntelliSense/autocomplete** for DataTree and GH_Path methods
2. **Type checking** that catches errors before runtime
3. **Better documentation** with inline docstrings from the official API
4. **Generic type support** for DataTree (e.g., `DataTree[str]`, `DataTree[Aperture]`)

## Example Usage

```python
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object

# VS Code now knows all the methods and properties
output_ = DataTree[Object]()  # Generic type support
path = GH_Path(0)  # Constructor autocomplete
output_.Add(item, path)  # Method autocomplete with type hints
```

## Maintenance

These stubs are based on the Grasshopper API for Rhino 8. If the API changes, update these files accordingly.

## Related Packages

- `Grasshopper-stubs`: Provides partial stubs (installed in your venv)
- `Rhino-stubs`: Provides Rhino/RhinoCommon type stubs

This custom stub directory supplements these packages with missing definitions.
