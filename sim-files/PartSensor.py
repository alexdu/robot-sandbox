#       PartSensor.py
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

class PartSensor:
    def __init__(self,
                magic_word = "Box",
                name = "Part Sensor",
                disp_offset = (0,0,0),
                disp_radius = 10e-3,
                material_on=GLMaterial(diffuse=(0.2,0,0), emission=(0.8,0,0)),
                material_off=GLMaterial(diffuse=(0.3,0,0)),
                pos = (0,0,0), 
                size = (0.1,0.1,0.1),
                signal = None):
        
        
        self.name = name
        self.size = size                
        self.pos = pos
        self.signal = signal
        self.material_on = material_on
        self.material_off = material_off
        self.magic_word = re.compile(magic_word)
        self.state = None
        
        self.lightBulb = Sphere(name=name, pos=vec3(pos) + vec3(disp_offset), radius=disp_radius, material=material_off)

        self.sensingArea = createBoxStack(1, name=self.name + " - Sensing Area", 
                                                pos = self.pos, 
                                                size = self.size, 
                                                material=GLMaterial(diffuse=(1,0,0,0.2), blend_factors = (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)), 
                                                kinematic = True)[0]


        eventmanager.connect(ODE_COLLISION, self, priority=5)
        eventmanager.connect(ENV_RESET, self) 
        eventmanager.connect(STEP_FRAME, self)

    
    
    def onStepFrame(self):
        if self.signal != None:
            if bool(SIG(self.signal)) != self.state:
                vplus._SET_INP_SIGNAL(self.signal * (1 if self.state else -1))
                self.lightBulb.setMaterial(self.material_on if self.state else self.material_off)
                        
        self.state = False
    def onODECollision(self, col):
        pair = [col.obj1, col.obj2]
        if self.sensingArea in pair:
            del(col.contacts[:])
            
            pair.remove(self.sensingArea)
            if re.match(self.magic_word, pair[0].name):
                self.state = True
            
        
    def onEnvReset(self):
        #~ print "Destroying sensor"
        eventmanager.disconnect(ENV_RESET, self)
        eventmanager.disconnect(ODE_COLLISION, self)
        eventmanager.disconnect(STEP_FRAME, self)
        self.signal = None
        #~ print "Destroyed sensor"    
