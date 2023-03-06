#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2022, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
# Honeybee-PH is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published 
# by the Free Software Foundation; either version 3 of the License, 
# or (at your option) any later version. 
# 
# Honeybee-PH is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details.
# 
# For a copy of the GNU General Public License
# see <https://github.com/PH-Tools/honeybee_ph/blob/main/LICENSE>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
This component installs/updates all of the 'Honeybee-PH' plugin libraries for Ladybug Tools.
Please make sure that you have Ladybug-Tools with Honeybee-Energy ALREADY fully installed BEFORE
proceeding with this installation. Make sure you are connected to the internet in 
order to download the latest version of the plugin libraries and components.
-
This tool will download and install several new libraries into the Ladybug-Tools
python interpreter, and will download and install new Grasshopper components which
will be added to your Rhino / Grasshopper installation.
-
EM March 6, 2023
    Args:
        _install: (bool) Set to True to install Honeybee-PH on your computer.
        
        _require_admin: (bool) Set FALSE if you KNOW that you need to install HBPH without
            admin. Default=TRUE. In almost all cases, leave this set to TRUE unless you
            are absolutely certain and know what you are doing.
        
        _hbph_branch: (str) Default='main' Optional GitHub repo branch name for
            the honeybee-ph package to install (https://github.com/PH-Tools/honeybee_ph).
            If None is specified, will install the 'main' branch of the repo. If you don't 
            know what branch or package you want, leave this input empty and the 
            default will be installed.
        
        _hbph_gh_branch: (str) Default='main' Optional GitHub repo branch name for
            the honeybee-grasshopper-ph package to install (https://github.com/PH-Tools/honeybee_grasshopper_ph).
            If None is specified, will install the 'main' branch of the repo. If you don't 
            know what branch or package you want, leave this input empty and the 
            default will be installed.
        
        _phx_branch: (str) Default='main' Optional GitHub repo branch name for
            the PHX (Passive House Exchange) package to install (https://github.com/PH-Tools/PHX).
            If None is specified, will install the 'main' branch of the repo. If you don't 
            know what branch or package you want, leave this input empty and the 
            default will be installed.
            
        _hbph_ver: (str): The Version number of the Honeybee-PH package to install from PyPi.
            Note that if you leave this input empty, the latest version will be installed. For 
            more details on honeybee-ph version, see https://pypi.org/project/honeybee-ph/
       
        _phx_ver: (str): The Version number of the PHX package to install from PyPi.
            Note that if you leave this input empty, the latest version will be installed. For 
            more details on honeybee-ph version, see https://pypi.org/project/PHX/
"""

COMPONENT = ghenv.Component # type: ignore
COMPONENT.Name = 'HBPH Installer'
COMPONENT.NickName = 'HBPHInstall'
COMPONENT.Message = 'MAR_06_2023'
COMPONENT.Category = 'Honeybee-PH'
COMPONENT.SubCategory = '00 | Utils'
COMPONENT.AdditionalHelpFromDocStrings = '0'

# -- Required Versions
MIN_VER_RHINO = (7, 18)
MIN_VER_HB_CORE = (1, 54, 34)

import os
import sys

try:
    from typing import Optional, Tuple
except ImportError:
    pass # IronPython 2.7

try:
    from exceptions import IOError # type: ignore
except ImportError:
    pass # IronPython 2.7

try:
    import Rhino # type: ignore
except ImportError:
    pass # Outside Rhino/Grasshopper

try:
    from Grasshopper.Folders import UserObjectFolders # type: ignore
except ImportError:
    pass # Outside Rhino/Grasshopper

try:
    from ladybug_rhino.versioning import change
    from ladybug_rhino import grasshopper as lbt_gh
except ImportError as e:
    msg =   'Failed to import ladybug_rhino:'\
            'Please make sure Ladybug and Honeybee are installed properly before proceeding.\t{}'.format(e)
    raise ImportError(msg)

try:
    from ladybug import futil
except ImportError as e:
    msg =   'Failed to import ladybug.futil:'\
            'Please make sure Ladybug and Honeybee are installed properly before proceeding.\t{}'.format(e)
    raise ImportError(msg)

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    msg =   'Failed to import honeybee.config.folders:'\
            'Please make sure Ladybug and Honeybee are installed properly before proceeding.\t{}'.format(e)
    raise ImportError(msg)


def check_rhino_version_compatibility(_min_version_allowed):
    # type: (Tuple[int, int]) -> bool
    """Return True if the current Rhino version meets the minimum compatibility requirements.
    
    Arguments:
    ----------
        * _min_version_allowed (Tuple[int, int]): The Minimum Rhino version compatible
            with Honeybee-PH. 
    
    Returns:
    --------
        * (bool)
    """
    
    # -- Only check against Major / Minor version
    minimum_major_version = _min_version_allowed[0]
    minimum_minor_version = _min_version_allowed[1]
    
    if Rhino.RhinoApp.Version.Major >= minimum_major_version:
        if Rhino.RhinoApp.Version.Minor >= minimum_minor_version:
            print ("Rhino version: {}.{} found.".format(Rhino.RhinoApp.Version.Major, Rhino.RhinoApp.Version.Minor))
            return True
    
    msg = "Error: Honeybee-PH requires Rhino version: "\
        "{}.{} or better. Please update Rhino before proceeding.".format(
            minimum_major_version,
            minimum_minor_version
        )
    print(msg)
    raise Exception(msg)

def check_hb_core_version_compatibility(_min_version_allowed):
    # type: (Tuple[int, int, int]) -> bool
    """Return True if the installed Honeybee-Core version meets the minimum compatibility requirements.
    
    Arguments:
    ----------
        * _min_version_allowed (Tuple[int, int]): The Minimum Honeybee-Core version compatible
            with Honeybee-PH. 
    
    Returns:
    --------
        * (bool)
    """

    hb_core_version_installed =  hb_folders.honeybee_core_version
    if not hb_core_version_installed: # -> (1, 50, 0)
        msg = (
            "Error: Please make sure that you have Ladybug Tools and Honeybee installed "
            "before proceeding with the installation. "
            "Cannot determine the Honeybee-Core version installed? "
            " - honeybee.config.folders.honeybee_core_version={} ".format(hb_folders.honeybee_core_version)
            )
        raise Exception(msg)


    print("Honeybee-Core version: {}.{}.{} found.".format(*hb_core_version_installed))
    print("- "*25)
    
    for inst_ver, min_ver in zip(hb_core_version_installed, _min_version_allowed):
        if inst_ver > min_ver:
            break
        elif inst_ver < min_ver:
            msg = "Error: Honeybee-PH is not "\
                "compatible with the version of Honeybee installed on this computer [v{}]. Honeybee-PH requires "\
                "at least Honeybee-Core v{} in order to work properly. Please "\
                "update your Ladybug Tools/Honeybee installation to a compatible version before proceeding "\
                "with the Honeybee-PH installation. You can use the Ladybug 'LB Versioner' component to update "\
                "your Honeybee installation, and then restart Rhino before trying to install Honeybee-PH again.".format(hb_core_version_installed, _min_version_allowed)
            raise Exception(msg)
    return True

def pip_install(_package_name, _package_version, _lbt_python_exe_path, _lbt_python_package_path, _package_install_folder_name=None):
    # type: (str, Optional[str], str, str, Optional[str]) -> None
    """PIP install a specified package from PyPi to the Ladybug Tools Python.
    
    Arguments:
    ----------
        * _package_name (str): The name of the package to install from PyPi
        * _package_version: (Optional[str]) The version of the package to install.
            If None, the most recent version is installed.
        * _lbt_python_exe_path (str): The path to the Ladybug Tools python installation.
        * _lbt_python_package_path (str): The path to the Ladybug Tools python site-packages directory.
        * _package_install_folder_name (Optional[str]): An optional folder name for 
            the package once it is installed. This is used to verify installation went
            correctly. Note that in many cases the install folder name will be 
            different than the package name (ie: "honeybee-ph" --> "honeybee_ph"). If None
            is supplied, will try and automatically create the folder name by replacing all
            hyphens with underscores.
    
    Returns:
    --------
        * None
    """
    if not _package_install_folder_name:
        _package_install_folder_name = _package_name.replace("-", "_")

    print('- '*25)
    print('Installing Python package: {}.'.format(_package_name))
    stderr = change.update_libraries_pip(_lbt_python_exe_path, _package_name, _package_version)
    package_install_folder = os.path.join(_lbt_python_package_path, "{}-{}.dist-info".format(_package_install_folder_name, _package_version))
    
    if os.path.isdir(package_install_folder):
        print('Package {} v{} successfully installed to: {} '.format(_package_name, _package_version, _lbt_python_package_path))
    else:
        print('Package {} v{} failed to install to: '.format(_package_name, _package_version, _lbt_python_package_path))
        lbt_gh.give_warning(COMPONENT, stderr)
        print(stderr)

def copy_repo_contents_to_site_packages(_source_directory, _target_directory, _branch):
    # type: (str, str, str) -> None
    """Copy a directory's contents to the Ladybug Tools site-packages directory.
    
    Arguments:
    ----------
        * _source_directory (str): The full path to the directory to copy the contents of.
        * _target_directory (str): The full path to the directory to copy to.
    
    Returns:
    --------
        * None
    """
    
    directories_to_exclude = {'.github', 'tests', 'docs', 'diagrams',} 
    for _dir in os.listdir(_source_directory):
        src_dir = os.path.join(_source_directory, _dir)
        
        if _dir in directories_to_exclude: # don't copy any of these to site-packages
            continue
        
        if not os.path.isdir(src_dir): # If the target folder doesn't exist already
            continue
        
        print('Copying "{}" to:: {}'.format(_dir, _target_directory))
        futil.copy_file_tree(src_dir, os.path.join(_target_directory, _dir))

def get_files_from_github_repo(_github_repo_name, _target_directory, _branch='main'):
    # type: (str, str, str) -> None
    """Download, unzip and copy files from a GitHub repo into a target directory.
    
    Arguments:
    ----------
        * _github_repo_name (str): The name of the GitHub repo to download.
        * _target_directory (str): The full path of the directory to put the
            downloaded files in.
        * _branch (str): default='main' The target branch name to download.
    
    Returns:
    --------
        * None
    """

    # -------------------------------------------------------------------------
    # -- Setup all the file and directory paths
    github_url = "https://github.com/PH-Tools/{}/archive/refs/heads/{}.zip".format(_github_repo_name, _branch)
    directory_to_download_to = hb_folders.python_package_path
    name_of_zipfile_to_download = '{}.zip'.format(_github_repo_name)
    downloaded_zip_file_path = os.path.join(directory_to_download_to, name_of_zipfile_to_download)
    temp_unzip_directory = os.path.join(directory_to_download_to, "{}-{}".format(_github_repo_name, _branch))
    
    # -------------------------------------------------------------------------
    #-- Try and download the Github Repo as a .zip file, then unzip the file
    try:
        print("- "*25)
        print("Downloading:: {}to:: {}".format(github_url, downloaded_zip_file_path))
        futil.download_file_by_name(github_url, directory_to_download_to, name_of_zipfile_to_download, mkdir=True)
        
        print("Unzipping:: {}to:: {}/".format(downloaded_zip_file_path, temp_unzip_directory))
        futil.unzip_file(downloaded_zip_file_path, directory_to_download_to, mkdir=True)
    except IOError as e:
        msg = (
            "There was an error downloading the {} package to your computer."
            "If you have Ladybug Tools installed in you 'ProgramFiles' directory, (ie: if you "
            "are using Pollination instead of the Food4Rhino LBT installer) you may "
            "need to run Rhino 'as administrator' in order to "
            "install to this directory?".format(_github_repo_name)
            )
        raise IOError(msg)
    except Exception as e:
        msg = "There was a error downloading {} to {} and unzipping the file "\
            "to {}.{}".format(github_url, downloaded_zip_file_path, temp_unzip_directory, e)
        raise Exception(msg)


    # -------------------------------------------------------------------------
    # -- Copy the unzipped files/folders over to the Ladybug site-packages folder
    copy_repo_contents_to_site_packages(temp_unzip_directory, _target_directory, _branch)
    
    
    # -------------------------------------------------------------------------
    # -- Cleanup: Remove the downloaded folder and zip file
    print("Removing directory: {}".format(temp_unzip_directory))
    futil.nukedir(temp_unzip_directory, True)

    print("Removing downloaded file: {}".format(downloaded_zip_file_path))
    os.remove(downloaded_zip_file_path)

def copy_grasshopper_components_to_UserObjects(_repo_name, _download_directory, _target_directory):
    # type: (str, str, str) -> None
    """Copy all of the GH-User objects from the source dir over the Grasshopper UserObjects directory. 

    This is used when downloading from the "honeybee_grasshopper_ph" github repo, since the .ghuser objects 
    are nested down in the unzipped directory. This function should get called after download and unzip from 
    the "honeybee_grasshopper_ph" github repo.
    
    Arguments:
    ---------- 
        * _repo_name (str): The name of the honeybee_grasshopper_ph repo.
        * _download_directory (str): The path to the download directory.
        * _target_directory (str): The Grasshopper UserObjects directory to copy to .ghuser files to.
    
    Returns:
    --------
        * None
    """
    
    repo_download_directory = os.path.join(_download_directory, _repo_name)
    hbph_gh_source_folder = os.path.join(repo_download_directory, 'user_objects')
    
    if not os.path.isdir(hbph_gh_source_folder):
        msg = (
            "Cannot find the Grasshopper Component directory: {}? Please be sure"
            "you downloaded and unzipped the '{}' GitHub repo before trying to copy to"
            "the Grasshopper UserObjects directory".format(hbph_gh_source_folder, _repo_name)
        )
        print(msg)
        return
    
    target = os.path.join(_target_directory[0], 'honeybee_grasshopper_ph')
    
    print('- '*25)
    print('Copying Honeybee-PH Grasshopper Components from::{} to::{}'.format(hbph_gh_source_folder, target))
    
    futil.copy_file_tree(hbph_gh_source_folder, target, overwrite=True)
    
    print("Removing directory: {}".format(repo_download_directory))
    futil.nukedir(repo_download_directory, True)

def install_from_GitHub(_hbph_branch, _phx_branch, _hbph_gh_branch, _rich_version, 
                        _xlwings_version, _lbt_python_exe_path, _lbt_python_package_path):
    # type: (Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], str, str) -> None
    """Download all the files directly from the GitHub repositories into the Ladybug Python site-packages.
    
    Arguments:
    ----------
        * _hbph_branch (Optional[str]): The name of the 'honeybee_ph' Github branch to 
            install. If None, 'main' will be used.
        * _phx_branch (Optional[str]): The name of the 'phx' Github branch to 
            install. If None, 'main' will be used.
        * _hbph_gh_branch (Optional[str]): The name of the 'honeybee_grasshopper_ph' Github branch to 
            install. If None, 'main' will be used.
        * _rich_version (Optional[str]): The version of Rich to install from PyPi. If None
            is supplied, will install the most recent version.
        * _xlwings_version (Optional[str]): The version of XLWings to install from PyPi. If None
            is supplied, will install the most recent version.
        * _lbt_python_exe_path (str): The path to the Ladybug Tools python.exe
        * _lbt_python_package_path (str): The path to the Ladybug Tools python site-packages directory.
    
    Returns:
    --------
        * None
    """

    # -- In this case, also Pip install the XLWings and Rich dependencies
    # -------------------------------------------------------------------------
    pip_install('rich', _rich_version, _lbt_python_exe_path, _lbt_python_package_path)
    pip_install('xlwings', _xlwings_version, _lbt_python_exe_path, _lbt_python_package_path)

    # -- Get the required Honeybee-PH repo's from GitHub
    # -------------------------------------------------------------------------
    get_files_from_github_repo('honeybee_ph', hb_folders.python_package_path, _hbph_branch or 'main')
    get_files_from_github_repo('PHX', hb_folders.python_package_path, _phx_branch or 'main')
    get_files_from_github_repo('honeybee_grasshopper_ph', hb_folders.python_package_path, _hbph_gh_branch or 'main')
    copy_grasshopper_components_to_UserObjects('honeybee_grasshopper_ph', hb_folders.python_package_path, UserObjectFolders)

    # -------------------------------------------------------------------------
    # -- Give a success message
    success_msg = 'Honeybee-PH has been successfully installed'
    restart_msg = 'RESTART RHINO to load the new components + library.'
    for msg in (success_msg, restart_msg):
        print(msg)
    lbt_gh.give_popup_message(''.join([success_msg, restart_msg]), 'Installation Successful!')
    return

def install_from_PyPi(_hbph_version, _phx_version, _hbph_gh_branch, _lbt_python_exe_path, _lbt_python_package_path):
    # type: (Optional[str], Optional[str], Optional[str], str, str) -> None
    """Install Honeybee-PH and PHX Packages from PIP, download Grasshopper components from Github.
    
    Arguments:
    ----------
        * _hbph_version (Optional[str]): The Honeybee-PH version to install from PyPi. If
            None is supplied, will install the most recent.
        * _phx_version (Optional[str]): The PHX version to install from PyPi. If
            None is supplied, will install the most recent.
        * _hbph_gh_branch (Optional[str]): The name of the 'honeybee_grasshopper_ph' Github branch to 
            install. If None is supplied, 'main' will be used.
        * _lbt_python_exe_path (str): The path to the Ladybug Tools python.exe
        * _lbt_python_package_path (str): The path to the Ladybug Tools python site-packages directory.
    
    Returns:
    --------
        * None
    """

    # -------------------------------------------------------------------------
    # Install the Honeybee-PH and PHX packages from PyPi
    pip_install('honeybee-ph', _hbph_version, _lbt_python_exe_path, _lbt_python_package_path)
    pip_install('phx', _phx_version, _lbt_python_exe_path, _lbt_python_package_path)
    
    # -------------------------------------------------------------------------
    # -- Install the Rhino / Grasshopper Components and Libraries from GitHub
    get_files_from_github_repo('honeybee_grasshopper_ph', hb_folders.python_package_path, _hbph_gh_branch or 'main')
    copy_grasshopper_components_to_UserObjects('honeybee_grasshopper_ph', hb_folders.python_package_path, UserObjectFolders)
    
    # -------------------------------------------------------------------------
    # Give a success message
    success_msg = 'Honeybee-PH and PHX have been successfully installed!'
    restart_msg = 'RESTART RHINO to load the new components + libraries.'
    for msg in (success_msg, restart_msg):
        print(msg)
    lbt_gh.give_popup_message(''.join([success_msg, restart_msg]), 'Installation Successful!')
    return

def require_admin(_component_input):
    # type: (Optional[bool]) -> bool
    """There may be cases where the user wants to install WITHOUT admin."""
    if _component_input is not None:
        return _component_input
    else:
        return True


def install_honeybee_ph(_install, _hbph_branch, _hbph_gh_branch, _phx_branch, _hbph_version, _phx_version, _min_ver_rhino, _min_ver_hb, _require_admin):
    # type: (bool, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str], Tuple[int, int], Tuple[int, int, int, bool]) -> None
    """Install the Honeybee-PH plugin.
    
    Arguments:
    ----------
        * _install (bool): Set True to run the installer. 
        * _hbph_branch (Optional[str]): The name of the GitHub branch to install (ie: 'main').
        * _hbph_gh_branch (Optional[str]): The name of the GitHub branch to install (ie: 'main').
        * _phx_branch (Optional[str]): The name of the GitHub branch to install (ie: 'main').
        * _hbph_version (Optional[str]): The version number of Honeybee-PH to install from PyPi.
        * _phx_version (Optional[str]): The version number of PHX to install from PyPi.
    
    Returns:
    --------
        * None
    """

    # -------------------------------------------------------------------------
    # -- Check version compatibility
    check_rhino_version_compatibility(_min_ver_rhino)
    check_hb_core_version_compatibility(_min_ver_hb)

    # -------------------------------------------------------------------------
    # -- Check to make sure the user has admin rights, otherwise PyPi will silently
    # -- fall back to other python installations on the user' computer, which will mess 
    # -- up all sorts of things. This error should be raised BEFORE any installation 
    # -- to ensure that nothing gets mistakenly installed elsewhere on the user's system.
    if _require_admin:
        if (os.name == 'nt') and (not lbt_gh.is_user_admin()):
            msg = "Warning: You must have 'Admin' privileges on this computer in order "\
                "to properly install Honeybee-PH. Try restarting Rhino using "\
                "'Run as administrator' before proceeding."
            raise Exception(msg)
    else:
        msg = "Note: You have chosen to install WITHOUT admin privledges. This may cause "\
            "HBPH to be installed in an unexpected location on your system? If you don't "\
            "know where you want your HBPH installed, leave '_require_admin' set to TRUE"
        print msg
    
    # -------------------------------------------------------------------------    
    if any((_hbph_branch, _phx_branch, _hbph_gh_branch)):
        # -- If the user supplies any GitHub branch name, use the GitHub versions for all.
        # -- In this case, supply the dependency versions to install as well (since no PIP resolution)
        rich_version = None # None=defaults to newest
        xlwings_version = None # None=defaults to newest
        install_from_GitHub(
                        _hbph_branch,
                        _phx_branch,
                        _hbph_gh_branch,
                        rich_version,
                        xlwings_version, 
                        hb_folders.python_exe_path,
                        hb_folders.python_package_path,
                        )
        return
    else:
        # -- Otherwise, just install everything from PyPi
        install_from_PyPi(  _hbph_version,
                            _phx_version,
                            _hbph_gh_branch, 
                            hb_folders.python_exe_path,
                            hb_folders.python_package_path,
                        )
        return

admin = require_admin(_require_admin)

if _install:
    install_honeybee_ph(_install, _hbph_branch, _hbph_gh_branch, _phx_branch,
                        _hbph_version, _phx_version, MIN_VER_RHINO, MIN_VER_HB_CORE, admin)
else:
    msg = 'Please:'\
    '- Be sure you have already installed Ladybug Tools.'\
    '- Are connected to the internet.'\
    '- Set _install to "True" to install Honeybee-PH and all dependencies on this system.'   
    print(msg)