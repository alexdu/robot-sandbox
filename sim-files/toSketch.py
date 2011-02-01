#       toSketch.py
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

# Exports current cgkit scene as a Sketch drawing (useful for including in documents)

sketchTemplate = """
def rgb<>
def limb<>
input{lib/defaults.sk}
{
    input{lib/objects.sk}
    def style [cull=false, draw=black, fill=black!5]
    {coordsys}

    %s
    
}

global {
    language tikz
    camera %s * scale(20) then translate([0,0,-100]) then perspective(30)
}
"""

def trans2sk(T):
    sk = "[[%g,%g,%g,%g] [%g,%g,%g,%g] [%g,%g,%g,%g] [%g,%g,%g,%g]]" % tuple(T.toList(True))
    return sk

base.meshname = "base"
link1.meshname = "link1"
link2.meshname = "link2"
link3.meshname = "link3"
link4.meshname = "link4"
link5.meshname = "link5"
link6.meshname = "link6"
gripper.meshname = "grip"

def toSketch(filename):
    scene = getScene()
    cam = worldObject('TargetCamera')
    lookat = cam.worldtransform * (0,0,1)
    skcam = "view((%g,%g,%g),(%g,%g,%g),[%g,%g,%g])" % (cam.pos.x, cam.pos.y, cam.pos.z, lookat.x, lookat.y, lookat.z, scene.up.x, scene.up.y, scene.up.z)
    sk = ""
    for b in getScene().walkWorld():
        if not b.visible: continue
        sk += "\n    # %s\n" % b.name
        if type(b.geom) == cgkit.boxgeom.BoxGeom:
           sk += "    put {%s * scale([%g,%g,%g])}{box}\n" % (trans2sk(b.worldtransform), b.lx,b.ly,b.lz)
        elif hasattr(b, 'meshname'):
           sk += "    put {%s * scale(0.001) * rotate(180,[Z])}{input{meshes/%s.sk}{%s}}\n" % (trans2sk(b.worldtransform), b.meshname, b.meshname)
    ske = sketchTemplate % (sk,skcam)

    skf = open(os.path.join(sys.basepath, "sketch", filename + ".sk"), "w")
    skf.write(ske)
    skf.close()
