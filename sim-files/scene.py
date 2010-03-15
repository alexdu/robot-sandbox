#       scene.py#       #       Copyright 2010 Alex Dumitrache <alex@cimr.pub.ro>#       #       This program is free software; you can redistribute it and/or modify#       it under the terms of the GNU General Public License as published by#       the Free Software Foundation; either version 2 of the License, or#       (at your option) any later version.#       #       This program is distributed in the hope that it will be useful,#       but WITHOUT ANY WARRANTY; without even the implied warranty of#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the#       GNU General Public License for more details.#       #       You should have received a copy of the GNU General Public License#       along with this program; if not, write to the Free Software#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,#       MA 02110-1301, USA.

from __future__ import division
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
link6 = Box("Gripper Mounting Support", lx = 50E-3, ly = 30E-3, lz = 30E-3, mass=0.1)
#gripper = Box(lx = 15, ly = 15, lz = 30, mass=1)
gripper = Box("Gripper", lx = 20E-3, ly = 30E-3, lz = 100E-3, mass=1)
finger1 = Box("Gripper Finger 1", lx = 30E-3, ly = 30E-3, lz = 15E-3, mass=0.001)
finger2 = Box("Gripper Finger 2", lx = 30E-3, ly = 30E-3, lz = 15E-3, mass=0.001)


matFloor = GLMaterial(diffuse=(0,1,1))
floor = Box("Floor", lx=1500E-3, ly=1500E-3, lz=50E-3, material=matFloor)
floor.mass = 1
floor.pos = (0,0,-25E-3)




## link(link2, link1, relative=True)
## link(link1, base, relative=True)





global t
t = 0

def enforceSpeedLimit(maxspeed):
    for b in scene.walkWorld():
        if b.linearvel.length() > maxspeed:
            odeSim.createBodyManipulator(b).setLinearVel(b.linearvel.normalize() * maxspeed)
            print "speed limit exceeded"
        if b.angularvel.length() > maxspeed:
            odeSim.createBodyManipulator(b).setAngularVel(b.angularvel.normalize() * maxspeed)
            print "angular vel limit exceeded"
            

def enforcePose(m, P):
    #~ if int(scene._timer.frame) |MOD| 30 == 0:
    if True:
        oldPos = m.body.pos
        (pos,b,c) = P.decompose()
        m.setRot(P.getMat3().inverse().toList())
        m.setPos(pos)
        m.setLinearVel((0,0,0))
        m.setAngularVel((0,0,0))
        m.odebody.setGravityMode(False)

def changePose(m, P):
    #if int(scene._timer.frame) |MOD| 30 == 0:
        oldPos = m.body.pos
        (pos,b,c) = P.decompose()
        dt = 1/RobotSim.fps
        vel = (pos - oldPos).__div__(dt)
        m.setLinearVel(vel)
        
        oldRot = m.body.rot
        rot = P.getMat3()
        rotDif = quat(oldRot * rot.inverse()).inverse().toAngleAxis()
        angle = rotDif[0]
        axis = rotDif[1]
        v = angle/dt
        
        #m.setPos(pos)
        
        m.setAngularVel((axis[0] * v, axis[1] * v, axis[2] * v))



def enforceRobotPos(J, grip_pos = -1):

    j = (mat(J) * pi/180).tolist()[0]

    R = mat4(1)
    P = R
    enforcePose(M["base"], P)
    P = R.rotation(j[0], (0,0,1)) * R.translation((0,0,203E-3)) * P
    enforcePose(M["link1"], P)
    P = P * R.translation((75E-3,0,335E-3 - 203E-3)) * R.rotation(j[1]+pi/2, (0,1,0))
    enforcePose(M["link2"], P)
    P = P * R.translation((0,0,270E-3)) * R.rotation(j[2]-pi, (0,1,0))
    enforcePose(M["link3"], P)
    P = P * R.translation((108E-3,0,90E-3)) * R.rotation(j[3], (1,0,0))
    enforcePose(M["link4"], P)
    P = P * R.translation((295E-3 - 108E-3,0,0)) * R.rotation(j[4], (0,1,0))
    enforcePose(M["link5"], P)
    P = P * R.translation((80E-3 + 20E-3,0,0)) * R.rotation(j[5], (1,0,0))
    enforcePose(M["link6"], P)
    P = P * R.translation((20E-3 + 15E-3,0,0))
    enforcePose(M["gripper"], P)

    enforcePose(M["floor"], R.translation((0,0,-25E-3)))

    if grip_pos >= 0:
        P1 = P * R.translation((10E-3 + 15E-3,0, grip_pos))
        enforcePose(M["finger1"], P1)
        P2 = P * R.translation((10E-3 + 15E-3,0,-grip_pos))
        enforcePose(M["finger2"], P2)


