#       ConveyorBelt.py
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

import Image

class ConveyorBelt:
    def __init__(self,
                name = "Conveyor Belt",
                size = (1400E-3,150E-3,1E-3),
                pos = (0, -300E-3, 0.5E-3), 
                rot = mat3(1), 
                signal = None, 
                support = False):
        
        size = list(size)
        pos = list(pos)

        if support:
            sizeSup = list(size)
            sizeSup[2] *= 0.9
            size[2] *= 0.1
            posSup = list(pos)
            posSup[2] -= size[2]/2
            pos[2] += sizeSup[2]/2
            createBoxStack(1, name=name + " Support", size=sizeSup, pos=posSup, rot=rot, kinematic=True, material=matBlueBox)

        self.name = name
        self.size = size                
        self.pos = pos
        self.rot = rot
        self.signal = signal
        self.worldObj = None
        
        

        self.initTexture()

        self.Start()
        
        eventmanager.connect(STEP_FRAME, self.tick) 
        eventmanager.connect(ENV_RESET, self.destroy)
        
        
    def initTexture(self):
        self._texPos = 0
        self.aspect_ratio = self.size[0] / self.size[1]
        imagename = os.path.join(sys.basepath, "img", "pattern-chevrons-3.png")
        im = Image.open(imagename)
        self.tex = GLTexture(image=im, size=(64,64), mode=GL_REPLACE)
        self.tex.transform = mat4(1).scale((self.aspect_ratio,1,1))
        self.matRender = GLMaterial(texture=self.tex)
        
    def tick(self):
        if self.signal:
            if self.running:
                if not SIG(self.signal):
                    self.Stop()
            else:
                if SIG(self.signal):
                    self.Start()
                    return
        if self.running:
            self._incr = -0.1 / RobotSim.fps / self.size[0] * self.aspect_ratio
            self._texPos += self._incr
            self.tex.transform = mat4(1).translate((self._texPos,0,0)).scale((self.aspect_ratio,1,1))
            
        
        
    def Start(self):
        #~ print "Starting " + self.name
        self._removeObj()
        self.worldObj = createBoxStack(1, name = self.name, size=self.size, pos=self.pos, rot=self.rot, material=matConveyorRunning, kinematic=True)[0]
        self.worldObj.setMaterial(self.matRender)
        self.worldObj.belt = self
        self.running = True
        
        for obj in scene.walkWorld():
            try:
                obj.manip.odebody.enable()
            except:
                pass
    def Stop(self):
        #~ print "Stopping " + self.name
        self._removeObj()
        self.worldObj = createBoxStack(1, name = self.name, size=self.size, pos=self.pos, rot=self.rot, material=matConveyorStopped, kinematic=True)[0]
        self.worldObj.setMaterial(self.matRender)
        self.worldObj.belt = self
        self.running = False

    def _removeObj(self):
        if self.worldObj != None:
            odeSim.remove(self.worldObj)
            worldroot.removeChild(self.worldObj)
            self.worldObj = None
        
    def destroy(self):
        #~ print "Destroying conveyor"
        try:
            eventmanager.disconnect(STEP_FRAME, self.tick)
            eventmanager.disconnect(ENV_RESET, self.destroy)
            self.signal = None
        except:
            pass
        return False
            
