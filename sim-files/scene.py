
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
import OpenGL.GL as GL
from copy import copy

ENV_RESET = "EnvReset"
NEW_BOX_CREATED = "NewBoxCreated"

execfile("env.py")
execfile("ConveyorBelt.py")
execfile("PartSensor.py")
execfile("PartDispenser.py")
execfile("PenAndPaper.py")
execfile("PalletDispenser.py")
execfile("BlackHole.py")

defaultContactProps = ODEContactProperties(bounce = 0, mu = 0.1, soft_erp=0.2, soft_cfm=1E-4)
contactProps_BoxBox = ODEContactProperties(bounce = 0, mu = 0.1, soft_erp=0.1, soft_cfm=1E-4)
contactProps_PalBox = ODEContactProperties(bounce = 0, mu = 0.1, soft_erp=0.2, soft_cfm=1E-6)
contactProps_FloorBox = ODEContactProperties(bounce = 0, mu = 0.1, soft_erp=0.2, soft_cfm=1E-6)
contactProps_GripBox = ODEContactProperties(bounce = 0, mu = 100, soft_erp=0.2, soft_cfm=0.0001)
contactProps_GripPal = ODEContactProperties(bounce = 0, mu = 10, soft_erp=0.2, soft_cfm=0.0001)

contactProps_ConveyorBox_Running = ODEContactProperties(bounce = 0.5, mu = 0.1, soft_erp=0.2, soft_cfm=1E-6, motion1 = 0.1, fdir1 = (1,0,0))
contactProps_ConveyorBox_Stopped = ODEContactProperties(bounce = 0.5, mu = 0.1, soft_erp=0.2, soft_cfm=1E-6)

contactProps_ConveyorPal_Running = ODEContactProperties(bounce = 0, mu = 10, soft_erp=0.2, soft_cfm=1E-6, motion1 = 0.1, fdir1 = (1,0,0))
contactProps_ConveyorPal_Stopped = ODEContactProperties(bounce = 0, mu = 10, soft_erp=0.2, soft_cfm=1E-6)


odeSim = ODEDynamics(gravity=9.81/5, substeps=2, cfm=1E-5, erp=0.2, defaultcontactproperties = defaultContactProps,
               show_contacts=0, contactmarkersize=1E-3, contactnormalsize=0.1, use_quick_step = False, collision_events = True)

odeSim.world.setLinearDamping(0.01)
odeSim.world.setAngularDamping(0.01)
odeSim.world.setContactMaxCorrectingVel(1)
odeSim.world.setContactSurfaceLayer(1E-10)
odeSim.world.setAutoDisableFlag(True)
odeSim.world.setAutoDisableLinearThreshold(0.01)
odeSim.world.setAutoDisableAngularThreshold(0.01)
odeSim.world.setMaxAngularSpeed(100)


odeSim.setContactProperties((matPallet, matConveyorRunning), contactProps_ConveyorPal_Running)
odeSim.setContactProperties((matPallet, matConveyorStopped), contactProps_ConveyorPal_Stopped)

odeSim.setContactProperties((matGripper, matPallet), contactProps_GripPal)

for matBox in matBoxes:
    odeSim.setContactProperties((matGripper, matBox), contactProps_GripBox)
    odeSim.setContactProperties((matFloor, matBox), contactProps_FloorBox)
    odeSim.setContactProperties((matPallet, matBox), contactProps_PalBox)
    odeSim.setContactProperties((matBox, matConveyorRunning), contactProps_ConveyorBox_Running)
    odeSim.setContactProperties((matBox, matConveyorStopped), contactProps_ConveyorBox_Stopped)

#odeSim.setContactProperties((matConveyor, matFloor), contactProps_ConveyorBox)

for matBox1 in matBoxes:
    for matBox2 in matBoxes:
        odeSim.setContactProperties((matBox1, matBox2), contactProps_BoxBox)


def load_robot_link(file, name):
    print "Loading %s ..." % name
    load(file)
    obj = worldObject("vcg")
    obj.name = name
    obj.mass = 0.1
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
gripper = Box("Gripper", lx = 20E-3, ly = 30E-3, lz = 100E-3, mass=100, material=matGripper)
finger1 = Box("Gripper Finger 1", lx = 30E-3, ly = 30E-3, lz = 15E-3, mass=0.1, material=matGripper)
finger2 = Box("Gripper Finger 2", lx = 30E-3, ly = 30E-3, lz = 15E-3, mass=0.1, material=matGripper)