def changeRobotPos(J):

    j = (mat(J) * pi/180).tolist()[0]

    R = mat4(1)
    P = R
    changePose(M["base"], P)
    P = R.rotation(j[0], (0,0,1)) * R.translation((0,0,203E-3)) * P
    changePose(M["link1"], P)
    P = P * R.translation((75E-3,0,335E-3 - 203E-3)) * R.rotation(j[1]+pi/2, (0,1,0))
    changePose(M["link2"], P)
    P = P * R.translation((0,0,270E-3)) * R.rotation(j[2]-pi, (0,1,0))
    changePose(M["link3"], P)
    P = P * R.translation((108E-3,0,90E-3)) * R.rotation(j[3], (1,0,0))
    changePose(M["link4"], P)
    P = P * R.translation((295E-3 - 108E-3,0,0)) * R.rotation(j[4], (0,1,0))
    changePose(M["link5"], P)
    P = P * R.translation((80E-3 + 20E-3,0,0)) * R.rotation(j[5], (1,0,0))
    changePose(M["link6"], P)
    P = P * R.translation((20E-3 + 15E-3,0,0))
    changePose(M["gripper"], P)




def setGripperForces(open, close):
    gripForce = 10
    slider_finger1.motorfmax = gripForce
    slider_finger2.motorfmax = gripForce
    slider_finger1.fudgefactor = 0
    slider_finger2.fudgefactor = 0
    
    if open:
        gripForce = 0.1
        slider_finger1.motorvel = 0.1
        slider_finger2.motorvel = -0.1
        slider_finger1.histop = 40E-3
        slider_finger2.lostop = -40E-3
    if close:
        slider_finger1.motorvel = -0.5
        slider_finger1.motorfmax = gripForce

        slider_finger2.motorvel = 0.5
        slider_finger2.motorfmax = gripForce
        
        pos = abs(slider_finger2.position)
        pos = min(pos, 40E-3)
        pos = max(pos, 10E-3)
        slider_finger1.histop = pos + 0.1E-3
        slider_finger1.lostop = pos - 5E-3
        slider_finger2.histop = -pos + 5E-3
        slider_finger2.lostop = -pos - 0.1E-3
        
        #slider_finger2.lostop = -pos-0.01E-3
        
    #~ if open:
        #~ M["finger1"].addForce((0,0,gripForce), True)
        #~ M["finger2"].addForce((0,0,-gripForce), True)
        #~ slider_finger1.histop = 40
        #~ slider_finger2.lostop = -40
        
    #~ if close:
        #~ M["finger1"].addForce((0,0,-gripForce), True)
        #~ M["finger2"].addForce((0,0,gripForce), True)
        #~ pos = (slider_finger1.position - slider_finger2.position)/2
        #~ pos = min(pos, 40)
        #~ pos = max(pos, 10)
        #~ slider_finger1.histop = pos+0.1
        #~ slider_finger2.lostop = -pos-0.1

    #~ M["finger1"].setLinearVel((0,0,0))
    #~ M["finger2"].setLinearVel((0,0,0))
    #~ M["finger1"].setAngularVel((0,0,0))
    #~ M["finger2"].setAngularVel((0,0,0))
    #~ 

RobotSim.pauseTick = False

def tick():
    if int(scene._timer.frame) == 1:
        programspath = os.path.normpath(os.path.join(os.getcwd(), "..", "robot-programs"))
        os.chdir(programspath)

    if int(scene._timer.frame) |MOD| 10 == 1:
        jobs._status_new()
        if len(jobs.jobs_comp) > 0:
            jobs.flush_finished()
        


    while RobotSim.pauseTick:
        time.sleep(0.1)

    lock = threading.Lock()
    lock.acquire()
    try:
        #print RobotSim.currentJointPos
        setGripperForces(RobotSim.sig_open, RobotSim.sig_close)
        
        changeRobotPos(RobotSim.currentJointPos)
        enforceSpeedLimit(50) # ca sa nu crape ODE

        # avans la urmatorul punct pe traiectorie
        
        if RobotSim.arm_trajectory_index < len(RobotSim.arm_trajectory) - 1:
            RobotSim.arm_trajectory_index = RobotSim.arm_trajectory_index + 1
            RobotSim.currentJointPos = RobotSim.arm_trajectory[RobotSim.arm_trajectory_index].J
    finally:
        lock.release() 
    

    
eventmanager.connect(STEP_FRAME, tick) 

    


prop = ODEContactProperties(bounce = 0, mu = ode.Infinity, soft_erp=0.1, soft_cfm=1E-4)
odeSim = ODEDynamics(gravity=9.81/5, substeps=10, cfm=1E-3, erp=0.5, defaultcontactproperties = prop,
               show_contacts=0, contactmarkersize=1E-3, contactnormalsize=0.1)
# category bits:
# 1 = robot (se ciocneste de piese)
# 2 = floor (se ciocneste de piese)
# 4 = piese (se ciocneste de orice)




