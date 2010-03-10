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

import math
import numpy
from numpy import matrix, mat
from vplus import *
from math import pi
import threading
import cgkit

currentJointPos = [0,-90,180,0,0,0]

lefty = True
above = True
flip = False
single = False



startJointPos = currentJointPos     # de unde am inceput miscarea
destJointPos = currentJointPos      # unde ma opresc
#intermedJointPos = currentJointPos  # punctul intermediar (pt MOVE-uri fara BREAK)
        
#interp_mode_straight_line = False
sw_power = False
param = dict()
param["HAND.TIME"] = 0.5

speed_monitor = 50
speed_always = 100
speed_always_unit = "%"
speed_next_motion = 100
speed_next_motion_unit = "%"

fps = 30

tool_trans = NULL

open_flag = False
close_flag = False
sig_open = False
sig_close = False


arm_trajectory_index = 0
arm_trajectory = []



def rotx(ang):
    c = COS(ang)
    s = SIN(ang)
    return mat([[1,  0,  0], \
                [0,  c, -s], \
                [0,  s,  c]])

def roty(ang):
    c = COS(ang)
    s = SIN(ang)
    return mat([[ c, 0,  s], \
                [ 0, 1,  0], \
                [-s, 0,  c]])

def rotz(ang):
    c = COS(ang)
    s = SIN(ang)
    return mat([[c, -s,  0], \
                [s,  c,  0], \
                [0,  0,  1]])

def omorot(r):
    z31 = mat(numpy.zeros((3,1)))
    z13 = mat(numpy.zeros((1,3)))

    return numpy.bmat([[r,      z31],\
                       [z13, mat(1)]])


def omotrans(x,y,z):
    return mat([[1, 0, 0, x],\
                [0, 1, 0, y],\
                [0, 0, 1, z],\
                [0, 0, 0, 1]])


def decompose(T):
    [x,y,z] = T[0:3, 3].flatten().tolist()[0]
    
    yaw   = ATAN2(T[1,2],T[0,2]);
    pitch = ATAN2(SQRT((T[2,0])**2 + (T[2,1])**2), T[2,2]);
    roll  = ATAN2(T[2,1],-T[2,0]);


    if ABS(pitch) < 1E-4:
        yaw = 0
        roll = ATAN2(T[1,0],T[0,0])

    if ABS(ABS(pitch) - 180) < 1E-4:
        yaw = 0;
        roll = ATAN2(T[1,0],-T[0,0]);

    return (x, y, z, yaw, pitch, roll)
    
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

    
    
def IK(loc):
    """Cinematica directa
    
    Momentan implementata doar pentru Viper s650, LEFTY, ABOVE, FLIP/NOFLIP
    loc: pozitia dorita a efectorului terminal (obiect de tip TRANS)
    Returneaza un obiect de tip TRANS
    Se ia in calcul si transformarea TOOL curenta
    TODO: 
        - exceptii (ce se intampla daca nu am solutie?)
        - RIGHTY, BELOW, SINGLE/MULTIPLE
    """
    try:
        loc = loc * INVERSE(tool_trans)
        # merge doar FLIP/NOFLIP
        J = [0,0,0,0,0,0]
            
        x = DX(loc) - 80 * loc.HTM[0,2]
        y = DY(loc) - 80 * loc.HTM[1,2]
        z = DZ(loc) - 80 * loc.HTM[2,2]
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

        T03i = TRANS(HTM = omorot(mat([[ca + cb, sa + sb, -math.sin(j2 + j3)],\
                                              [-math.sin(j1), math.cos(j1), 0],\
                                              [sb - sa, ca - cb, math.cos(j2+j3)]])))
        

        T36 = T03i * loc;
        (x,y,z,j4,j5,j6) = decompose(T36.HTM)

        J[0] = j1 * 180/pi
        J[1] = j2 * 180/pi
        J[2] = j3 * 180/pi
        J[3] = j4
        J[4] = j5
        J[5] = j6


        if flip:
            J[4] = J[4] + 180;
            J[5] = -j(5);
            J[6] = J[6] + 180;

    except ValueError:
        print "IK: Out of range (no solution)."
        return PPOINT(currentJointPos)

    return PPOINT(J)
    
def ActuateGripper():
    global sig_open, sig_close
    
    if open_flag:
        sig_close = False
        sig_open = True
    if close_flag:
        sig_open = False
        sig_close = True
    
    
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
    qi = cgkit.cgtypes.slerp(t, qa, qb)
    
    (pa,cucu,bau) = a.decompose()
    (pb,cucu,bau) = b.decompose()
    pi = pa * (1-t) + pb * t
    res = cgkit.cgtypes.mat4(1).translate(pi) * qi.toMat4()
    res = mat(res.toList()).reshape(4,4).T
    return TRANS(HTM = res)
    

    

def ctraj(jdest):        
    # Calculeaza traiectoria robotului pentru miscari in linie dreapta (MOVES)
    # Rezultatul este memorat pe articulatii, in arm_trajectory
    global arm_trajectory, startJointPos, destJointPos

    lock = threading.Lock()
    lock.acquire()
    try:
        destJointPos = jdest.J

        p1 = DK(currentJointPos)
        p2 = DK(destJointPos)

        # Viteza de 100% o consider 1000 mm / secunda
    
        d = DISTANCE(p1,p2)
        time = d / 1000 / (speed_next_motion/100.0) / (speed_monitor/100.0)
        steps = 1 + round(time * fps)
        arm_trajectory_index = 0
        for t in numpy.linspace(0,1,steps):
            p = lin_interp(p1,p2,t)
            j = IK(p)
            arm_trajectory.append(j)
    finally:
        lock.release() 
        
def jtraj(jdest):
    # Calculeaza traiectoria robotului pentru miscari in linie dreapta (MOVES)
    # Rezultatul este memorat pe articulatii, in arm_trajectory

    # Viteza de 100% o consider 180 deg / secunda

    global arm_trajectory, startJointPos, destJointPos
    
    lock = threading.Lock()
    lock.acquire()
    try:
        startJointPos = currentJointPos
        destJointPos = jdest.J
        ja = mat(currentJointPos)
        jb = mat(destJointPos)
        dif = ja - jb
        maxrot = abs(dif).max()
        time = maxrot / 180.0 / (speed_next_motion/100.0) / (speed_monitor/100.0)
        steps = 1 + round(time * fps)
        #print steps
        
        #from IPython.Shell import IPShellEmbed; ipshell = IPShellEmbed(); ipshell()

        arm_trajectory_index = 0
        for t in numpy.linspace(0,1,steps):
            j = ja * (1-t) + jb * t
            j = j.tolist()[0]
            arm_trajectory.append(PPOINT(j))
        #print arm_trajectory

    finally:
        lock.release() 

