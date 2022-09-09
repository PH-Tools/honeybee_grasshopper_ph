# honeybee-grasshopper-ph

* src: The source folder includes python files with all the code used by the Grasshopper components. This is included here for reference purposes only.
* ghuser: The actual Grasshopper component files. These can be added to your Rhino / Grasshopper installation in order to expose the new Honeybee-PH functionality.

# Python Version:

All Classes should be written to comply with Python 2.7 (IronPython) format <u>only</u>. Because these classes are used within the McNeel Rhinoceros/Grasshopper platform, all classes must be backwards compatible to Python 2.7 / IronPython.

Note: It is recommended to include type hints for documentation purposes on all classes and functions. For details on type hints in Python 2.7, See: [MYPY Type hints in Python 2](https://mypy.readthedocs.io/en/stable/cheat_sheet.html)

<i>Note: Grasshopper IronPython does NOT include the 'typing' module for some reason - ensure that no modules 'import typing' or it will raise an error when Grasshopper attempts to import. Nest all 'import typing' inside a try...except.</i>