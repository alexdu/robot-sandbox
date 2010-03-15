#       vplus.py
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


# Programele robot au acces la toate functiile si variabilele definite aici

from __future__ import division
from numpy import matrix, mat
from math import pi
from geom import *
import math
import numpy
import time
import os
import re
numpy.set_printoptions(precision=2, suppress=True)

PI = pi
TRUE = 1
FALSE = 0
ON = 1
OFF = 0



def SIN(ang):
    return numpy.sin(ang * pi/180)
def COS(ang):
    return numpy.cos(ang * pi/180)
def TAN(ang):
    return numpy.tan(ang * pi/180)
def ATAN2(dy, dx):
    return numpy.arctan2(dy, dx) * 180/pi
def INT(x):
    return x.__int__()
def FRACT(x):
    return x - INT(x)
def ABS(x):
    return abs(x)
def SIGN(x):
    if x >= 0:
        return 1
    else:
        return -1
def SQR(x):
    return x*x
def SQRT(x):
    return math.sqrt(x)
def MIN(a,b):
    if a > b:
        return a
    else:
        return b
def MAX(a,b):
    return -MIN(-a,-b)

    

def INVERSE(a):
    return TRANS(HTM = numpy.linalg.inv(a.HTM))    

def RX(ang):
    return TRANS(HTM = RobotSim.omorot(rotx(ang)))

def RY(ang):
    return TRANS(HTM = RobotSim.omorot(roty(ang)))

def RZ(ang):
    return TRANS(HTM = RobotSim.omorot(rotz(ang)))
    
def DX(a):
    return a.x
def DY(a):
    return a.y
def DZ(a):
    return a.z

