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
EM June 27, 2024
    Args:
        _install: (bool) Set to True to install Honeybee-PH on your computer.
        
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
COMPONENT.Message = 'JUN_27_2024'
COMPONENT.Category = 'Honeybee-PH'
COMPONENT.SubCategory = '00 | Utils'
COMPONENT.AdditionalHelpFromDocStrings = '0'

try:
    COMPONENT.ToggleObsolete(False)
except AttributeError:
    pass # Rhino 7
    
import os
import sys
import json
import subprocess

try:
    import ctypes
except:
    pass # MacOs

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
    #from ladybug_rhino.versioning import change
    from ladybug_rhino import grasshopper as lbt_gh
    from ladybug_rhino.config import folders as lbr_folders
    lbr_loaded = True
except ImportError as e:
    lbr_loaded = False
    msg =   '\nFailed to import ladybug_rhino:\n'\
            'Please make sure Ladybug and Honeybee are installed properly before proceeding.\n\t{}'.format(e)
    raise ImportError(msg)

try:
    from ladybug import futil
except ImportError as e:
    msg =   '\nFailed to import ladybug.futil:\n'\
            'Please make sure Ladybug and Honeybee are installed properly before proceeding.\n\t{}'.format(e)
    raise ImportError(msg)

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    msg =   '\nFailed to import honeybee.config.folders:\n'\
            'Please make sure Ladybug and Honeybee are installed properly before proceeding.\n\t{}'.format(e)
    raise ImportError(msg)



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# -- Required Versions
MIN_VER_RHINO = (8, 9)
MIN_VER_LBT_GH = (1, 8, 30)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# -- System Check


def is_windows_user_admin():
    # type: () -> bool
    """For Windows only, return True if the user opened Rhino 'As Administrator' and False if not."""
    if (os.name != 'nt'): # In case used on MacOs
        return True
    
    try:
        mode = ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        raise Exception(e)
    
    if mode != 0:
        return True
    else:
        return False

def user_system_meets_min_rhino_version(_min_version_allowed):
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
    rh_min_version_allowed = (_min_version_allowed[0], _min_version_allowed[1])
    rh_version_found = (Rhino.RhinoApp.Version.Major, Rhino.RhinoApp.Version.Minor)
    
    # ---------------------------------------------------------------------------
    print ("Rhino version: {}.{}".format(Rhino.RhinoApp.Version.Major, Rhino.RhinoApp.Version.Minor))
    
    if rh_version_found < rh_min_version_allowed:
        return False
    else:
        
        return True

def user_system_meets_min_LBT_version(_min_version_allowed):
    # type: (Tuple[int, int, int]) -> bool
    """Return True if the installed LBT Grasshopper version meets the minimum compatibility requirements.
    
    Arguments:
    ----------
        * _min_version_allowed (Tuple[int, int]): The Minimum Ladybug Grasshopper version compatible
            with Honeybee-PH. 
    
    Returns:
    --------
        * (bool)
    """
    # ---------------------------------------------------------------------------
    lbt_gh = lbr_folders.lbt_grasshopper_version
    if not lbt_gh:
        msg = (
            "Error: Please make sure that you have Ladybug Tools and Honeybee installed "
            "before proceeding with the installation. \n"
            "Cannot determine the Ladybug Tools version installed? \n"
            " - ladybug_rhino.config.lbt_grasshopper_version={} \n".format(lbt_gh)
            )
        print msg
        raise Exception(msg)
    
    # ---------------------------------------------------------------------------
    print("Ladybug-Tools-Grasshopper version: {}.{}.{}".format(*lbt_gh))
    
    # ---------------------------------------------------------------------------
    if lbt_gh < _min_version_allowed:
        return False
    else:
        return True

