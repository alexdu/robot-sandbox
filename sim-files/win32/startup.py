#       win32/startup.py
#       
#       Copyright 2010 Alex Dumitrache <alex@cimr.pub.ro>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


# "Bootloader" for windows binary release

print "win32 'bootloader' startup..."

import numpy.lib.io   # bug in py2exe?!

import os
import sys
path = os.path.abspath(sys.argv[0])
[path,file] = os.path.split(path)
basepath = os.path.normpath(os.path.join(path, ".."))
os.chdir(basepath)


import IPython.ipapi
print "creating IPython session..."
IPython.ipapi.make_session()
ip = IPython.ipapi.get()
ip.magic("%run main.py")