def DISTANCE(a,b):
    return SQRT((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

def SHIFT(a, dx, dy, dz):
	return TRANS(dx,dy,dz) * a

def FRAME(a,b,c,d):
    x = b.POS - a.POS
    y_tmp = c.POS - a.POS
    z = numpy.cross(x.T, y_tmp.T).T
    y = numpy.cross(z.T, x.T).T
    
    x = x / numpy.linalg.norm(x)
    y = y / numpy.linalg.norm(y)
    z = z / numpy.linalg.norm(z)
    
    return TRANS(HTM = numpy.vstack([numpy.hstack([x,y,z,d.POS]), \
                                              mat((0,0,0,1))]))
    

class infix:
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)

    
MOD = infix(lambda x,y: numpy.mod(x,y))

def _xrange(a,b):
    if a < b:
        return range(a, b+1)
    else:
        return range(a, b-1, -1)
TO = infix(lambda x,y: _xrange(x,y))


class TRANS:
    def __init__(self, x=0, y=0, z=0, yaw=0, pitch=0, roll=0, HTM=0):
        
        if type(HTM).__name__ == 'matrix':
            (self.x, self.y, self.z, self.yaw, self.pitch, self.roll) = decompose(HTM)
        else:
            self.x = x
            self.y = y
            self.z = z
            self.yaw = yaw
            self.pitch = pitch
            self.roll = roll
            (self.x, self.y, self.z, self.yaw, self.pitch, self.roll) = decompose(self.get_htm())
        
    def __repr__(self):
        x = round(self.x, 3)
        y = round(self.y, 3)
        z = round(self.z, 3)
        yaw = round(self.yaw, 3)
        pitch = round(self.pitch, 3)
        roll = round(self.roll, 3)
        return "TRANS(%.3g, %.3g, %.3g, %.3g, %.3g, %.3g)" % \
            (x, y, z, yaw, pitch, roll)
                 
    def get_htm(self):
        return omotrans(self.x, self.y, self.z) * \
               omorot(rotz(self.yaw) * \
               roty(self.pitch) * rotz(self.roll))
    def get_pos(self):
        return (mat((self.x, self.y, self.z))).T
        
    HTM = property(get_htm)
    POS = property(get_pos)


    def __mul__(self, right):
        return TRANS(HTM = self.HTM * right.HTM)
    def __or__(self, right):
        return TRANS(HTM = self.HTM * right.HTM)
        


NULL = TRANS(0,0,0,0,0,0)


class PPOINT:
    def __init__(self, a=0,b=0,c=0,d=0,e=0,f=0):
        if type(a).__name__ == 'int' or type(a).__name__ == 'float':
            self.J = [a,b,c,d,e,f]
        else:
            self.J = list(a)

    def spanac(self):
        print "spanac"

    def __getitem__(self, key):
        return self.J[key]
        
    def __repr__(self):
        a = round(self.J[0], 3)
        b = round(self.J[1], 3)
        c = round(self.J[2], 3)
        d = round(self.J[3], 3)
        e = round(self.J[4], 3)
        f = round(self.J[5], 3)
        return "PPOINT(%.3g, %.3g, %.3g, %.3g, %.3g, %.3g)" % (a,b,c,d,e,f)




MONITOR = 1
ALWAYS  = 2
MMPS    = 4
IPS     = 8



# de aici incolo sunt functii care altereaza starea simulatorului robot
import RobotSim




def SPEED(spd, flags=0):
    """ Seteaza viteza robotului

    spd: viteza dorita
    flags: 
           MONITOR = seteaza viteza monitor
           ALWAYS  = seteaza viteza program globala
           nici MONITOR, nici ALWAYS = seteaza viteza program pt urmatoarea miscare
           
           doar pentru vitezele program:
           MMPS    = viteza masurata in mm/secunda
           IPS     = inci/secunda
           nici MMPS, nici IPS = procente din viteza maxima
    """
    if (flags & MONITOR) and not (flags & ALWAYS) and not (flags & MMPS) and not (flags & IPS):
        RobotSim.speed_monitor = max(0, min(spd, 100))
        return
        
    if flags & MMPS:
        unit = "MMPS"
        spd = max(0, min(spd, RobotSim.max_cartesian_speed))
    elif flags & IPS:
        unit = "IPS"
        spd = max(0, min(spd, RobotSim.max_cartesian_speed/25.4))
    else:
        unit = "%"
        spd = max(0, min(spd, 100))
        
    if flags & ALWAYS:
        RobotSim.speed_always = spd
        RobotSim.speed_always_unit = unit
    if not (flags & ALWAYS) and not (flags & MONITOR):
        RobotSim.speed_next_motion = spd
        RobotSim.speed_next_motion_unit = unit
        

def LEFTY():
	RobotSim.lefty = True
def LEFTY():
	RobotSim.lefty = False
def ABOVE():
	RobotSim.above = True
def BELOW():
	RobotSim.above = False
def FLIP():
	RobotSim.flip = True
def NOFLIP():
	RobotSim.flip = False
def SINGLE():
	RobotSim.single = True
def MULTIPLE():
	RobotSim.single = False
def OPEN():
    RobotSim.open_flag = True
    RobotSim.close_flag = False
def CLOSE():
    RobotSim.open_flag = False
    RobotSim.close_flag = True
def BREAK():
    RobotSim.ActuateGripper()
    
    while RobotSim.arm_trajectory_index < len(RobotSim.arm_trajectory) - 1:
        time.sleep(0.1)
    
    
def OPENI():
    BREAK()
    OPEN()
    BREAK()
    time.sleep(RobotSim.param["HAND.TIME"])
    
def CLOSEI():
    BREAK()
    CLOSE()
    BREAK()
    time.sleep(RobotSim.param["HAND.TIME"])
    

def HERE():
	return RobotSim.DK(RobotSim.currentJointPos)
def DEST():
	return RobotSim.DK(RobotSim.destJointPos)

def PHERE():
	return PPOINT(RobotSim.currentJointPos)
def PDEST():
	return PPOINT(RobotSim.destJointPos)

def MOVE(a):
    RobotSim.ActuateGripper() 

    if a.__class__.__name__ == 'TRANS':
        RobotSim.jtraj(RobotSim.IK(a))
    elif a.__class__.__name__ == 'PPOINT':
        RobotSim.jtraj(a)
    else:
        print "MOVE: invalid argument"
        
    # pentru urmatoarea miscare, revenim la viteza always 
    RobotSim.speed_next_motion = RobotSim.speed_always
    RobotSim.speed_next_motion_unit = RobotSim.speed_always_unit

    
def MOVES(a):
    RobotSim.ActuateGripper()

    if a.__class__.__name__ == 'TRANS':
        RobotSim.ctraj(RobotSim.IK(a))
    elif a.__class__.__name__ == 'PPOINT':
        RobotSim.ctraj(a)
    else:
        print "MOVES: invalid argument"

    # pentru urmatoarea miscare, revenim la viteza always 
    RobotSim.speed_next_motion = RobotSim.speed_always
    RobotSim.speed_next_motion_unit = RobotSim.speed_always_unit

def MOVET(a, grip):
    if grip:
        OPEN
    else:
        CLOSE
    MOVE(a)
    
def MOVEST(a, grip):
    if grip:
        OPEN
    else:
        CLOSE
    MOVES(a)
    
def APPRO(a, h):
    MOVE(a * TRANS(0, 0, -h))
def DEPART(h):
    MOVE(DEST() * TRANS(0, 0, -h))
def APPROS(a, h):
    MOVES(a * TRANS(0, 0, -h))
def DEPARTS(h):
    MOVES(DEST() * TRANS(0, 0, -h))

def PARAMETER(param_name, value):
    RobotSim.param[param_name] = value

def TOOL(t = None):
    if t != None:
        RobotSim.tool_trans = t
    return RobotSim.tool_trans

safe = PPOINT(0,-90,180,0,0,0)






# comenzi monitor
############################################

import IPython.ipapi
def EXECUTE(prog):
    jobs._status_new()
    if len(jobs.jobs_all) > 0:
        jobs.flush_finished()
    ip = IPython.ipapi.get()
    ip.ex("from vplus import *")

    if not re.match("^.*\.py$", prog):
        prog = prog + ".py" 
    ip.magic("%%bg _ip.magic('%%run -i %s')" % prog)

def _CM_EXEC(self, prog):
    """
        
    Monitor command for executing a robot program.

    Example:

    exec stiva
    """
    EXECUTE(prog)

def _CM_HERE(self, var):
    """
        
    Monitor command for teaching robot locations.

    Examples:

    here a       # records current end-effector position as a transformation 
    here #b      # records current joint position as a precision point
    here bs:a    # records end-effector position in the local reference frame "bs"
    """
    #IPShellEmbed()()
    ip = IPython.ipapi.get()
    
    reSingleVar = """
        ^
        [a-z]?        # start with lowercase letter
        [a-z0-9_]*    # may contain letter, digit or underscore
        $
        """
    rePPoint = """
        ^
        \#                    # start with #
        ([a-z]?[a-z0-9_]*)    # following variable name
        $
        """
    reBaseTransform = """
        ^
        ([^:]*)    # base (expression)
        :                     # colon operator
        ([a-z]?[a-z0-9_]*)    # variable
        $
        """
    
    mSingleVar = re.match(reSingleVar, var, re.VERBOSE)
    mPPoint = re.match(rePPoint, var, re.VERBOSE)
    mBaseTransform = re.match(reBaseTransform, var, re.VERBOSE)
    
    if mSingleVar:
        cmd = var + " = HERE()"
    elif mPPoint:
        var = mPPoint.groups()[0]
        cmd = var + " = PHERE()"
    elif mBaseTransform:
        bs = mBaseTransform.groups()[0]
        var = mBaseTransform.groups()[1]
        cmd = var + " = INVERSE(" + bs + ") * HERE()"
    else:
        print "here (monitor command): syntax error"
        return

    print "(debug) " + cmd
    ip.runlines(cmd)
    ip.runlines("vplus.%s = %s" % (var,var))
    ip.runlines(var)


    
    
def _CM_STATUS(self, var):    
    """
        
    Displays robot speeds and running programs.

    """
    print "Monitor speed: ", RobotSim.speed_monitor
    print "Program speed (ALWAYS): ", RobotSim.speed_always
    print "Program speed for next motion: ", RobotSim.speed_next_motion
    for i, j in enumerate(jobs.jobs_run):
        print i, j, j.status

def _CM_TOOL(self, var):
    """
        
    Set the tool transformation.

    Examples:

    t = TRANS(0,0,100)
    tool t

    tool TRANS(0,0,100)

    tool RZ(45)

    """
    ip = IPython.ipapi.get()
    ip.runlines("TOOL(" + var + ")")


def _CM_PARAM(self, var):
    """

    Set a parameter.

    Example:

    parameter hand.time = 0.5

    """
    if len(var) == 0:
        print RobotSim.param
    else:
        m = re.match("^([^=]+)=([^=]+)$", var)
        if m:
            name = m.groups()[0]
            value = m.groups()[1]
            RobotSim.param[name.upper().strip()] = eval(value)
        else:
            print "parameter (monitor command): syntax error"
        

def _CM_ENABLE(self, var):
    """

    Enable a switch.

    Example:

    enable power

    """
    RobotSim.switch[var.upper()] = True



def _CM_DISABLE(self, var):
    """

    Disable a switch.

    Example:

    disable power

    """
    RobotSim.switch[var.upper()] = False

def _CM_SWITCH(self, var):
    """

    List switches and their values.

    """
    if len(var) == 0:
        print RobotSim.switch
    else:
        print RobotSim.switch[var.upper()]

def _CM_CALIBRATE(self, var):
    """

    Does nothing.

    """
    print "Simulated robots do not need calibration :)"


def _CM_SEE(self, prog):
    """

    Edits a robot program.

    Example:

    see stiva

    Editor is vplus._editor 
    Default editor on Windows: notepad2 (included).
    If not found, falls back to notepad.

    """
    if not re.match("^.*\.py$", prog):
        prog = prog + ".py" 
    
    print "editing %s ..." % prog
    os.popen('%s %s' % (_editor, prog))

def _CM_SPEED(self, var):
    """

    Set monitor speed.

    Example:

    speed 100

    Tip: you may change the monitor speed while a robot program is running.
    """
    spd = eval('int(%s)' % var)
    print "Setting monitor speed to %d" % spd
    SPEED(spd, MONITOR)

from IPython.Shell import IPShellEmbed
def _CM_LISTL(self, var):
    """

    Lists location variables (TRANS and PPOINT).
    """
    print "Location variables:"
    print "==================="
    print "Transformations:"
    for k,v in globals().iteritems(): 
        if type(v).__name__ == 'instance':
            if v.__class__.__name__ == 'TRANS':
                print k, " = ", v
    print ""
    print "Precision points:"
    for k,v in globals().iteritems(): 
        if type(v).__name__ == 'instance':
            if v.__class__.__name__ == 'PPOINT':
                print k, " = ", v


def _CM_LISTR(self, var):
    """

    Lists real and integer variables.
    """
    print "Real and integer variables:"
    print "=========================="
    print "Reals:"
    for k,v in globals().iteritems(): 
        if type(v).__name__ == 'float':
            print k, " = ", v
    print ""
    print "Integers:"
    for k,v in globals().iteritems(): 
        if type(v).__name__ == 'int':
            print k, " = ", v
            
def _CM_LISTS(self, var):
    """

    Lists string variables.
    """
    print "String variables:"
    print "================="
    for k,v in globals().iteritems(): 
        if type(v).__name__ == type('string').__name__:
            print k, " = ", v




def _CM_ENV(self, prog):
    """

    Initializes the work environment for the robot.
    """
    if not re.match("^.*\.env$", prog):
        prog = prog + ".env" 
        
    print "setting work environment (%s)..." % prog
    print " "
    
    ip = IPython.ipapi.get()
    ip.runlines("resetBoxes()")

    RobotSim.pauseTick = True
    try:
        time.sleep(0.2)
        f = open(prog)
        r = f.read()
        f.close()
        ip.runlines(r)
    finally:
        RobotSim.pauseTick = False
    


def _CM_MC(self, var):
    """

    Displays a list of supported monitor commands.

    """
    print "Monitor commands:"
    print "================="
    print "here           # teach a robot location"
    print "speed          # set monitor speed"
    print "see            # edit a robot program"
    print "exec           # execute a robot program"
    print "status         # display system status"
    print "listl          # list location variables"
    print "listr          # list real and integer variables"
    print "lists          # list string variables"
    print "enable         # enable a switch"
    print "disable        # disable a switch"
    print "switch         # list switches"
    print "parameter      # set a parameter"
    print "tool           # set the tool transformation"
    print "cd <folder>    # change directory"
    print "ls             # list files"
    print ""
    print "For more help, type a monitor command followed by '?'"    
    print "e.g. here?"    