floorPlane = Plane()
floorPlane.pos = (0,0,-50E-3)

odeSim.add(floor, categorybits=2, collidebits=4)
odeSim.add(floorPlane, categorybits=2, collidebits=4)
odeSim.add(base,  categorybits=1, collidebits=0)
odeSim.add(link1,  categorybits=1, collidebits=4)
odeSim.add(link2,  categorybits=1, collidebits=4)
odeSim.add(link3,  categorybits=1, collidebits=4)
odeSim.add(link4,  categorybits=1, collidebits=4)
odeSim.add(link5,  categorybits=1, collidebits=4)
odeSim.add(link6,  categorybits=1, collidebits=4)
odeSim.add(gripper,  categorybits=1, collidebits=6)
odeSim.add(finger1,  categorybits=1, collidebits=6)
odeSim.add(finger2,  categorybits=1, collidebits=6)



boxes = []
for i in range(20):
    b = Box("Box1", lx=100E-3,ly=30E-3,lz=15E-3,material=GLMaterial(diffuse=(random.uniform(0,1), random.uniform(0,0.5), random.uniform(0,1))))
    b.mass = 1E-2
    b.pos = (0.5, 0.5, -0.01)
    boxes.append(b)
    odeSim.add(b, categorybits=4, collidebits=0)
    odeSim.createBodyManipulator(b).odebody.setKinematic()

def resetBoxes():
    RobotSim.pauseTick = True
    try:
        time.sleep(0.1)
    
        for b in boxes:
            mb = odeSim.createBodyManipulator(b)
            mb.odebody.setKinematic()
            b.mass = 1E-2
            mb.setPos((0.5, 0.5, -0.01))
            mb.setRot(mat3(1).toList())
            b.lx = 100E-3
            b.ly = 30E-3
            b.lz = 15E-3
            mb.odebody.disable()
            for ob in odeSim.bodies:
                if ob.odebody == mb.odebody:
                    ob.odegeoms[0].setCollideBits(0)
                    ob.odegeoms[0].getGeom().setCollideBits(0)
            
    finally:
        RobotSim.pauseTick = False

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
M["floor"] = odeSim.createBodyManipulator(floor)
M["base"] = odeSim.createBodyManipulator(base)
M["link1"] = odeSim.createBodyManipulator(link1)
M["link2"] = odeSim.createBodyManipulator(link2)
M["link3"] = odeSim.createBodyManipulator(link3)
M["link4"] = odeSim.createBodyManipulator(link4)
M["link5"] = odeSim.createBodyManipulator(link5)
M["link6"] = odeSim.createBodyManipulator(link6)
M["gripper"] = odeSim.createBodyManipulator(gripper)
M["finger1"] = odeSim.createBodyManipulator(finger1)
M["finger2"] = odeSim.createBodyManipulator(finger2)


M["floor"].odebody.setKinematic()



enforceRobotPos([0, -90, 90, 0, 0, 0], 0)
slider_finger1 = ODESliderJoint("Slider for Finger 1", gripper, finger1)
slider_finger2 = ODESliderJoint("Slider for Finger 2", gripper, finger2)
slider_finger1.histop = 40E-3
slider_finger1.lostop = 10E-3

slider_finger2.lostop = -40E-3
slider_finger2.histop = -10E-3



odeSim.add(slider_finger1)
odeSim.add(slider_finger2)






def stdevBoxes():
    x = numpy.zeros(len(boxes))
    y = x + 0
    for i, b in enumerate(boxes):
        x[i] = b.pos[0]
        y[i] = b.pos[1]
    sx = numpy.std(x)
    sy = numpy.std(y)
    print sx, sy

def listBoxes():
    for b in boxes:
        print b.pos


boxloc = NULL
def pickBox(i):
    global boxloc
    p = worldObject("Box%d"%i).pos * 1000
    boxloc = TRANS(p[0],p[1],100,0,180,90)
    OPENI()
    APPRO(boxloc, 100)
    BREAK()
    MOVES(boxloc)
    CLOSEI()
    DEPARTS(100)
    BREAK()
    MOVE(safe)



# pentru env

def setSizePosRot(box, size, pos, rot):
    mb = odeSim.createBodyManipulator(box)
    box.lx = size[0]
    box.ly = size[1]
    box.lz = size[2]
    mb.body.geom.lx = box.lx
    mb.body.geom.ly = box.ly
    mb.body.geom.lz = box.lz
    
    mb.setPos(pos)
    mb.setRot(rot)
    mb.odebody.setDynamic()
    mb.odebody.enable()
    mb.setLinearVel((0,0,0))
    mb.setAngularVel((0,0,0))
    

    for b in odeSim.bodies:
        if b.odebody == mb.odebody:
            b.odegeoms[0].getGeom().setLengths(size)
            b.odegeoms[0].setCollideBits(7)
            b.odegeoms[0].getGeom().setCollideBits(7)








execfile("console.py")





