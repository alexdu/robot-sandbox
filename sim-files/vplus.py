#       vplus.py
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


# Programele robot au acces la toate functiile si variabilele definite aici

from __future__ import division
from numpy import matrix, mat
from math import pi
from geom import *
import math
import numpy
import time
import os
import sys
import re
import subprocess
import string
from v2py import *
from pprint import pprint
from IPython.Shell import IPShellEmbed
import traceback
from copy import copy, deepcopy

numpy.set_printoptions(precision=2, suppress=True)

PI = pi
TRUE = 1
FALSE = 0
ON = 1
OFF = 0

numeric = ['int', 'float']
location = ['TRANS', 'PPOINT']
def check_args(args, types):
    if type(args).__name__ != 'list':
        args = [args]
        
    if type(types).__name__ != 'list':
        types = [types]
    
    if len(types) == 1:
        types = types * len(args)
    elif len(types) != len(args):
        types = [types] * len(args)

    typeslist = []
    for t in types:
        if type(t).__name__ == 'list':
            typeslist.append(t)
        else:
            typeslist.append([t])
    argtypes = []
    for arg in args:
        if type(arg).__name__ == 'instance':
            argtypes.append(arg.__class__.__name__)
        else:
            argtypes.append(type(arg).__name__)
    #~ print argtypes
    #~ print typeslist
            
    for i, t in enumerate(argtypes):
        allowedtypes = typeslist[i]
        if not (t in allowedtypes):
            caller = traceback.extract_stack()[-2][2]
            raise TypeError, "%s expects argument %d to be '%s', not '%s'." % (caller, i+1, string.join(allowedtypes, "' or '"), t)


def SIN(ang):
    check_args(ang, numeric)
    return numpy.sin(ang * pi/180)
def COS(ang):
    check_args(ang, numeric)
    return numpy.cos(ang * pi/180)
def TAN(ang):
    check_args(ang, numeric)
    return numpy.tan(ang * pi/180)
def ATAN2(dy, dx):
    check_args([dy,dx], [numeric])
    return numpy.arctan2(dy, dx) * 180/pi
def INT(x):
    check_args(x, numeric)
    return x.__int__()
def FRACT(x):
    check_args(x, numeric)
    return x - INT(x)
def ABS(x):
    check_args(x, numeric)
    return abs(x)
def SIGN(x):
    check_args(x, numeric)
    if x >= 0:
        return 1
    else:
        return -1
def SQR(x):
    check_args(x, numeric)
    return x*x
def SQRT(x):
    check_args(x, numeric)
    return math.sqrt(x)
def MIN(a,b):
    check_args([a,b], [numeric])
    if a > b:
        return b
    else:
        return a
def MAX(a,b):
    check_args([a,b], [numeric])
    return -MIN(-a,-b)

    

def INVERSE(a):
    check_args(a, "TRANS")
    return TRANS(HTM = numpy.linalg.inv(a.HTM))    

def RX(ang):
    check_args(ang, numeric)
    return TRANS(HTM = RobotSim.omorot(rotx(ang)))

def RY(ang):
    check_args(ang, numeric)
    return TRANS(HTM = RobotSim.omorot(roty(ang)))


def RZ(ang):
    check_args(ang, numeric)
    return TRANS(HTM = RobotSim.omorot(rotz(ang)))
    
def DX(a):
    check_args(a, "TRANS")
    return a.x
def DY(a):
    check_args(a, "TRANS")
    return a.y
def DZ(a):
    check_args(a, "TRANS")
    return a.z

