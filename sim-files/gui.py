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
import time
#####################

import RobotSim

processViewerEvents = True

leftPanel = [None, None]
rightPanel = [None, None]    # gui, surf    
bottomPanel = [None, None]    # gui, surf    
panels = [leftPanel, bottomPanel, rightPanel]



speedPotMonitor = False
speedMonitor = 25
speedMCP = 50

fps = 0

modeswitch = None
speedpot = None
speedlabel = None
plusminus = []
signalsVBox = None

jogEnabled = False
jogAxis = 0
jogMode = "world"
jogSpeed = 100

        


def initGUI():
    global gui_screen, myguiapp, speedpot, speedlabel, modeswitch, opclo, fpsindic, signalsVBox
    
    leftPanel[1] = lamina.LaminaPartialScreenSurface(100, 250, 10, -10)
    rightPanel[1] = lamina.LaminaPartialScreenSurface(100, 300, -10, -10)
    bottomPanel[1] = lamina.LaminaPartialScreenSurface(510, 30, 0.0, 10)
    
    leftPanel[0] = gui.Container(width=100, height=250, surface=leftPanel[1].surf)
    rightPanel[0] = gui.Container(width=100, height=300, surface=rightPanel[1].surf)
    bottomPanel[0] = gui.Container(width=510, height=30, surface=bottomPanel[1].surf)
    
    leftPanel[0].value = "left panel"
    rightPanel[0].value = "right panel"
    bottomPanel[0].value = "bottom panel"

    leftPanel[0].style["bgimage"] = "none"
    rightPanel[0].style["bgimage"] = "none"
    bottomPanel[0].style["bgimage"] = "none"

    adjust_panels()

    labels = ["X", "Y", "Z", "RX", "RY", "RZ"]

    modeswitch = gui.Switch(0, ["Comp", 'World', 'Tool', 'Joint'], [0,1,2,3], x=0, y=0, width=65)
    modeswitch.label.style["color"] = (255,255,255)
    modeswitch.style["align"] = "center"
    modeswitch.label.style["font-size"] = 14
    enableStealEvents([modeswitch])
    modeswitch.connect(CHANGE, onModeSwitch)
    rightPanel[0].add(modeswitch)

    opclo = gui.Switch(0, ["OPEN", "CLOSE"], [0,1], x=0, y=35*7, width=65)
    opclo.label.style["color"] = (255,255,255)
    opclo.style["align"] = "center"
    opclo.style["valign"] = "top"
    opclo.label.style["font-size"] = 14
    enableStealEvents([opclo])
    opclo.connect(CHANGE, onOpenClose)
    rightPanel[0].add(opclo)
    

    speedpot = gui.HSlider(value=50, min_value=1, length=99, x=0, y=0, width=300)
    speedpot.style["align"] = "right"
    speedpot.style["valign"] = "center"
    enableStealEvents([speedpot])
    bottomPanel[0].add(speedpot)

    speedlabel = gui.Button("MCP Speed: 50", x=0, y=0, width=130)
    speedlabel.style["align"] = "left"
    speedlabel.style["valign"] = "center"
    speedlabel.label.style["color"] = (255,255,255)
    speedlabel.label.style["font-size"] = 14
    speedlabel.connect(CLICK, onSpeedToggle)
    #speedlabel.style["bgimage"] = "none"

    enableStealEvents([speedlabel])
    bottomPanel[0].add(speedlabel)

    speedpot.connect(CHANGE, onSpeedChange)

    #con = gui.TextBlock(value="spanac\ncastraveti", x=0, y=-50, width=300)
    #con.style["align"] = "center"
    #con.style["valign"] = "bottom"
    #enableStealEvents([con])
    #myguiapp.add(con)

    for i, l in enumerate(labels):
        addPlusMinus(rightPanel[0], l, i+1)


    onModeSwitch()

    #~ fpsindic = gui.Button("0 fps", x=0, y=0, width=70)
    #~ fpsindic.style["align"] = "left"
    #~ fpsindic.style["valign"] = "top"
    #~ fpsindic.label.style["color"] = (255,255,255)
    #~ fpsindic.label.style["font-size"] = 14
    #~ leftPanel[0].add(fpsindic)

    signalsVBox = gui.VBox(x = 0, y = 0, width = 90)
    signalsVBox.value = "signals"
    leftPanel[0].add(signalsVBox)



