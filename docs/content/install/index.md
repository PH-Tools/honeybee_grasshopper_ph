---
title: "Install"
weight: 10
---
Honeybee-PH and the Grasshopper toolkit are free and open-source. Feel free download  and give it a try.

## Requirements
In order to successfully install Honeybee-PH, please make sure that your system already has all of the required software installed and working:
- [Rhino-3D v7+](https://www.rhino3d.com/)
- [Ladybug-Tools v1.5+](https://www.ladybug.tools/)
- [WUFI-Passive](https://wufi.de/en/software/wufi-passive/) (If you want to open your files in WUFI-Passive)
- [PHPP v9+](https://passivehouse.com/04_phpp/04_phpp.htm) (If you want to open your files in PHPP)
- Windows OS. &#128551; While almost all the Rhino/Grasshopper tools work fine on MacOS, we are still having trouble [getting Rhino to talk to Microsoft Excel on MacOS](https://discourse.mcneel.com/t/python-subprocess-permissions-error-on-mac-os-1743/142830). Sorry. For now, you will need Windows in order to use the PHPP exporter, and WUFI-Passive only runs on Windows.

{{< raw_html >}}
  <p class="important">
    <strong>Please Note:</strong> The installation file for Honeybee-PH does <strong>NOT</strong> include either <a target="_blank" href="https://wufi.de/en/software/wufi-passive/">WUFI-Passive</a> or <a target="_blank" href="https://passivehouse.com/04_phpp/04_phpp.htm">PHPP</a>. Those programs must be purchased separately in order to use them. Honeybee-PH is an interface for those tools, not a replacement for them.
  </p>
{{< /raw_html >}}

## Rhino / Grasshopper Installation
In order to successfully install the <strong>honeybee-ph</strong> toolkit, follow the steps outlined below:

- Step 1: Download the Installation File: {{< installer_button >}}
- Step 2: Open the Installation File using Rhino / Grasshopper and follow the instructions. (*Note: if you run into permissions trouble during install, try opening Rhino 'as administrator'.)*
- Step 3: Restart Rhino and Grasshopper to ensure that all the new components are properly added to your installation.

## Install Trouble?
If you run into any errors or trouble during install:
- Do you have Rhino and Grasshopper v7? Right now, this is the only version of Rhino we support.
- Are you sure you already have Ladybug-Tools and Honeybee installed? You can use the Honeybee "HB Check Versions" component to check that your Python, Radiance, and OS installs are working properly?
![HB Check Versions](/img/install/hb_config.png)
- Are you using vanilla Ladybug-Tools, or are you using [Pollination](https://www.pollination.cloud/)? If you are using Pollination on Windows, it is possible that your Ladybug-Tools are installed in a different directory than normal. This means you may need additional permissions before you can install Honeybee-PH. If you run into any permissions issues, try running Rhino 'Run as administrator' from your Start Menu and then running the Installation.
![Run as Admin](/img/install/run_admin.png)
- Still having trouble? Check out the [Contact](/contact/) page for additional resources.