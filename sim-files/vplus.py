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

from numpy import matrix, mat
from math import pi
from geom import *
import math
import numpy
import time
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

TO = infix(lambda x,y: range(x,y+1))


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
        RobotSim.speed_monitor = spd
        return
        
    if flags & MMPS:
        unit = "MMPS"
    elif flags & IPS:
        unit = "IPS"
    else:
        unit = "%"
        
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


safe = PPOINT(0,-90,180,0,0,0)


import IPython.ipapi
def EXECUTE(prog):
    ip = IPython.ipapi.get()
    ip.ex("from vplus import *")
    ip.magic("%%bg _ip.magic('%%run -i ../robot-programs/%s.py')" % prog)
def EXEC(prog):
    EXECUTE(prog)
