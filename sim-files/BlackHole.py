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
                name = "Black Hole",
                material = GLMaterial(diffuse=(1,0.3,1,0.7)),
                pos = (0.3,0.3,0.3), 
                size = (0.1,0.1,0.1), 
                signal = None, 
                freq = 0.5):
        
        self.name = name
        self.size = size                
        self.pos = pos
        self.freq = freq
        self.material = GLMaterial(diffuse=material.diffuse, blend_factors = (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA))
        self.magic_word = re.compile(magic_word)
        self.signal = signal
        self.prev_state = None
        self.triggered = False
        self.t = 0
        self.sensingArea = createBoxStack(1, name=self.name,
                                                pos = self.pos, 
                                                size = self.size, 
                                                material=self.material,
                                                kinematic = True)[0]

        eventmanager.connect(ODE_COLLISION, self)
        eventmanager.connect(ENV_RESET, self) 
        eventmanager.connect(STEP_FRAME, self) 

        
        self.gomi = []

    def onStepFrame(self):
        if self.signal == None or SIG(self.signal):
            self.t += 1/RobotSim.fps
            (r,g,b,a) = self.material.diffuse
            self.material.diffuse = (r,g,b, 0.2 + 0.6*cos(pi*self.freq*self.t)**2)
            self.sensingArea.visible = True
        else:
            self.t = 0
            (r,g,b,a) = self.material.diffuse
            self.material.diffuse = (r,g,b,0)
            self.sensingArea.visible = False
                
        # empty trash 
        for o in self.gomi:
            try: odeSim.remove(o)
            except: pass
            
            try: worldroot.removeChild(o)
            except: pass
        self.gomi = []

        if self.signal != None:
            s = SIG(self.signal)
            self.triggered = fedge(s, self.prev_state)
            self.prev_state = s
            
    def onODECollision(self, col):
        pair = [col.obj1, col.obj2]
        if self.sensingArea in pair:
            del(col.contacts[:])
            
            if self.signal == None or self.triggered:
                pair.remove(self.sensingArea)
                if re.match(self.magic_word, pair[0].name):
                    self.gomi.append(pair[0])
                        
    def onEnvReset(self):
        eventmanager.disconnect(ENV_RESET, self)
        eventmanager.disconnect(ODE_COLLISION, self)
        eventmanager.disconnect(STEP_FRAME, self)
        self.signal = None
        #~ print "Destroyed sensor"    