def DISTANCE(a,b):
    check_args([a,b], "TRANS")
    return SQRT((a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2)

def SHIFT(a, dx, dy, dz):
    check_args([a, dx, dy, dz], ["TRANS", numeric, numeric, numeric])
    
    return TRANS(dx,dy,dz) * a

def FRAME(a,b,c,d):
    check_args([a, b, c, d], "TRANS")
    
    x = b.POS - a.POS
    y_tmp = c.POS - a.POS
    z = numpy.cross(x.T, y_tmp.T).T
    y = numpy.cross(z.T, x.T).T
    
    x = x / numpy.linalg.norm(x)
    y = y / numpy.linalg.norm(y)
    z = z / numpy.linalg.norm(z)
    
    return TRANS(HTM = numpy.vstack([numpy.hstack([x,y,z,d.POS]), \
                                              mat((0,0,0,1))]))
    

class infix:
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)

    
#~ MOD = infix(lambda x,y: _MOD(x,y))
#~ def _MOD(a,b):
    #~ check_args([a, b], [numeric])
    #~ return a % b

TO = infix(lambda x,y: _TO(x,y))
def _TO(a,b):
    check_args([a, b], [numeric])

    if a < b:
        return range(a, b+1)
    else:
        return range(a, b-1, -1)
TO = infix(lambda x,y: _TO(x,y))


class TRANS:
    """
    Transformation (location variable)
    Components: x, y, z, yaw, pitch, roll.
    Convention for yaw-pitch,roll: ZYZ'
    
    V+ monitor console (case insensitive):
    .here a
    .do set b = TRANS(100,100,100,0,180,0)
    .do set c = a:rz(45)

    V+ program (case insensitive):
    HERE a
    SET b = TRANS(100,100,100,0,180,0)
    SET c = a:RZ(45)
    
    Python (case sensitive):
    a = HERE()
    b = TRANS(100,100,100,0,180,0)
    c = a*RZ(45) 
    """
    def __init__(self, x=0, y=0, z=0, yaw=0, pitch=0, roll=0, HTM=0):
        check_args([self,x,y,z,yaw,pitch,roll], ['TRANS'] + [numeric] * 6)
        
        if type(HTM).__name__ == 'matrix':
            (self.x, self.y, self.z, self.yaw, self.pitch, self.roll) = decompose(HTM)
        else:
            self.x = x
            self.y = y
            self.z = z
            self.yaw = yaw
            self.pitch = pitch
            self.roll = roll
            (self.x, self.y, self.z, self.yaw, self.pitch, self.roll) = decompose(self.get_htm())

    def __repr__(self):
        x = round(self.x, 3)
        y = round(self.y, 3)
        z = round(self.z, 3)
        yaw = round(self.yaw, 3)
        pitch = round(self.pitch, 3)
        roll = round(self.roll, 3)
        return "TRANS(%4.3g, %4.3g, %4.3g, %4.3g, %4.3g, %4.3g)" % \
            (x, y, z, yaw, pitch, roll)
    def __eq__(a, b):
        try:
            return (a.x == b.x) and (a.y == b.y) and (a.z == b.z) and (a.yaw == b.yaw) and (a.pitch == b.pitch) and (a.roll == b.roll)
        except:
            return False
                 
    def get_htm(self):
        return omotrans(self.x, self.y, self.z) * \
               omorot(rotz(self.yaw) * \
               roty(self.pitch) * rotz(self.roll))
    def get_pos(self):
        return (mat((self.x, self.y, self.z))).T
        
    HTM = property(get_htm)
    POS = property(get_pos)


    def __mul__(self, right):
        return _TRANS_COMPOSE(self, right)
    def __or__(self, right):
        return _TRANS_COMPOSE(self, right)
        
def _TRANS_COMPOSE(a, b):
    check_args([a, b], "TRANS")
    return TRANS(HTM = a.HTM * b.HTM)


NULL = TRANS(0,0,0,0,0,0)


class PPOINT:
    """
    Precision point.
    
    .do set x = #PPOINT(0,-90,90,0,180,0)    
    """
    def __init__(self, a=0,b=0,c=0,d=0,e=0,f=0):
        if type(a).__name__ == 'int' or type(a).__name__ == 'float':
            self.J = [a,b,c,d,e,f]
        else:
            self.J = list(a)

    def __getitem__(self, key):
        return self.J[key]
        
    def __repr__(self):
        a = round(self.J[0], 3)
        b = round(self.J[1], 3)
        c = round(self.J[2], 3)
        d = round(self.J[3], 3)
        e = round(self.J[4], 3)
        f = round(self.J[5], 3)
        return "PPOINT(%4.3g, %4.3g, %4.3g, %4.3g, %4.3g, %4.3g)" % (a,b,c,d,e,f)







