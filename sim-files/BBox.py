#       Drawing.py
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

import OpenGL
OpenGL.ERROR_CHECKING = True
OpenGL.ERROR_ON_COPY = True

from cgkit.cgtypes import *
from cgkit.Interfaces import *
from cgkit.worldobject import WorldObject
import protocols
import cgkit._core


from cgkit._OpenGL.GL import *

#import cgkit.bisect
from cgkit.geomobject import *
from cgkit.slots import *
from cgkit.cgtypes import *
from cgkit.boundingbox import BoundingBox
import protocols
from cgkit.ribexport import IGeometry
from cgkit.ri import *
import time
import numpy
from cgkit.scene import getScene


def drawBoxGL():
    #print "draw"
    #glutSolidCube(1)

    glColor3f(0,0,0)
    glLineWidth(2)
    glDisable(GL_LIGHTING)
    
    for b in getScene().walkWorld():
        if type(b.geom) == cgkit.boxgeom.BoxGeom:
            x,y,z = b.pos.x,b.pos.y,b.pos.z
            x,y,z = 0,0,0
            l,w,h = b.lx/2, b.ly/2, b.lz/2

            glPushMatrix()
            glMultMatrixd(b.worldtransform.toList())
            glBegin(GL_LINE_STRIP)
            glVertex3f(x-l,y-w,z-h)
            glVertex3f(x+l,y-w,z-h)
            glVertex3f(x+l,y+w,z-h)
            glVertex3f(x-l,y+w,z-h)
            glVertex3f(x-l,y-w,z-h)

            glVertex3f(x-l,y-w,z+h)
            glVertex3f(x+l,y-w,z+h)
            glVertex3f(x+l,y+w,z+h)
            glVertex3f(x-l,y+w,z+h)
            glVertex3f(x-l,y-w,z+h)
            glEnd()

            glBegin(GL_LINE_STRIP)
            glVertex3f(x-l,y-w,z-h)
            glVertex3f(x-l,y-w,z+h)
            glEnd()

            glBegin(GL_LINE_STRIP)
            glVertex3f(x-l,y+w,z-h)
            glVertex3f(x-l,y+w,z+h)
            glEnd()

            glBegin(GL_LINE_STRIP)
            glVertex3f(x+l,y+w,z-h)
            glVertex3f(x+l,y+w,z+h)
            glEnd()

            glBegin(GL_LINE_STRIP)
            glVertex3f(x+l,y-w,z-h)
            glVertex3f(x+l,y-w,z+h)
            glEnd()


            glPopMatrix()
