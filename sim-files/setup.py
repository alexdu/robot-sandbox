from distutils.core import setup
from os.path import join
import py2exe

import sys, os
import zipfile
import shutil

def rmrf(folder, exc = False):
    if sys.platform == "win32":
        rm = "rmdir /s /q "
    else:
        rm = "rm -rf "

    print rm + folder
    ret = os.system(rm + folder)
    if exc:
        if ret != 0: 
            raise Exception, "error deleting " + folder

def unzip(file, dir):
    zfobj = zipfile.ZipFile(file)
    mainfolder = zfobj.namelist()[0][:-1]
    for name in zfobj.namelist():
        print name
        fullname = os.path.join(dir, name)
        d = os.path.dirname(fullname)
        if d != "":
            if not os.path.isdir(d):
                os.makedirs(d)
        if not os.path.isdir(fullname):
            outfile = open(fullname, 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()
    return mainfolder


if 'test' in sys.argv:
    os.chdir("dist")
    rmrf("library")
    mainfolder = unzip('library.zip', 'library')

    print os.path.realpath("../../libs/OpenGL")
    unzip("../../libs/OpenGL.zip", "library")

    surse = os.listdir("..")    
    for f in surse:
        if f.endswith(".py"):
            pyc = os.path.join("library", f + "c")
            if os.path.isfile(pyc):
                print pyc
                os.remove(pyc)
    sys.exit(0)
    

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
# si apoi redenumit startup.exe => robot-sandbox.exe

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
            "includes": ["main"],
            "excludes": ["wx", "matplotlib", "OpenGL", "gooeypy", "profilestats"],
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