# de aici incolo sunt functii care altereaza starea simulatorului robot
import RobotSim




def SPEED(spd, flag1=None, flag2=None):
    
    """ Seteaza viteza robotului

    spd: viteza dorita
    flags: 
           MONITOR = seteaza viteza monitor
           ALWAYS  = seteaza viteza program globala
           nici MONITOR, nici ALWAYS = seteaza viteza program pt urmatoarea miscare
           
           doar pentru vitezele program:
           MMPS    = viteza masurata in mm/secunda
           IPS     = inci/secunda
           nici MMPS, nici IPS = procente din viteza maxima
    """
    check_args([spd, flag1, flag2], [numeric, ["str", "NoneType"], ["str", "NoneType"]])
    
    MONITOR = False
    ALWAYS  = False
    MMPS    = False
    IPS     = False
    
    if "MONITOR" in [flag1, flag2]:
        MONITOR = True
    if "ALWAYS" in [flag1, flag2]:
        ALWAYS = True
    if flag1 == "MMPS":
        MMPS = True
    if flag1 == "IPS":
        IPS = True
        
    
    if MONITOR:
        if not ALWAYS and not MMPS and not IPS:
            RobotSim.speed_monitor = max(0, min(spd, 100))
        else:
            raise SyntaxError, "Expected: SPEED xx MONITOR  (without ALWAYS or MMPS or IPS)"
    else:
        if MMPS:
            unit = "MMPS"
            spd = max(0, min(spd, RobotSim.max_cartesian_speed))
        elif IPS:
            unit = "IPS"
            spd = max(0, min(spd, RobotSim.max_cartesian_speed/25.4))
        else:
            unit = "%"
            spd = max(0, min(spd, 100))
            
        if ALWAYS:
            RobotSim.speed_always = spd
            RobotSim.speed_always_unit = unit
        else:
            RobotSim.speed_next_motion = spd
            RobotSim.speed_next_motion_unit = unit
        

def LEFTY():
	RobotSim.lefty = True
def LEFTY():
	RobotSim.lefty = False
def ABOVE():
	RobotSim.above = True
def BELOW():
	RobotSim.above = False
def FLIP():
	RobotSim.flip = True
def NOFLIP():
	RobotSim.flip = False
def SINGLE():
	RobotSim.single = True
def MULTIPLE():
	RobotSim.single = False
def OPEN():
    RobotSim.open_flag = True
    RobotSim.close_flag = False
def CLOSE():
    RobotSim.open_flag = False
    RobotSim.close_flag = True
def BREAK():
    RobotSim.ActuateGripper()
    
    while RobotSim.arm_trajectory_index < len(RobotSim.arm_trajectory) - 1:
        time.sleep(0.01)
        if RobotSim.abort_flag:
            RobotSim.abort_flag = False
            raise UserAbort
    
    
def OPENI():
    BREAK()
    OPEN()
    BREAK()
    if not RobotSim.switch["DRY.RUN"]:
        time.sleep(RobotSim.param["HAND.TIME"])
    
def CLOSEI():
    BREAK()
    CLOSE()
    BREAK()
    if not RobotSim.switch["DRY.RUN"]:
        time.sleep(RobotSim.param["HAND.TIME"])
    

def HERE():
	return RobotSim.DK(RobotSim.currentJointPos)
def DEST():
	return RobotSim.DK(RobotSim.destJointPos)

def PHERE():
	return PPOINT(RobotSim.currentJointPos)
def PDEST():
	return PPOINT(RobotSim.destJointPos)

    
def SET(a):
    check_args(a, location)
    return a

def _convert_to_trans(a):
    if a.__class__.__name__ == 'TRANS':
        return a
    elif a.__class__.__name__ == 'PPOINT':
        return RobotSim.DK(a)
    else:
        raise SyntaxError, "Expected argument type: TRANS or PPOINT'"
        
