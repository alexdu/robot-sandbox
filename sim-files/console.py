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
from __future__ import division
import sys
import os
import threading
#print sys.argv
sys.argv.pop()
sys.argv.pop()
import IPython
from IPython.Shell import IPShellEmbed
from vplus import *
import vplus
import time


# acum sunt in folderul cu sursele (src, sim-files)
_dir = os.getcwd()
_args = ['-pi1','. ','-po','=> ', '-colors', 'LightBG', '-xmode', 'Plain', '-autocall', '0']
_ipshell = IPShellEmbed(_args, banner="V+ simulation console ready.")


class ConsoleThread ( threading.Thread ):
    def run(self):

        from IPython.genutils import Term
        sys.sys_stdout = sys.stdout
        sys.ipy_stdout = Term.cout

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
        IPython.ipapi.get().expose_magic("speed", vplus._CM_SPEED)
        IPython.ipapi.get().expose_magic("listl", vplus._CM_LISTL)
        IPython.ipapi.get().expose_magic("listr", vplus._CM_LISTR)
        IPython.ipapi.get().expose_magic("lists", vplus._CM_LISTS)
        IPython.ipapi.get().expose_magic("mc", vplus._CM_MC)
        IPython.ipapi.get().expose_magic("cm", vplus._CM_MC)
        IPython.ipapi.get().expose_magic("env", vplus._CM_ENV)
        IPython.ipapi.get().expose_magic("do", vplus._CM_DO)
        IPython.ipapi.get().expose_magic("abort", vplus._CM_ABORT)
        IPython.ipapi.get().expose_magic("dir", vplus._CM_DIR)
        IPython.ipapi.get().expose_magic("load", vplus._CM_LOAD)
        IPython.ipapi.get().expose_magic("zero", vplus._CM_ZERO)
        
        print
        print "Type 'mc' to see a list of monitor commands."
        print "Use ! to invoke operating system commands (dir, ls, copy...)"
        print
        print "TRACE is ON."
        print

        
        _ipshell() 
        _ipshell.IP.savehist()
        os.abort()
        raise SystemExit

ConsoleThread().start()

time.sleep(1)
_ip = IPython.ipapi.get()
_ip.runlines("from __future__ import division")


