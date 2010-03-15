#       main.py
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


print "robot-sandbox (development version) starting..."
print " "



import sys
import os

print "cwd: ", os.getcwd()
(path,file) = os.path.split(os.getcwd())

#print path
#print file

if file != 'sim-files':
    print "abs path: ", os.path.abspath(__file__)
    [basepath,file] = os.path.split(os.path.abspath(__file__))
    libpath = os.path.join(basepath, "dist", "library.zip")
    print "base folder:", basepath
    print "library zip:", libpath
    os.chdir(basepath)
    (path,file) = os.path.split(os.getcwd())
    if file == 'sim-files':
        pass
        #print "path is ok"
    else:
        print "WARNING: working folder is not 'sim-files'"
else:
    print "path is OK"    
    basepath = os.getcwd()
#raise SystemExit





from vplus import *
import vplus


vplus._editor = '"' + os.path.join(basepath, "notepad2", "Notepad2.exe") + '"'
if not os.path.exists(vplus._editor):
    vplus._editor = "notepad.exe"



#ipshell = IPShellEmbed()
#ipshell() 

import viewer 


sys.argv.append("--navigation-mode=Softimage")
sys.argv.append("scene.py")
V = viewer.Viewer()
V.run()