def _convert_to_ppoint(a):
    if a.__class__.__name__ == 'TRANS':
        return RobotSim.IK(a)
    elif a.__class__.__name__ == 'PPOINT':
        return a
    else:
        raise SyntaxError, "Expected argument type: TRANS or PPOINT'"
    
    

def MOVE(a):
    check_args(a, location)
    
    RobotSim.ActuateGripper() 
    RobotSim.jtraj(_convert_to_ppoint(a))
        
    # pentru urmatoarea miscare, revenim la viteza always 
    RobotSim.speed_next_motion = RobotSim.speed_always
    RobotSim.speed_next_motion_unit = RobotSim.speed_always_unit

  
def MOVES(a):
    check_args(a, location)

    RobotSim.ActuateGripper()
    RobotSim.ctraj(_convert_to_ppoint(a))

    # pentru urmatoarea miscare, revenim la viteza always 
    RobotSim.speed_next_motion = RobotSim.speed_always
    RobotSim.speed_next_motion_unit = RobotSim.speed_always_unit

def MOVET(a, grip):
    check_args([a, grip], [location, numeric])

    if grip:
        OPEN
    else:
        CLOSE
    MOVE(a)
    
def MOVEST(a, grip):
    check_args([a, grip], [location, numeric])

    if grip:
        OPEN
    else:
        CLOSE
    MOVES(a)
    
def APPRO(a, h):
    check_args([a, h], [location, numeric])
    a = _convert_to_trans(a)
    MOVE(a * TRANS(0, 0, -h))
def DEPART(h):
    check_args(h, numeric)
    MOVE(DEST() * TRANS(0, 0, -h))
def APPROS(a, h):
    check_args([a, h], [location, numeric])
    a = _convert_to_trans(a)
    MOVES(a * TRANS(0, 0, -h))
def DEPARTS(h):
    check_args(h, numeric)
    MOVES(DEST() * TRANS(0, 0, -h))

def PARAMETER(param_name, value):
    check_args([param_name, value], ["str", numeric])
    param_name = param_name.replace("_", ".")
    RobotSim.param[param_name] = value

def TOOL(t = None):
    check_args(t, ["TRANS", "NoneType"])
    if t != None:
        RobotSim.tool_trans = t
    return RobotSim.tool_trans

safe = PPOINT(0,-90,180,0,0,0)






# comenzi monitor
############################################

import IPython.ipapi

class UserAbort(Exception):
    pass



from IPython import ColorANSI
from IPython.genutils import Term
tc = ColorANSI.TermColors()

_code_tracing_cache = {}
_color_dic = {}
_dic_locals = {}
_dic_globals = {}
_spaces_last_line = ""
def init_trace():
    global _code_tracing_cache, _color_dic, _dic_locals, _dic_globals
    _code_tracing_cache = {}
    _color_dic = {"<module>": tc.DarkGray}
    _dic_locals = {}
    _dic_globals = {}
    _spaces_last_line = ""
    
def get_color(func):
    colors = [tc.DarkGray, tc.Normal, tc.Green, tc.Blue, tc.Red, tc.Brown, tc.Purple]
    if func in _color_dic:
        return _color_dic[func]
    else:
        _color_dic[func] = colors[len(_color_dic) % len(colors)]
        return _color_dic[func]
        
def str_compact(val):
    s = str(val)
    while "  " in s:
        s = s.replace("  ", " ")
    return s
def print_new_vars(func, newvars):
    newvars.sort()
    
    for name, val in newvars:
        if (type(val).__name__ == 'instance') and (val.__class__.__name__ == 'TRANS'):
            print >> Term.cout, "%s%snew variable: %s%s = %s%s" % (_spaces_last_line, tc.DarkGray, get_color(func), name, str_compact(val), tc.Normal)
            
    for name, val in newvars:
        if (type(val).__name__ == 'instance') and (val.__class__.__name__ == 'PPOINT'):
            print >> Term.cout, "%s%snew variable: %s%s = %s%s" % (_spaces_last_line, tc.DarkGray, get_color(func), name, str_compact(val), tc.Normal)
    
    smallchanges = []
    for name, val in newvars:
        if (type(val).__name__ != 'instance') or not(val.__class__.__name__ in ['TRANS', 'PPOINT']):
            smallchanges.append("%s%s = %s%s" % (get_color(func), name, str(val), tc.Normal))
    if len(smallchanges):
        print >> Term.cout, _spaces_last_line + tc.DarkGray + "new variables: " + string.join(smallchanges, ", ")
    
