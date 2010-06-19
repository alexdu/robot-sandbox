# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is the Python Computer Graphics Kit.
#
# The Initial Developer of the Original Code is Matthias Baas.
# Portions created by the Initial Developer are Copyright (C) 2004
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****
# $Id: odedynamics.py,v 1.8 2006/05/26 17:08:04 mbaas Exp $

## \file EZDynamics.py
## Contains a modified version of the cgkit's ODEDynamics class.
## (C) 2010 Alex Dumitrache, alex@cimr.pub.ro
## 

from __future__ import division
import time
import cgkit.all
import cgkit.cmds as cmds
from cgkit.scene import getScene
import cgkit._core as _core
import ode
import weakref
from cgkit.cgtypes import *
from cgkit.all import ODE_COLLISION
import random
import protocols
from cgkit.Interfaces import *
from math import *

def rx(ang):
    return mat3(1).rotate(radians(ang), (1,0,0))
def ry(ang):
    return mat3(1).rotate(radians(ang), (0,1,0))
def rz(ang):
    return mat3(1).rotate(radians(ang), (0,0,1))
def rotaa(angle, axis):
    return mat3(1).rotate(radians(ang), axis)
    
def remove(objs):
    objs = cmds.worldObjects(objs)
    
    for o in objs:
        for c in o.iterChilds():
            remove(c)
        for s in getScene().items:
            if type(s) == ODEDynamics:
                try: s.remove(o)
                except: pass
            if type(s) == cgkit._core.WorldObject:
                try: s.removeChild(o)
                except: pass
        

class ODECollisionEvent(cgkit.odedynamics.ODECollisionEvent):
    

    # averageContactGeom
    def averageContactGeom(self, normal_weight_depth = False):
        """ averageContactGeom(self, normal_weight_depth = False)
            Return the average contact position, normal and depth, and also the two geoms.
            
            If normal_weight_depth is True, normal is weighted using penetration depth.
            This reduces the chances that the contact normal becomes 0 after averaging.
        """
        pos = vec3(0)
        normal = vec3(0)
        depth = 0.0
        for c in self.contacts:
            p,n,d,g1,g2 = c.getContactGeomParams()
            pos += vec3(p)
            normal += vec3(n) * (d if normal_weight_depth else 1)
            depth += d

        # n is not 0 (the event wouldn't have been generated if it was)
        n = len(self.contacts)
        pos /= n
        normal = normal.normalize()      # Normal should be a unit vector (otherwise, ODE crashes)
        depth /= n
        
        return pos,normal,depth,g1,g2
    
    def averageAllContacts(self):
        """
        Merge all contacts from this collision event into a single one, 
        using the average value for position, normal and depth.
        
        Example:
        
        Too many contacts will make the simulation slow, especially with ode.step()
        Simple solution: if there are more than 5 contacts, merge all of them into a single one.
        This decision is taken in the ODE_COLLISION event handler (from the scene).
        
        def collision(C):       # C is an ODECollisionEvent
            if len(C.contacts) > 5: 
                C.averageAllContacts()
            
            # Now, len(C.contacts) => 1
            
        eventmanager.connect(ODE_COLLISION, collision)
        
        This solution may affect the accuracy of collision response between complex 
        geometries, but it is very fast. 
        """
        try:
            print "simplifying contacts..."
            p,n,d,g1,g2 = self.averageContactGeom(True)
            self.contacts[0].setContactGeomParams(p,n,d,g1,g2)
            del self.contacts[1:]
        except ZeroDivisionError: # Contact normal is zero (why?!)
            print "Contact normal is zero, skipping simplification..."
            
        
