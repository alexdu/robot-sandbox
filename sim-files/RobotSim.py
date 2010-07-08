
#       RobotSim.py
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

from __future__ import division
import math
import numpy
from numpy import matrix, mat
from vplus import *
from math import pi
from geom import *
import threading
import cgkit
import time
from pprint import pprint
import IPython

class IKError(Exception):
    pass


clock = 0
# incrementez la fiecare frame


currentJointPos = [0,-90,180,0,0,0]

lefty = True
above = True
flip = False
single = False


debug = 0



startJointPos = currentJointPos     # de unde am inceput miscarea
destJointPos = currentJointPos      # unde ma opresc
#intermedJointPos = currentJointPos  # punctul intermediar (pt MOVE-uri fara BREAK)
        
#interp_mode_straight_line = False
param = dict()
param["HAND.TIME"] = 0.5

switch = dict()
switch["POWER"] = True
switch["TRACE"] = False
switch["DRY.RUN"] = False
switch["GUI"] = True
switch["CP"] = True

timers = {}
def init_timers():
    global clock
    for i in range(-3, 16):
        timers[i] = clock
init_timers()

signals = {}
signals_dirty = True

global speed_monitor, speed_always, speed_next_motion
speed_monitor = 25.0
speed_always = 100.0
speed_always_unit = "%"
speed_next_motion = 100.0
speed_next_motion_unit = "%"


max_joint_speed = [328.0, 300.0, 375.0, 375.0, 375.0, 600.0]
max_cartesian_speed = 2000.0
lim_min = [-170, -190, -29, -190, -120, -360]
lim_max = [ 170,   45, 256,  190,  120,  360]

fps = 30.0

tool_trans = NULL

open_flag = False
close_flag = False
sig_open = False
sig_close = False


abort_flag = False
comp_mode = True
        

def checkJointLimits(J):

    for i in range(0,6):
        if J[i] < lim_min[i]:
            raise IKError, "Joint %d: lower limit exceeded" % (i+1)
        if J[i] > lim_max[i]:
            raise IKError, "Joint %d: upper limit exceeded" % (i+1)
    
def DK(J):
    """Cinematica directa
    
    Momentan implementata doar pentru Viper s650
    J: lista cu 6 elemente, exprimate in grade, e.g. [0,-90,180,90,0]
    Returneaza un obiect de tip TRANS
    Se ia in calcul si transformarea TOOL curenta
    """
    
    Txz = omotrans(-20,0,0)*omorot(roty(-90))
    T65 = omotrans(-60,0,0)*omorot(rotx(-J[5]-180))
    T54 = omotrans(-187,0,0)*omorot(roty(-J[4]))
    T43 = omotrans(-108,0,90)*omorot(rotx(-J[3]))
    T32 = omotrans(0,0,270)*omorot(roty(-J[2]+180))
    T21 = omotrans(-75,0,132)*omorot(roty(-J[1]-90))
    T10 = omotrans(0,0,203)*omorot(rotz(J[0]))
    T0 =  omorot(rotz(180))
    
    Tdk = TRANS(HTM = T0 * T10 * T21 * T32 * T43 * T54 * T65 * Txz * tool_trans.HTM);
    return Tdk


    
def IK(loc, ppoint = True):
    """Cinematica inversa
    
    Momentan implementata doar pentru Viper s650, LEFTY, ABOVE, FLIP/NOFLIP
    loc: pozitia dorita a efectorului terminal (obiect de tip TRANS)
    Returneaza un obiect de tip TRANS
    Se ia in calcul si transformarea TOOL curenta
    TODO: 
        - exceptii (ce se intampla daca nu am solutie?)
        - RIGHTY, BELOW, SINGLE/MULTIPLE
    """


    try:
        t = tool_trans.HTM
        t[0:3,3] = -t[0:3,3]
        t[0:3,0:3] = t[0:3,0:3].T
        loc = loc.HTM * t
        # loc = loc:INVERSE(tool.trans)
        
        # merge doar FLIP/NOFLIP
        J = [0,0,0,0,0,0]
        
        (x,y,z) = (loc[0:3,3] - 80 * loc[0:3,2]).flatten().tolist()[0]
        j1 = math.atan2(y,x)
        
        L1 = 270
        L2 = math.sqrt(90*90 + 295*295)
        L3 = math.sqrt(x*x + y*y) - 75
        Lip = math.sqrt(L3*L3 + (z - 335)*(z - 335))
        ang = math.acos((L1*L1 + L2*L2 - Lip*Lip) / (2 * L1 * L2))			
        j3 = 5639074329176643.0/1125899906842624.0 - ang;

        angip = math.atan2(z - 335, L3)
        p = (L1 + L2 + Lip) / 2
        area = math.sqrt(p*(p-L1)*(p-L2)*(p-Lip))
        h = area * 2 / Lip
        ang2 = math.asin(h / L1)
        j2 = -(ang2 + angip)

        ca = 0.5*math.cos(-j3+j1-j2);
        sa = 0.5*math.sin(-j3+j1-j2);
        cb = 0.5*math.cos(j3+j1+j2);
        sb = 0.5*math.sin(j3+j1+j2);

        R03i = mat([[ca + cb, sa + sb, -math.sin(j2 + j3)],\
                    [-math.sin(j1), math.cos(j1), 0],\
                    [sb - sa, ca - cb, math.cos(j2+j3)]])
        

        R36 = R03i * loc[0:3, 0:3];
        (j4,j5,j6) = mat2ypr(R36)

        J[0] = j1 * 180/pi
        J[1] = j2 * 180/pi
        J[2] = j3 * 180/pi
        J[3] = j4
        J[4] = j5
        J[5] = j6


        if flip:
            J[3] = J[3] + 180;
            J[4] = -J[4];
            J[5] = J[5] + 180;

    except ValueError:
        raise IKError, "No solution"

    if not all(numpy.isfinite(J)):
        raise IKError, "No solution"
    
    checkJointLimits(J)
    
    return PPOINT(J) if ppoint else J

    