def print_changed_vars(func, changedvars):
    changedvars.sort()
    
    for name, old_val, new_val in changedvars:
        if (type(new_val).__name__ == 'instance') and (new_val.__class__.__name__ == 'TRANS'):
            print >> Term.cout, "%s%s%s changed to: %s\n%s%s(previous value: %s)%s" % (_spaces_last_line, get_color(func), name, str_compact(new_val), _spaces_last_line, tc.DarkGray, str_compact(old_val), tc.Normal)
            
    for name, old_val, new_val in changedvars:
        if (type(new_val).__name__ == 'instance') and (new_val.__class__.__name__ == 'PPOINT'):
            print >> Term.cout, "%s%s%s changed to: %s\n%s%s(previous value: %s)%s" % (_spaces_last_line, get_color(func), name, str_compact(new_val), _spaces_last_line, tc.DarkGray, str_compact(old_val), tc.Normal)

    
    smallchanges = []
    for name, old_val, new_val in changedvars:
        if (type(new_val).__name__ != 'instance') or not(new_val.__class__.__name__ in ['TRANS', 'PPOINT']):
            smallchanges.append("%s%s = %s %s(was %s)%s" % (get_color(func), name, str(new_val), tc.DarkGray, str(old_val), tc.Normal))
    
    if len(smallchanges):
        print >> Term.cout, _spaces_last_line + tc.DarkGray + "changed: " + string.join(smallchanges, ", ")

def print_new_and_changed_variables(func, locals, globals):
    global _dic_locals, _dic_globals
    
    newvars = []
    changedvars = []
    
    if func in _dic_locals:
        prev_locals = _dic_locals[func]
        for v in locals:
            if not (v in prev_locals):
                newvars.append((v, locals[v]))
            elif (type(locals[v]).__name__ == 'list') and (type(prev_locals[v]).__name__ == 'list'):
                #print "vector: ", locals[v]
                #print "  prev: ", prev_locals[v]
                for i, vl in enumerate(locals[v]):
                    if not (prev_locals[v][i] == vl):
                        changedvars.append(("%s[%d]" % (v,i), prev_locals[v][i], vl))
            elif not(prev_locals[v] == locals[v]):
                changedvars.append((v, prev_locals[v], locals[v]))
                        
            
            
    print_new_vars(func, newvars)
    print_changed_vars(func, changedvars)
    
    localscopy = locals.copy()
    for k,v in localscopy.iteritems():
        if type(v).__name__ == 'list':
            localscopy[k] = copy(v)
    _dic_locals[func] = localscopy
    

def print_code_line(file, func, lineno):
    try:
        if not (file in _code_tracing_cache):
            f = open(file)
            code = f.readlines()
            _code_tracing_cache[file] = code
            f.close()
        line = _code_tracing_cache[file][lineno-1]
        line = line.strip("\n")
        slineno = str(lineno).ljust(3)
        print >> Term.cout, "%s%s[%s]:%s %s%s" % (get_color(func), file, func, slineno, line, tc.Normal)
    except:
        slineno = str(lineno).ljust(3)
        print >> Term.cout, "%s%s[%s]:%s <%s:%s>%s" % (get_color(func), file, func, slineno, sys.exc_type.__name__, sys.exc_value, tc.Normal)
    
    global _spaces_last_line    
    _spaces_last_line = " " * (len(re.match("(\ *)", line).groups()[0]) + len(file) + len(func) + len(slineno) + 4)
    