floor = Box("Floor", lx=1500E-3, ly=1500E-3, lz=50E-3, material=matFloor)
floor.mass = 1
floor.pos = (0,0,-25E-3)




def setGripperForces(open, close):
    if open:
        slider_finger1.histop = slider_finger1.lostop = 40E-3
        slider_finger2.histop = slider_finger2.lostop = -40E-3
    if close: 
        pos = max(10e-3, slider_finger1.histop - 10e-3)
        slider_finger1.histop = slider_finger1.lostop = pos
        slider_finger2.histop = slider_finger2.lostop = -pos
        

def enforcePose(m, P):
    #~ if int(scene._timer.frame) |MOD| 30 == 0:
    if True:
        
        m.odebody.enable()
        
        oldPos = m.body.pos
        (pos,b,c) = P.decompose()
        m.setRot(P.getMat3())
        m.setPos(pos)
        m.setLinearVel((0,0,0))
        m.setAngularVel((0,0,0))
        m.odebody.setGravityMode(False)

def changePose(m, P):
    #~ if int(scene._timer.frame) % 30 == 15:
    
        m.odebody.enable()
        
        oldPos = m.body.pos
        pos = P.decompose()[0]
        dt = 1/RobotSim.fps
        vel = (pos - oldPos).__div__(dt)
        m.setLinearVel(vel)
        
        oldRot = m.body.rot
        rot = P.getMat3()
        rotDif = quat(rot * oldRot.inverse()).toAngleAxis()
        angle = rotDif[0]
        axis = rotDif[1]
        v = angle/dt
        
        
        
        #m.setPos(pos)
        
        m.setAngularVel((axis[0] * v, axis[1] * v, axis[2] * v))

        


def enforceRobotPos(J, grip_pos = -1):

    j = (mat(J) * pi/180).tolist()[0]

    R = mat4(1)
    P = R
    enforcePose(base.manip, P)
    P = R.rotation(j[0], (0,0,1)) * R.translation((0,0,203E-3)) * P
    enforcePose(link1.manip, P)
    P = P * R.translation((75E-3,0,335E-3 - 203E-3)) * R.rotation(j[1]+pi/2, (0,1,0))
    enforcePose(link2.manip, P)
    P = P * R.translation((0,0,270E-3)) * R.rotation(j[2]-pi, (0,1,0))
    enforcePose(link3.manip, P)
    P = P * R.translation((108E-3,0,90E-3)) * R.rotation(j[3], (1,0,0))
    enforcePose(link4.manip, P)
    P = P * R.translation((295E-3 - 108E-3,0,0)) * R.rotation(j[4], (0,1,0))
    enforcePose(link5.manip, P)
    P = P * R.translation((80E-3 + 20E-3,0,0)) * R.rotation(j[5], (1,0,0))
    enforcePose(link6.manip, P)
    P = P * R.translation((20E-3 + 15E-3,0,0))
    enforcePose(gripper.manip, P)

    enforcePose(floor.manip, R.translation((0,0,-25E-3)))

    if grip_pos >= 0:
        P1 = P * R.translation((10E-3 + 15E-3,0, grip_pos))
        enforcePose(finger1.manip, P1)
        P2 = P * R.translation((10E-3 + 15E-3,0,-grip_pos))
        enforcePose(finger2.manip, P2)


def changeRobotPos(J):

    j = (mat(J) * pi/180).tolist()[0]

    R = mat4(1)
    P = R
    changePose(base.manip, P)
    P = R.rotation(j[0], (0,0,1)) * R.translation((0,0,203E-3)) * P
    changePose(link1.manip, P)
    P = P * R.translation((75E-3,0,335E-3 - 203E-3)) * R.rotation(j[1]+pi/2, (0,1,0))
    changePose(link2.manip, P)
    P = P * R.translation((0,0,270E-3)) * R.rotation(j[2]-pi, (0,1,0))
    changePose(link3.manip, P)
    P = P * R.translation((108E-3,0,90E-3)) * R.rotation(j[3], (1,0,0))
    changePose(link4.manip, P)
    P = P * R.translation((295E-3 - 108E-3,0,0)) * R.rotation(j[4], (0,1,0))
    changePose(link5.manip, P)
    P = P * R.translation((80E-3 + 20E-3,0,0)) * R.rotation(j[5], (1,0,0))
    changePose(link6.manip, P)
    P = P * R.translation((20E-3 + 15E-3,0,0))
    changePose(gripper.manip, P)