# ODEDynamics
class ODEDynamics(cgkit.odedynamics.ODEDynamics):
    """Dynamics component using the ODE rigid body dynamics package.
    """
    def __init__(self, *args, **kwargs):
        try: 
            self.randomness = kwargs['randomness']
            del kwargs['randomness']
        except: self.randomness = 0

        cgkit.odedynamics.ODEDynamics.__init__(self, *args, **kwargs)

    # remove
    def remove(self, objs):
        """Remove a world object from the simulation.

        \param objs World objects to be simulated (given as names or objects)
        """
        #~ print "Removing...", objs
        objs = cmds.worldObjects(objs)
        for obj in objs:
            #~ print obj.name
            self._remove(obj)
        #~ print "Removed ", objs
    
    def _remove(self, obj):
        for body in self.bodies:
            if body.obj == obj:
                # after deleting all the references to the body, 
                # PyODE will remove it from simulation (in the destructor)
                self.bodies.remove(body)
                del self.body_dict[obj]
                del body.odegeoms
                del body.odebody
                del obj.odebody
                del obj.odegeoms
                if hasattr(obj, 'manip'):
                    del(obj.manip)
                break
        

    # add
    def add(self, objs, categorybits=None, collidebits=None):
        """Add a world object to the simulation.

        \param objs World objects to be simulated (given as names or objects)
        """
        objs = cmds.worldObjects(objs)
        for obj in objs:
            if obj.mass <= 0 and not isinstance(obj, cgkit.odedynamics.ODEJointBase):
                print "Using default mass=1 for " + str(obj)
                obj.mass = 1
            self._add(obj, categorybits, collidebits)
            if obj in self.body_dict:
                obj.odebody = self.body_dict[obj].odebody
                obj.odegeoms = self.body_dict[obj].odegeoms 
                manip = self.createBodyManipulator(obj)
                if manip != None:
                    obj.manip = manip


    # createBodyManipulator
    def createBodyManipulator(self, obj):
        bm = ODEBodyManipulator(self.body_dict[obj])
        if bm.odebody:
            self.body_manips.append(weakref.ref(bm))
            return bm
        else:
            return None

    # setContactProperties
    def setContactProperties(self, (mat1, mat2), props):
        """Set the contact properties of a pair of materials.

        The contact properties \a props are applied whenever an object
        with material \a mat1 collides with an object with material \a mat2.

        \param mat1 (\c Material) Material 1
        \param mat2 (\c Material) Material 2
        \param props (\c ODEContactProperties) Contact properties
        """
        self.contactprops[(mat1,mat2)] = props  
        # Collision events are forced to appear in (mat1,mat2) order
     
    # getContactProperties
    def getContactProperties(self, matpair):
        """Return the contact properties for a material pair.

        \param matpair A 2-tuple of two Material objects
        \return Contact properties (\c ODEContactProperties)
        """
        cp = self.contactprops.get(matpair)
        if cp==None:
#            print 'ODEDynamics: Warning: No contact properties defined for material "%s" and "%s"'%(matpair[0].name, matpair[1].name)
            cp = self.defaultcontactprops
        return cp
        
    def getContactPropsList(self, matpair):
        cp = self.contactprops.get(matpair)
        if cp==None:
#            print 'ODEDynamics: Warning: No contact properties defined for material "%s" and "%s"'%(matpair[0].name, matpair[1].name)
            cp = self.defaultcontactprops
        return cp.getSurfaceParamsList()

    # nearCallback
    def nearCallback(self, args, geom1, geom2):        
        try:            
            # Force collision event to appear in (mat1, mat2) order
            # (i.e. the order in which the material pair was defined in contactprops)
            if not (geom1.material, geom2.material) in self.contactprops:
                (geom1, geom2) = (geom2, geom1)
        except:
            #print "ups"
            pass

        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # No contacts? then return immediately
        if len(contacts)==0:
            return
        
#        print len(contacts),"contacts"

        # Get the contact properties
        cp = self.getContactProperties((geom1.material, geom2.material))

        # Create a collision event?
        if self.collision_events:
            obj1 = getattr(geom1, "worldobj", None)
            obj2 = getattr(geom2, "worldobj", None)
            evt = ODECollisionEvent(obj1, obj2, contacts, cp)
            self.eventmanager.event(ODE_COLLISION, evt)

        # Some event handler could change the number of contacts (simplify them)
        self.numcontacts += len(contacts) 


        cp = cp.getSurfaceParamsList()
    
        # Create contact joints
        for c in contacts:
            if self.show_contacts:
                p,n,d,g1,g2 = c.getContactGeomParams()
                cmds.drawMarker(p, size=self.contactmarkersize, color=(1,0,0))
                cmds.drawLine(p, vec3(p)+self.contactnormalsize*vec3(n), color=(1,0.5,0.5))