def trace_calls(frame, event, arg):
    if RobotSim.abort_flag:
        RobotSim.abort_flag = False
        raise UserAbort


    if event == 'line':
        co = frame.f_code
        line_no = frame.f_lineno
        filename = co.co_filename
        func_name = co.co_name
        #~ print filename + ":%d" % (line_no)
        if RobotSim.switch["TRACE"]:
            print_new_and_changed_variables(func_name, frame.f_locals, frame.f_globals)
            print_code_line(filename, func_name, line_no)
        return trace_calls

    if event == 'call':
            
        co = frame.f_code
        func_name = co.co_name
        func_line_no = frame.f_lineno
        func_filename = co.co_filename
        if func_filename.lower().endswith(".v2"):
            return trace_calls

        #~ caller = frame.f_back
        #~ caller_line_no = caller.f_lineno
        #~ caller_filename = caller.f_code.co_filename
        #~ 
        #~ if caller_filename.lower().endswith(".v2"):
            #~ print 'Call to %s on line %s of %s from line %s of %s' % \
                #~ (func_name, func_line_no, func_filename,
                 #~ caller_line_no, caller_filename)
    return

def EXECUTE(file):
    dic = _build_dictionary()

    init_trace()
    
    code = translate_program(file)        
    code = compile(code, file, "exec")
    
    (name,ext) = os.path.splitext(file)
    name = translate_expression(name)
    bootloader = compile("%s()\n" % name, "<exec loader>", "exec")
    
    sys.settrace(trace_calls)
    try:
        exec(code) in dic
        exec(bootloader) in dic
    except:
        raise
    finally:
        sys.settrace(None)
        

def _flush_completed_jobs():
    toFlush = []
    for i,j in jobs.jobs_all.iteritems():
        if j.stat_code != j.stat_running_c:
            toFlush.append(i)
            if j in jobs.jobs_run:
                jobs.jobs_run.remove(j)
            if j in jobs.jobs_comp:
                jobs.jobs_comp.remove(j)
            if j in jobs.jobs_dead:
                jobs.jobs_dead.remove(j)
    for i in toFlush:
        del jobs.jobs_all[i]
    
def _CM_ABORT(self, arg):
    print "Aborting robot program..."
    RobotSim.abort_flag = True


    
def _CM_EXEC(self, prog):
    """
        
    Monitor command for executing a robot program.

    Example:

    exec stiva
    """

    if RobotSim.abort_flag:
        print "Please wait for previous robot program to finish."
        return

    ip = IPython.ipapi.get()

    if not re.match("^.*\.[^.]*$", prog): # fara extensie, ii adaug .v2
        prog = prog + ".v2" 

    
    _flush_completed_jobs()
    
    ip.runlines("%%bg _ip.runlines(\"EXECUTE('%s')\")" % prog)


def _CM_HERE(self, var):
    """
        
    Monitor command for teaching robot locations.

    Examples:

    here a       # records current end-effector position as a transformation 
    here #b      # records current joint position as a precision point
    here bs:a    # records end-effector position in the local reference frame "bs"
    """
    #IPShellEmbed()()
    ip = IPython.ipapi.get()
    
    if len(var.strip()) == 0:
        ip.runlines("HERE()")
        return
        
    var = var.lower()
    
    reSingleVar = """
        ^
        [a-z]?        # start with lowercase letter
        [a-z0-9_]*    # may contain letter, digit or underscore
        $
        """
    rePPoint = """
        ^
        \#                    # start with #
        ([a-z]?[a-z0-9_]*)    # following variable name
        $
        """
    reBaseTransform = """
        ^
        (.*)                  # base (expression)
        :                     # colon operator
        ([a-z]?[a-z0-9_]*)    # variable
        $
        """
    
    mSingleVar = re.match(reSingleVar, var, re.VERBOSE)
    mPPoint = re.match(rePPoint, var, re.VERBOSE)
    mBaseTransform = re.match(reBaseTransform, var, re.VERBOSE)
    
    if mSingleVar:
        cmd = var + " = HERE()"
    elif mPPoint:
        var = mPPoint.groups()[0]
        cmd = var + " = PHERE()"
    elif mBaseTransform:
        bs = mBaseTransform.groups()[0]
        var = mBaseTransform.groups()[1]
        cmd = var + " = INVERSE(" + translate_expression(bs) + ") * HERE()"
    else:
        print "here (monitor command): syntax error"
        return

    if RobotSim.debug:
        print "(debug) " + cmd    
    ip.runlines(cmd + "\r\n" \
        + var)


    
    
