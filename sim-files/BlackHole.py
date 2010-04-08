#       BlackHole.py
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

class BlackHole:
    def __init__(self,
                magic_word = "(Box|Pallet)",
                name = "BlackHole",
                disp_offset = (0,0,0),
                material = GLMaterial(diffuse=(1,0.3,1,0.7), blend_factors = (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)),
                pos = (0,0,0), 
                size = (0.1,0.1,0.1)):
        
        
        self.name = name
        self.size = size                
        self.pos = pos
        self.magic_word = magic_word
        self.material = material
        
        self.worldObj = Box(name=self.name, 
                                  pos = vec3(self.pos) + vec3(disp_offset), 
                                  lx = self.size[0], 
                                  ly = self.size[1], 
                                  lz = self.size[2], 
                                  material=self.material)
        
        self.refreshMonitoredObjects()
        eventmanager.connect(STEP_FRAME, self.tick) 
        eventmanager.connect(ENV_RESET, self.destroy) 
        eventmanager.connect(NEW_BOX_CREATED, self.refreshMonitoredObjects)
        

    def refreshMonitoredObjects(self):
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

    def doTheMagic(self):
        for obj in self.monitored_objects:
            if self._isInProximity(obj):                
                try:    odeSim.remove(obj)
                except: pass

                try:    worldroot.removeChild(obj)
                except: pass
                

    def tick(self):
        if self.worldObj == None:
            return
            
        self.doTheMagic()
            
    def _removeObj(self):
        if self.worldObj != None:
            if worldroot.hasChild(self.worldObj.name):
                worldroot.removeChild(self.worldObj)
                self.worldObj = None
        
    def destroy(self):
        eventmanager.disconnect(STEP_FRAME, self.tick)
        eventmanager.disconnect(ENV_RESET, self.destroy)
        eventmanager.disconnect(NEW_BOX_CREATED, self.refreshMonitoredObjects)
        self._removeObj()
