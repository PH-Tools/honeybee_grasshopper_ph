---
title: "Install"
weight: 10
---
Honeybee-PH and its Grasshopper toolkit are free and open-source. Feel free download  and give it a try.

## YouTube Walk Through
Watch a detailed step-by-step walk through showing both the LadybugTools installation and the Honeybee-PH installation here:
[Installation Walk Through](https://youtu.be/DvH_Wxf1D8A)


## Requirements
In order to successfully install Honeybee-PH, please make sure that your system already has all of the required software installed and working:
- [Rhino-3D v7+](https://www.rhino3d.com/)
- [Ladybug-Tools v1.7+](https://www.ladybug.tools/)
- [WUFI-Passive](https://wufi.de/en/software/wufi-passive/)
- [PHPP v9 or v10](https://passivehouse.com/04_phpp/04_phpp.htm)
- Windows v10+ or MacOS v13+

{{< raw_html >}}
  <p class="important">
    <strong>Please Note:</strong> The installation file for Honeybee-PH does <strong>NOT</strong> include either <a target="_blank" href="https://wufi.de/en/software/wufi-passive/">WUFI-Passive</a> or <a target="_blank" href="https://passivehouse.com/04_phpp/04_phpp.htm">PHPP</a>. Those programs must be purchased separately in order to use them. Honeybee-PH is an interface for those tools, not a replacement for them.
  </p>
{{< /raw_html >}}

## Rhino / Grasshopper Installation
In order to successfully install the **Honeybee-PH** toolkit, follow the steps outlined below:

- Step 1: Ensure you have Rhino v7 or better installed.
- Step 2: **WINDOWS USERS** Use the [**One-Click Installer for Grasshopper**](https://app.pollination.cloud/cad-plugins) in order to install Ladybug Tools onto your system.
- Step 3: **MACOS USERS** Use the [**Food4Rhino Installer**](https://www.food4rhino.com/en/app/ladybug-tools) in order to install Ladybug Tools onto your system.
- Step 4: In Grasshopper, use the Ladybug Tools "LB Versioner" component to update your installation to the latest version.
![LB Versioner](/honeybee_grasshopper_ph/img/install/lb_versioner.png)
- Step 5: Download the HBPH Installation File: {{< installer_button >}}
- Step 6: Open the HBPH Installation File using Rhino / Grasshopper and follow the instructions shown. (*Note: If you are on Windows and you run into permissions trouble during the install, try opening Rhino 'as administrator'.)*
- Step 7: Restart Rhino and Grasshopper to ensure that all the new components are properly added to your installation. Done!

## Install Trouble?
If you run into any errors or trouble during install, check:
- Do you have Rhino **v7** or **v8**? HBPH is not compatible with earlier versions of Rhino.

- If you are on Windows, are you using the Ladybug Tools Pollination [**One-Click Installer for Grasshopper**](https://app.pollination.cloud/cad-plugins)? This is the recommended method now for all Windows users. It's free, and much easier than the older Food4Rhino installer.

- Are you sure you already have Ladybug-Tools and Honeybee installed? You can use the Honeybee "HB Check Versions" component to check that your Python, Radiance, and OS installs are working properly?
![HB Check Versions](/honeybee_grasshopper_ph/img/install/hb_config.png)

- Do you have a compatible version of Ladybug Tools installed? Honeybee-PH requires Ladybug Tools v1.7 or better to work properly. If you have an older version of Ladybug Tools installed, you should use the Ladybug Tools "LB Versioner" component to update your installation to the latest version before trying to use Honeybee-PH.

- Are you using vanilla Ladybug-Tools, or are you using [Pollination](https://www.pollination.cloud/)? If you are using Pollination on Windows, it is possible that your Ladybug-Tools are installed in a different directory than normal. This means you may need additional permissions before you can install Honeybee-PH. If you run into any permissions issues, try running Rhino 'Run as administrator' from your Start Menu and then running the Installation.
![Run as Admin](/honeybee_grasshopper_ph/img/install/run_admin.png)

- Still having trouble? Check out the [Contact](/{{< gh_pages_name >}}/contact/) page for additional resources.