def _CM_STATUS(self, var):    
    """
        
    Displays robot speeds and running programs.

    """
    print "Monitor speed: ", RobotSim.speed_monitor
    print "Program speed (ALWAYS): ", RobotSim.speed_always
    print "Program speed for next motion: ", RobotSim.speed_next_motion
    for i, j in enumerate(jobs.jobs_run):
        print i, j, j.status

def _CM_TOOL(self, var):
    """
        
    Set the tool transformation.

    Examples:

    t = TRANS(0,0,100)
    tool t

    tool TRANS(0,0,100)

    tool RZ(45)

    """
    ip = IPython.ipapi.get()
    ip.runlines("TOOL(" + translate_expression(var) + ")")


    
def _CM_PARAM(self, var):
    """

    Set a parameter.

    Example:

    parameter hand.time = 0.5

    """
    if len(var) == 0:
        print RobotSim.param
    else:
        (name, value) = split_at_equal_sign(var)
        RobotSim.param[name.upper().strip()] = eval(value)
        

def _CM_ENABLE(self, var):
    """

    Enable a switch.

    Example:

    enable power

    """
    RobotSim.switch[var.upper()] = True



def _CM_DISABLE(self, var):
    """

    Disable a switch.

    Example:

    disable power

    """
    RobotSim.switch[var.upper()] = False

def _CM_SWITCH(self, var):
    """

    List switches and their values.

    """
    if len(var) == 0:
        print RobotSim.switch
    else:
        print RobotSim.switch[var.upper()]

def _CM_CALIBRATE(self, var):
    """

    Does nothing.

    """
    print "Simulated robots do not need calibration :)"


def _CM_SEE(self, prog):
    """

    Edits a robot program.

    Example:

    see stiva

    Editor is vplus._editor 
    Default editor on Windows: notepad2 (included).
    If not found, falls back to notepad.

    """
    if not re.match("^.*\.[^.]*$", prog): # fara extensie, ii adaug .v2
        prog = prog + ".v2" 
    
    print "editing %s ..." % prog
    subprocess.Popen('%s %s' % (_editor, prog))

def _CM_SPEED(self, var):
    """

    Set monitor speed.

    Example:

    speed 100

    Tip: you may change the monitor speed while a robot program is running.
    """
    spd = eval('int(%s)' % var)
    print "Setting monitor speed to %d" % spd
    SPEED(spd, "MONITOR")


def _build_dictionary():
    code = """
    _k = 0
    _v = 0
    _K = list(set(locals().keys() + globals().keys()))
    _K.sort()
    _vars = []

    for _k in _K:
        if _k[0] != '_': 
            _v = eval(_k)
            if type(_v).__name__ == 'instance':
                if _v.__class__.__name__ in ['TRANS', 'PPOINT']:
                    _vars.append(_k)
            if type(_v).__name__ in ['str', 'int', 'float']:
                if _k.lower() == _k:
                    _vars.append(_k)
    _dic = {}
    for _k in _vars:
        _dic[_k] = eval(_k)
    for _k in vplus.__dict__.keys():
         if _k[0] != '_': 
            if _k.upper() == _k:
                _dic[_k] = eval(_k)
    
    _dic["vplus"] = vplus
    """
    
    ip = IPython.ipapi.get()
    ip.runlines(code)
    
    
    return ip.user_ns["_dic"]
    
