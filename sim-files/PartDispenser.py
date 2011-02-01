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

def RandomChoiceFromList(L):
    if type(L) == list:
        return L[random.randint(1, len(L)) - 1]
    else:
        return L


class ParamList():
    def __init__(self, *args, **kwargs):
        self.dic = kwargs
    
    def RandomChoice(self):
        #~ print self.dic.keys()
        d = {}
        for key,val in self.dic.iteritems():
            val = RandomChoiceFromList(val)
            if type(val).__name__ == 'instance' and val.__class__ == ParamList:
                # merge param lists
                cd = val.RandomChoice()
                for k, v in cd.iteritems():
                    d[k] = v
            else:
                d[key] = val
        return d
            
        
    
class PartDispenser:
    def __init__(self,
                name = "Part Dispenser",
                disp_pos = (0,0,50e-3),
                disp_size = (200e-3, 200e-3, 50e-3),
                disp_material=GLMaterial(diffuse=(0.3,1,0.1)),
                delay_range = [5,10],
                signal = None,
                partinfo =  ParamList(
                                        group = 
                                        [ 
                                            ParamList(size = (100E-3,  30E-3, 15E-3), rot = rz(0)), 
                                            ParamList(size = (100E-3, 100E-3, 15E-3), rot = rz(90)) 
                                        ],
                                        pos = (0.3,0.3,0.3),
                                        material = matBoxes
                                    )
                ):
        
        
        self.name = name
        self.partinfo = partinfo
        self.signal = signal
        self.prev_state = None
        self.delay_range = delay_range
        if self.delay_range != None:
            self.delay = random.uniform(*self.delay_range)
        
        (lx,ly,lz) = disp_size
        self.worldObj = Box(name=name, pos=disp_pos, lx=lx, ly=ly, lz=lz, material=disp_material, mass=1)
        odeSim.add(self.worldObj)
        self.worldObj.manip.odebody.setKinematic()

        
        eventManager().connect(STEP_FRAME, self.tick) 
        eventManager().connect(ENV_RESET, self.destroy) 
        
    
        
    def dispense(self):
        # dispense new part
        self.last_dispense = RobotSim.clock
        
        p = self.partinfo.RandomChoice()
        pos = p["pos"]
        rot = p["rot"]
        size = p["size"]
        mat = p["material"]
        name = p["name"]


        #~ (dx, dy, dz) = self.part_pos_stdev
        #~ pos = vec3(self.part_pos) + vec3(random.gauss(0,dx), random.gauss(0,dy), random.gauss(0,dz))

            
        #~ (rx, ry, rz) = self.part_rot_range_xyz
        #~ rot = self.part_rot.rotate(random.uniform(-rx,rx)/2, (1,0,0)).rotate(random.gauss(-ry,ry)/2, (0,1,0)).rotate(random.gauss(-rz,rz)/2, (0,0,1))
        
        box = createBoxStack(1, name=name, pos=pos, rot=rot, size=size, material=mat)[0]
        return box
        
    def tick(self):
        if self.signal != None and self.delay_range == None: # doar pe semnal
            if (not self.prev_state) and SIG(self.signal):
                self.dispense()
            self.prev_state = SIG(self.signal)

        if self.delay_range != None:
            if self.signal == None or SIG(self.signal):
                self.delay -= 1/RobotSim.fps
    
            if self.delay < 0:
                self.dispense()
                self.delay = random.uniform(*self.delay_range)

    def destroy(self):
        eventmanager.disconnect(STEP_FRAME, self.tick)
        eventmanager.disconnect(ENV_RESET, self.destroy)
        self.signal = None
        
