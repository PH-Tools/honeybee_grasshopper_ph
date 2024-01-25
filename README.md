# honeybee-grasshopper-ph:

Honeybee-PH plugins and components for Rhino / Grasshopper.

![Screenshot 2024-01-25 at 6 50 49 PM](https://github.com/PH-Tools/honeybee_grasshopper_ph/assets/69652712/47b0556a-bcb8-4266-8fe3-99548bbccf36)

This repository contains all PH (Passive House) modeling Grasshopper components for the Honeybee-PH plugin. Once installed, these new Grasshopper components will allow you to add detailed 'Passive House' style data to your Honeybee models, and to export the Honeybee models to both the Passive House Planning Package (PHPP) and WUFI-Passive. The package includes both the userobjects (`.ghuser`) and the Python source (`.py`). Note that this library only possesses the Grasshopper components. In order to use the plugin the core Honeybee, Honeybee-PH and PHX libraries must also be installed in a way that they can be found by Rhino (see dependencies and install instructions below).

More information, examples, and tutorials can be found on the [Honeybee-PH](https://ph-tools.github.io/honeybee_grasshopper_ph/) page.

# How To Install honeybee-grasshoper-ph:
See the [Honeybee-PH Installation](https://ph-tools.github.io/honeybee_grasshopper_ph/install/) page for more information on how to add this package to your system.

Check out the [detailed installation walkthrough on YouTube](https://youtu.be/DvH_Wxf1D8A)

## Dependencies

The honeybee-grasshopper-ph plugin has the following package dependencies:

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
* [PH_units](https://github.com/PH-Tools/PH_units)

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
