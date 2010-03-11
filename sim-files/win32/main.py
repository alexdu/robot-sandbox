#       win32/main.py
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

import sys
import os

[path,file] = os.path.split(os.path.realpath(sys.argv[0]))
#print path
#print file

basepath = os.path.normpath(os.path.join(path, ".."))
sys.path.append(basepath)
os.chdir(basepath)

import numpy.lib.io   # bug in py2exe?!

import main