def check_system_setup():
    # type: () -> None
    """Provide messages related to System compatibility."""
    
    print "Rhino running in 'Admin' mode:", is_windows_user_admin()
    if not is_windows_user_admin():
        msg = " Error: This Honeybee-PH installer will only work if Rhino is started in 'Admin' mode.\n"\
                "To proceed with the installation: \n"\
                "Please close Rhino and re-open it by 'right-clicking' on the Rhino application, and selecting 'Run as Administrator'.\n"\
                "Once you are in 'admin' mode, please re-open this installer and you will be able to continue with the Honeybee-PH Installation."
        raise Exception(msg)
    
    if not user_system_meets_min_rhino_version(MIN_VER_RHINO):
        msg = "Error: Honeybee-PH requires Rhino version: "\
            "{}.{} or better. Please update Rhino before proceeding. "\
            "Got version: {}.{}".format(
                MIN_VER_RHINO[0],
                MIN_VER_RHINO[1],
                Rhino.RhinoApp.Version.Major,
                Rhino.RhinoApp.Version.Minor,
            )
        print(msg)
        raise Exception(msg)
    
    if not user_system_meets_min_LBT_version(MIN_VER_LBT_GH):
        msg = "Error: Honeybee-PH requires Ladybug-Tools version: "\
            "{}.{} or better. Please update Ladybug-Tools before proceeding. "\
            "Got version: {}.{}".format(
                MIN_VER_LBT_GH[0],
                MIN_VER_LBT_GH[1],
                lbr_folders.lbt_grasshopper_version[0],
                lbr_folders.lbt_grasshopper_version[1],
            )
        print(msg)
        raise Exception(msg)
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    print "Ladybug Tools Python .exe:", hb_folders.python_exe_path
    print "Ladybug Tools Python packages:", hb_folders.python_package_path


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# -- PIP Install


def run_pip_command(python_exe, package_name, version=None, target=None, _env=None):
    # type: (str, str, str, str, Optional[Dict]) -> str
    """Update or Install Python libraries using pip within a python subprocess.
    
    Args:
        * python_exe (str): The path to the Python executable to be used for installation.
        
        * package_name (str): The name of the PyPI package to install
        
        * version (str): An optional string for the version of the package to install.
        
        * target (str): An optional target directory into which the package will be installed.
        
        * _env (Optional[Dict]): The OS Environment to be used for the Pip-Install
    Returns:
        * error_msg (str)
    """
    
    # Set the environment for pip install to fix Rhino-8 issues
    if _env == None:
        _env = os.environ
        
    # build up the command using the inputs
    if version is not None:
            package_name = '{}=={}'.format(package_name, version)
    
    cmds = [python_exe, '-m', 'pip', 'install', package_name]
    
    if version is None:
        cmds.append('-U')
    
    if target is not None:
        cmds.extend(['--target', target, '--upgrade'])

    # execute the command and print any errors
    print('Installing "{}" version via pip'.format(package_name))
    
    use_shell = True if os.name == 'nt' else False
    
    # Use the ENV passed in to fix any Rhino-8 issues
    process = subprocess.Popen(
        cmds, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=_env)
    
    output = process.communicate()
    
    stdout, stderr = output
    
    error_msg = 'Package "{}" may not have been updated correctly\n' \
        'or its usage in the plugin may have changed. See pip stderr below:\n' \
        '{}'.format(package_name, stderr)
    
    return error_msg

def update_pip(python_exe, _env=None):
    # type: (str, Optional[Dict]) -> str
    """Update 'Pip' to avoid seeing those error.
    
    Args:
        * python_exe (str): The path to the Python executable to be used for installation.
        
        * _env (Optional[Dict]): The OS Environment to be used for the Pip-Install
    
    Returns:
        error_msg (str)
    """
    
    # Set the environment for pip install to fix Rhino-8 issues
    if _env == None:
        _env = os.environ
        
    # build up the command using the inputs
    cmds = [python_exe, '-m', 'pip', 'install', '--upgrade', 'pip']
    
    # execute the command and print any errors
    print('Updating Pip...')
    
    use_shell = True if os.name == 'nt' else False
    
    # Use the ENV passed in to fix any Rhino-8 issues
    try:
        process = subprocess.Popen(
            cmds, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=_env)
        
        output = process.communicate()
        
        stdout, stderr = output
        
        error_msg = 'Command: {} may have failed for some reason'.format(cmds)
    except Exception as e:
        error_msg = e

    return error_msg