RobotSim.pauseTick = False

def tick():
    t0 = time.time()
    frameno = int(scene._timer.frame)
    if frameno == 1:
        
        # some dirty init
        
        programspath = os.path.normpath(os.path.join(os.getcwd(), "..", "robot-programs"))
        os.chdir(programspath)

        cam = worldObject("TargetCamera")
        cam.fov = 40
        cam.pos = (2,1,1)
        cam.target = (0,0,0.2)
        
        #~ _ip = IPython.ipapi.get()
        #~ _ip.runlines("env hanoi")
        #~ _ip.runlines("load hanoi")
        #~ _ip.runlines("speed 100")
        #~ _ip.runlines("exec hanoi_main")
        
        
    while RobotSim.pauseTick:  # la schimbarea environmentului
        time.sleep(0.1)

    RobotSim.fps = scene.timer().fps
    RobotSim.clock += 1/RobotSim.fps

    setGripperForces(RobotSim.sig_open, RobotSim.sig_close)
    changeRobotPos(RobotSim.currentJointPos)

    # avans la urmatorul punct pe traiectorie
    
    RobotSim.Step()


    if frameno % 5 == 0:
        vplus.fileChangePoll()

eventmanager.connect(STEP_FRAME, tick) 





def collision(C):
    if len(C.contacts) > 10:
        C.averageAllContacts()

eventmanager.connect(ODE_COLLISION, collision)




floorPlane = Plane(pos = (0,0,-1000E-3), lx = 0.01, ly = 0.01)

odeSim.add(floor,       categorybits=CB_FLOOR, collidebits=CB_PARTS)
odeSim.add(floorPlane,  categorybits=CB_FLOOR, collidebits=CB_PARTS)
odeSim.add(base,        categorybits=CB_ROBOT, collidebits=0)
odeSim.add(link1,       categorybits=CB_ROBOT, collidebits=CB_PARTS)
odeSim.add(link2,       categorybits=CB_ROBOT, collidebits=CB_PARTS)
odeSim.add(link3,       categorybits=CB_ROBOT, collidebits=CB_PARTS)
odeSim.add(link4,       categorybits=CB_ROBOT, collidebits=CB_PARTS)
odeSim.add(link5,       categorybits=CB_ROBOT, collidebits=CB_PARTS)
odeSim.add(link6,       categorybits=CB_ROBOT, collidebits=CB_PARTS)
odeSim.add(gripper,     categorybits=CB_ROBOT, collidebits=CB_PARTS|CB_FLOOR)
odeSim.add(finger1,     categorybits=CB_ROBOT, collidebits=CB_PARTS|CB_FLOOR)
odeSim.add(finger2,     categorybits=CB_ROBOT, collidebits=CB_PARTS|CB_FLOOR)


    
def resetEnv():

    RobotSim.pauseTick = True
    time.sleep(0.2)
    try:
        print "firing reset event"
        eventmanager.event(ENV_RESET)
        time.sleep(0.2)
            
        gomi = []
        for obj in scene.walkWorld():
            if not hasattr(obj, "keepitsafe"):
                gomi.append(obj)
        
        for obj in gomi:
            odeSim.remove(obj)
            worldroot.removeChild(obj)

        RobotSim.signals = {}
        RobotSim.signals_dirty = True
                    
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
floor.manip.odebody.setKinematic()

enforceRobotPos([0, -90, 90, 0, 0, 0], 0)

slider_finger1 = ODESliderJoint("Slider for Finger 1", gripper, finger1)
slider_finger2 = ODESliderJoint("Slider for Finger 2", gripper, finger2)
slider_finger1.histop = 40E-3
slider_finger1.lostop = 10E-3
slider_finger2.lostop = -40E-3
slider_finger2.histop = -10E-3
slider_finger1.fudgefactor = 0
slider_finger2.fudgefactor = 0
slider_finger1.stopcfm = 1E-3
slider_finger2.stopcfm = 1E-3
slider_finger1.cfm = 1E-5
slider_finger2.cfm = 1E-5


odeSim.add(slider_finger1)
odeSim.add(slider_finger2)


for obj in scene.walkWorld():
    obj.keepitsafe = True





execfile("console.py")





