
# Materiale pentru randare si contact properties

matRobot = GLMaterial(name="robot", diffuse=(1,0.95,0.9))
matFloor = GLMaterial(name="floor", diffuse=(0,1,1))
matGripper = GLMaterial(name="gripper", diffuse=(0.5,0.5,0.5))
matPallet = GLMaterial(name="pallet", diffuse=(1,1,1))
matConveyorRunning = GLMaterial(name="conveyor running", diffuse=(0.3,0.3,1))
matConveyorStopped = GLMaterial(name="conveyor stopped", diffuse=(0.25,0.25,0.9))

matRedBox = GLMaterial(name="RedBox", diffuse=(1,0,0))
matYellowBox = GLMaterial(name="YellowBox", diffuse=(1,1,0))
matGreenBox = GLMaterial(name="GreenBox", diffuse=(0,1,0))
matBlueBox = GLMaterial(name="BlueBox", diffuse=(0,0,1))
matPinkBox = GLMaterial(name="PinkBox", diffuse=(1,0,1))
matCyanBox = GLMaterial(name="PinkBox", diffuse=(0,1,1))
matLightBlueBox = GLMaterial(name="PinkBox", diffuse=(0.7,0.7,1))
matBoxes = [matRedBox, matYellowBox, matGreenBox, matBlueBox, matPinkBox, matCyanBox, matLightBlueBox]

# category bits:
# 1 = robot (se ciocneste de piese)
# 2 = floor (se ciocneste de piese)
# 4 = piese (se ciocneste de orice)

CB_ROBOT = 1
CB_FLOOR = 2
CB_PARTS = 4
CB_PEN_BALLPOINT = 1024
CB_PEN_SUPPORT = 2048
CB_PAPER = 4096
CB_PEN_HANDLE = CB_PARTS


# functii pentru env

def resizeBox(box, size):
    (box.lx, box.ly, box.lz) = size
    box.manip.odegeoms[0].getGeom().setLengths(size)


def setSizePosRot(box, size, pos, rot):
    mb = box.manip
    box.lx = size[0]
    box.ly = size[1]
    box.lz = size[2]

    mb.setPos(pos)
    mb.setRot(rot)

    mb.body.geom.lx = box.lx
    mb.body.geom.ly = box.ly
    mb.body.geom.lz = box.lz
    
    mb.setLinearVel((0,0,0))
    mb.setAngularVel((0,0,0))

    #~ for b in odeSim.bodies:
        #~ if b.odebody == mb.odebody:
            #~ b.odegeoms[0].getGeom().setLengths(size)
            #~ b.odegeoms[0].setCollideBits(7)
            #~ b.odegeoms[0].getGeom().setCollideBits(7)