def pip_install(_package_name, _package_version, _lbt_python_exe_path, _lbt_python_package_path, _package_install_folder_name=None, _env=None):
    # type: (str, Optional[str], str, str, Optional[str], Optional[Dict]) -> None
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
            is supplied, will try and automatically create the folder name by just replacing all
            hyphens with underscores.
        
        * _env (Optional[Dict]): The OS Environment to use for the Pip-Install. This should have
            "PYTHONHOME" set to: "" in order to avoid the Rhino Python-3 install issues.
    Returns:
    --------
        * None
    """
    
    # Set the environment for pip install to fix Rhino-8 issues
    if _env == None:
        _env = os.environ
    
    if not _package_install_folder_name:
        _package_install_folder_name = _package_name.replace("-", "_")
    
    print '- '*50 
    print 'Installing Python package: "{}" (v{}) to: {}'.format(_package_name, _package_version, _lbt_python_package_path) 
    print "  _package_name=", _package_name
    print "  _package_version=", _package_version
    print "  _lbt_python_exe_path=", _lbt_python_exe_path
    print "  _lbt_python_package_path=", _lbt_python_package_path
    print "  _package_install_folder_name=", _package_install_folder_name
    print "  _env['PYTHONHOME']=", _env['PYTHONHOME'] 
    package_dist_folder_name = "{}-{}.dist-info".format(_package_install_folder_name, _package_version)
    print "package_dist_folder_name=", package_dist_folder_name
    package_dist_folder_path = os.path.join(_lbt_python_package_path, package_dist_folder_name)
    print "package_dist_folder_path=", package_dist_folder_path
    
    stderr = run_pip_command(_lbt_python_exe_path, _package_name, _package_version, _env=_env)
    
    if os.path.isdir(package_dist_folder_path):
        print("Package '{}' (v-{}) successfully installed to: {}".format(_package_name, _package_version, _lbt_python_package_path))
    else:
        print("Could not find {}".format(package_dist_folder_path))
        print("Package '{}' (v-{}) failed to install to: {}".format(_package_name, _package_version, _lbt_python_package_path))
        lbt_gh.give_warning(COMPONENT, stderr)
        print(stderr)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# -- GitHub


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
        print("Downloading:: {}\nto:: {}".format(github_url, downloaded_zip_file_path))
        futil.download_file_by_name(github_url, directory_to_download_to, name_of_zipfile_to_download, mkdir=True)
        
        print("Unzipping:: {}\nto:: {}/".format(downloaded_zip_file_path, temp_unzip_directory))
        futil.unzip_file(downloaded_zip_file_path, directory_to_download_to, mkdir=True)
    except IOError as e:
        msg = (
            "There was an error downloading the {} package to your computer.\n"
            "If you have Ladybug Tools installed in you 'ProgramFiles' directory, (ie: if you "
            "are using Pollination instead of the Food4Rhino LBT installer) you may \n"
            "need to run Rhino 'as administrator' in order to "
            "install to this directory?\n".format(_github_repo_name)
            )
        raise IOError(msg)
    except Exception as e:
        msg = "There was a error downloading {} to {} and unzipping the file "\
            "to {}.\n{}".format(github_url, downloaded_zip_file_path, temp_unzip_directory, e)
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
    
    target = os.path.join(_target_directory[0], _repo_name)
    
    # -- Clean out any existing files in the target directory.
    if os.path.exists(target):
        for file_name in os.listdir(target):
            file_path = os.path.join(target, file_name)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print("Error deleting file or directory: {}".format(e))

    print('- '*25)
    print('Copying downloaded Grasshopper Components from::\n{} to::\n{}'.format(hbph_gh_source_folder, target))
    
    futil.copy_file_tree(hbph_gh_source_folder, target, overwrite=True)
    
    print("Cleaning up and removing download directory: {}".format(repo_download_directory))
    futil.nukedir(repo_download_directory, True)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# -- Main


def install_honeybee_ph(_hbph_version, _phx_version, _hbph_gh_branch, _lbt_python_exe_path, _lbt_python_package_path, _env=None):
    # type: (Optional[str], Optional[str], Optional[str], str, str, Optional[Dict]) -> None
    """Install Honeybee-PH and PHX Packages from PIP, then download Grasshopper components from Github.
    
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
        
        * _env: The os.environ dict to use for pip-install
    
    Returns:
    --------
        * None
    """
    
    # Set the environment for pip install to fix Rhino-8 issues
    if _env == None:
        _env = os.environ
    
    # -------------------------------------------------------------------------
    # Install the Honeybee-PH and PHX packages from PyPi
    update_pip(_lbt_python_exe_path, _env=_env)
    pip_install(
        _package_name='honeybee-ph', 
        _package_version=_hbph_version,
        _lbt_python_exe_path=_lbt_python_exe_path,
        _lbt_python_package_path=_lbt_python_package_path,
        _package_install_folder_name=None,
        _env=_env
    )
    pip_install(
        _package_name='phx', 
        _package_version=_phx_version,
        _lbt_python_exe_path=_lbt_python_exe_path,
        _lbt_python_package_path=_lbt_python_package_path,
        _package_install_folder_name=None,
        _env=_env
    )
    
    # -------------------------------------------------------------------------
    # -- Install the Honeybee-PH Grasshopper Components and Libraries from GitHub
    get_files_from_github_repo(
        _github_repo_name='honeybee_grasshopper_ph',
        _target_directory=_lbt_python_package_path,
        _branch=_hbph_gh_branch or 'main'
    )
    copy_grasshopper_components_to_UserObjects(
        _repo_name='honeybee_grasshopper_ph',
        _download_directory=_lbt_python_package_path,
        _target_directory=UserObjectFolders
    )
    
    # -------------------------------------------------------------------------
    # -- Install the Honeybee-PH+ Grasshopper Components and Libraries from GitHub
    get_files_from_github_repo(
        _github_repo_name='honeybee_grasshopper_ph_plus',
        _target_directory=_lbt_python_package_path,
        _branch=_hbph_gh_branch or 'main'
    )
    copy_grasshopper_components_to_UserObjects(
        _repo_name='honeybee_grasshopper_ph_plus',
        _download_directory=_lbt_python_package_path,
        _target_directory=UserObjectFolders
    )
    
    # -------------------------------------------------------------------------
    # Give a success message
    print "- " * 50
    msg = 'Honeybee-PH and PHX have been successfully installed!\n'\
        'Please RESTART RHINO to being using the new components + libraries.'
    print(msg)
    lbt_gh.give_popup_message(msg, 'Installation Successful!')
    
    return None


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


# -- Required for Rhino 8, otherwise the new py3.9 hijacks the pip install
CUSTOM_ENV = os.environ.copy()
CUSTOM_ENV['PYTHONHOME'] = ''

check_system_setup()

if _install:
    install_honeybee_ph(
        _hbph_version=_hbph_version,
        _phx_version=_phx_version,
        _hbph_gh_branch=None,
        _lbt_python_exe_path=hb_folders.python_exe_path,
        _lbt_python_package_path=hb_folders.python_package_path,
        _env=CUSTOM_ENV
    )
else:
    msg = 'Please:\n'\
    '- Be sure you have already installed Ladybug Tools.\n'\
    '- Are connected to the internet.\n'\
    '- Set _install to "True" to install Honeybee-PH and all its dependencies on this system.'   
    print(msg)