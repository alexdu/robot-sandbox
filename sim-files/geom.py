#       geom.py
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
import math
from math import pi


def rotx(ang):
    c = math.cos(ang * pi/180)
    s = math.sin(ang * pi/180)
    return mat([[1,  0,  0], \
                [0,  c, -s], \
                [0,  s,  c]])

def roty(ang):
    c = math.cos(ang * pi/180)
    s = math.sin(ang * pi/180)
    return mat([[ c, 0,  s], \
                [ 0, 1,  0], \
                [-s, 0,  c]])

def rotz(ang):
    c = math.cos(ang * pi/180)
    s = math.sin(ang * pi/180)
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


def decompose(M):
    [x,y,z] = M[0:3, 3].flatten().tolist()[0]
    
    yaw   = math.atan2(M[1,2],M[0,2]);
    pitch = math.atan2(math.sqrt((M[2,0])**2 + (M[2,1])**2), M[2,2]);
    roll  = math.atan2(M[2,1],-M[2,0]);


    if abs(pitch) < 1E-4:
        yaw = 0
        roll = math.atan2(M[1,0],M[0,0])

    if abs(abs(pitch) - pi) < 1E-4:
        yaw = 0;
        roll = math.atan2(M[1,0],-M[0,0]);

    
    return (x, y, z, yaw*180/pi, pitch*180/pi, roll*180/pi)
