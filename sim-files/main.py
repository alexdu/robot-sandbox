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

#from IPython.Shell import IPShellEmbed

print "robot-sandbox (development version) starting..."
print " "
import sys
import os
#print sys.path

from vplus import *

#editor = os.path.join(dir, "notepad2", "Notepad2.exe")



#ipshell = IPShellEmbed()
#ipshell() 

import viewer 


sys.argv.append("--navigation-mode=Softimage")
sys.argv.append("scene.py")
V = viewer.Viewer()
V.run()