def ActuateGripper():
    global sig_open, sig_close
    if open_flag:
        sig_close = False
        sig_open = True
    elif close_flag:
        sig_open = False
        sig_close = True
    else:
        sig_open = False
        sig_close = False
    
def ang_distance(A,B):
    a = cgkit.cgtypes.mat4(A.HTM.flatten().tolist()[0])
    b = cgkit.cgtypes.mat4(B.HTM.flatten().tolist()[0])
    qa = cgkit.cgtypes.quat(a)
    qb = cgkit.cgtypes.quat(b)
    qdif = qa.inverse() * qb
    angle,axis = qdif.toAngleAxis()
    angle = angdif(angle, 0)  # intre -pi/pi
    return abs(angle * 180/pi)
    
def lin_interp(A,B,t):
    """ Interpolare liniara intre doua transformari (pentru MOVES)
    
    A, B: obiecte de tip TRANS
    t: real de la 0 la 1; 
       cand e 0, se returneaza A, cand e 1 se returneaza B
       cand e 0.5 se returneaza punctul de la jumatate (dintre A si B)
    Interpolarea este liniara pe X, Y, Z si "slerp" pe orientare
    """
    a = cgkit.cgtypes.mat4(A.HTM.flatten().tolist()[0])
    b = cgkit.cgtypes.mat4(B.HTM.flatten().tolist()[0])
    qa = cgkit.cgtypes.quat(a)
    qb = cgkit.cgtypes.quat(b)
    qdif = qa.inverse() * qb
    angle, axis = qdif.toAngleAxis()
    angle = angdif(angle, 0)
    
    qdifi = cgkit.cgtypes.quat(angle * t, axis)
    qi = qa * qdifi
    
    (pa,cucu,bau) = a.decompose()
    (pb,cucu,bau) = b.decompose()
    pint = pa * (1-t) + pb * t
    res = cgkit.cgtypes.mat4(1).translate(pint) * qi.toMat4()
    res = mat(res.toList()).reshape(4,4).T
    return TRANS(HTM = res)
    

def lin_interp_q(a,b,t):
    """ Interpolare liniara intre doua transformari reprezentate ca mat4
    """
    qa = cgkit.cgtypes.quat(a)
    qb = cgkit.cgtypes.quat(b)
    qdif = qa.inverse() * qb
    angle, axis = qdif.toAngleAxis()
    angle = angdif(angle, 0)
    
    qdifi = cgkit.cgtypes.quat(angle * t, axis)
    qi = qa * qdifi
    
    (pa,cucu,bau) = a.decompose()
    (pb,cucu,bau) = b.decompose()
    pint = pa * (1-t) + pb * t
    res = cgkit.cgtypes.mat4(1).translate(pint) * qi.toMat4()
    res = mat(res.toList()).reshape(4,4).T
    return TRANS(HTM = res)


class TrajSegment_Proc:
    def __init__(self, seg1, seg2):
        self.seg1 = seg1
        self.seg2 = seg2
        self.t = 0
    def step(self, dryrun=False):
        dt1 = self.seg1.step(dryrun)
        dt2 = self.seg2.step(dryrun)
        
        dt = dt1 * (1-self.t) + dt2 * self.t 
        dt = dt/2
        self.t = min(self.t + dt, 1)
        self.seg1.t = self.t
        self.seg2.t = self.t

        return dt
        
        
    def where(self):
        a = self.seg1.where()
        b = self.seg2.where()
        ja = mat(a)
        jb = mat(b)
        j = ja * (1-self.t) + jb * self.t
        j = j.tolist()[0]
        return j
        

