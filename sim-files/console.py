#       console.py
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


# Comenzile monitor sunt implementate ca "magic commands" in IPython
import sys
import os
import threading
global ipshell
#print sys.argv
sys.argv.pop()
sys.argv.pop()
import IPython
from IPython.Shell import IPShellEmbed
from vplus import *
import vplus

# acum sunt in folderul cu sursele (src, sim-files)
dir = os.getcwd()
args = ['-pi1','. ','-po','=> ', '-colors', 'LightBG', '-xmode', 'Plain']
ipshell = IPShellEmbed(args, banner="\r\nV+ simulation console ready.")




class ConsoleThread ( threading.Thread ):
    def run(self):
        IPython.ipapi.get().expose_magic("exec", vplus._CM_EXEC)
        IPython.ipapi.get().expose_magic("here", vplus._CM_HERE)
        IPython.ipapi.get().expose_magic("status", vplus._CM_STATUS)
        IPython.ipapi.get().expose_magic("tool", vplus._CM_TOOL)
        IPython.ipapi.get().expose_magic("enable", vplus._CM_ENABLE)
        IPython.ipapi.get().expose_magic("en", vplus._CM_ENABLE)
        IPython.ipapi.get().expose_magic("disable", vplus._CM_DISABLE)
        IPython.ipapi.get().expose_magic("dis", vplus._CM_DISABLE)
        IPython.ipapi.get().expose_magic("switch", vplus._CM_SWITCH)
        IPython.ipapi.get().expose_magic("parameter", vplus._CM_PARAM)
        IPython.ipapi.get().expose_magic("param", vplus._CM_PARAM)
        IPython.ipapi.get().expose_magic("cal", vplus._CM_CALIBRATE)
        IPython.ipapi.get().expose_magic("calibrate", vplus._CM_CALIBRATE)
        IPython.ipapi.get().expose_magic("see", vplus._CM_SEE)
        ipshell() 
        os.abort()
        raise SystemExit