def addPlusMinus(guiapp, text, i):
    y0 = i * 35
    wm = gui.Button("-", x=-30, y=y0, width=10)
    wp = gui.Button("+", x=30, y=y0, width=10)
    wl = gui.Button(text, x=0, y=y0, width=0)

    wp.style["align"] = "center"
    wm.style["align"] = "center"
    wl.style["align"] = "center"
    
    wm.style["min-width"] = 0
    wp.style["min-width"] = 0
    wl.style["min-width"] = 0
    
    wl.stylesets["hover"]["bgimage"] = "none"
    wl.stylesets["default"]["bgimage"] = "none"
    wl.stylesets["down"]["bgimage"] = "none"
    wl.stylesets["focused"]["bgimage"] = "none"
    wp.label.style["font-size"] = 14
    wm.label.style["font-size"] = 14
    wl.label.style["font-size"] = 14

    wl.label.style["color"] = (255,255,255)
    wm.label.style["color"] = (255,255,255)
    wp.label.style["color"] = (255,255,255)

    wm.connect(MOUSEBUTTONDOWN, onJogStart, (i, -1))
    wm.connect(MOUSEBUTTONUP, onJogEnd, (i, -1))    
    wp.connect(MOUSEBUTTONDOWN, onJogStart, (i, 1))
    wp.connect(MOUSEBUTTONUP, onJogEnd, (i, 1))    
    
    #enableStealEvents([wp, wm, wl])   # fur evenimentele separat aici
    guiapp.add(wm,wl,wp)
    
    global plusminus
    plusminus.append([wm,wl,wp])

def adjust_panels():
    for p in panels:
        w = p[0]
        s = p[1]
        (top, bottom, left, right) = s.tblr
        (W,H) = pygame.display.get_surface().get_size()
        w.x = left
        w.y = H - top


def resizeGUI(w, h):
    for panel in panels:
        panel[1].setup()
    adjust_panels()
#    for panel in panels:
#        panel[1].setup()
#        panel[0].top_surface = panel[1].surf
#        panel[0].dirty = True



def stealEvents(steal):
    global processViewerEvents
    if steal: 
        processViewerEvents = False
    else:
        processViewerEvents = True
        
def enableStealEvents(widgets):
    for w in widgets:
        w.connect(MOUSEBUTTONDOWN, stealEvents, True)
        w.connect(MOUSEBUTTONUP, stealEvents, False)


    
def onJogStart(args):
    (i,sign) = args
    global jogEnabled, jogAxis, jogSpeed
    jogEnabled = True
    jogAxis = i
    jogSpeed = speedpot.value * sign

    #~ print "jog start:", jogAxis, jogSpeed
    stealEvents(True)
    
def onJogEnd(args):
    (i,sign) = args
    global jogEnabled
    jogEnabled = False
    #~ print "jog end:", jogAxis
    stealEvents(False)
    

def onOpenClose():
    if opclo.value == 0:
        RobotSim.open_flag = False
        RobotSim.close_flag = True
    else:
        RobotSim.open_flag = True
        RobotSim.close_flag = False
        
    RobotSim.ActuateGripper()
        
    
def onModeSwitch():    
    modeindex = modeswitch.value
    
    global jogMode
    jogMode = modeswitch.labels[modeindex]
    
    labels_xyz = ["X", "Y", "Z", "RX", "RY", "RZ"]
    labels_jts = ["J1", "J2", "J3", "J4", "J5", "J6"]
    labels = [labels_xyz, labels_xyz, labels_xyz, labels_jts]
    
    for i in range(6):
        if modeindex == 0:
            RobotSim.comp_mode = True
            for w in plusminus[i]:
                w.active = False
            opclo.active = False
            if not speedPotMonitor:
                onSpeedToggle()            
        else:
            RobotSim.comp_mode = False
            for w in plusminus[i]:
                w.active = True
            if speedPotMonitor:
                onSpeedToggle()
            opclo.active = True
            wl = plusminus[i][1]
            wl.active = True
            wl.label.value = labels[modeindex][i]
        
        #plusminus[i][1].style["bgcolor"] = (0,0,0)
        
    # fixme: cum fac fara sa regenerez textura de la zero? (doar s-o sterg)
    rightPanel[1].clear()
    rightPanel[0].top_surface = rightPanel[1].surf
    rightPanel[0].dirty = 1

def onSpeedChange():

    global speedPotMonitor, speedMCP, speedMonitor
    if speedPotMonitor:
        speedlabel.label.value = "Monitor Speed: %d" % speedpot.value
        speedMonitor = speedpot.value
        RobotSim.speed_monitor = speedMonitor
    else:
        speedlabel.label.value = "MCP Speed: %d" % speedpot.value
        speedMCP = speedpot.value

    speedlabel.dirty = True


