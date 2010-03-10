from math import *

def load_robot_link(file, name):
	print "Loading %s ..." % name
	load(file)
	obj = worldObject("VCG")
	obj.name = name
	obj.mass = 0.1


load_robot_link('hi/base.stl', 'Robot Base')
load_robot_link('hi/link1.stl', 'Robot Link 1')
load_robot_link('hi/link2.stl', 'Robot Link 2')
load_robot_link('hi/link3.stl', 'Robot Link 3')
load_robot_link('hi/link4.stl', 'Robot Link 4')
load_robot_link('hi/link5.stl', 'Robot Link 5-6')

base = worldObject("Robot Base")
link1 = worldObject("Robot Link 1")
link2 = worldObject("Robot Link 2")
link3 = worldObject("Robot Link 3")
link4 = worldObject("Robot Link 4")
link5 = worldObject("Robot Link 5-6")



base.pos = (0,0,0)
link1.pos = (0, 0, 203)
link2.pos = (75, 0, 335)
link3.pos = (75, 0, 335 + 270)
link4.pos = (75 + 108, 0, 335 + 270 + 90)
link5.pos = (75 + 295, 0, 335 + 270 + 90)


link(link2, link1)
link(link1, base)
link(link3, link2)
link(link4, link3)
link(link5, link4)


e1 = Expression("mat3(1).rotate(sin(t), vec3(0,0,1))")
e2 = Expression("mat3(1).rotate(sin(3*t)/3, vec3(0,1,0))")
e3 = Expression("mat3(1).rotate(cos(2*t)/3, vec3(0,1,0))")
e4 = Expression("mat3(1).rotate(t, vec3(1,0,0))")
e5 = Expression("mat3(1).rotate(cos(10*t)*pi/2, vec3(0,1,0))")

e1.output_slot.connect(link1.rot_slot)
e2.output_slot.connect(link2.rot_slot)
e3.output_slot.connect(link3.rot_slot)
e4.output_slot.connect(link4.rot_slot)
e5.output_slot.connect(link5.rot_slot)