#~ def jreldist(ppa,ppb):
    #~ ja = mat(ppa.J)
    #~ jb = mat(ppb.J)
    #~ dif = ja - jb
    #~ return abs(dif / mat(max_joint_speed)).max()  
    
class TrajSegment_Joint:
    def __init__(self, ppstart, ppend, program_speed):
        self.ppstart = ppstart
        self.ppend = ppend
        self.program_speed = program_speed
        self.cartesian = False
        self.t = 0

        self.ja = mat(ppstart.J)
        self.jb = mat(ppend.J)
        dif = self.ja - self.jb
        self.drel = abs(dif / mat(max_joint_speed)).max()   # 1 = 100%

    def step(self, dryrun=False):
        if dryrun: 
            steps = 1
        else:
            time = self.drel / (self.program_speed/100.0) / (speed_monitor/100.0)
            steps = 1 + round(time * fps)
        dt = 1/steps
        self.t = min(self.t + dt, 1)
        return dt
    
    def where(self):
        j = self.ja * (1-self.t) + self.jb * self.t
        j = j.tolist()[0]
        return j

class TrajSegment_Cart:
    def __init__(self, ppstart, ppend, program_speed):
        self.ppstart = ppstart
        self.ppend = ppend
        self.program_speed = program_speed
        self.cartesian = True
        self.t = 0
    
        self.p1 = DK(ppstart)
        self.p2 = DK(ppend)
        self.m1 = cgkit.cgtypes.mat4(self.p1.HTM.flatten().tolist()[0])
        self.m2 = cgkit.cgtypes.mat4(self.p2.HTM.flatten().tolist()[0])
        self.drel = (DISTANCE(self.p1, self.p2) + ang_distance(self.p1,self.p2)) / max_cartesian_speed

    def step(self, dryrun = False):
        if dryrun: 
            steps = 1
        else:
            time = self.drel / (self.program_speed/100.0) / (speed_monitor/100.0)
            steps = 1 + round(time * fps)
            
        dt = 1/steps
        self.t = min(self.t + dt, 1)
        return dt
        
    def where(self):
        p = lin_interp_q(self.m1, self.m2, self.t)
        return IK(p, False)

trajQueue = []

def Step():
    t0 = time.time()
    global currentJointPos, trajQueue
    removed = False
    
    dryrun = switch["DRY.RUN"]
    if len(trajQueue) > 0:
        ActuateGripper() 

        ts = trajQueue[0]
        try:
            ts.step(dryrun)
            if not dryrun:
                currentJointPos = ts.where()
        except IKError:
            ex = sys.exc_info()[1]
            print "IKError: " + str(ex)
            
            
        
        if ts.t == 1:
            removed = True
            #~ print "finished"
            trajQueue = trajQueue[1:]
    t1 = time.time()
    dt = t1 - t0
    #~ if dt > 0.01:
        #~ print "Step(): ", dt
        #~ print removed
        #~ print ts
        #~ pass

def splitSegment(ts, t = None):
    if t != None:
        ts.t = t
    ppmid = PPOINT(ts.where())
    if ts.cartesian:
        a = TrajSegment_Cart(ts.ppstart, ppmid, ts.program_speed)
        b = TrajSegment_Cart(ppmid, ts.ppend, ts.program_speed)        
    else:
        a = TrajSegment_Joint(ts.ppstart, ppmid, ts.program_speed)
        b = TrajSegment_Joint(ppmid, ts.ppend, ts.program_speed)        
    return (a,b)

# miscare normala: un TrajSegment_Cart sau TrajSegment_Joint
# procedurala:
#   - renunt la segmentul curent
#   - sparg segmentul de la HERE pana la DEST in doua
#   - prima jumatate o pun la coada
#   - apoi sparg si segmentul de la DEST la NEXT_DEST in doua
#   - fac blend intre sparturile din mijloc
#   - ultima spartura o pun la coada
#   => am 3 segmente la procedurala; 2 daca sunt la blending; 
#   cand raman cu 1 pot sa incep miscare procedurala din nou

    

