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


class Polyline(WorldObject):

    protocols.advise(instancesProvide=[ISceneItem])

    def __init__(self,
                 name = "Polyline",
                 pts = None,
                 color=(0,0,0),
                 **params):
        WorldObject.__init__(self, name=name, **params)

        self.geom = PolylineGeom(pts=pts, color=color)



class PolylineGeom(GeomObject):

    protocols.advise(instancesProvide=[IGeometry])
    
    def __init__(self,
                 pts = None,
                 color = (0,0,0)):

        GeomObject.__init__(self)
        self.pts = pts      # all points
        self.wpts = pts     # work set
        self.fpts = []      # frozen points (for fast OpenGL calls)
        self.color = color
        self.lastUpdate = time.time()

    # boundingBox
    def boundingBox(self):
        """Return the bounding box of the control polygon.
        """
        bb = BoundingBox()
        #for p in self.pts:
            #bb.addPoint(BezierPoint(p))
        return bb
    
    def addNewPoint(self, p):
        self.pts.append(p)
        self.wpts.append(p)
        self.lastUpdate = time.time()
        
        if len(self.wpts) > 20:
            #~ print "freezing"
            self.freeze(len(self.pts))

    def freeze(self, n):
        self.fpts = numpy.array(self.pts[:n], dtype=numpy.float32)
        self.wpts = self.pts[n-1:]
        #~ print len(self.wpts)
    # drawGL
    def drawGL(self):

        freezeAll = False
        dt = time.time() - self.lastUpdate
        if dt > 0.5 and len(self.wpts) > 1:
            #~ print "No update since 0.5 seconds; freezing"
            self.freeze(len(self.pts))
        
        
            
        

        t0 = time.time()
        glPushAttrib(GL_LIGHTING_BIT)
        glDisable(GL_LIGHTING)
        glLineWidth(2)
        glColor3fv(self.color)
        

        if len(self.fpts) > 1:
            glVertexPointerf(self.fpts)
            glEnableClientState( GL_VERTEX_ARRAY )
            glDrawArrays(GL_LINE_STRIP, 0, len(self.fpts))

        #~ glColor3f(1,0,0)
        if len(self.wpts) > 1:
            glVertexPointerf(self.wpts)
            glEnableClientState( GL_VERTEX_ARRAY )
            glDrawArrays(GL_LINE_STRIP, 0, len(self.wpts))

        #~ glBegin(GL_LINE_STRIP)
        #~ for p in self.pts:
            #~ glVertex3fv(p)
        #~ glEnd()

        glPopAttrib()

        t1 = time.time()
        #~ if t1 - t0 > 0.01:
            #~ print "drawGL takes too long: ", t1-t0
