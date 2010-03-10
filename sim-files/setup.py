from distutils.core import setup
from os.path import join
import py2exe

#mfcdir = 'C:/WINDOWS/WinSxS/x86_Microsoft.VC90.MFC_1fc8b3b9a1e18e3b_9.0.30729.4148_x-ww_a57c1f53'

#mfcfiles = [join(mfcdir, i) for i in ["mfc90.dll",  "mfc90u.dll",  "mfcm90.dll",  "mfcm90u.dll",  "Microsoft.VC90.MFC.manifest"]]

#data_files = [("Microsoft.VC90.MFC", mfcfiles)]
 
data_files=[("viper-model-hi", ["viper-model-hi/base.stl",\
								"viper-model-hi/link1.stl",\
								"viper-model-hi/link2.stl",\
								"viper-model-hi/link3.stl",\
								"viper-model-hi/link4.stl",\
								"viper-model-hi/link5.stl"]),
			(".", ["scene.py"])]
             


setup(
	name='robot-sandbox',
    version='0.1',
    description='V+ Robot Arm Simulator',
    author='Alex Dumitrache',

    console=['main.py'],
    data_files = data_files,
    options = {"py2exe": { "dll_excludes": ["wintab32.dll", "MSVCP90.dll"]}}
  )