#                print p,n,d
            
            ode.CreateContactJointQ(self.world, self.contactgroup, c, cp, geom1, geom2)
            # Set the properties
            #cp.apply(c)
            # Create the contact joint
            #~ c.setContactSurfaceParams(*cp.getSurfaceParamsList())
            #~ j = ode.ContactJoint(self.world, self.contactgroup, c)
            #~ b1 = geom1.getBody()
            #~ b2 = geom2.getBody()
#            if b1==None:
#                b1=ode.environment
#            if b2==None:
#                b2=ode.environment
            #~ j.attach(b1, b2)
#        time.sleep(0.1)


    def _addRandomness(self):
        #~ print "rand"
        for obj in self.body_dict:
            try:                
                rx = random.gauss(0, self.randomness)
                ry = random.gauss(0, self.randomness)
                rz = random.gauss(0, self.randomness)
                obj.manip.addForce((rx,ry,rz))
            except: 
                pass
    
    def autoAdd(self):
        scene = getScene()
        # Add all rigid bodies first...
        for obj in scene.worldRoot().iterChilds():
            if obj not in self.body_dict:
                try:
                    obj = protocols.adapt(obj, IRigidBody)
                    self.add(obj)
                except NotImplementedError:
                    pass

        # Then add all joints...
        for obj in scene.worldRoot().iterChilds():
            if obj not in self.joints:
                if isinstance(obj, cgkit.odedynamics.ODEJointBase):
                    self.add(obj)
        

    # onStepFrame
    def onStepFrame(self):
        """Callback for the StepFrame event.
        """
        if self.substeps==0 or not self.enabled:
            return
            
        if self.randomness != 0:
            self._addRandomness()

        T0 = time.time()
    
        if self.show_contacts:
            cmds.drawClear()

        # Remove dead body manipulators...
        self.body_manips = filter(lambda x: x() is not None, self.body_manips)

        #~ collision_receivers_present = ODE_COLLISION in eventManager().scene_connections
            
        self.stepTime = 0
        
        # Sim loop...
        subdt = getScene().timer().timestep/self.substeps
        for i in range(self.substeps):
            self.numcontacts = 0
            
            
            # Apply body manipulators
            for bmref in self.body_manips:
                bm = bmref()
                if bm is not None:
                    bm._apply()
            
            # Detect collisions and create contact joints
            self.space.collide(None, self.nearCallback)
            #print "#Contacts:",self.numcontacts

            # Simulation step
            t0 = time.time()
            if self.use_quick_step or self.numcontacts > 100:
                #~ print "quickStep"
                self.world.quickStep(subdt)
            else:
                #~ print "step"
                self.world.step(subdt)
            t1 = time.time()
            self.stepTime = t1 - t0

            # Remove all contact joints
            self.contactgroup.empty()

            
        # Update the world objects
        for body in self.bodies:
            if body.odebody != None and body.odebody.isEnabled():
                body.updateObj()
        
        # Update geoms
        for body in self.bodies:
            try: body.obj.geom.radius = body.odegeoms[0].geom.radius
            except: pass
            try: body.obj.geom.length = body.odegeoms[0].geom.length
            except: pass
            try: body.obj.geom.lx, body.obj.geom.ly, body.obj.geom.lz = body.odegeoms[0].geom.lengths
            except: pass
                

        # Reset body manipulators
        for bmref in self.body_manips:
            bm = bmref()
            if bm is not None:
                bm._reset()

        T1 = time.time()
        self.stepFrameTime = T1 - T0

######################################################################