def _CM_LISTL(self, var):
    """

    Lists location variables (TRANS and PPOINT).
    """

    ip = IPython.ipapi.get()
    if len(var) > 0:
        var = translate_expression(var)
        ip.runlines("pprint.pprint([" + var + "])")
        return
    code = """
        _k = 0
        _v = 0
        _K = list(set(locals().keys() + globals().keys()))
        _K.sort()

        print "Location variables:"
        print "==================="
        print ""
        print "Transformations:"
        for _k in _K:
            _v = eval(_k)
            if type(_v).__name__ == 'instance':
                if _v.__class__.__name__ == 'TRANS':
                    if _k[0] != '_': 
                        print "%10s = " % _k, _v
        print ""
        print "Precision points:"
        for _k in _K:
            _v = eval(_k)
            if type(_v).__name__ == 'instance':
                if _v.__class__.__name__ == 'PPOINT':
                    if _k[0] != '_': 
                        print "%10s =" % ("#" + _k), _v
        print ""
        print "Tool transformation:"
        print "             ", TOOL()
    """
    ip.runlines(code)

def _CM_LISTR(self, var):
    """

    Lists real and integer variables.
    """
    code = """
        _k = 0
        _v = 0
        _K = list(set(locals().keys() + globals().keys()))
        _K.sort()

        print "Real and integer variables:"
        print "==========================="
        print ""
        print "Reals:"
        for _k in _K:
            _v = eval(_k)
            if type(_v).__name__ == 'float':
                if _k[0] != '_': 
                    if _k.lower() == _k:
                        print "%10s = " % _k, _v
        print ""
        print "Integers:"
        for _k in _K:
            _v = eval(_k)
            if type(_v).__name__ == 'int':
                if _k[0] != '_': 
                    if _k.lower() == _k:
                        print "%10s = " % _k, _v
    """
    ip = IPython.ipapi.get()
    ip.runlines(code)
            
def _CM_LISTS(self, var):
    """

    Lists string variables.
    """
    code = """
        _k = 0
        _v = 0
        _K = list(set(locals().keys() + globals().keys()))
        _K.sort()

        print "String variables:"
        print "================="
        print ""
        for _k in _K:
            _v = eval(_k)
            if type(_v).__name__ == 'str':
                if _k[0] != '_': 
                    if _k.lower() == _k:
                        print "%10s = " % _k, _v
    """
    ip = IPython.ipapi.get()
    ip.runlines(code)




def _CM_ENV(self, prog):
    """

    Initializes the work environment for the robot.
    """
    ip = IPython.ipapi.get()
    envs = []
    prog = prog.strip()
    if len(prog)==0:
        files = os.listdir(".")
        for f in files:
            if f.lower().endswith(".env"):
                envs.append(f)
        envs.sort()
        print "Available environments:"
        for e in envs:
            print "  * ", e[:-4]
        return
        
    if not re.match("^.*\.env$", prog):
        prog = prog + ".env" 
        
    print "setting work environment (%s)..." % prog
    print " "
    
    ip.runlines("resetBoxes()")

    RobotSim.pauseTick = True
    try:
        time.sleep(0.2)
        f = open(prog)
        r = f.read()
        f.close()
        ip.runlines(r)
    finally:
        RobotSim.pauseTick = False
    

    
def _CM_DO(self, var):
    var = translate_line(var)
    if RobotSim.debug:
        print "(debug) " + var
    
    ip = IPython.ipapi.get()
    ip.runlines(var)

def _CM_MC(self, var):
    """

    Displays a list of supported monitor commands.

    """
    print "Monitor commands:"
    print "================="
    print "here           # teach a robot location"
    print "speed          # set monitor speed"
    print "see            # edit a robot program"
    print "exec           # execute a robot program"
    print "status         # display system status"
    print "listl          # list location variables"
    print "listr          # list real and integer variables"
    print "lists          # list string variables"
    print "enable         # enable a switch"
    print "disable        # disable a switch"
    print "switch         # list switches"
    print "parameter      # set a parameter"
    print "tool           # set the tool transformation"
    print "cd <folder>    # change directory"
    print "ls             # list files"
    print ""
    print "For more help, type a monitor command followed by '?'"    
    print "e.g. here?"    



