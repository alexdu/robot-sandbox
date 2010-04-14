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
import sys
import re
import subprocess
import string
from v2py import *
from pprint import pprint
from IPython.Shell import IPShellEmbed
import traceback
from copy import copy, deepcopy

numpy.set_printoptions(precision=2, suppress=True)

PI = pi
TRUE = 1
FALSE = 0
ON = 1
OFF = 0

numeric = ['int', 'int32', 'float']
location = ['TRANS', 'PPOINT']
def check_args(args, types):
    if type(args).__name__ != 'list':
        args = [args]
        
    if type(types).__name__ != 'list':
        types = [types]
    
    if len(types) == 1:
        types = types * len(args)
    elif len(types) != len(args):
        types = [types] * len(args)

    typeslist = []
    for t in types:
        if type(t).__name__ == 'list':
            typeslist.append(t)
        else:
            typeslist.append([t])
    argtypes = []
    for arg in args:
        if type(arg).__name__ == 'instance':
            argtypes.append(arg.__class__.__name__)
        else:
            argtypes.append(type(arg).__name__)
    #~ print argtypes
    #~ print typeslist
            
    for i, t in enumerate(argtypes):
        allowedtypes = typeslist[i]
        if not (t in allowedtypes):
            caller = traceback.extract_stack()[-2][2]
            raise TypeError, "%s expects argument %d to be '%s', not '%s'." % (caller, i+1, string.join(allowedtypes, "' or '"), t)

def DEFINED(x):
    return not(x == None)

def SIN(ang):
    check_args(ang, numeric)
    return float(numpy.sin(ang * pi/180))
def COS(ang):
    check_args(ang, numeric)
    return float(numpy.cos(ang * pi/180))
def TAN(ang):
    check_args(ang, numeric)
    return float(numpy.tan(ang * pi/180))
def ATAN2(dy, dx):
    """
    Arctangent function
    Arguments: delta Y and delta X
    
    ATAN2(1,1) => 45
    
    """
    check_args([dy,dx], [numeric])
    return float(numpy.arctan2(dy, dx) * 180/pi)
def INT(x):
    check_args(x, numeric)
    return x.__int__()
def FRACT(x):
    """
    
    Computes the fractional part of x
    (x is scalar)
    
    FRACT(1.2) => 0.2
    
    """
    check_args(x, numeric)
    return x - INT(x)
def ABS(x):
    """
    
    Computes the absolute value of x
    (x is scalar)
    
    ABS(-5) => 5
    ABS(10) => 10
    
    """
    check_args(x, numeric)
    return abs(x)
def SIGN(x):
    """
    
    SIGN(x) = 1 if x >= 0,
              0 otherwise
    
    """
    check_args(x, numeric)
    if x >= 0:
        return 1
    else:
        return -1
def SQR(x):
    """
    
    Computes x^2 
    (x is scalar)
    
    """
    check_args(x, numeric)
    return x*x
def SQRT(x):
    """
    
    Square root of a scalar variable
    
    """
    check_args(x, numeric)
    return math.sqrt(x)
def MIN(a,b):
    """
    
    Minimum value between 2 scalar variables
    
    """
    check_args([a,b], [numeric])
    if a > b:
        return b
    else:
        return a
def MAX(a,b):
    """
    
    Maximum value between 2 scalar variables
    
    """
    check_args([a,b], [numeric])
    return -MIN(-a,-b)

    

def INVERSE(a):
    """
    
    Computes the inverse of a transformation matrix
    
    Examples:
    
    .do set inv = INVERSE(RX(45))
    .do set tool = old.tool:INVERSE(HERE):ref.loc
    
    """
    check_args(a, "TRANS")
    t = a.HTM
    t[0:3,3] = -t[0:3,3]
    t[0:3,0:3] = t[0:3,0:3].T
    return TRANS(HTM = t)

def RX(ang):
    """
    
    Elementary rotation around X axis.
    
    Example:
    
    RX(45)
    .do moves here:rx(45)
    
    """
    check_args(ang, numeric)
    return TRANS(HTM = RobotSim.omorot(rotx(ang)))

def RY(ang):
    """
    
    Elementary rotation around Y axis.
    
    Example:
    
    RY(45)
    .do moves here:ry(45)
    
    """
    check_args(ang, numeric)
    return TRANS(HTM = RobotSim.omorot(roty(ang)))


def RZ(ang):
    """
    
    Elementary rotation around Z axis.
    
    Example:
    
    RZ(45)
    .do moves here:rz(45)
    
    """
    check_args(ang, numeric)
    return TRANS(HTM = RobotSim.omorot(rotz(ang)))
    
def DX(a):
    """
    Extracts the X component from a transformation.
    
    Examples:
    
    DX(TRANS(1,2,3)) => 1
    
    .do type DX(HERE)
    
    """
    check_args(a, "TRANS")
    return a.x

def DY(a):
    """
    Extracts the Y component from a transformation.
    
    Examples:
    
    DY(TRANS(1,2,3)) => 2
    
    .do type DY(HERE)
    
    """
    check_args(a, "TRANS")
    return a.y
    
    
def DZ(a):
    """
    Extracts the Z component from a transformation.
    
    Examples:
    
    DZ(TRANS(1,2,3)) => 3
    
    .do type DZ(HERE)
    
    """
    check_args(a, "TRANS")
    return a.z