# ODEContactProperties
class ODEContactProperties:

    """Contact properties.

    This class stores contact properties that are used whenever
    two objects collide. The attributes are used to initialize
    ODE contact joints.
    """    
    
    def __init__(self,
                 mode = 0,
                 mu = 0.3,
                 mu2 = None,
                 bounce = None,
                 bounce_vel = None,
                 soft_erp = None,
                 soft_cfm = None,
                 motion1 = None,
                 motion2 = None,
                 slip1 = None,
                 slip2 = None,
                 fdir1 = None):
        """Constructor.

        See the ODE manual for an explanation of the parameters.

        The flags for the mode parameter are automatically set.
        However, you can initially set the ContactApprox flags.
        """

        if mu2!=None:
            mode |= ode.ContactMu2
        else:
            mu2 = 0.0

        if bounce!=None:
            mode |= ode.ContactBounce
        else:
            bounce = 0.0

        if bounce_vel==None:
            bounce_vel = 0.0

        if soft_erp!=None:
            mode |= ode.ContactSoftERP
        else:
            soft_erp = 0.0

        if soft_cfm!=None:
            mode |= ode.ContactSoftCFM
        else:
            soft_cfm = 0.0

        if motion1!=None:
            mode |= ode.ContactMotion1
        else:
            motion1 = 0.0

        if motion2!=None:
            mode |= ode.ContactMotion2
        else:
            motion2 = 0.0

        if slip1!=None:
            mode |= ode.ContactSlip1
        else:
            slip1 = 0.0

        if slip2!=None:
            mode |= ode.ContactSlip2
        else:
            slip2 = 0.0

        if fdir1!=None:
            mode |= ode.ContactFDir1
        else:
            fdir1 = (0,0,0)

        self.mode = mode
#        print "ODEContactProps: mode =",mode
        self.mu = mu
        self.mu2 = mu2
        self.bounce = bounce
        self.bounce_vel = bounce_vel
        self.soft_erp = soft_erp
        self.soft_cfm = soft_cfm
        self.motion1 = motion1
        self.motion2 = motion2
        self.slip1 = slip1
        self.slip2 = slip2
        self.fdir1 = fdir1

    def getSurfaceParamsList(self):
        return (self.mode, self.mu, self.mu2, self.bounce, self.bounce_vel, 
                self.motion1, self.motion2, self.slip1, self.slip2, 
                self.soft_erp, self.soft_cfm, self.fdir1)
   
######################################################################

