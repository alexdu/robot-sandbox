#       PalletDispenser.py
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


class PalletDispenser:
    def __init__(self,
                name = "Pal Dispenser",
                disp_offset = (0,0,0),
                disp_size = (200e-3, 200e-3, 50e-3),
                disp_material=GLMaterial(diffuse=(0.3,0.3,1,0.7), blend_factors = (GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)),
                pal_size = (100E-3, 150E-3, 20E-3),
                pal_pos = (0.3,0.3,0.3),
                pal_rot = mat3(1), 
                delay_range = [2,5]):
        
        
        self.name = name
        
        self.pal_size = pal_size                
        self.pal_pos = pal_pos
        self.pal_rot = pal_rot
        self.delay_range = delay_range
        
        
        (lx,ly,lz) = disp_size
        self.worldObj = Box(name=name, pos=vec3(pal_pos) + vec3(disp_offset), lx=lx, ly=ly, lz=lz, material=disp_material)
        self.pal = None
        self.last_seen = RobotSim.clock
        self.delay = None
        
        eventManager().connect(STEP_FRAME, self.tick) 
        eventManager().connect(ENV_RESET, self.destroy) 
    
        self.part_material_index = 0
    
    def dispense(self):
        # dispense new pallet
        mat = matPallet
        pos = vec3(self.pal_pos)
        rot = self.pal_rot
        
        self.pal = createBoxStack(1, name="Pallet", pos=pos, rot=rot, size=self.pal_size, material=mat)[0]
        return self.pal
        
    def tick(self):
        if not (self.pal in odeSim.body_dict):
            if self.delay == None:
                (a,b) = self.delay_range
                self.delay = random.uniform(a,b)
                if RobotSim.debug: print self.name, self.delay
        
            if RobotSim.clock > self.last_seen + self.delay:
                self.dispense()
        else:
            self.last_seen = RobotSim.clock
            self.delay = None

            
    def _removeObj(self):
        if self.worldObj != None:
            if worldroot.hasChild(self.worldObj.name):
                worldroot.removeChild(self.worldObj)
                self.worldObj = None
        
    def destroy(self):
        eventmanager.disconnect(STEP_FRAME, self.tick)
        eventmanager.disconnect(ENV_RESET, self.destroy)
        self._removeObj()
        
