#       PenAndPaper.py
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

# Called from scene.py with execfile


matPaper = GLMaterial(name="paper", diffuse=(1,1,1), emission=(0.8,0.8,0.8))
matBallpointPen = GLMaterial(name="ballpoint pen", diffuse=(0,0,1))

contactProps_PenPaper = ODEContactProperties(bounce = 0, mu = 0, soft_erp=0.2, soft_cfm=0.001)

from Drawing import Polyline


class Paper:
    def __init__(self,
                name = "Paper",
                size = (200E-3,300E-3,10E-3),
                pos = (0.5, 0, 0.01), 
                rot = mat3(1)):
        
        (lx,ly,lz) = size
        self.worldObj = Box(name=name, lx=lx, ly=ly, lz=lz, pos=pos, material=matPaper, mass=1)
        self.worldObj.paperObj = self
        odeSim.add(self.worldObj, categorybits=CB_PAPER, collidebits=CB_PEN_BALLPOINT)
        self.worldObj.manip.odebody.setKinematic()
        
        odeSim.setContactProperties((matBallpointPen, matPaper), contactProps_PenPaper)

        eventmanager.connect(ODE_COLLISION, self.PenOnPaper)
        eventmanager.connect(ENV_RESET, self.destroy)

        self.polylines = []
        self.last_pen_event = time.time()
        self.last_point = (0,0,0)
    
        
        
    def PenOnPaper(self, col):
        if col.obj2 == self.worldObj:
            if hasattr(col.obj1, 'ballpoint'):
                c = col.contacts[0]
                (pos, normal, depth, geom1, geom2) = c.getContactGeomParams()

                if time.time() - self.last_pen_event > 0.5:
                    self.polylines.append(Polyline(pts=[], color=(0,0,0.5)))
                    #print "Pen down"
                
                if (vec3(pos) - vec3(self.last_point)).length() > 3e-3:
                    posz = [pos[0], pos[1], self.worldObj.pos[2] + self.worldObj.lz/2 + 0.5e-3]
                    self.polylines[-1].addNewPoint(posz)
                    self.last_point = pos
                    
                #print pos
                self.last_pen_event = time.time()
            
    def _removeObj(self):
        if self.worldObj != None:
            if worldroot.hasChild(self.worldObj.name):
                odeSim.remove(self.worldObj)
                worldroot.removeChild(self.worldObj)
                self.worldObj = None
        
    def destroy(self):
        try:
            eventmanager.disconnect(ODE_COLLISION, self.PenOnPaper)
            eventmanager.disconnect(ENV_RESET, self.destroy)
            self._removeObj()
        except:
            pass
        return False
            





class Pen:
    def __init__(self,
                name = "Pen",
                pos = (0.3, -0.3, 0.025)):
        
        name = copy(name)
        pos = copy(pos)
        
        penfile = os.path.join(sys.basepath, "pen", "pen_cone.stl")
        load(penfile)
        self.pen_cone = worldObject("unnamed")
        self.pen_cone.name = name + " Cone"
        self.pen_cone.pos = pos
        self.pen_cone.mass = 1
        
        self.pen_box = Box(name = name + " Box (Handle)", 
                           pos=vec3(pos) + vec3(0,0,50e-3), 
                           lx=10e-3, ly=10e-3, lz=20e-3, 
                           material=matBlueBox, mass=0.01)
        odeSim.add(self.pen_box, categorybits=CB_PEN_HANDLE, collidebits=CB_ROBOT|CB_PEN_SUPPORT|CB_FLOOR)
        link(self.pen_cone, self.pen_box)
        
        self.pen_ballpoint = Sphere(name = name + " Ballpoint", 
                                    pos = vec3(pos), radius = 2e-3, 
                                    material=matBallpointPen, mass=0.01)
        odeSim.add(self.pen_ballpoint, categorybits=CB_PEN_BALLPOINT, collidebits=CB_PAPER|CB_FLOOR)
        self.pen_ballpoint.manip.odebody.setAutoDisableFlag(False)
        self.pen_ballpoint.ballpoint = True
        
        self.fixed_joint = ODEFixedJoint(name=name + " Glue", body1=self.pen_box, body2=self.pen_ballpoint)
        odeSim.add(self.fixed_joint)

        
        self.support = Box(name=name + " Support", 
                           pos=pos, lx=0.02, ly=0.02, lz=0.05, 
                           material=matLightBlueBox, mass=1)
        odeSim.add(self.support, categorybits=CB_PEN_SUPPORT, collidebits=CB_PEN_HANDLE)
        self.support.manip.odebody.setKinematic()
        
        eventmanager.connect(ENV_RESET, self.destroy)

        self.pen_box.manip.setPos(vec3(pos) + vec3((0,0,0.2)))
            
    def _removeObj(self):
        for obj in [self.pen_box, self.pen_ballpoint, self.pen_cone, self.fixed_joint, self.support]:
            if obj != None:
                if worldroot.hasChild(obj.name):
                    worldroot.removeChild(obj)
                if obj in odeSim.body_dict:
                    odeSim.remove(obj)
                obj = None
        
    def destroy(self):
        try:
            eventmanager.disconnect(ENV_RESET, self.destroy)
            self._removeObj()
        except:
            pass
        return False
            
