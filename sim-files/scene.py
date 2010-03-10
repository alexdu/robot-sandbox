#       scene.py#       #       Copyright 2010 Alex Dumitrache <alex@cimr.pub.ro>#       #       This program is free software; you can redistribute it and/or modify#       it under the terms of the GNU General Public License as published by#       the Free Software Foundation; either version 2 of the License, or#       (at your option) any later version.#       #       This program is distributed in the hope that it will be useful,#       but WITHOUT ANY WARRANTY; without even the implied warranty of#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the#       GNU General Public License for more details.#       #       You should have received a copy of the GNU General Public License#       along with this program; if not, write to the Free Software#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,#       MA 02110-1301, USA.

import math
import random
import threading
from vplus import *
import vplus
from geom import *
import sys
import os
import RobotSim
import ode

global ipshell
#print sys.argv
sys.argv.pop()
sys.argv.pop()
from IPython.Shell import IPShellEmbed

# acum sunt in folderul cu sursele (src, sim-files)
dir = os.getcwd()
args = ['-pi1','. ','-po','=> ', '-colors', 'LightBG']
ipshell = IPShellEmbed(args, banner="\r\nV+ simulation console ready.")

class MyThread ( threading.Thread ):
    def run(self):	
        ipshell() 
        raise SystemExit

def load_robot_link(file, name):
	print "Loading %s ..." % name
	load(file)
	obj = worldObject("vcg")
	obj.name = name
	obj.mass = 0.1
	matRobot = GLMaterial(diffuse=(1,0.95,0.9))
	obj.setMaterial(matRobot)

	


load_robot_link('6dof-robot-model/base.stl', 'Robot Base')
load_robot_link('6dof-robot-model/link1.stl', 'Robot Link 1')
load_robot_link('6dof-robot-model/link2.stl', 'Robot Link 2')
load_robot_link('6dof-robot-model/link3.stl', 'Robot Link 3')
load_robot_link('6dof-robot-model/link4.stl', 'Robot Link 4')
load_robot_link('6dof-robot-model/link56.stl', 'Robot Link 5-6')


base = worldObject("Robot Base")
link1 = worldObject("Robot Link 1")
link2 = worldObject("Robot Link 2")
link3 = worldObject("Robot Link 3")
link4 = worldObject("Robot Link 4")
link5 = worldObject("Robot Link 5-6")
link6 = Box("Gripper Mounting Support", lx = 50, ly = 30, lz = 30, mass=0.1)
#gripper = Box(lx = 15, ly = 15, lz = 30, mass=1)
gripper = Box("Gripper", lx = 20, ly = 30, lz = 100, mass=1)
finger1 = Box("Gripper Finger 1", lx = 30, ly = 30, lz = 15, mass=0.01)
finger2 = Box("Gripper Finger 2", lx = 30, ly = 30, lz = 15, mass=0.01)


matFloor = GLMaterial(diffuse=(0,1,1))
floor = Box("Floor", lx=1500, ly=1500, lz=50, material=matFloor)
floor.mass = 0.1
floor.pos = (0,0,-25)




## link(link2, link1, relative=True)
## link(link1, base, relative=True)





global t	
t = 0

def enforcePose(m, P):
	(pos,b,c) = P.decompose()
	m.setRot(P.getMat3().inverse().toList())
	m.setPos(pos)
        m.setLinearVel((0,0,0))
        m.setAngularVel((0,0,0))


def setRobotPos(J, grip_pos = -1):

    j = (mat(J) * pi/180).tolist()[0]

    R = mat4(1)
    P = R
    enforcePose(M["base"], P)
    P = R.rotation(j[0], (0,0,1)) * R.translation((0,0,203)) * P
    enforcePose(M["link1"], P)
    P = P * R.translation((75,0,335-203)) * R.rotation(j[1]+pi/2, (0,1,0))
    enforcePose(M["link2"], P)
    P = P * R.translation((0,0,270)) * R.rotation(j[2]-pi, (0,1,0))
    enforcePose(M["link3"], P)
    P = P * R.translation((108,0,90)) * R.rotation(j[3], (1,0,0))
    enforcePose(M["link4"], P)
    P = P * R.translation((295-108,0,0)) * R.rotation(j[4], (0,1,0))
    enforcePose(M["link5"], P)
    P = P * R.translation((80+20,0,0)) * R.rotation(j[5], (1,0,0))
    enforcePose(M["link6"], P)
    P = P * R.translation((20+15,0,0))
    enforcePose(M["gripper"], P)

    enforcePose(M["floor"], R.translation((0,0,-25)))

    if grip_pos >= 0:
        P1 = P * R.translation((10+15,0, grip_pos))
        enforcePose(M["finger1"], P1)
        P2 = P * R.translation((10+15,0,-grip_pos))
        enforcePose(M["finger2"], P2)
	
def setGripperForces(open, close):
    gripForce = 500
    
    if open:
        M["finger1"].addForce((0,0,gripForce), True)
        M["finger2"].addForce((0,0,-gripForce), True)
        slider_finger1.histop = 40
        slider_finger2.lostop = -40
        
    if close:
        M["finger1"].addForce((0,0,-gripForce), True)
        M["finger2"].addForce((0,0,gripForce), True)
        pos = (slider_finger1.position - slider_finger2.position)/2
        pos = min(pos, 40)
        pos = max(pos, 10)
        slider_finger1.histop = pos+0.1
        slider_finger2.lostop = -pos-0.1

    M["finger1"].setLinearVel((0,0,0))
    M["finger2"].setLinearVel((0,0,0))
    M["finger1"].setAngularVel((0,0,0))
    M["finger2"].setAngularVel((0,0,0))
    