# ODEBodyManipulator
class ODEBodyManipulator(object):
    """Body manipulator class.

    This class can be used to apply external forces/torques to a body
    or to manipulate the position/orientation/velocities directly.

    You should not create instances of this class yourself. Instead, use
    the createBodyManipulator() method of the ODEDynamics component.
    """
    
    def __init__(self, body):
        """Constructor.

        \param body (\c ODEBody) The internal body object representing the
               rigid body to manipulate.
        """
        self._body = body
        self._odebody = body.odebody
        self._reset()
        

    # setPos
    def setPos(self, pos):
        """Set the position of the body.

        pos must be a 3-sequence of floats.
        """
        self._odebody.enable()
        self._odebody.setPosition(pos)

    # setRot
    def setRot(self, rot):
        """Set the rotation of the body.

        rot must be a mat3 containing the orientation.
        """
        self._odebody.enable()
        self._odebody.setRotation(mat3(rot).toList(True))  # Now setRot really accepts a mat3 (and also a list with 9 elements)

    # setLinearVel
    def setLinearVel(self, vel):
        """Set the linear velocity.

        vel must be a 3-sequence of floats.
        """
        self._odebody.enable()
        self._odebody.setLinearVel(vel)

    # setAngularVel
    def setAngularVel(self, vel):
        """Set the angular velocity.

        vel must be a 3-sequence of floats.
        """
        self._odebody.enable()
        self._odebody.setAngularVel(vel)

    # setInitialPos
    def setInitialPos(self, pos):
        """Set the initial position.

        pos must be a 3-sequence of floats.
        """
        self._body.initial_pos = vec3(pos)

    # setInitialRot
    def setInitialRot(self, rot):
        """Set the initial orientation.

        rot must be a mat3.
        """
        self._body.initial_rot = mat3(rot)

    # setInitialLinearVel
    def setInitialLinearVel(self, vel):
        """Set the initial linear velocity.

        vel must be a 3-sequence of floats.
        """
        self._odebody.initial_linearvel = vec3(vel)

    # setInitialAngularVel
    def setInitialAngularVel(self, vel):
        """Set the initial angular velocity.

        vel must be a 3-sequence of floats.
        """
        self._odebody.initial_angularvel = vec3(vel)

    # addForce
    def addForce(self, force, relforce=False, pos=None, relpos=False):
        """Apply an external force to a rigid body.
        
        Add an external force to the current force vector. force is a
        vector containing the force to apply. If relforce is True the
        force is interpreted in local object space, otherwise it is
        assumed to be given in global world space. By default, the
        force is applied at the center of gravity. You can also pass a
        different position in the pos argument which must describe a
        point in space. relpos determines if the point is given in
        object space or world space (default).
        """
        
        R = None
        force = vec3(force)
        if relforce:
            R = mat3(self._odebody.getRotation())
            force = R*force
        # Is a position given? then add the corresponding torque
        if pos!=None:
            pos = vec3(pos)
            bodyorig = vec3(self._odebody.getPosition())
            if relpos:
                if R==None:
                    R = mat3(self._odebody.getRotation())
                pos = R*pos + bodyorig

            self._torque += (pos-bodyorig).cross(force)
            self._torque_flag = True
            
        self._force += vec3(force)
        self._force_flag = True
                    
    # addTorque
    def addTorque(self, torque, reltorque=False):
        """Apply an external torque to a rigid body.
        
        Add an external torque to the current torque vector. torque is
        a vector containing the torque to apply. reltorque determines
        if the torque vector is given in object space or world space
        (default).
        """
        
        torque = vec3(torque)
        if reltorque:
            R = mat3(self._odebody.getRotation())
            torque = R*torque
            
        self._torque += torque
        self._torque_flag = True

    # _apply
    def _apply(self):
        """Apply the stored force/torque.

        This method is called by the ODEDynamics object during the simulation
        step (once for every sub step).
        """
        
        if self._force_flag or self._torque_flag:
            self._odebody.enable()
            
        if self._force_flag:
            self._odebody.addForce(self._force)
        if self._torque_flag:
            self._odebody.addTorque(self._torque)

    # _reset
    def _reset(self):
        """Reset the stored force/torque.

        This method is called by the ODEDynamics object at the end of one
        entire simulation step.
        """
        self._force = _core.vec3(0)
        self._torque = _core.vec3(0)
        
        self._force_flag = False
        self._torque_flag = False

    ## protected:
        
    # "body" property...
    
    def _getBody(self):
        """Return the current body (WorldObject).

        This method is used for retrieving the \a body property.

        \return Rigid body
        """
        return self._body.obj

    body = property(_getBody, None, None, "Rigid body")

    # "odebody" property...
    # Someone may think this method would return an ODEBody, not an ode.Body
    # That's why I changed the case.
    def _get_odeBody(self):
        """Return the current ODE body (type ode.Body from PyODE). 

        This method is used for retrieving the \a odebody property.

        \return ODE body
        """
        return self._odebody

    odebody = property(_get_odeBody, None, None, "ODE body")

    # odegeoms property
    
    def _get_odeGeoms(self):
        """Return the current ODE geom list.

        This method is used for retrieving the \a odegeoms property.

        \return ODE geom list
        """
        return self._body.odegeoms

    odegeoms = property(_get_odeGeoms, None, None, "ODE geoms")


# FixedJoint
class ODEFixedJoint(cgkit.odedynamics.ODEJointBase):
    """
    Fixed Joint: Glues two bodies together.
    Not recommended by ODE manual, but useful when a solid body has different contact properties on different sides.
    """

    def __init__(self,
                 name = "ODEFixedJoint",
                 body1 = None,
                 body2 = None,
                 **params):
        cgkit.odedynamics.ODEJointBase.__init__(self, name=name, body1=body1, body2=body2,
                              **params)

        self._createSlots()

    # _createODEjoint
    def _createODEjoint(self):
        # Create the ODE joint
        self.odejoint = ode.FixedJoint(self.odedynamics.world)

    # _initODEjoint
    def _initODEjoint(self):
        self.attach(self.body1, self.body2)
        self.odejoint.setFixed()