def DISTANCE(a,b):
    """
    
    Computes the 3D (XYZ) distance between two transformations (robot locations).
    
    EXAMPLE:
    
    .do type distance(here, TRANS(100,0,0))
    
    """
    check_args([a,b], "TRANS")
    return SQRT((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

def SHIFT(a, dx, dy, dz):
    """
    Translates a transformation (robot location) in the World reference frame.
    
    Examples:
    
    .do set b = SHIFT(a BY 10, 20, 30)
    
    SHIFT(loc BY dx, dy, dz) is equivalent to TRANS(dx, dy, dz):loc
    
    """
    check_args([a, dx, dy, dz], ["TRANS", numeric, numeric, numeric])
    
    return TRANS(dx,dy,dz) * a

def FRAME(a,b,c,d):
    """

    Computes a right-handed reference frame determined by 4 transformations (robot locations).
    
    a - b       : is the direction of local X axis
    a - b - c   : defines the XY plane and the sign of Y axis
    d           : defines the origin of the frame

    EXAMPLES:
    .do set bs = FRAME(a,b,c,d)
    .here bs:a
    .do appro bs:a, 100
    """
    check_args([a, b, c, d], "TRANS")
    
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

    
#~ MOD = infix(lambda x,y: _MOD(x,y))
#~ def _MOD(a,b):
    #~ check_args([a, b], [numeric])
    #~ return a % b

TO = infix(lambda x,y: FOR_RANGE(x,y))
def FOR_RANGE(a,b,step=1):
    """
    Creates an interval to be used in FOR loops:
    FOR_RANGE(1,5) = [1,2,3,4,5]
    FOR_RANGE(1,1) = [1]
    FOR_RANGE(5,1) = []
    FOR_RANGE(5,1,-1) = [5,4,3,2,1]
    
    1 |TO| 5 is the same as FOR_RANGE(1,5)
    
    Usage in V+ program:
              
    FOR i = 1 TO 5           ; =>  1 |TO| 5 => FOR_RANGE(1,5)
        TYPE i
    END

    FOR i = 5 TO 1 STEP -1   ; => FOR_RANGE(5,1,-1)
        TYPE i
    END
    
    """    
    check_args([a, b, step], [numeric])
    if int(a) == a and int(b)==b and int(step)==step:
        return numpy.arange(a, b + numpy.sign(step), step).tolist()
    else:
        return numpy.arange(a, b + numpy.sign(step) * 1e-10, step).tolist()
    
TO = infix(lambda x,y: FOR_RANGE(x,y))




def _XOR(a,b):
    """
    Logical XOR
    """    
    check_args([a, b], [numeric])
    return bool(a) ^ bool(b)
XOR = infix(lambda x,y: _XOR(x,y))

class TRANS:
    """
    Transformation (location variable)
    Components: x, y, z, yaw, pitch, roll.
    Convention for yaw-pitch,roll: ZYZ'
    
    V+ monitor console (case insensitive):
    .here a
    .do set b = TRANS(100,100,100,0,180,0)
    .do set c = a:rz(45)

    V+ program (case insensitive):
    HERE a
    SET b = TRANS(100,100,100,0,180,0)
    SET c = a:RZ(45)
    
    Python (case sensitive):
    a = HERE()
    b = TRANS(100,100,100,0,180,0)
    c = a*RZ(45) 
    """
    def __init__(self, x=0, y=0, z=0, yaw=0, pitch=0, roll=0, HTM=0):
        check_args([self,x,y,z,yaw,pitch,roll], ['TRANS'] + [numeric] * 6)
        
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
        return "TRANS(%4.3g, %4.3g, %4.3g, %4.3g, %4.3g, %4.3g)" % \
            (x, y, z, yaw, pitch, roll)
    def __eq__(a, b):
        try:
            return (a.x == b.x) and (a.y == b.y) and (a.z == b.z) and (a.yaw == b.yaw) and (a.pitch == b.pitch) and (a.roll == b.roll)
        except:
            return False
                 
    def get_htm(self):
        cy = math.cos(self.yaw * pi/180)
        sy = math.sin(self.yaw * pi/180)
        cp = math.cos(self.pitch * pi/180)
        sp = math.sin(self.pitch * pi/180)
        cr = math.cos(self.roll * pi/180)
        sr = math.sin(self.roll * pi/180)
        cpcr = cp*cr
        cpsr = cp*sr
        return mat([[cy*cpcr - sy*sr, -cy*cpsr - sy*cr, cy*sp, self.x],
                    [sy*cpcr + cy*sr, -sy*cpsr + cy*cr, sy*sp, self.y],
                    [         -sp*cr,            sp*sr,    cp, self.z], 
                    [              0,                0,     0,      1]])

        #~ return omotrans(self.x, self.y, self.z) * \
               #~ omorot(rotz(self.yaw) * \
               #~ roty(self.pitch) * rotz(self.roll))
    def get_pos(self):
        return (mat((self.x, self.y, self.z))).T
        
    HTM = property(get_htm)
    POS = property(get_pos)


    def __mul__(self, right):
        return _TRANS_COMPOSE(self, right)
    def __or__(self, right):
        return _TRANS_COMPOSE(self, right)
        
def _TRANS_COMPOSE(a, b):
    check_args([a, b], "TRANS")
    return TRANS(HTM = a.HTM * b.HTM)


NULL = TRANS(0,0,0,0,0,0)


class PPOINT:
    """
    Precision point.
    
    .do set x = #PPOINT(0,-90,90,0,180,0)    
    """
    def __init__(self, a=0,b=0,c=0,d=0,e=0,f=0):
        if type(a).__name__ == 'int' or type(a).__name__ == 'float':
            self.J = [a,b,c,d,e,f]
        else:
            self.J = list(a)

    def __getitem__(self, key):
        return self.J[key]
        
    def __repr__(self):
        a = round(self.J[0], 3)
        b = round(self.J[1], 3)
        c = round(self.J[2], 3)
        d = round(self.J[3], 3)
        e = round(self.J[4], 3)
        f = round(self.J[5], 3)
        return "PPOINT(%4.3g, %4.3g, %4.3g, %4.3g, %4.3g, %4.3g)" % (a,b,c,d,e,f)







# de aici incolo sunt functii care altereaza starea simulatorului robot
import RobotSim



def DURATION(*args):
    pass

def SPEED(spd, flag1=None, flag2=None):
    
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
    check_args([spd, flag1, flag2], [numeric, ["str", "NoneType"], ["str", "NoneType"]])
    
    MONITOR = False
    ALWAYS  = False
    MMPS    = False
    IPS     = False
    
    if "MONITOR" in [flag1, flag2]:
        MONITOR = True
    if "ALWAYS" in [flag1, flag2]:
        ALWAYS = True
    if flag1 == "MMPS":
        MMPS = True
    if flag1 == "IPS":
        IPS = True
        
    
    if MONITOR:
        if not ALWAYS and not MMPS and not IPS:
            RobotSim.speed_monitor = max(1, min(spd, 100))
        else:
            raise SyntaxError, "Expected: SPEED xx MONITOR  (without ALWAYS or MMPS or IPS)"
    else:
        if MMPS:
            unit = "MMPS"
            spd = max(0, min(spd, RobotSim.max_cartesian_speed))
        elif IPS:
            unit = "IPS"
            spd = max(0, min(spd, RobotSim.max_cartesian_speed/25.4))
        else:
            unit = "%"
            spd = max(0, min(spd, 100))
            
        if ALWAYS:
            RobotSim.speed_always = spd
            RobotSim.speed_always_unit = unit
        else:
            RobotSim.speed_next_motion = spd
            RobotSim.speed_next_motion_unit = unit
        

def LEFTY():
    """
    Asserts the LEFTY configuration flag.
    Effect: at the next motion, the robot will try to reach locations
    (transformation variables) in the LEFTY configuration.
    
    For SCARA and planar arm, LEFTY looks like this (view from above):
        o
       /       
      /
      \
       \
      (())
    """
    RobotSim.lefty = True
def RIGHTY():
    """
    Asserts the RIGHTY configuration flag.
    Effect: at the next motion, the robot will try to reach locations
    (transformation variables) in the RIGHTY configuration.
    
    For SCARA and planar arm, RIGHTY looks like this (view from above):
        o
         \       
          \
          /
         /
       (())
    """
    
    RobotSim.lefty = False
def ABOVE():
    """
    For vertical robots: sets the ELBOW above the line between SHOULDER and WRIST.
    Not implemented.
    """
    RobotSim.above = True
def BELOW():
    """
    For vertical robots: sets the ELBOW below the line between SHOULDER and WRIST.
    Not implemented.
    """
    RobotSim.above = False
def FLIP():
    """
    FLIP configuration mode for spherical wrist.
    """
    RobotSim.flip = True
def NOFLIP():
    """
    NOFLIP configuration mode for spherical wrist.
    """
    RobotSim.flip = False
def SINGLE():
    RobotSim.single = True
def MULTIPLE():
    RobotSim.single = False
def OPEN():
    """
    The robot will open the gripper at the next motion instruction
    (MOVE, APPRO, BREAK etc.)
    """
    RobotSim.open_flag = True
    RobotSim.close_flag = False
def CLOSE():
    """
    The robot will close the gripper at the next motion instruction
    (MOVE, APPRO, BREAK etc.)
    """
    RobotSim.open_flag = False
    RobotSim.close_flag = True
def BREAK(extra_delay=True):
    """
    Waits for the robot to finish the current motion.
    """

    if RobotSim.switch["DRY.RUN"]:
        return

    RobotSim.ActuateGripper()
    
    while len(RobotSim.trajQueue) > 0:
        time.sleep(0.01)
        if RobotSim.abort_flag:
            RobotSim.abort_flag = False
            raise UserAbort
        if not RobotSim.comp_mode:
            raise CompModeDisabled
    time.sleep(0.1)
    
    
def OPENI():
    """
    Waits for the current robot motion to finish, 
    then OPENs the gripper immediately, 
    then waits for (PARAMETER HAND.TIME) seconds.
    """

    if RobotSim.switch["DRY.RUN"]:
        return

    BREAK(False)
    OPEN()
    BREAK(False)
    if not RobotSim.switch["DRY.RUN"]:
        time.sleep(RobotSim.param["HAND.TIME"])
    
def CLOSEI():
    """
    Waits for the current robot motion to finish, 
    then CLOSEs the gripper immediately, 
    then waits for (PARAMETER HAND.TIME) seconds.
    """

    if RobotSim.switch["DRY.RUN"]:
        return

    BREAK()
    CLOSE()
    BREAK(False)
    time.sleep(RobotSim.param["HAND.TIME"])
    

def HERE():
    """
    Returns the current location of the robot.
    
    Examples:
    
    Using HERE as monitor command:
    .here a       ; "a" will contain the current robot location, as a transformation (TRANS)
    .here #safe   ; "#safe" will contain the current robot location, as a precision point (PPOINT)
    .here bs:b    ; "b" will contain the current robot location, as a TRANS, 
                  ; relative to the "bs" reference frame. In contrast, "a" is relative to "World" frame.
    
    Using HERE in a V+ program:
    
    HERE a        ; as a statement; useful for recording the robot trajectory
    
    
    IF DISTANCE(HERE, DEST) > 10  ; as a function
        WAIT
    END
    """
    return RobotSim.DK(RobotSim.currentJointPos)
def DEST():
    """
    Returns the current destination of the robot, as a transformation variable.
    This is usually the argument of the last motion instruction.
    
    Example:
    .do move trans(200,300,100,0,180,0)  ; start a robot motion
    .do print dest                       ; print its destination (while the robot is moving)
    
    """
    return RobotSim.DK(RobotSim.destJointPos)

def PHERE():
    """
    Returns the current robot position as a precision point. 
    It is used in V+ programs as a function.
    
    See also: HERE
    """
    return PPOINT(RobotSim.currentJointPos)
def PDEST():
    """
    Returns the current robot destination as a precision point.     
    
    See also: DEST
    """
    return PPOINT(RobotSim.destJointPos)

    
def SET(a):
    """
    PROGRAM INSTRUCTION
    Sets the value of a transformation or a precision point.
    
    Usage:
    
    At monitor console (using "do"):
    .do set a = shift(b by 1,2,3)
    
    In V+ program:
    SET pick = SHIFT(st BY 0, 0, 100)
    
    """
    check_args(a, location)
    return a

def _convert_to_trans(a):
    if a.__class__.__name__ == 'TRANS':
        return a
    elif a.__class__.__name__ == 'PPOINT':
        return RobotSim.DK(a)
    else:
        raise SyntaxError, "Expected argument type: TRANS or PPOINT'"
        
def _convert_to_ppoint(a):
    if a.__class__.__name__ == 'TRANS':
        return RobotSim.IK(a)
    elif a.__class__.__name__ == 'PPOINT':
        return a
    else:
        raise SyntaxError, "Expected argument type: TRANS or PPOINT'"
    
    

def _MOVE_START():
    """
    Actiuni care se fac imediat inainte de generarea traiectoriei
    (parte comuna si la MOVE si la MOVES)
    """
    RobotSim.ActuateGripper() 

def _MOVE_END():
    """
    Actiuni care se fac imediat dupa generarea traiectoriei
    (parte comuna si la MOVE si la MOVES)
    """
    # pentru urmatoarea miscare, revenim la viteza always 
    RobotSim.speed_next_motion = RobotSim.speed_always
    RobotSim.speed_next_motion_unit = RobotSim.speed_always_unit

    if not RobotSim.switch["CP"]:
        BREAK()
    

def MOVE(a):
    """
    Starts a joint interpolated motion towards "a".
    a is a robot location (TRANS or PPOINT)
    
    The function returns immediatly after the trajectory is generated.
    
    Use BREAK for forcing the program to wait for the current motion to finish.
    
    Two or more succesive MOVE calls perform procedural motion (not implemented yet).
    
    """
    check_args(a, location)
    _MOVE_START()
    RobotSim.jtraj(_convert_to_ppoint(a))
    _MOVE_END()
  
def MOVES(a):
    """
    Starts a straight line motion towards "a".
    a is a robot location (TRANS or PPOINT)
    
    The function returns immediatly after the trajectory is generated.
    
    Use BREAK for forcing the program to wait for the current motion to finish.
    
    Two or more succesive MOVES calls perform procedural motion (not implemented yet).
    
    """
    check_args(a, location)

    _MOVE_START()
    RobotSim.ctraj(_convert_to_ppoint(a))
    _MOVE_END()

    # pentru urmatoarea miscare, revenim la viteza always 
    RobotSim.speed_next_motion = RobotSim.speed_always
    RobotSim.speed_next_motion_unit = RobotSim.speed_always_unit

    if not RobotSim.switch["CP"]:
        BREAK()

def MOVET(a, grip):
    """
    PROGRAM INSTRUCTION
    
    MOVET a, grip
    is a shortcut for:
    Shortcut for:
    
        OPEN           ; when grip = TRUE
        MOVE(a)
    
    and 

        CLOSE          ; when grip = FALSE
        MOVE(a)
    
    """
    check_args([a, grip], [location, numeric])

    if grip:
        OPEN
    else:
        CLOSE
    MOVE(a)
    
def MOVEST(a, grip):
    """
    PROGRAM INSTRUCTION
    
    MOVEST a, grip
    is a shortcut for:
    
        OPEN           ; when grip = TRUE
        MOVES(a)
    
    and 

        CLOSE          ; when grip = FALSE
        MOVES(a)
    
    """
    check_args([a, grip], [location, numeric])

    if grip:
        OPEN
    else:
        CLOSE
    MOVES(a)
    
def APPRO(a, h):
    """
    PROGRAM INSTRUCTION
    
    APPRO a, h
    Moves the robot "behind" 'a' at a distance 'h', 
    using a joint interpolated motion (similar to MOVE).
    
    'a' is a robot location (TRANS or PPOINT)
    
    "Behind" means in the negative direction of a's Z axis.
    
    If 'a' is PPOINT, it is converted to a TRANS using DK in order to determine its Z axis.
    
    Equivalent to:
    MOVE a:TRANS(0,0,-h)
    
    """
    check_args([a, h], [location, numeric])
    a = _convert_to_trans(a)
    MOVE(a * TRANS(0, 0, -h))
    
def DEPART(h):
    """
    PROGRAM INSTRUCTION
    
    DEPART h
    Moves the robot "backwards" from the current position, at a distance 'h',
    using a joint interpolated motion (similar to MOVE).
    
    
    'a' is a robot location (TRANS or PPOINT)
    
    "Backwards" means in the negative direction of the Z axis of DEST.
    If robot is not moving, DEST is identical to HERE.
    
    Equivalent to:
    MOVE DEST:TRANS(0,0,-h)
    
    """
    check_args(h, numeric)
    MOVE(DEST() * TRANS(0, 0, -h))
def APPROS(a, h):
    """
    Similar to APPRO, but uses a straight line trajectory.
    """
    check_args([a, h], [location, numeric])
    a = _convert_to_trans(a)
    MOVES(a * TRANS(0, 0, -h))
def DEPARTS(h):
    """
    Similar to DEPART, but uses a straight line trajectory.
    """
    check_args(h, numeric)
    MOVES(DEST() * TRANS(0, 0, -h))

def PARAMETER(param_name, value = None):
    """
    PROGRAM INSTRUCTION and MONITOR COMMAND
    
    Sets a V+ parameter.
    
    Usage as monitor command:
    .parameter hand.time = 100
    .parameter
    
    Usage as program instruction:
    
    PARAMETER HAND.TIME = 100
    """
    
    if value == None:
        check_args([param_name], ["str"])
        param_name = param_name.replace("_", ".")
        return RobotSim.param[param_name.upper()]
    else:
        check_args([param_name, value], ["str", numeric])
        param_name = param_name.replace("_", ".")
        RobotSim.param[param_name.upper()] = value

def TOOL(t = None):
    """
    Sets the tool transformation.
    """
    check_args(t, ["TRANS", "NoneType"])
    if t != None:
        RobotSim.tool_trans = t
    return RobotSim.tool_trans



def ALIGN():
    a = HERE()
    yr = round(a.yaw / 90) * 90
    pr = round(a.pitch / 90) * 90
    b = TRANS(a.x, a.y, a.z, yr, pr, a.roll)
    MOVES(b)


def BRAKE():
    del(RobotSim.trajQueue[:])


def ABORT(arg = None):    
    _CM_ABORT(None, arg)

def _valid_signal(x, inp = False, out = False, soft = False):
    if out and 0 < x and x <= 512:
        return True
    if inp and 1000 < x and x <= 1512:
        return True
    if soft and 2000 < x and x <= 2512:
        return True
    raise Exception, "Invalid signal address: %d" % x


def SIGNAL(*X):
    """

    Sets or resets one or more digital signals (output or software).
    
    Output signals:      1 ... 512
    Software signals: 2001 ... 2512
    
    Negative logic is achieved by changing the sign of the address:

    SIGNAL 5              # sets the digital i/o line 5 to TRUE
    SIGNAL -5             # resets line 5 (to FALSE)
    SIGNAL 1,2,-3         # sets 1 and 2, resets 3

    """
    check_args(list(X), "int")
    for x in X:
        _valid_signal(abs(x), False, True, True)
        RobotSim.signals[abs(x)] = (x > 0)
        RobotSim.signals_dirty = True


def _SET_INP_SIGNAL(*X):
    check_args(list(X), "int")
    for x in X:
        _valid_signal(abs(x), True, False, False)
        RobotSim.signals[abs(x)] = (x > 0)
        RobotSim.signals_dirty = True
        
def SIG(*X):
    """

    Reads the state of a digital signal.
    
    Input signals:    1001 ... 1512
    Output signals:      1 ... 512
    Software signals: 2001 ... 2512
    
    Negative logic is achieved by changing the sign of the address:
    
    SIG(1001)      returns -1 if digital i/o line 1001 is TRUE
    SIG(-1001)     returns 0
    
    SIG(1001, -1002, 1003)  <=> SIG(1001) AND SIG(-1002) AND SIG(-1003)

    """
    check_args(list(X), "int")
    bigval = True
    for x in X:
        _valid_signal(abs(x), True, True, True)

        addr = abs(x)
        if not (addr in RobotSim.signals): 
            RobotSim.signals[addr] = False
            RobotSim.signals_dirty = True
        
        val = RobotSim.signals[addr]
        if x < 0:
            val = not val
        bigval = bigval and val
    
    return (-1 if bigval else 0)
        
def TIMER(x, value = None):
    x = int(eval(str(x)))
    if not (x in RobotSim.timers):
        raise Exception, "Timer " + str(x) + " does not exist. Only timers from -3 to 15 are valid."
    
    if value == None:
        return RobotSim.clock - RobotSim.timers[x]
    else:
        RobotSim.timers[x] = RobotSim.clock - value

def WAIT_EVENT(unused, delay):
    t0 = RobotSim.clock
    while RobotSim.clock < t0 + delay:
        time.sleep(0.01)
        if RobotSim.abort_flag:
            RobotSim.abort_flag = False
            raise UserAbort
        if not RobotSim.comp_mode:
            raise CompModeDisabled


safe = PPOINT(0,-90,180,0,0,0)


def LAST(x):
    """
    Last index used (not None) in a 1-D array (list).
    """
    check_args([x], 'list')
    for i in range(len(x)-1, 0, -1):
        if x[i] != None:
            return i
    return -1

def ASC(str, i=1):
    check_args([str,i], ["str", numeric])
    i = int(i)
    return str[max(0, i-1)]

def VAL(str):
    check_args([str], ["str"])
    return eval(str)

def BMASK(*bits):
    check_args(list(bits), [numeric])
    val = 0
    for b in bits:
        val = val | (1 << (int(b)-1))
    return val


# comenzi monitor
############################################

import IPython.ipapi

class UserAbort(Exception):
    pass

class CompModeDisabled(Exception):
    pass


from IPython import ColorANSI
tc = ColorANSI.TermColors()
Term = None

_code_tracing_cache = {}
_color_dic = {}
_dic_locals = {}
_dic_globals = {}
_spaces_last_line = ""
def init_trace():
    global _code_tracing_cache, _color_dic, _dic_locals, _dic_globals, _spaces_last_line
    _code_tracing_cache = {}
    _color_dic = {"<module>": tc.LightGray}
    _dic_locals = {}
    _dic_globals = {}
    _spaces_last_line = ""
    
def get_color(func):
    colors = [tc.LightGray, tc.Normal, tc.Green, tc.Blue, tc.Red, tc.Brown, tc.Purple]
    if func in _color_dic:
        return _color_dic[func]
    else:
        _color_dic[func] = colors[len(_color_dic) % len(colors)]
        return _color_dic[func]
        
def str_compact(val):
    s = str(val)
    while "  " in s:
        s = s.replace("  ", " ")
    return s
def print_new_vars(func, newvars, flags):

    if flags == 'global':
        globstr = "global "
    else:
        globstr = ""

    newvars.sort()
    
    for name, val in newvars:
        if (type(val).__name__ == 'instance') and (val.__class__.__name__ == 'TRANS'):
            print "%s%snew %svariable: %s%s = %s%s" % (_spaces_last_line, tc.LightGray, globstr, get_color(func), name, str_compact(val), tc.Normal)
            
    for name, val in newvars:
        if (type(val).__name__ == 'instance') and (val.__class__.__name__ == 'PPOINT'):
            print "%s%snew %svariable: %s%s = %s%s" % (_spaces_last_line, tc.LightGray, globstr, get_color(func), name, str_compact(val), tc.Normal)

    for name, val in newvars:
        if type(val).__name__ == 'list':
            print "%s%snew %sarray: %s%s = %s%s" % (_spaces_last_line, tc.LightGray, globstr, get_color(func), name, str_compact(val), tc.Normal)
    
    smallchanges = []
    for name, val in newvars:
        if (type(val).__name__ != 'instance') or not(val.__class__.__name__ in ['TRANS', 'PPOINT']):
            if not (type(val).__name__  in ['list', 'function', 'classobj', 'module']):
                smallchanges.append("%s%s = %s" % (get_color(func), name, str(val)))
                
    if len(smallchanges):
        print _spaces_last_line + tc.LightGray + "new " + globstr + "variables: " + string.join(smallchanges, ", ") + tc.Normal
    
def print_changed_vars(func, changedvars, flags):
    
    if flags == 'global':
        globstr = "global "
    else:
        globstr = ""
        
    changedvars.sort()
    
    for name, old_val, new_val in changedvars:
        if (type(new_val).__name__ == 'instance') and (new_val.__class__.__name__ == 'TRANS'):
            print "%s%s%s%s changed to: %s\n%s%s(previous value: %s)%s" % (_spaces_last_line, get_color(func), globstr, name, str_compact(new_val), _spaces_last_line, tc.LightGray, str_compact(old_val), tc.Normal)
            
    for name, old_val, new_val in changedvars:
        if (type(new_val).__name__ == 'instance') and (new_val.__class__.__name__ == 'PPOINT'):
            print "%s%s%s%s changed to: %s\n%s%s(previous value: %s)%s" % (_spaces_last_line, get_color(func), globstr, name, str_compact(new_val), _spaces_last_line, tc.LightGray, str_compact(old_val), tc.Normal)

    
    smallchanges = []
    for name, old_val, new_val in changedvars:
        if (type(new_val).__name__ != 'instance') or not(new_val.__class__.__name__ in ['TRANS', 'PPOINT']):
            smallchanges.append("%s%s = %s %s(was %s)" % (get_color(func), name, str(new_val), tc.LightGray, str(old_val)))
    
    if len(smallchanges):
        if len(globstr) > 0:
            print _spaces_last_line + tc.LightGray + "global%s changed: " % ("s" if len(smallchanges) != 1 else "") + string.join(smallchanges, ", ") + tc.Normal
        else:
            print _spaces_last_line + tc.LightGray + "changed: " + string.join(smallchanges, ", ") + tc.Normal

def make_list_of_new_and_changed_variables(func, dic, prev_dic):
    global _dic_locals, _dic_globals
    
    newvars = []
    changedvars = []
    
        
    for v in dic:
        if v[0] != "_":
            if v[0].lower() == v[0]:
                if not (v in prev_dic):
                    newvars.append((v, dic[v]))
                elif (type(dic[v]).__name__ == 'list') and (type(prev_dic[v]).__name__ == 'list'):
                    for i, vl in enumerate(dic[v]):
                        if not (prev_dic[v][i] == vl):
                            changedvars.append(("%s[%d]" % (v,i), prev_dic[v][i], vl))
                elif not(prev_dic[v] == dic[v]):
                    changedvars.append((v, prev_dic[v], dic[v]))
        
    return (newvars, changedvars)
    
def print_new_and_changed_variables(func, locals, globals):
    global _dic_locals, _dic_globals
    

    prev_locals = {}
    if func in _dic_locals:
        prev_locals = _dic_locals[func]
    
    prev_globals = _dic_globals
    
    (newvars, changedvars) = make_list_of_new_and_changed_variables(func, locals, prev_locals)    
    print_new_vars(func, newvars, 'local')
    print_changed_vars(func, changedvars, 'local')
    
    
    (newvars, changedvars) = make_list_of_new_and_changed_variables(func, globals, prev_globals)    
    print_new_vars(func, newvars, 'global')
    print_changed_vars(func, changedvars, 'global')

    
    localscopy = locals.copy()
    for k,v in localscopy.iteritems():
        if type(v).__name__ == 'list':
            localscopy[k] = copy(v)
    _dic_locals[func] = localscopy
    
    globalscopy = globals.copy()
    for k,v in globalscopy.iteritems():
        if type(v).__name__ == 'list':
            globalscopy[k] = copy(v)
    _dic_globals = globalscopy
    

def print_code_line(frame):
    co = frame.f_code
    lineno = frame.f_lineno
    slineno = str(lineno).ljust(3)
    file = co.co_filename
    func = co.co_name
    global _spaces_last_line    
    try:
        if not (file in _code_tracing_cache):
            f = open(file)
            code = f.readlines()
            _code_tracing_cache[file] = code
            f.close()
        line = _code_tracing_cache[file][lineno-1]
        line = line.strip("\n")
        print "%s%s[%s]:%s %s%s" % (get_color(func), file, func, slineno, line, tc.Normal)
        _spaces_last_line = " " * (len(re.match("(\ *)", line).groups()[0]) + len(file) + len(func) + len(slineno) + 4)
    except:
        slineno = str(lineno).ljust(3)
        print "%s%s[%s]:%s <%s:%s>%s" % (get_color(func), file, func, slineno, sys.exc_type.__name__, sys.exc_value, tc.Normal)
        _spaces_last_line = " " * (len(file) + len(func) + len(slineno) + 4)
    



def print_return(frame):
    
    co = frame.f_code
    func = co.co_name
    caller = frame.f_back
    caller_func = caller.f_code.co_name
    
    if caller_func in ["<module>", "EXECUTE"]:
        return
    
    
    print "%s%sReturning to '%s'%s" % (get_color(func), _spaces_last_line, caller_func, tc.Normal)

    
def trace_calls(frame, event, arg):
    if RobotSim.abort_flag:
        RobotSim.abort_flag = False
        raise UserAbort
    if not RobotSim.comp_mode:
        raise CompModeDisabled

    if event == 'return':
        co = frame.f_code
        line_no = frame.f_lineno
        filename = co.co_filename
        func_name = co.co_name
        #~ print filename + ":%d" % (line_no)
        if RobotSim.switch["TRACE"]:
            print_return(frame)
            print_new_and_changed_variables(func_name, frame.f_locals, frame.f_globals)
        return

    if event == 'line':
        func_name = frame.f_code.co_name
        if RobotSim.switch["TRACE"]:
            print_new_and_changed_variables(func_name, frame.f_locals, frame.f_globals)
            print_code_line(frame)
        return trace_calls

    if event == 'call':
            
        co = frame.f_code
        func_name = co.co_name
        func_line_no = frame.f_lineno
        func_filename = co.co_filename
        if func_filename.lower().endswith(".v2"):
            if RobotSim.switch["TRACE"]:
                if func_name != "<module>":
                    print_code_line(frame)
            return trace_calls
        

        #~ caller = frame.f_back
        #~ caller_line_no = caller.f_lineno
        #~ caller_filename = caller.f_code.co_filename
        #~ 
        #~ if caller_filename.lower().endswith(".v2"):
            #~ print 'Call to %s on line %s of %s from line %s of %s' % \
                #~ (func_name, func_line_no, func_filename,
                 #~ caller_line_no, caller_filename)
    return




def consoleprompt(self, cont):
    
    try:
        busy = _some_jobs_running()
    except:
        return "<" + sys.exc_info()[:2] + ">"
        
    if cont:
        return "<continue previous line>... "
    
    global prevbusy
    if busy:
        if prevbusy:
            prompt = "* "
        else:
            prompt = ""     # imediat dupa exec nu afisez promptul
    else:
        prompt = ". "
    
    prevbusy = busy
    
    return prompt
    
def exec_init():
    init_trace()
    sys.stdout.flush()
    sys.stdout = sys.ipy_stdout
    sys.settrace(trace_calls)    
    time.sleep(0.2)
    print 
    
def exec_end():
    print
    print "Program completed."
    print "Press ENTER to continue "
    print 
    sys.settrace(None)
    sys.stdout.flush()
    sys.stdout = sys.sys_stdout
    # daca nu dau ENTER, ramane consola "ametita"


    #~ _ip = IPython.ipapi.get()
    #~ _ip.runlines("Quit")
    


def completers_setup():
    ip = IPython.ipapi.get()
    ip.set_hook('complete_command', load_completers, str_key = 'load')
    ip.set_hook('complete_command', env_completers, str_key = 'env')
    ip.set_hook('complete_command', exec_completers, str_key = 'exec')
    ip.set_hook('complete_command', param_completers, str_key = 'param')
    ip.set_hook('complete_command', param_completers, str_key = 'parameter')
    ip.set_hook('complete_command', switch_completers, str_key = 'switch')
    ip.set_hook('complete_command', switch_completers, str_key = 'enable')
    ip.set_hook('complete_command', switch_completers, str_key = 'disable')
    ip.set_hook('complete_command', switch_completers, str_key = 'en')
    ip.set_hook('complete_command', switch_completers, str_key = 'dis')
    ip.set_hook('complete_command', see_completers, str_key = 'see')
    


def see_completers(self, event):
    ex = exec_completers(self, event)
    if '<no robot programs loaded>' in ex:
        ex = []
    lo = load_completers(self, event)
    lox = []
    for l in lo:
        lox.append(l + ".v2")
    en = env_completers(self, event)
    enx = []
    for e in en:
        enx.append(e + ".env")
    return ex + lox + enx
    
def load_completers(self, event):
    progfiles = []
    files = os.listdir(".")
    for f in files:
        if f.lower().endswith(".v2"):
            progfiles.append(f[:-3])
    progfiles.sort()
    return progfiles

def env_completers(self, event):
    progfiles = []
    files = os.listdir(".")
    for f in files:
        if f.lower().endswith(".env"):
            progfiles.append(f[:-4])
    progfiles.sort()
    return progfiles

def exec_completers(self, event):    
    programe = programDict.keys()
    programe.sort()
    if len(programe) == 0:
        return ["<no robot programs loaded>", "..."]
    return programe
    
def param_completers(self, event):
    e = RobotSim.param.keys()
    e.sort()
    return e

def switch_completers(self, event):
    e = RobotSim.switch.keys()
    e.sort()
    return e


def EXECUTE(prog):
    """
    Executes a robot program.
    """
    
    (func, args, args_ref) = parse_function_call(prog)
    if func in programDict:

        # auto-reload
        _LOAD(programDict[func][1], True)

        exec_init()
        try:
            _build_dictionary()
            if RobotSim.debug:
                _list_dictionary()
            
            loader_code = "CALL['%s'](%s)" % (func, args)
            loader = compile(loader_code, "<exec loader>", "exec")
            loc = {}
            
            exec(loader) in globalVplusNames
        except UserAbort:
            print "Robot program aborted by user."
        except CompModeDisabled:
            print "COMP mode disabled."
        except:
            raise
        finally:
            exec_end()
    else:
        print "Program '%s' not loaded." % func
        
        
def _some_jobs_running():
    for i,j in jobs.jobs_all.iteritems():
        if j.stat_code == j.stat_running_c:
            return True
    return False


def _flush_completed_jobs():
    toFlush = []
    for i,j in jobs.jobs_all.iteritems():
        if j.stat_code != j.stat_running_c:
            toFlush.append(i)
            if j in jobs.jobs_run:
                jobs.jobs_run.remove(j)
            if j in jobs.jobs_comp:
                jobs.jobs_comp.remove(j)
            if j in jobs.jobs_dead:
                jobs.jobs_dead.remove(j)
    for i in toFlush:
        del jobs.jobs_all[i]
    
def _CM_ABORT(self, arg):
    """
    Aborts a robot program.
    You may type "abort" while a robot program is running.
    """

    _flush_completed_jobs()
    if len(jobs.jobs_all) > 0:
        print "Aborting robot program..."
        RobotSim.abort_flag = True
    else:
        print "No robot program is running."
        RobotSim.abort_flag = False



def _CM_DIR(self, arg):
    programe = programDict.keys()
    programe.sort()

    print "Loaded programs:"
    print "================"
    for v in programe:
        args = programDict[v][0]
        file = programDict[v][1]
        lineno = programDict[v][2]
        slineno = str(lineno).ljust(3)
        if len(args) > 0:
            print "%15s : %s  =>  .PROGRAM %s(%s)" % (file, slineno, v, args)
        else:
            print "%15s : %s  =>  .PROGRAM %s" % (file, slineno, v)

def _LOAD(file, reload=False):
    ip = IPython.ipapi.get()

    file = file.strip()
    if len(file) == 0:
        print "Robot programs in current directory:"
        for e in load_completers(None, None):
            print "  * ", e
        return

    if not re.match("^.*\.[^.]*$", file): # fara extensie, ii adaug .v2
        file = file + ".v2" 
    
    if not reload:
        print "Loading %s ..." % file
    else:
        print "Reloading %s ..." % file
    code = translate_program(file)
    
    file_timestamps[file] = os.path.getmtime(file)
    code = compile(code, file, "exec")

    _build_dictionary()
    loc = {}
    exec(code) in globalVplusNames, loc

    # programele din fisierul incarcat apar in loc

    locale = loc.keys()
    locale.sort()
    
    for v in locale:
        if type(loc[v]).__name__ == 'function':
            vplus_name = programMangleP2V[v]
            args = programDict[vplus_name][0]
            programDict[vplus_name][3] = loc[v]
            
            if not reload:
                if len(args) > 0:
                    print "   .PROGRAM %s(%s)" % (vplus_name, args)
                else:
                    print "   .PROGRAM %s" % vplus_name


def _CM_LOAD(self, file):
    """
        
    Monitor command for loading a file containing robot programs.

    Example:

    load hanoi
    """

    if not check_no_prog_running(): return
    

    _LOAD(file.strip())



def _CM_EXEC(self, prog):
    """
        
    Monitor command for executing a robot program.

    Example:

    exec stiva
    """

    if not check_no_prog_running(): return

    ip = IPython.ipapi.get()

    if not RobotSim.comp_mode:
        print "COMP mode disabled."
        return

    _build_dictionary() 
    if RobotSim.debug:
        _list_dictionary()

    ip.runlines("%%bg _ip.runlines(\"EXECUTE('%s')\")" % prog.strip())


def _CM_HERE(self, var):
    """
        
    Monitor command for teaching robot locations.

    Examples:

    here a       # records current end-effector position as a transformation 
    here #b      # records current joint position as a precision point
    here bs:a    # records end-effector position in the local reference frame "bs"
    """

    if not check_no_prog_running(): return
    
    ip = IPython.ipapi.get()
    
    if len(var.strip()) == 0:
        ip.runlines("HERE()")
        return
        
    var = var.lower()
    var = var.replace(".", "_")
    
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
        (.*)                  # base (expression)
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
        cmd = var + " = INVERSE(" + translate_expression(bs) + ") * HERE()"
    else:
        print "here (monitor command): syntax error"
        return

    if RobotSim.debug:
        print "(debug) " + cmd    
    ip.runlines(cmd + "\r\n" \
        + var)


    
    
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
    if not check_no_prog_running(): return
    ip = IPython.ipapi.get()
    ip.runlines("TOOL(" + translate_expression(var) + ")")


    
def _CM_PARAM(self, var):
    """

    Set a parameter.

    Example:

    parameter hand.time = 0.5

    """
    if len(var) == 0:
        print RobotSim.param
    else:
        (name, value) = split_at_equal_sign(var)
        RobotSim.param[name.upper().strip()] = eval(value)
        

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


file_timestamps = {}
def fileChangePoll():
    d = os.listdir(".")
    for f in d:
        if f.endswith(".v2"):
            if f in file_timestamps:
                t = file_timestamps[f]
                t2 = os.path.getmtime(f)
                if t != t2:
                    file_timestamps[f] = t2
                    print "File %s was changed." % f
                    beautify_program(f)
                    file_timestamps[f] = os.path.getmtime(f)
            else:
                file_timestamps[f] = os.path.getmtime(f)

def _edit(file, lineno = None):
    if sys.platform == 'win32':
        if lineno and ('notepad2.exe' in _editor.lower()):
            subprocess.Popen("%s /g %d %s" % (_editor, lineno, file))
        else:
            subprocess.Popen("%s %s" % (_editor, file))
    else:
        subprocess.Popen([_editor, file])


vplus_program_template = """.PROGRAM %s()     
    
    ; Author: <put your name here>
    
    ; What does this program do?
    
    GLOBAL a,b,c           ; Declare global variables here
    AUTO x,y,z             ; Declare local variables here

    ; Write your program here    
    


.END

"""
def _CM_SEE(self, prog):
    """

    Edits a robot program or a text file.

    Example:
    
    see hanoi         ; edits program "hanoi" (it should be loaded first)
    see hanoi.v2      ; edits file hanoi.v2
    see hanoi.env     ; edits file hanoi.env
    

    Editor is vplus._editor 
    
    At startup, vplus._editor is assigned to the first program 
    found from the following list:
    
    Windows editors: notepad2 (included) or notepad.
    Linux editors: gedit, kwrite, vim, vi
    
    
    """
    
    if len(prog.strip()) == 0:
        _CM_DIR(None, None)
        return
        
    # mai intai vad daca e incarcat in memorie
    if prog in programDict:
        (file, lineno) = programDict[prog][1:3]
        print "editing .PROGRAM %s() from file '%s:%d' ..." % (prog, file, lineno)
        _edit(file, lineno)
    elif re.match("^.*\.[^.]{1,3}$", prog): # ceva cu extensie => probabil e un fisier
        if os.path.isfile(prog):
            print "editing file '%s' ..." % prog
            _edit(prog)
        else:  # new file
            progname = prog[:-3].lower()
            print 
            ans = raw_input("Create new file '%s'? [y/n] " % prog)
            if ans.lower() == 'y':
                if prog.lower().endswith('.v2'):
                    template = vplus_program_template % progname
                    f = open(prog, "w")
                    f.write(template)
                    f.close()
                    
                _edit(prog)
            elif (ans.lower() == 'n') or (ans == ""):
                pass
            else:
                print "I guess your answer was 'no'."
    else:
        print "Program '%s' not loaded." % prog
        print
        print "To edit program '%s', first load it from a file." % prog
        print
        print "To create or edit a file, please specify its full name and extension."
        if os.path.isfile("%s.v2" % prog):
            print "e.g. 'see %s.v2' for editing the file '%s.v2'." % (prog, prog)
        else:
            print "e.g. 'see %s.v2' for creating a new file named '%s.v2'." % (prog, prog)

def _CM_SPEED(self, var):
    """
    MONITOR COMMAND
    
    Set monitor speed.

    Example:

    speed 100

    Tip: you may change the monitor speed while a robot program is running.
    
    There is also the program instruction SPEED, whose effect is not the same!
    """
    spd = eval('int(%s)' % var)
    print "Setting monitor speed to %d" % spd
    SPEED(spd, "MONITOR")

def _list_dictionary():
    dic = globalVplusNames
    K = dic.keys()
    K.sort()
    for k in K:
        if k.lower() == k:
            print k,
    print ""


globalVplusNames = {}


def callDict():
    d = {}
    for p in programDict:
        d[p] = programDict[p][3]
    return d

def _build_dictionary():
    code = """
_k = 0
_v = 0
_K = list(set(locals().keys() + globals().keys()))
_K.sort()
_vars = []

for _k in _K:
    if _k[0] != '_': 
        _v = eval(_k)
        if type(_v).__name__ == 'instance':
            if _v.__class__.__name__ in ['TRANS', 'PPOINT']:
                _vars.append(_k)
        elif type(_v).__name__ in ['str', 'int', 'float']:
            if _k.lower() == _k:
                _vars.append(_k)

for _k in _vars:
    globalVplusNames[_k] = eval(_k)

for _k in vplus.__dict__.keys():
    if _k[0] != '_': 
        if _k.upper() == _k:
            globalVplusNames[_k] = eval(_k)

globalVplusNames["CALL"] = callDict()
"""
    
    ip = IPython.ipapi.get()
    ip.runlines(code)


def _CM_RESET(self, var):
    """
    MONITOR COMMAND
    
    Resets I/O signals.
    """
    if not check_no_prog_running(): return

    print "Turning off signals..."

    RobotSim.signals = {}
    RobotSim.signals_dirty = True

    
def _CM_ZERO(self, var):
    """
    MONITOR COMMAND
    
    Deletes all robot programs and variables.
    """
    if not check_no_prog_running(): return

    print "Deleting all robot programs and variables..."
    
    _build_dictionary()
    names = globalVplusNames.keys()
    ip = IPython.ipapi.get()

    TOOL(NULL)
    
    for var in names:
        if var[0] != "_" and var.lower() == var:
            value = globalVplusNames[var]
            if type(value).__name__ == 'instance':
                if value.__class__.__name__ in ['TRANS', 'PPOINT']:
                    ip.runlines("try: del " + var + "\nexcept: pass")
            if type(value).__name__ in ['int', 'float', 'str', 'list']:
                ip.runlines("try: del " + var + "\nexcept: pass")
    
    globalVplusNames.clear()
    programDict.clear()
    programMangleP2V.clear()
    programMangleV2P.clear()
    
    _CM_RESET(None, None)
    
    _build_dictionary()
    
def _CM_LISTL(self, var):
    """

    Lists location variables (TRANS and PPOINT).
    """
    
    if len(var) > 0:
        ip = IPython.ipapi.get()
        var = translate_expression(var)
        ip.runlines("pprint([" + var + "])")
        return

    _build_dictionary()
    names = globalVplusNames.keys()
    names.sort()

    print "Location variables:"
    print "==================="
    print ""
    print "Transformations:"
    print
    for var in names:
        if var[0] != "_" and var.lower() == var:
            value = globalVplusNames[var]
            if type(value).__name__ == 'instance':
                if value.__class__.__name__ == 'TRANS':
                    print "%10s = " % var, value
    print
    print "Precision points:"
    print
    for var in names:
        if var[0] != "_" and var.lower() == var:
            value = globalVplusNames[var]
            if type(value).__name__ == 'instance':
                if value.__class__.__name__ == 'PPOINT':
                        print "%10s =" % ("#" + var), value
    print ""
    print "Tool transformation:"
    print "             ", TOOL()

def _CM_LISTR(self, var):
    """

    Lists real and integer variables.
    """

    if len(var) > 0:
        ip = IPython.ipapi.get()
        var = translate_expression(var)
        ip.runlines("pprint.pprint([" + var + "])")
        return

    _build_dictionary()
    names = globalVplusNames.keys()
    names.sort()

    print "Real and integer variables:"
    print "==========================="
    print ""
    print "Reals:"
    print
    for var in names:
        if var[0] != "_" and var.lower() == var:
            value = globalVplusNames[var]
            if type(value).__name__ == 'float':
                    print "%10s = " % var, value
    print
    print "Integers:"
    print
    for var in names:
        if var[0] != "_" and var.lower() == var:
            value = globalVplusNames[var]
            if type(value).__name__ == 'int':
                    print "%10s = " % var, value
            
def _CM_LISTS(self, var):
    """

    Lists string variables.
    """

    if len(var) > 0:
        ip = IPython.ipapi.get()
        var = translate_expression(var)
        ip.runlines("pprint.pprint([" + var + "])")
        return

    _build_dictionary()
    names = globalVplusNames.keys()
    names.sort()

    print "String variables:"
    print "================="
    print ""
    for var in names:
        if var[0] != "_" and var.lower() == var:
            value = globalVplusNames[var]
            if type(value).__name__ == 'str':
                    print "%10s = " % var, value



def check_no_prog_running(): 
    _flush_completed_jobs()
    if len(jobs.jobs_all) > 0:
        print "A robot program is already running."
        print "Please stop the program first."
        print "  (hint: you may use either the 'COMP' button or the 'abort' command)."
        print 
        return False
    return True
        

def _CM_ENV(self, prog):
    """

    Initializes the work environment for the robot.
    """
    if not check_no_prog_running(): return
    
    ip = IPython.ipapi.get()
    prog = prog.strip()

    if len(prog)==0:
        print "Available environments:"
        for e in env_completers(None, None):
            print "  * ", e
        return
    
        
    if not re.match("^.*\.env$", prog):
        prog = prog + ".env" 
    
        
    (func, args, args_ref) = parse_function_call(prog[:-4])
    prog = func + ".env"
    
    print args

    print "setting work environment (%s)..." % prog
    print " "

    RobotSim.pauseTick = True
    try:
        time.sleep(0.2)
        ip.runlines("_env_args = [" + args + "]")
        ip.runlines("resetEnv()")
        ip.runlines("execfile('%s')" % prog)
    finally:
        RobotSim.pauseTick = False
    
    time.sleep(0.2)
    print 
    
def _CM_DO(self, var):
    if not check_no_prog_running(): return
    if not RobotSim.comp_mode:
        print "COMP mode disabled."
        return

    var = translate_line(var)
    
    if RobotSim.debug:
        print "(debug) " + var
    
    ip = IPython.ipapi.get()
    ip.runlines(var)


def _CM_SIGNAL(self, var):

    var = translate_line(var)
    
    if RobotSim.debug:
        print "(debug) " + var
    
    ip = IPython.ipapi.get()
    ip.runlines("SIGNAL(%s)" % var)
    

def _CM_MC(self, var):
    """

    Displays a list of supported monitor commands.

    """
    print """
Monitor commands:
=================
env            # load an environment
load           # load a file with robot program(s)
see            # edit a robot program or a text file
exec           # execute a robot program

here           # teach a robot location
do             # execute a robot program instruction at the console
               # e.g. do departs 100
               
status         # display system status
speed          # set monitor speed
abort          # abort a robot program

enable         # enable a switch
disable        # disable a switch
switch         # list switches
parameter      # set a parameter

listl          # list location variables
listr          # list real and integer variables
lists          # list string variables
tool           # set the tool transformation

cd <folder>    # change directory
ls             # list files
%dir           # list programs loaded into memory
zero           # deletes robot programs and variables from memory
    
For more help, type a monitor command followed by '?'
e.g. here?
"""