def onSpeedToggle():
    global speedPotMonitor, speedMCP, speedMonitor
    speedPotMonitor = not speedPotMonitor
    
    if speedPotMonitor:
        speedpot.value = speedMonitor
    else:
        speedpot.value = speedMCP
        
    onSpeedChange()
    speedpot.dirty = True
    
    
def onSignalToggle(addr):
    if addr > 1000:
        RobotSim.signals[addr] = - (1 - abs(RobotSim.signals[addr]))
        RobotSim.signals_dirty = True


refreshTime = 0
    
def refreshSignals():
    global signalsVBox
    if RobotSim.signals_dirty:
        #~ print "refreshing"
        try:
            
            n = len(RobotSim.signals)
            m = len(signalsVBox.widgets)
            
            if n > m:
                for i in range(n - m):
                    w = gui.Button("spanac", width=10)
                    w.label.style["width"] = 10
                    w.label.style["font-size"] = 14
                    signalsVBox.add(w)
                    enableStealEvents([w])
            elif n < m:
                leftPanel[1].clear()
                leftPanel[0].top_surface = leftPanel[1].surf
                leftPanel[0].dirty = 1
                for i in range(m - n):
                    signalsVBox.remove(signalsVBox.widgets[-1])
            
            i = 0
            addresses = RobotSim.signals.keys()
            addresses.sort()
            for addr in addresses:
                val = RobotSim.signals[addr]
                w = signalsVBox.widgets[i]
                try:
                    (oldaddr, oldval) = w.sig
                    refresh = (oldaddr, oldval) != (addr, val)
                except:
                    refresh = True
                
                if refresh:
                    #~ print "refreshing ", addr, val
                    signalsVBox.dirty = True
                    if addr < 1000:
                        type = "out"
                    elif addr < 2000:
                        type = "in"
                    else:
                        type = "soft"
                        
                    if val:
                        sval = "on"
                    else:
                        sval = "off"
                    
                    w.value = "%s: %d" % (type, addr)
                    w.label.style["color"] = (255,255,255)
                    w.label.style["font-size"] = 14
                    #w.style["width"] = 70
                    w.style["height"] = 20
                    w.style["padding"] = (5,10)
                    w.stylesets["default"]["bgimage"] = "data/%s-%s.png slice" % (type, sval)
                    w.stylesets["hover"]["bgimage"] = "data/%s-%s.png slice" % (type, sval)
                    w.stylesets["focused"]["bgimage"] = "data/%s-%s.png slice" % (type, sval)
                    w.stylesets["down"]["bgimage"] = "data/%s-%s.png slice" % (type, sval)
                    w.sig = (addr, val)
                    w.dirty = True
                    w.connect(CLICK, onSignalToggle, addr)
                    #~ print "refresh done"
                    
                i += 1
                

            RobotSim.signals_dirty = False
            
            #~ print "resizetest"
            (w, h, x, y) = leftPanel[1]._whxy            
            signalsh = 30 * n
            if signalsh > h:
                print "growing to ", h * 2
                leftPanel[1] = lamina.LaminaPartialScreenSurface(100, h * 2, 10, -10)
                leftPanel[0].top_surface = leftPanel[1].surf
                leftPanel[0].dirty = True
                
            #~ print "resizetest done"

            
        except RuntimeError:
            #~ print "runtime error"
            pass
        #~ print "done"
            

def refresh():
    if RobotSim.switch["GUI"]:
        t0 = time.time()

        refreshSignals()
        
        #~ for w in signalsVBox.widgets:
            #~ if w.dirty:
                #~ print w

        
        global speedpot, speedMonitor
        if speedMonitor != RobotSim.speed_monitor:
            speedMonitor = RobotSim.speed_monitor
            speedpot.value = speedMonitor
            onSpeedChange()

        if jogEnabled:
            RobotSim.jog(jogMode, jogAxis, jogSpeed)
            
        #~ fpsindic.label.value = "%d fps" % fps
        #~ fpsindic.dirty = True
            
        # hack
        global modeswitch, opclo
        for w in [modeswitch, opclo]:
            if w.label.style["font-size"] != 14:
                w.label.style["color"] = (255,255,255)
                w.label.style["font-size"] = 14

        for panel in panels:
            panel[0].draw()
            panel[1].refreshPosition()
            panel[1].refresh()
            panel[1].display()

        t1 = time.time()
        refreshTime = t0 - t1

        if refreshTime > 0.1:
            print refreshTime

            
    else: # GUI disabled
        RobotSim.comp_mode = True
    
    pygame.display.set_caption("OpenGL Viewer [%d fps]" % fps)




def run(events):
    global processViewerEvents
    
    
    
    if RobotSim.switch["GUI"]:
        for panel in panels:
            panel[0].run(events)
    else:
        processViewerEvents = True