def tick():
    lock = threading.Lock()
    lock.acquire()
    try:
        #print RobotSim.currentJointPos
        setRobotPos(RobotSim.currentJointPos)
        setGripperForces(RobotSim.sig_open, RobotSim.sig_close)
        

        # avans la urmatorul punct pe traiectorie
        
        if RobotSim.arm_trajectory_index < len(RobotSim.arm_trajectory) - 1:
            RobotSim.arm_trajectory_index = RobotSim.arm_trajectory_index + 1
            RobotSim.currentJointPos = RobotSim.arm_trajectory[RobotSim.arm_trajectory_index].J
    finally:
		lock.release() 
    

    
eventmanager.connect(STEP_FRAME, tick) 




prop = ODEContactProperties(bounce = 0, mu = 10000, soft_erp=0.2, soft_cfm=0.001)
ode = ODEDynamics(gravity=9.81*100, substeps=30, cfm=1E-5, erp=0.2, defaultcontactproperties = prop)\
               #show_contacts=1, contactmarkersize=1, contactnormalsize=100)
# category bits:
# 1 = robot (se ciocneste de piese)
# 2 = floor (se ciocneste de piese)
# 4 = piese (se ciocneste de orice)



floorPlane = Plane()
floorPlane.pos = (0,0,-50)
ode.add(floor, categorybits=2, collidebits=6)
ode.add(floorPlane, categorybits=2, collidebits=6)
ode.add(base,  categorybits=1, collidebits=0)
ode.add(link1,  categorybits=1, collidebits=0)
ode.add(link2,  categorybits=1, collidebits=0)
ode.add(link3,  categorybits=1, collidebits=0)
ode.add(link4,  categorybits=1, collidebits=0)
ode.add(link5,  categorybits=1, collidebits=0)
ode.add(link6,  categorybits=1, collidebits=0)
ode.add(gripper,  categorybits=1, collidebits=4)
ode.add(finger1,  categorybits=1, collidebits=4)
ode.add(finger2,  categorybits=1, collidebits=4)


boxes = []
for i in range(5):
    b = Box("Box1", lx=100,ly=30,lz=15,material=GLMaterial(diffuse=(random.uniform(0,1), random.uniform(0,0.5), random.uniform(0,1))))
    b.mass = 0.001
    ode.add(b, categorybits=4, collidebits=7)
    boxes.append(b)
    
    

base.setOffsetTransform(mat4(1))
link1.setOffsetTransform(mat4(1))
link2.setOffsetTransform(mat4(1))
link3.setOffsetTransform(mat4(1))
link4.setOffsetTransform(mat4(1))
link5.setOffsetTransform(mat4(1))
link6.setOffsetTransform(mat4(1))
gripper.setOffsetTransform(mat4(1))
finger1.setOffsetTransform(mat4(1))
finger2.setOffsetTransform(mat4(1))

M = {}
M["floor"] = ode.createBodyManipulator(floor)
M["base"] = ode.createBodyManipulator(base)
M["link1"] = ode.createBodyManipulator(link1)
M["link2"] = ode.createBodyManipulator(link2)
M["link3"] = ode.createBodyManipulator(link3)
M["link4"] = ode.createBodyManipulator(link4)
M["link5"] = ode.createBodyManipulator(link5)
M["link6"] = ode.createBodyManipulator(link6)
M["gripper"] = ode.createBodyManipulator(gripper)
M["finger1"] = ode.createBodyManipulator(finger1)
M["finger2"] = ode.createBodyManipulator(finger2)


setRobotPos([0, -90, 90, 0, 0, 0], 0)
slider_finger1 = ODESliderJoint("Slider for Finger 1", gripper, finger1)
slider_finger2 = ODESliderJoint("Slider for Finger 2", gripper, finger2)
slider_finger1.histop = 40
slider_finger1.lostop = 10

slider_finger2.lostop = -40
slider_finger2.histop = -10

ode.add(slider_finger1)
ode.add(slider_finger2)

#for i in scene.walkWorld():
#    i.mass = i.mass / 100


MyThread().start()


def randomizeBoxes():
    for b in boxes:
        mb = ode.createBodyManipulator(b)
        r = random.uniform(400, 600)
        a = random.uniform(0, 360)
        x = r * COS(a)
        y = r * SIN(a)
        mb.setPos((x,y,10))
        mb.setRot(mat3(1).toList())

randomizeBoxes()



def listBoxes():
    for b in boxes:
        print b.pos


boxloc = NULL
def pickBox(i):
    global boxloc
    p = worldObject("Box%d"%i).pos
    boxloc = TRANS(p[0],p[1],100,0,180,90)
    OPENI()
    APPRO(boxloc, 100)
    BREAK()
    MOVES(boxloc)
    CLOSEI()
    DEPARTS(100)
    


#def EXEC(prog):
#    execfile("robot-programs/%s.py"%prog)


# Obiecte care vor fi disponibile programelor robot
vplus.worldObject = worldObject
