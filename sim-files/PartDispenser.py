#       PartDispenser.py
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


class PartDispenser:
    def __init__(self,
                name = "Part Dispenser",
                disp_offset = (0,0,50e-3),
                disp_size = (200e-3, 200e-3, 50e-3),
                disp_material=GLMaterial(diffuse=(0.3,1,0.1)),
                part_size = (100E-3, 30E-3, 15E-3),
                part_pos = (0.3,0.3,0.3),
                part_pos_stdev = (0,0,0), 
                part_rot = mat3(1),
                part_rot_range_xyz = (0,0,0), 
                part_materials = matBoxes,
                part_material_random = False,
                signal = None):
        
        
        self.name = name
        
        self.part_size = part_size                
        self.part_pos = part_pos
        self.part_pos_stdev = part_pos_stdev
        self.part_rot = part_rot
        self.part_rot_range_xyz = part_rot_range_xyz
        self.part_materials = part_materials
        self.part_material_random = part_material_random
        
        self.signal = signal
        
        #~ self.disp_size = disp_size
        #~ self.disp_offset = disp_offset
        #~ self.disp_material = disp_material
        
        self.prev_state = None
        
        (lx,ly,lz) = disp_size
        self.worldObj = Box(name=name, pos=vec3(part_pos) + vec3(disp_offset), lx=lx, ly=ly, lz=lz, material=disp_material, mass=1)
        odeSim.add(self.worldObj)
        self.worldObj.manip.odebody.setKinematic()
        
        eventManager().connect(STEP_FRAME, self.tick) 
        eventManager().connect(ENV_RESET, self.destroy) 
        
    
        self.part_material_index = 0
    
    def dispense(self):
        # dispense new part
        if self.part_material_random:
            self.part_material_index = random.randint(1, len(self.part_materials)) - 1
        else:
            self.part_material_index = (self.part_material_index + 1) % len(self.part_materials)
        mat = self.part_materials[self.part_material_index]
        
        (dx, dy, dz) = self.part_pos_stdev
        pos = vec3(self.part_pos) + vec3(random.gauss(0,dx), random.gauss(0,dy), random.gauss(0,dz))
        
        (rx, ry, rz) = self.part_rot_range_xyz
        rot = self.part_rot.rotate(random.uniform(-rx,rx)/2, (1,0,0)).rotate(random.gauss(-ry,ry)/2, (0,1,0)).rotate(random.gauss(-rz,rz)/2, (0,0,1))
        
        box = createBoxStack(1, pos=pos, rot=rot, size=self.part_size, material=mat)[0]
        return box
        
    def tick(self):
        if self.signal != None:
            if (not self.prev_state) and SIG(self.signal):
                self.dispense()
            self.prev_state = SIG(self.signal)
                
            
    def _removeObj(self):
        if self.worldObj != None:
            if worldroot.hasChild(self.worldObj.name):
                odeSim.remove(self.worldObj)
                worldroot.removeChild(self.worldObj)
                self.worldObj = None
        
    def destroy(self):
        eventmanager.disconnect(STEP_FRAME, self.tick)
        eventmanager.disconnect(ENV_RESET, self.destroy)
        self._removeObj()
        self.signal = None
        
