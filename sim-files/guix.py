#       gui.py
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

##################### GUI
import gooeypy as gui
from gooeypy.const import *
import lamina
#####################

import RobotSim
    
gui_screen = None
myguiapp = None


def resizeGUI(w, h):
    gui_screen.setup()
    myguiapp.top_surface = gui_screen.surf
    myguiapp.dirty = True


def refreshState():
    pass
def initGUI():
    global gui_screen, myguiapp, speedpot, speedlabel, modeswitch, opclo
    
    gui_screen = lamina.LaminaPartialScreenSurface(100,500,10,-10)
    
    myguiapp = gui.Container(width=640, height=480, surface=gui_screen.surf)
    #myguiapp.style["bgimage"] = "none"

    modeswitch = gui.Switch(0, ["Comp", 'World', 'Tool', 'Joint'], [0,1,2,3], x=-10, y=30, width=65)
    modeswitch.label.style["color"] = (255,255,255)
    modeswitch.style["align"] = "right"
    modeswitch.label.style["font-size"] = 14
    myguiapp.add(modeswitch)