def ctraj(jdest):
    global startJointPos, destJointPos

    while len(trajQueue) > 1:
        #~ print "waiting for proc motion to finish"
        time.sleep(0.01)
    
    if len(trajQueue) == 0:
        # incerc sa aproximez cu jtraj daca traiectoria e suficient de scurta
        ts = TrajSegment_Joint(PPOINT(currentJointPos), jdest, speed_next_motion)
        if ts.step() < 0.5:
            ts = TrajSegment_Cart(PPOINT(currentJointPos), jdest, speed_next_motion)
        else:
            #~ ts.t = 0  # aproximez
            #~ print "ctraj aprox
            pass
            
        trajQueue.append(ts)
    else:
        ts = TrajSegment_Joint(PPOINT(destJointPos), jdest, speed_next_motion)
        if ts.step() < 0.5:
            global pauseTick
            pauseTick = True
            npseg = TrajSegment_Cart(PPOINT(destJointPos), jdest, speed_next_motion)
            #~ print "proc"
            #~ print trajQueue[0].t
            (a,b) = splitSegment(trajQueue[0])
            (a,b) = splitSegment(b, 0.5)
            (c,d) = splitSegment(npseg, 0.5)
            del(trajQueue[0])
            trajQueue.append(a)
            trajQueue.append(TrajSegment_Proc(b,c))
            trajQueue.append(d)
            #~ print trajQueue
            #IPython.Shell.IPShellEmbed([])()
            pauseTick = False
        else:
            #~ ts.t = 0  # aproximez
            #~ print "pctraj aprox"
            trajQueue.append(ts)

    startJointPos = currentJointPos
    destJointPos = jdest.J
        
def jtraj(jdest):
    global startJointPos, destJointPos
    while len(trajQueue) > 1:
        #~ print "waiting for proc motion to finish"
        time.sleep(0.01)


    if len(trajQueue) == 0:
        ts = TrajSegment_Joint(PPOINT(destJointPos), jdest, speed_next_motion)
        trajQueue.append(ts)
    else:
        ts = TrajSegment_Joint(PPOINT(currentJointPos), jdest, speed_next_motion)
        if ts.step() < 0.5:
            global pauseTick
            pauseTick = True
            npseg = TrajSegment_Joint(PPOINT(destJointPos), jdest, speed_next_motion)
            (a,b) = splitSegment(trajQueue[0])
            (a,b) = splitSegment(b, 0.5)
            (c,d) = splitSegment(npseg, 0.5)
            del(trajQueue[0])
            trajQueue.append(a)
            trajQueue.append(TrajSegment_Proc(b,c))
            trajQueue.append(d)
            pauseTick = False
        else:
            #~ ts.t = 0  # aproximez
            #~ print "pjtraj aprox"
            trajQueue.append(ts)

    startJointPos = currentJointPos
    destJointPos = jdest.J
        

def jog(mode, axis, signed_speed):
    """
    Jog the robot.
    mode: "world", "tool", "joint"
    axis: 1...6
    signed_speed: -100...100
    """
    
    try:
        a0 = axis - 1
        
        global currentJointPos, destJointPos
        
        if mode.lower() == 'world':
            here = DK(currentJointPos)
            transl = [0,0,0]
            d = signed_speed/100.0 * max_cartesian_speed / 3 / fps
            
            rot = NULL
            scaleRot = 0.3
            if axis <= 3:
                transl[a0] = d
            elif axis == 4:
                rot = RX(d * scaleRot)
            elif axis == 5:
                rot = RY(d * scaleRot)
            elif axis == 6:
                rot = RZ(d * scaleRot)
            
            pos = SHIFT(here, transl[0], transl[1], transl[2])
            rot = rot * SHIFT(here, -DX(here), -DY(here), -DZ(here))
            dest = TRANS(DX(pos), DY(pos), DZ(pos)) * rot
            
            jdest = IK(dest)
            currentJointPos = jdest.J
            destJointPos = currentJointPos
        elif mode.lower() == 'tool':
            here = DK(currentJointPos)
            transl = [0,0,0]
            d = signed_speed/100.0 * max_cartesian_speed / 3 / fps
            
            rot = NULL
            scaleRot = 0.3
            if axis <= 3:
                transl[a0] = d
            elif axis == 4:
                rot = RX(d * scaleRot)
            elif axis == 5:
                rot = RY(d * scaleRot)
            elif axis == 6:
                rot = RZ(d * scaleRot)
            
            dest = here * TRANS(transl[0], transl[1], transl[2]) * rot
            jdest = IK(dest)
            currentJointPos = jdest.J
            destJointPos = currentJointPos
                
            
        elif mode.lower() == 'joint':
            J = copy(currentJointPos)
            J[a0] = J[a0] + signed_speed/100.0 * max_joint_speed[a0] / 3 / fps
            checkJointLimits(J)
            currentJointPos = J
            destJointPos = J
    except IKError:
        ex = sys.exc_info()[1]
        return "IKError: " + str(ex)


def AlignMCP():
    global currentJointPos, destJointPos
    
    try:
        a = DK(currentJointPos)
        yr = round(a.yaw / 90.0) * 90
        pr = round(a.pitch / 90.0) * 90
        rr = round(a.roll / 90.0) * 90
            
        b = TRANS(a.x, a.y, a.z, yr, pr, rr)
        
        ctraj(IK(b))
        #currentJointPos = IK(b).J
        #destJointPos = currentJointPos

    except IKError:
        ex = sys.exc_info()[1]
        return "IKError: " + str(ex)
