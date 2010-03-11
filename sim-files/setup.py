from distutils.core import setup
from os.path import join
import py2exe

#mfcdir = 'C:/WINDOWS/WinSxS/x86_Microsoft.VC90.MFC_1fc8b3b9a1e18e3b_9.0.30729.4148_x-ww_a57c1f53'

#mfcfiles = [join(mfcdir, i) for i in ["mfc90.dll",  "mfc90u.dll",  "mfcm90.dll",  "mfcm90u.dll",  "Microsoft.VC90.MFC.manifest"]]

#data_files = [("Microsoft.VC90.MFC", mfcfiles)]
 
#~ data_files=[("6dof-robot-model", ["6dof-robot-model/base.stl",\
								#~ "6dof-robot-model/link1.stl",\
								#~ "6dof-robot-model/link2.stl",\
								#~ "6dof-robot-model/link3.stl",\
								#~ "6dof-robot-model/link4.stl",\
								#~ "6dof-robot-model/link56.stl"]),
			#~ (".", ["scene.py", "vplus.py", "RobotSim.py", "viewer.py", "geom.py", "main.py"])]
             
# TODO: sters fisierele sursa (vplus.py ... main.py) din library.zip


setup(
	name='robot-sandbox',
    version='0.1.1',
    description='Robot Arm Simulator with Rigid Body Dynamics',
    author='Alex Dumitrache and contributors',

    console=['win32/startup.py'],
    #~ data_files = data_files,
    options = 
    {
        "py2exe": 
        { 
            "excludes": ["wx", "matplotlib"],
            "dll_excludes": ["wintab32.dll", "MSVCP90.dll", 
                            "libgtk-win32-2.0-0.dll",
                            "libgdk-win32-2.0-0.dll",
                            "libgdk_pixbuf-2.0-0.dll",
                            "libpangoft2-1.0-0.dll",
                            "libglib-2.0-0.dll",
                            #"tk84.dll", 
                            #"tcl84.dll",
                            "libgio-2.0-0.dll",
                            #"freetype6.dll",
                            #"libfreetype-6.dll",
                            #"_ssl.pyd",
                            
                            ],
            #'bundle_files':  
        }
    }
  )
