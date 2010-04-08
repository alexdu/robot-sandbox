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
        self.magic_word = magic_word
        self.prev_state = None
        
        self.worldObj = Sphere(name=name, pos=vec3(pos) + vec3(disp_offset), radius=disp_radius, material=material_off)
        self.sensingAreaObj = None
        
        self.refreshMonitoredObjects()
        eventmanager.connect(STEP_FRAME, self.tick) 
        eventmanager.connect(ENV_RESET, self.destroy) 
        eventmanager.connect(NEW_BOX_CREATED, self.refreshMonitoredObjects)
        

    def showSensingArea(self):
        self.sensingAreaObj = Box(name=self.name + " - Sensing Area", 
                                  pos = self.pos, 
                                  lx = self.size[0], 
                                  ly = self.size[1], 
                                  lz = self.size[2], 
                                  material=GLMaterial(diffuse=(1,0,0,0.2), blend_factors = (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)))
    def hideSensingArea(self):
        if self.sensingAreaObj != None:
            worldroot.removeChild(self.sensingAreaObj)
            self.sensingAreaObj = None
    
    def refreshMonitoredObjects(self):
        #~ print "sensor refresh"
        self.monitored_objects = []
        for obj in scene.walkWorld():
            try:
                if obj != self.worldObj:
                    if obj.name.startswith(self.magic_word) or re.match(self.magic_word, obj.name):
                        self.monitored_objects.append(obj)
                        if RobotSim.debug: print self.name, "monitoring:", obj, obj.name
            except:
                pass
        
    def _isInProximity(self,obj):
        pos = obj.pos
        dif = (pos - self.pos)
        reldif = [abs(dif[0]/self.size[0]), abs(dif[1]/self.size[1]), abs(dif[2]/self.size[2])]
        return vec3(reldif) < vec3(0.5,0.5,0.5)

    def detectPart(self):
        for obj in self.monitored_objects:
            if self._isInProximity(obj):
                self.part_present = obj
                return True

    def tick(self):
        if self.worldObj == None:
            return
            
        part_present = self.detectPart()
        
        if part_present != self.prev_state:
            self.prev_state = part_present
        
            if part_present:
                self.worldObj.setMaterial(self.material_on)
            else:
                self.worldObj.setMaterial(self.material_off)

        if self.signal != None:
            if bool(SIG(self.signal)) != part_present:
                vplus._SET_INP_SIGNAL(self.signal * (1 if part_present else -1))
                
                
            
    def _removeObj(self):
        if self.worldObj != None:
            if worldroot.hasChild(self.worldObj.name):
                worldroot.removeChild(self.worldObj)
                self.worldObj = None
        if self.sensingAreaObj != None:
            if worldroot.hasChild(self.sensingAreaObj.name):
                worldroot.removeChild(self.sensingAreaObj)
                self.sensingAreaObj = None
        
    def destroy(self):
        #~ print "Destroying sensor"
        eventmanager.disconnect(STEP_FRAME, self.tick)
        eventmanager.disconnect(ENV_RESET, self.destroy)
        eventmanager.disconnect(NEW_BOX_CREATED, self.refreshMonitoredObjects)
        self._removeObj()
        self.signal = None
        #~ print "Destroyed sensor"    
