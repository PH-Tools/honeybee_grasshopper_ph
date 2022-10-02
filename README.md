# honeybee-grasshopper-ph:

Honeybee-PH plugins and components for Rhino / Grasshopper.

<img width="978" alt="image" src="https://user-images.githubusercontent.com/69652712/193476135-cfe77702-21e1-4e5e-905e-98191ce5c3e3.png">

This repository contains all PH (Passive House) modeling Grasshopper components for the Honeybee-PH
plugin. The package includes both the userobjects (`.ghuser`) and the Python
source (`.py`). Note that this library only possesses the Grasshopper components
and. On order to run the plugin the core Honeybee AND Honeybee-PH / PHX libraries must be installed in a way that
they can be found by Rhino (see dependencies and install instructions below).

More information, examples and tutorials can be found on the [Honeybee-PH](https://ph-tools.github.io/honeybee_grasshopper_ph/) page.

# How To Install honeybee-grasshoper-ph:
See the [Honeybee-PH Installation](https://ph-tools.github.io/honeybee_grasshopper_ph/install/) page for more information on how to add this package to your system.

## Dependencies

The honeybee-grasshopper-ph plugin has the following dependencies on core libraries:

* [ladybug-core](https://github.com/ladybug-tools/ladybug)
* [ladybug-geometry](https://github.com/ladybug-tools/ladybug-geometry)
* [ladybug-geometry-polyskel](https://github.com/ladybug-tools/ladybug-geometry-polyskel)
* [ladybug-comfort](https://github.com/ladybug-tools/ladybug-comfort)
* [ladybug-rhino](https://github.com/ladybug-tools/ladybug-rhino)
* [honeybee-core](https://github.com/ladybug-tools/honeybee-core)
* [honeybee-energy](https://github.com/ladybug-tools/honeybee-energy)
* [honeybee-standards](https://github.com/ladybug-tools/honeybee-standards)
* [honeybee-energy-standards](https://github.com/ladybug-tools/honeybee-ph-standards)
* [honeybee-ph](https://github.com/PH-Tools/honeybee_ph)
* [PHX](https://github.com/PH-Tools/PHX)

## Other Required Components

The honeybee-grasshopper-ph plugin also requires the Grasshopper components within the
following repositories to be installed in order to work correctly:

* [ladybug-grasshopper](https://github.com/ladybug-tools/ladybug-grasshopper)
* [honeybee-grasshopper-core](https://github.com/ladybug-tools/honeybee-grasshopper-core)
* [honeybee-grasshopper-energy](https://github.com/ladybug-tools/honeybee-grasshopper-energy)

## Ladybug Installation

See the [Wiki of the lbt-grasshopper repository](https://github.com/ladybug-tools/lbt-grasshopper/wiki)
for the installation instructions for the entire Ladybug Tools Grasshopper plugin.


[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)
