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
EM October 11, 2022
    Args:
        _install: (bool) Set to True to install Honeybee-PH on your computer.
        
        _hbph_branch: (str) Default='Main' Optional GitHub repo branch name for
            the honeybee-ph package to install (https://github.com/PH-Tools/honeybee_ph).
            If None is specified, will install the package from PIP. If you don't 
            know what branch or package you want, leave this input empty and the 
            default will be installed.
        
        _hbph_gh_branch: (str) Default='Main' Optional GitHub repo branch name for
            the honeybee-grasshopper-ph package to install (https://github.com/PH-Tools/honeybee_grasshopper_ph).
            If None is specified, will install the 'Main' branch of the repo. If you don't 
            know what branch or package you want, leave this input empty and the 
            default will be installed.
        
        _phx_branch: (str) Default='Main' Optional GitHub repo branch name for
            the PHX (Passive House Exchange) package to install (https://github.com/PH-Tools/PHX).
            If None is specified, will install the package from PIP. If you don't 
            know what branch or package you want, leave this input empty and the 
            default will be installed.
            
            
        _hbph_ver: (str): The Version number of the Honeybee-PH package to install from PIP.
            Note that if you leave this input empty, the latest version will be installed. For 
            more details on honeybee-ph version, see https://pypi.org/project/honeybee-ph/
       
        _phx_ver: (str): The Version number of the PHX package to install from PIP.
            Note that if you leave this input empty, the latest version will be installed. For 
            more details on honeybee-ph version, see https://pypi.org/project/PHX/
"""

ghenv.Component.Name = 'HBPH Installer'
ghenv.Component.NickName = 'HBPHInstall'
ghenv.Component.Message = 'OCT_11_2022'
ghenv.Component.Category = 'Honeybee-PH'
ghenv.Component.SubCategory = '0 | Installer'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


from exceptions import IOError
from distutils import dir_util
import subprocess
import shutil
import System
import os
import urllib
import zipfile

import Rhino
from Grasshopper.Folders import UserObjectFolders
from Grasshopper.Kernel import GH_RuntimeMessageLevel as Message

try:
    import honeybee
    hb_loaded = True
except ImportError as e:
    hb_loaded = False
    msg = '>> Failed to import honeybee:'\
        '>> Please be sure you have installed Ladybug Tools before proceeding.'\
        '>> See https://www.ladybug.tools/ for more information on downloading and installing Ladybug Tools.'
    raise ImportError('{}{}'.format(msg, e))

try:
    from honeybee_energy.config import folders as energy_folders
except ImportError as e:
    energy_loaded = False
    msg = "Failed to import honeybee_energy:> Please be sure you have installed Honeybee-Energy before proceeding."


def get_python_exe():
    """Get the path to the Python installed in the ladybug_tools folder.

    Will be None if Python is not installed.
    """
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    py_install = os.path.join(home_folder, 'ladybug_tools', 'python')
    py_exe_file = os.path.join(py_install, 'python.exe') if os.name == 'nt' else \
        os.path.join(py_install, 'bin', 'python3')
    py_site_pack = os.path.join(py_install, 'Lib', 'site-packages') if os.name == 'nt' else \
        os.path.join(py_install, 'lib', 'python3.7', 'site-packages')
    if os.path.isfile(py_exe_file):
        return py_exe_file, py_site_pack
    return None, None


def nukedir(target_dir, rmdir=False):
    # type: (str, bool) -> None
    """Delete all the files inside target_dir.

    This function has been copied from ladybug.futil.
    """
    d = os.path.normpath(target_dir)
    if not os.path.isdir(d):
        return
    
    files = os.listdir(d)
    for f in files:
        if f == '.' or f == '..':
            continue
        path = os.path.join(d, f)

        if os.path.isdir(path):
            nukedir(path)
        else:
            try:
                os.remove(path)
            except Exception as e:
                print e
                print("Failed to remove %s" % path)

    if rmdir:
        try:
            os.rmdir(d)
        except Exception:
            try:
                dir_util.remove_tree(d)
            except Exception as e:
                print e
                print("Failed to remove %s" % d)


def copy_file_tree(source_folder, dest_folder, overwrite=True):
    """Copy an entire file tree from a source_folder to a dest_folder.

    Args:
        source_folder: The source folder containing the files and folders to
            be copied.
        dest_folder: The destination folder into which all the files and folders
            of the source_folder will be copied.
        overwrite: Boolean to note whether an existing folder with the same
            name as the source_folder in the dest_folder directory should be
            overwritten. Default: True.
    """
    # make the dest_folder if it does not exist
    if not os.path.isdir(dest_folder):
        os.mkdir(dest_folder)
        

    # recursively copy each sub-folder and file
    for f in os.listdir(source_folder):
        # get the source and destination file paths
        src_file_path = os.path.join(source_folder, f)
        dst_file_path = os.path.join(dest_folder, f)

        # if overwrite is True, delete any existing files
        if overwrite:
            if os.path.isfile(dst_file_path):
                try:
                    os.remove(dst_file_path)
                except Exception:
                    raise IOError("Failed to remove %s" % f)
            elif os.path.isdir(dst_file_path):
                nukedir(dst_file_path, True)

        # copy the files and folders to their correct location
        if os.path.isfile(src_file_path):
            shutil.copyfile(src_file_path, dst_file_path)
        elif os.path.isdir(src_file_path):
            if not os.path.isdir(dst_file_path):
                os.mkdir(dst_file_path)
            copy_file_tree(src_file_path, dst_file_path, overwrite)


def get_paths(_repo="honeybee_ph", _branch='main'):
    # type: (str, str) -> Tuple[str, str]
    """Return the location of the url to download, and the target file location to save to."""
    
    download_url = "https://github.com/PH-Tools/{}/archive/refs/heads/{}.zip".format(_repo, _branch)
    download_folder = honeybee.config.folders.python_package_path
    download_file = os.path.join(download_folder, "main.zip")
    
    return download_url, download_file


def check_rhino_version(_min_version_allowed):
    # type: (Tuple[int, int]) -> Tuple[int, int]
    minimum_major_version = _min_version_allowed[0]
    minimum_minor_version = _min_version_allowed[1]
    
    if Rhino.RhinoApp.Version.Minor >= minimum_major_version:
        if Rhino.RhinoApp.Version.Minor >= minimum_minor_version:
            return (Rhino.RhinoApp.Version.Major, Rhino.RhinoApp.Version.Minor)
    msg = "Error: Honeybee-PH requires Rhino version: "\
        "{}.{} or better. Please update Rhino before proceeding.".format(minimum_major_version, minimum_minor_version)
    print msg
    raise Exception(msg)


def check_hb_core_version(_min_version_allowed):
    # type: (Tuple[int, int, int]) -> Tuple[int, int, int]
    try:
        hb_core_version_installed = honeybee.config.folders.honeybee_core_version # -> (1, 50, 0)
    except:
        msg = 'Error: Cannot load "honeybee.config.folders.honeybee_core_version" for some reason?'\
            'Please make sure you have Ladybug Tools installed, and updated to a the current version '\
            'before proceeding with the installation.'
        print msg
        ghenv.Component.AddRuntimeMessage(Message.Error,msg)
        return
    
    # Only check against Major and Minor, not the third number
    for inst_num, min_num in zip(hb_core_version_installed, _min_version_allowed):
        if inst_num < min_num:
            msg = "Error: Honeybee-PH is not "\
                "compatible with the version of Honeybee installed on this computer (v{}.{}.{}) Please "\
                "update your Ladybug Tools/Honeybee installation to a compatible version before proceeding "\
                "with the Honeybee-PH installation. You can use the Ladybug 'LB Versioner' component to update "\
                "your Honeybee installation, and then restart Rhino before trying to install Honeybee-PH again.".format(*hb_core_version_installed)
            print msg
            ghenv.Component.AddRuntimeMessage(Message.Error,msg)
            break
    return hb_core_version_installed


def download_repo_from_github(_download_url, _download_file):
    # type: (str, str) -> str
    """Download the specified URL to the specified location on this computer."""
    try:
        urllib.urlretrieve(_download_url, _download_file)
        print "Downloaded the file: ", _download_url
        print "To: ", _download_file
        return _download_file
    except IOError as e:
        msg = (
            "There was an error downloading the {} pacakge to your computer."
            "If you have Ladybug Tools installed in you 'ProgramFiles' directory, (ie: if you"
            "are using Pollination instead of the Food4Rhino LBT installer) you may"
            "need to run Rhino 'as administrator' in order to install to this directory?".format(_download_url)
            )
        raise IOError(msg)
    except Exception as e:
        msg = "Error downloading the {} package to your computer.".format(_download_url)
        raise e


def unzip_file(source_file):
    # type: (str) -> None
    """Unzip a compressed file.
    
    Arguments:
    ----------
        * source_file: (str) Full path to a valid compressed file (e.g. c:/ladybug/testPts.zip)
    Returns:
    --------
        * unzip_folder: (str) The full path to the folder unzipped
    """
    dest_dir, fname = os.path.split(source_file)
    
    # extract files to destination
    with zipfile.ZipFile(source_file) as zf:
        for member in zf.infolist():
            words = member.filename.split('\\')
            for word in words[:-1]:
                drive, word = os.path.splitdrive(word)
                head, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                dest_dir = os.path.join(dest_dir, word)
            zf.extract(member, dest_dir)
    
    return os.path.join(dest_dir, zf.infolist()[0].filename.replace('/', ''))


def copy_repo_contents_to_site_packages(_unzipped_src_dir, _repo_name):
    # type: (str) -> None
    """Copy the downloaded repo's Python libraries from the unzip-folder up one folder level."""
    
    # get the folder 'up' one level from the unzipped source dir.
    site_pckgs_folder = os.path.split(_unzipped_src_dir)[0]
    
    print '- '*25
    print 'Copying {} Python Packages to: {}'.format(_repo_name, site_pckgs_folder)
    
    src_dirs_to_exclude = ['tests', 'docs', 'diagrams', 'honeybee_grasshopper_ph'] # don't copy these to site-packages
    for dir in os.listdir(_unzipped_src_dir):
        if dir in src_dirs_to_exclude:
            continue
        if not os.path.isdir(os.path.join(_unzipped_src_dir, dir)):
            continue

        copy_file_tree(os.path.join(_unzipped_src_dir, dir), os.path.join(site_pckgs_folder, dir))


def copy_honeybee_ph_ghcomponents(_unzipped_src_dir, _gh_user_objects_folder):
    # type: (str, str) -> None
    """Copy all of the GH-User objects from the unzipped source dir over the Grasshopper UserObjects dir."""
    
    hbph_gh_source_folder = os.path.join(_unzipped_src_dir, 'honeybee_grasshopper_ph', 'user_objects')
    
    if not os.path.isdir(hbph_gh_source_folder):
        return 
    
    target = os.path.join(_gh_user_objects_folder[0], 'honeybee_grasshopper_ph')
    
    print '- '*25
    print 'Copying Honeybee-PH Grasshoppper Components to: {}'.format(target)
    
    copy_file_tree(hbph_gh_source_folder, target)


def give_popup_message(message, window_title=''):
    """Give a Windows popup message with an OK button.

    Useful in cases where you really need the user to pay attention to the message.

    Args:
        message: Text string for the popup message.
        window_title: Text string for the title of the popup window. (Default: "").
    """
    icon = System.Windows.Forms.MessageBoxIcon.Information
    buttons = System.Windows.Forms.MessageBoxButtons.OK
    Rhino.UI.Dialogs.ShowMessageBox(message, window_title, buttons, icon)


def update_libraries_pip(python_exe, package_name, version=None, target=None):
    """Update Python libraries using pip.

    Args:
        python_exe: The path to the Python executable to be used for installation.
        
        package_name: The name of the PyPI package to install
        
        version: An optional string for the version of the package to install.
        
        target: An optional target directory into which the package will be installed.
        """
        
    # build up the command using the inputs
    if version is not None:
        package_name = '{}=={}'.format(package_name, version)
    cmds = [python_exe, '-m', 'pip', 'install', package_name]
    if target is not None:
        cmds.extend(['--target', target, '--upgrade'])
        
    # execute the command and print any errors
    print('Installing {} via pip using{}'.format(package_name, python_exe))
    
    use_shell = True if os.name == 'nt' else False
    process = subprocess.Popen(
        cmds, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()
    stdout, stderr = output
    
    return stderr


def give_warning(message):
    """Give a warning message (turning the component orange).

    Args:
        message: Text string for the warning message.
    """
    ghenv.Component.AddRuntimeMessage(Message.Warning, message)


def copy_from_github_repo(_github_repo_name, _branch):
    # --------------------------------------------------------------------------
    # -- download the repo from github
    download_url, download_file = get_paths(_github_repo_name, _branch)
    download_file = download_repo_from_github(download_url, download_file)
    unzipped_folder = unzip_file(download_file)
    
    
    # --------------------------------------------------------------------------
    copy_repo_contents_to_site_packages(unzipped_folder, _github_repo_name)
    
    
    # --------------------------------------------------------------------------
    # -- copy repo grasshopper component
    copy_honeybee_ph_ghcomponents(unzipped_folder, UserObjectFolders)
    
    
    # --------------------------------------------------------------------------
    # remove the downloaded folder
    nukedir(unzipped_folder, True)
    os.remove(download_file)


def update_libraries_pip(python_exe, package_name, version=None, target=None):
    """Update Python libraries using pip.

    Args:
        python_exe: The path to the Python executable to be used for installation.
        
        package_name: The name of the PyPI package to install
        
        version: An optional string for the version of the package to install.
        
        target: An optional target directory into which the package will be installed.
        """
    # build up the command using the inputs
    if version is not None:
        package_name = '{}=={}'.format(package_name, version)
    cmds = [python_exe, '-m', 'pip', 'install', package_name]
    if target is not None:
        cmds.extend(['--target', target, '--upgrade'])

    # execute the command and print any errors
    print('Installing {} via pip using{}'.format(package_name, python_exe))
    use_shell = True if os.name == 'nt' else False
    process = subprocess.Popen(
        cmds, shell=use_shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()
    stdout, stderr = output
    return stderr

# Package versions
honeybee_ph_version =_hbph_ver # None defaults to newest
PHX_version = _phx_ver # None defaults to newest
rich_version = "12.4.1"
xlwings_version = "0.27.7"

# required versions
rhino_min_version = (7,18)
hb_core_min_version = (1, 51, 47)

# --------------------------------------------------------------------------
# -- Check version compatibility
rh_version_installed = check_rhino_version(rhino_min_version)
print "Rhino version: {}.{} found.".format(*rh_version_installed)

hb_core_version_installed = check_hb_core_version(hb_core_min_version)
print "Honeybee-Core version: {}.{}.{} found.".format(*hb_core_version_installed)

if _install and not (_hbph_branch or _phx_branch or _hbph_gh_branch):
    # -- Install the PIP version
    
    # --------------------------------------------------------------------------
    # Ensure that Python has been installed in the ladybug_tools folder
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    try:
        home_folder.decode('ascii')
    except UnicodeDecodeError:
        msg = 'Your username folder "{}" contains non-ASCII characters' \
            'While the latest version of Ladybug Tools supports most non-ASCII ' \
            'characters, there are some characters that can still cause issues.' \
            'To avoid all poential problems, you can create a new username with ' \
            'non-ASCII characters and install Ladybug Tools from that'.format(home_folder)
        print(msg)
        give_warning(msg)
    py_exe, py_lib = get_python_exe()
    assert py_exe is not None, \
        'No Python instalation was found at: {}.This is a requirement in ' \
        'order to contine with installation'.format(
            os.path.join(home_folder, 'ladybug_tools', 'python'))
    
    # --------------------------------------------------------------------------
    # Install the Honeybee-PH package
    
    print('Installing Honeybee-PH Python libraries.')
    stderr = update_libraries_pip(py_exe, 'honeybee-ph', honeybee_ph_version)
    if os.path.isdir(os.path.join(py_lib, 'honeybee-ph-{}.dist-info'.format(honeybee_ph_version))):
        print('Honeybee-PH Python libraries successfully installed! ')
    else:
        give_warning(stderr)
        print (stderr)
    
    
    # --------------------------------------------------------------------------
    # Install the PHX package
    print('Installing PHX (Passive House Exchange) Python libraries.')
    stderr = update_libraries_pip(py_exe, 'phx', PHX_version)
    if os.path.isdir(os.path.join(py_lib, 'phx-{}.dist-info'.format(PHX_version))):
        print('PHX Python libraries successfully installed! ')
    else:
        give_warning(stderr)
        print (stderr)
    
    
    # --------------------------------------------------------------------------
    # -- Install the Rhino / Grasshopper Components and Libraries
    copy_from_github_repo('honeybee_grasshopper_ph', _hbph_gh_branch or 'main')
    
    
    # --------------------------------------------------------------------------
    # give a success message
    success_msg = 'Honeybee-PH has been successfully installed'
    restart_msg = 'RESTART RHINO to load the new components + library.'
    for msg in (success_msg, restart_msg):
        print(msg)
    give_popup_message(''.join([success_msg, restart_msg]), 'Installation Successful!')
    
    
elif _install and (_hbph_branch or _phx_branch or _hbph_gh_branch):
    # -- Install the GitHub version
    # -- In this case, manually install the XLWings dependancy
    
    # --------------------------------------------------------------------------
    # Ensure that Python has been installed in the ladybug_tools folder
    home_folder = os.getenv('HOME') or os.path.expanduser('~')
    try:
        home_folder.decode('ascii')
    except UnicodeDecodeError:
        msg = 'Your username folder "{}" contains non-ASCII characters' \
            'While the latest version of Ladybug Tools supports most non-ASCII ' \
            'characters, there are some characters that can still cause issues.' \
            'To avoid all poential problems, you can create a new username with ' \
            'non-ASCII characters and install Ladybug Tools from that'.format(home_folder)
        print(msg)
        give_warning(msg)
    py_exe, py_lib = get_python_exe()
    assert py_exe is not None, \
        'No Python instalation was found at: {}.This is a requirement in ' \
        'order to contine with installation'.format(
            os.path.join(home_folder, 'ladybug_tools', 'python'))
    
    
    # --------------------------------------------------------------------------
    # Install the Rich dependancy
    print 'Installing Python package: Rich.'
    py_exe = honeybee.config.folders.python_exe_path
    py_lib = honeybee.config.folders.python_package_path
    stderr = update_libraries_pip(py_exe, 'rich', rich_version)

    if os.path.isdir(os.path.join(py_lib, 'rich-{}.dist-info'.format(rich_version))):
        print 'Rich Python package successfully installed! '
    else:
        give_warning(stderr)
        print stderr
    
    
    # --------------------------------------------------------------------------
    # Install the XLwings dependancy
    print 'Installing Python package: XLWings.'
    py_exe = honeybee.config.folders.python_exe_path
    py_lib = honeybee.config.folders.python_package_path
    stderr = update_libraries_pip(py_exe, 'xlwings', xlwings_version)

    if os.path.isdir(os.path.join(py_lib, 'xlwings-{}.dist-info'.format(rich_version))):
        print 'XLWings Python package successfully installed! '
    else:
        give_warning(stderr)
        print stderr
    
    
    # --------------------------------------------------------------------------
    copy_from_github_repo('honeybee_ph', _hbph_branch or 'main')
    copy_from_github_repo('PHX', _phx_branch or 'main')
    copy_from_github_repo('honeybee_grasshopper_ph', _hbph_gh_branch or 'main')
    
    
    # --------------------------------------------------------------------------
    # give a success message
    success_msg = 'Honeybee-PH has been successfully installed'
    restart_msg = 'RESTART RHINO to load the new components + library.'
    for msg in (success_msg, restart_msg):
        print(msg)
    give_popup_message(''.join([success_msg, restart_msg]), 'Installation Successful!')
    
    
else:  # give a message to the user about what to do
    if hb_loaded:
        check_hb_core_version(hb_core_min_version)
    print 'Please:- Be sure you have already installed Ladybug Tools.- Are connected to '\
    'the internet.- Set _install to "True" to install Honeybee-PH and all dependencies on this system.'   