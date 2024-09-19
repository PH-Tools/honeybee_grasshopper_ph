"""
Updates all the GH-Components in the Source dir (Github)
-
EM September 19, 2024 | Antwerp, Belgium
"""

ghenv.Component.Name = "__HBPH__Util_Update_GHCompos"
ghenv.Component.NickName = "HBPH_Update_Source"
ghenv.Component.Message = 'SEP_19_2024'
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Honeybee-PH"
ghenv.Component.SubCategory = "00 | Utils"
ghenv.Component.ToggleObsolete(False)

import os
import Grasshopper.Kernel as ghK
import shutil
from GhPython.Component import ZuiPythonComponent


class NamespaceComponentsOntoCanvas():
    """Context Manager class to add all of a namespace's GH-Components to the Canvas.
    
    #Usage: 
    >>>  with NamespaceComponentsOntoCanvas("HB-REVIVE", hb_revive_source_dir, ghdoc, ghK) as compos:
    >>>      ... ## do some things with the components
    """

    def __init__(self, _namespace, _source_dir, _ghdoc, _ghK):
        # type: (str, str, Any, Any) -> None
        self.namespace = _namespace
        self.source_dir = _source_dir
        self.compos = []
        self.ghdoc = _ghdoc
        self.ghK = _ghK
    
    def __enter__(self):
        """Add all of the namespace components to the canvas."""

        print('Adding all {} the Components to the Canvas'.format(self.namespace))
        ghuser_file_names = os.listdir(self.source_dir)
        
        for compo_name in ghuser_file_names:
            if '.' == compo_name[0]: continue # Fucking Mac OS....
            
            #if self.namespace not in compo_name: continue
            
            if not str(compo_name).startswith(self.namespace): continue
            if '__' == compo_name[:2]: continue
            
            print "Adding: {}".format(compo_name)
            compo_address = self.source_dir + compo_name
            compo = self.ghK.GH_UserObject(compo_address).InstantiateObject()
            self.ghdoc = ghenv.Component.OnPingDocument()
            self.ghdoc.AddObject(compo, False)
            
            # --  keep track of the components added to the canvas
            self.compos.append(compo)
            
        return self
      
    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Remove all the components added to the canvas."""

        print('Cleaning Up the Canvas')
        for compo in self.compos:
            self.ghdoc.RemoveObject(compo, False)


def copy_py_code(_gh_component, _target_path):
    # type: (ZuiPythonComponent, str) -> None
    """Copy the ghuse component python code over to a save file."""
    
    target_path_ = os.path.join(_target_path, _gh_component.Name + '.py')
    
    if 'Code' not in dir(_gh_component):
        # -- Value Lists items don't have Py code
        return None

    if os.path.exists(target_path_):
        os.remove(target_path_)

    print 'Writing {} code to: --> {}'.format(_gh_component.Name, target_path_)
    with open(target_path_, 'wb') as f:
        f.write(_gh_component.Code.encode('utf-8'))

    return None


def copy_ghuser(_gh_component, _source_path, _target_path):
    # type: (ZuiPythonComponent, str, str) -> None
    """Copy ghuser component to the save file."""

    src_path_ = os.path.join(_source_path, _gh_component.Name + '.ghuser')
    target_path_ = os.path.join(_target_path, _gh_component.Name + '.ghuser')
    
    if os.path.exists(src_path_):
        print 'Copying: {} --> {}'.format(src_path_, target_path_)
        shutil.copy(src_path_, target_path_)
    else:
        raise ValueError("Error: {} folder is missing?".format(src_path_))

    return None


if _run:
    # - - - - - - HB-PH Components
    hbph_source_dir = str(r"/Users/em/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/Grasshopper (b45a29b1-4343-4035-989e-044e8580d9cf)/UserObjects/honeybee_grasshopper_ph/")
    hbph_save_dir_ghuser    = str(r"/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph/honeybee_grasshopper_ph/user_objects/")
    hbph_save_dir_ghuser_py = str(r"/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph/honeybee_grasshopper_ph/src/")

    print '- '*25, 'Backing up HBPH Components', '- '*25
    with NamespaceComponentsOntoCanvas("HBPH", hbph_source_dir, ghdoc, ghK) as compos:
        for compo in compos.compos:
            copy_ghuser(compo, hbph_source_dir, hbph_save_dir_ghuser)
            copy_py_code(compo, hbph_save_dir_ghuser_py)

    # # - - - - - HB-PH+ Components
    hbph_plus_source_dir = str(r"/Users/em/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/Grasshopper (b45a29b1-4343-4035-989e-044e8580d9cf)/UserObjects/honeybee_grasshopper_ph_plus/")
    hbph_plus_save_dir_ghuser    = str(r"/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph_plus/honeybee_grasshopper_ph_plus/user_objects/")
    hbph_plus_save_dir_ghuser_py = str(r"/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph_plus/honeybee_grasshopper_ph_plus/src/")
    
    print '- '*25, 'Backing up HBPH+ Components', '- '*25
    with NamespaceComponentsOntoCanvas("HBPH+", hbph_plus_source_dir, ghdoc, ghK) as compos:
        for compo in compos.compos:
            copy_ghuser(compo, hbph_plus_source_dir, hbph_plus_save_dir_ghuser)
            copy_py_code(compo, hbph_plus_save_dir_ghuser_py)

    # - - - - - HB-REVIVE Components
    hb_revive_source_dir = str(r"/Users/em/Library/Application Support/McNeel/Rhinoceros/8.0/Plug-ins/Grasshopper (b45a29b1-4343-4035-989e-044e8580d9cf)/UserObjects/honeybee_grasshopper_revive/")
    hb_revive_save_dir_ghuser    = str(r"/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_REVIVE/honeybee_revive_grasshopper/user_objects/")
    hb_revive_save_dir_ghuser_py = str(r"/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_REVIVE/honeybee_revive_grasshopper/src/")
    
    print '- '*25, 'Backing up HB-REVIVE Components', '- '*25
    with NamespaceComponentsOntoCanvas("HB-REVIVE", hb_revive_source_dir, ghdoc, ghK) as compos:
        for compo in compos.compos:
            copy_ghuser(compo, hb_revive_source_dir, hb_revive_save_dir_ghuser)
            copy_py_code(compo, hb_revive_save_dir_ghuser_py)
