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
- [Rhino-3D v8](https://www.rhino3d.com/)
- [Ladybug-Tools v1.8](https://www.ladybug.tools/)
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

- Step 1: Ensure you have Rhino v8 installed.
- Step 2: **WINDOWS USERS** Use the [**One-Click Installer for Grasshopper**](https://app.pollination.cloud/cad-plugins) in order to install Ladybug Tools onto your system.
- Step 3: **MACOS USERS** Use the [**Food4Rhino Installer**](https://www.food4rhino.com/en/app/ladybug-tools) in order to install Ladybug Tools onto your system.
- Step 4: In Grasshopper, use the Ladybug Tools "LB Versioner" component to update your installation to the latest version.
![LB Versioner](/honeybee_grasshopper_ph/img/install/lb_versioner.png)
- Step 5: Download the HBPH Installation File: {{< installer_button >}}
- Step 6: Open the HBPH Installation File using Rhino / Grasshopper and follow the instructions shown. (*Note: If you are on Windows and you run into permissions trouble during the install, try opening Rhino 'as administrator'.)*
- Step 7: Restart Rhino and Grasshopper to ensure that all the new components are properly added to your installation. Done!

## Install Trouble?
If you run into any errors or trouble during install, check:
- Do you have **Rhino v8**? Unfortunately HBPH is not compatible with earlier versions of Rhino.

- If you are on Windows, are you using the Ladybug Tools Pollination [**One-Click Installer for Grasshopper**](https://app.pollination.cloud/cad-plugins)? This is the recommended method now for all Windows users. It's free, and much easier than the older Food4Rhino installer.

- Are you sure you already have Ladybug-Tools and Honeybee installed? You can use the Honeybee "HB Check Versions" component to check that your Python, Radiance, and OS installs are working properly?
![HB Check Versions](/honeybee_grasshopper_ph/img/install/hb_config.png)

- Do you have a compatible version of Ladybug Tools installed? Honeybee-PH requires Ladybug Tools v1.8 or better to work properly. If you have an older version of Ladybug Tools installed, you should use the Ladybug Tools "LB Versioner" component to update your installation to the latest version before trying to use Honeybee-PH.

- Are you using vanilla Ladybug-Tools, or are you using [Pollination](https://www.pollination.cloud/)? If you are using Pollination on Windows, it is possible that your Ladybug-Tools are installed in a different directory than normal. This means you may need additional permissions before you can install Honeybee-PH. If you run into any permissions issues, try running Rhino 'Run as administrator' from your Start Menu and then running the Installation.
![Run as Admin](/honeybee_grasshopper_ph/img/install/run_admin.png)


## Error on Windows?
If you are on Windows, in some circumstances you may be getting an error during installation. This may sometimes be due to a weird behavior of the 'python' language that Honeybee and Honeybee-PH is written in. Try the steps below if you are encountering an error during installation:

1. Using **File Exporer** navigate to the `C:\Users\ --you-- \AppData\Roaming\` directory.
2. Look within this directory for a directory named 'Python' in there?
![Bad Python](/honeybee_grasshopper_ph/img/install/bad_python.png)
3. If you have a directory named 'Python, **delete it!** That isn't supposed to be there.
4. Now try running the Grasshopper Installer one more time.

{{< raw_html >}}
  <p class="important">
    <strong>Still having trouble?</strong> Check out the <a target="_blank" href="/{{< gh_pages_name >}}/contact/">Contact</a> page for ways to get in touch with us.
  </p>
{{< /raw_html >}}


## Manual Installation?
In some cases, users will not be able to utilize the automatic installer - for instance if Rhino cannot be run in 'admin' mode for some reason. In this case, it is still possible to manually install **Honeybee-PH** and the required libraries, although this is much more difficult and **not recommended** for most users. In order to manually install **Honeybee-PH**, follow the steps below:

**| Step 1:** Locate *YOUR* **`...\ladybug_tools\...`** folder. For most users, this will be: 

{{< raw_html >}}
  <p class="folder">
    C:\Program Files\ladybug_tools\
  </p>
{{< /raw_html >}}

but for some users it may also be located in: 

{{< raw_html >}}
  <p class="folder">
    C:\Users\--Your-User-Name--\ladybug_tools\
  </p>
{{< /raw_html >}}

**| Step 2:** Run **`Powershell`** from your windows start menu

**| Step 3:** In Powershell, [**`pip-install`**](https://packaging.python.org/en/latest/tutorials/installing-packages/) the required libraries into *YOUR* **`ladybug_tools`** folder (see above). This is done by using one of the following commands from inside Powershell, depending on where *YOUR* ladybug_tools folder is found (see above). Run *EITHER*: 

{{< raw_html >}}
  <p class="powershell">
    C:\"Program Files"\ladybug_tools\python\python -m pip install honeybee-ph PHX
  </p>
{{< /raw_html >}}

*OR*

{{< raw_html >}}
  <p class="powershell">
    C:\Users\--Your-User-Name--\ladybug_tools\python\python -m pip install honeybee-ph PHX
  </p>
{{< /raw_html >}}

**| Step 4:** Installation may take a few moments as it downloads the packages, and may require you to hit `enter` one or more times during the installation to confirm. If it succeeds, you should now see several **new** folders in *YOUR* **ladybug_tools** folder. To check, look in *EITHER*:

{{< raw_html >}}
  <p class="folder">
    C:\"Program Files"\ladybug_tools\python\Lib\site-packages\...
  </p>
{{< /raw_html >}}

*OR*

{{< raw_html >}}
  <p class="folder">
    C:\Users\--Your-User-Name--\ladybug_tools\python\Lib\site-packages\...
  </p>
{{< /raw_html >}}

Look for folders named **honeybee_ph, PHX, and ph_units**. If those folders are present, installation has succeeded!

**| Step 5:** Now that the new libraries are installed, you will need to download the Grasshopper tools, and manually copy/past them into the correct folders. Start by downloading the latest version of the **Honeybee-PH** Grasshopper Components here: 

> [Grasshopper Tools](https://github.com/PH-Tools/honeybee_grasshopper_ph/archive/refs/heads/main.zip)

**| Step 6:** Unzip the downloaded file, and copy the **`...\honeybee_ph_rhino`** folder into your Grasshopper **`...\ladybug_tools\python\lib\site-packages\`** folder.
![Copy GH Library](/honeybee_grasshopper_ph/img/install/copy_GH_libraries.png)

**| Step 7:** Now, copy the **`...\honeybee_grasshopper_ph\user_objects`** folder into your Grasshopper UserObjects folder. The Grasshopper UserObjects folder should be located in:

{{< raw_html >}}
  <p class="folder">
    C:\Users\--Your-User-Name--\AppData\Roaming\Grasshopper\UserObjects\...
  </p>
{{< /raw_html >}}
![Copy GH Components](/honeybee_grasshopper_ph/img/install/copy_GH_components.png)

**| Step 8:** Download the **Grasshopper Component-IO** library as well. Download it here:

> [Grasshopper Component-IO](https://github.com/PH-Tools/PH_GH_Component_IO/archive/refs/heads/main.zip)

**| Step 9:** Last, copy the **`...\ph_gh_component_io`** folder into your **`\ladybug_tools\python\lib\site-packages\`** folder.
![Copy GH-IO Library](/honeybee_grasshopper_ph/img/install/copy_GH_IO_library.png)

This should complete the manual installation of the Honeybee-PH tools. You should now be able to open Rhino and Grasshopper, and proceed to use the **Honeybee-PH** components as normal. 

{{< raw_html >}}
  <p class="important">
    <strong>Still having trouble?</strong> Check out the <a target="_blank" href="/{{< gh_pages_name >}}/contact/">Contact</a> page for ways to get in touch with us.
  </p>
{{< /raw_html >}}