
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
matCyanBox = GLMaterial(name="CyanBox", diffuse=(0,1,1))
matLightBlueBox = GLMaterial(name="LightBlueBox", diffuse=(0.7,0.7,1))
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

def createBoxStack(n, 
                   pos = (0,0,0), 
                   rot = mat3(1),
                   size = (100E-3, 30E-3, 15E-3),
                   material=matRedBox, 
                   mass = 1E-2, 
                   name = "Box", 
                   kinematic = False):
    """
    
    Create a stack of boxes (useful in environments).
    
    
    Args     |  meaning                    | default value
    ---------+-----------------------------+--------------
    pos      | stack bottom position       | (0,0,0)
    rot      | box orientation             | mat3(1)
    size     | box size                    | (100E-3, 30E-3, 15E-3)
    material | material for rendering and  | matRedBox
             |   contact properties        | 
    mass     | box mass                    | 1E-2
    name     | name root (=> Box1,Box2...) | "Box"
    kinematic| ODE kinematic flag          | False 
             | TRUE => not influenced      |
             |   by external forces        |
    """
    boxes = []
    
    if n > 1:
        name += "1"
    
    for i in range(n):
        b = Box(name, lx=size[0],ly=size[1],lz=size[2],material=material, mass=mass)
        (x,y,z) = pos
        z += i * size[2] * 1.1
        b.pos = (x,y,z)
        b.rot = rot
            
        boxes.append(b)
        odeSim.add(b, categorybits=CB_PARTS, collidebits=CB_PARTS|CB_FLOOR|CB_ROBOT)
        if kinematic:
            b.manip.odebody.setKinematic()

    eventmanager.event(NEW_BOX_CREATED)

    return boxes


def rx(ang):
    return mat3(1).rotate(radians(ang), (1,0,0))
def ry(ang):
    return mat3(1).rotate(radians(ang), (0,1,0))
def rz(ang):
    return mat3(1).rotate(radians(ang), (0,0,1))
def rotaa(angle, axis):
    return mat3(1).rotate(radians(ang), axis)


def redge(x, x_prev):
    return bool(x) and not bool(x_prev)
    
def fedge(x, x_prev):
    return not bool(x) and bool(x_prev)
