

#       v2py.py
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

# Translates from vplus syntax to python syntax

from __future__ import division
import re
import string
import math
import parser
import symbol
import token

from types import ListType, TupleType

programMangleP2V = {}     # numele programului in Python (mangled) => numele in V+ (initial)
programMangleV2P = {}     # numele programului in V+ => numele "mangled" (in Python) (pe dos)
programDict = {}          # p
# vplus_progname -> [args, file, lineno, function]


def match_subtree(pattern, data, vars=None):
    #~ print pattern
    #~ print data
    if vars is None:
        vars = {}
    if type(pattern) is ListType:
        vars[pattern[0]] = data
        return 1, vars
    if type(pattern) is not TupleType:
        return (pattern == data), vars
    if len(data) != len(pattern):
        return 0, vars
    for pattern, data in map(None, pattern, data):
        same, vars = match_subtree(pattern, data, vars)
        if not same:
            break
    return same, vars

def guess_name(code):
    if code in symbol.sym_name:
        return symbol.sym_name[code]
    if code in token.tok_name:
        return token.tok_name[code]
    return code
    
def convert_parse_tree(l):
    newl = []
    for i,e in enumerate(l):
        if type(e).__name__ == 'int':
            newl.append(guess_name(e))
        elif type(e).__name__ == 'list':
            newl.append(convert_parse_tree(e))
        else:
            newl.append(e)
    return newl
        

def find_params_passable_by_ref(args):
    pattern = (symbol.test, (symbol.or_test, (symbol.and_test, (symbol.not_test, (symbol.comparison, (symbol.expr, (symbol.xor_expr, (symbol.and_expr, (symbol.shift_expr, (symbol.arith_expr, (symbol.term, (symbol.factor, (symbol.power, (symbol.atom, (token.NAME, ['name'])))))))))))))))
    t = parser.expr(args).totuple()
    num_args = len(t[1]) // 2
    
    args = []
    for i in range(num_args):
        (found, var) = match_subtree(pattern, t[1][1 + 2*i])
        if found:
            args.append(var["name"])
        else:
            args.append("__")
    return args


def beautify_program(file):
    f = open(file)
    code = f.readlines()
    f.close()
    
    newcode = []
    
    indent = 0

    for line in code:
        (d_indent_now, d_indent_future) = get_indent(line)
        indent_now = indent + d_indent_now
        
        spaces = " " * indent_now * 4
        line = spaces + beautify_line(line.strip())
        #print line
        newcode.append(line + "\n")
        
        
        indent = indent + d_indent_future
        
        if indent < 0:
            print "Warning: too many END's."
            indent = 0
            
    if indent > 0:
        print "Warning: some END's are missing."
    
    
    f = open(file, "w")
    f.writelines(newcode)
    f.close()
    
def get_indent(line): # intoarce indentarea pentru linia curenta si pentru urmatoarele


    (kw, rest, vs) = split_after_keyword(line)
    if kw in [".PROGRAM", "FOR", "IF", "WHILE"]:
        return (0,1)
    if kw == "ELSE":
        return (-1,0)
    if kw in ["END", ".END"]:
        return (-1,-1)
    return (0,0)

def beautify_line(var):
    (code, comment) = split_comment(var)
    strsplit = split_strings(code)
    newstr = []
    for block in strsplit:
        if block[0] != '"':    # este ceva care nu e string, pot sa-l modific
            newstr.append(beautify_block(block))
        else:
            newstr.append(block)
    return string.join(newstr, "") + comment
def beautify_block(var):
    # un bloc care nu este string si nu contine stringuri si nici comentarii
    
    vplus_keywords = ['ABORT', 'ABOVE', 'ABS', 'ACCEL', 'ALIGN', 'ALTER', 'ALWAYS', 'AND', 'ANY', 
    'APPRO', 'APPROS', 'ASC', 'ATAN2', 'ATTACH', 'AUTO', 'BELOW', 'BREAK', 'BY', 'CALIBRATE', 'CALL', 
    'CASE', 'CLOSE', 'CLOSEI', 'COARSE', 'COS', 'DECOMPOSE', 'DEFINED', 'DELAY', 'DEPART', 'DEPARTS', 
    'DEST', 'DETACH', 'DISABLE', 'DISTANCE', 'DRIVE', 'DRY.RUN', 'DURATION', #DX, DY, DZ (nu le punem aici)
    'ELSE', 'ENABLE', 'END', '.END', 'ERROR', 'ESTOP', 'EXECUTE', 'EXIT', 'FALSE', 'FINE', 'FLIP', 'FOR', 'FRACT', 
    'FRAME', 'GLOBAL', 'HAND.TIME', 'HERE', 'IF', 'INRANGE', 'INT', 'INVERSE', 'IPS', 'JHERE', 'JMOVE', 
    'KILL', 'LAST', 'LEFTY', 'LEN', 'LOCAL', 'MAX', 'MC', 'MCS', 'MIN', 'MMPS', 'MOD', 'MOVE', 'MOVES', 
    'MOVET', 'MOVEST', 'MULTIPLE', 'NEXT', 'NOFLIP', 'NONULL', 'NOT', 'NULL', 'OFF', 'ON', 'OPEN', 'OPENI', 
    'OR', 'PARAMETER', 'PAUSE', 'PI', 'POS', 'POWER', '#PPOINT', 'PPOINT', '.PROGRAM', 'PROMPT', 'RANDOM', 
    'RELAX', 'RELAXI', 'RESET', 'RETURN', 'RETURNE', 'RIGHTY', 'ROBOT', 'RUNSIG', 'RX', 'RY', 'RZ', 
    'SEE', 'SELECT', 'SET', 'SHIFT', 'SIG', 'SIGN', 'SIGNAL', 'SIG', 'SINGLE', 'SPEED', 'SQR', 'SQRT', 
    'STATE', 'STATUS', 'STEP', 'STOP', 'SWITCH', 'TAS', 'TASK', 'TERMINAL', 'THEN', 'TIME', 'TIMER', 'TOOL', 'TRANS', 
    'TO', 'TRUE', 'TYPE', 'UNTIL', 'UPPER', 'VAL', 'VALUE', 'WAIT', 'WAIT.EVENT', 'WHILE', 'WRITE']

    vs = re.split("([a-zA-Z\#\.][a-zA-Z0-9_\.]*)", var)
    newvs = []

    vs.append("")
    for i,s in enumerate(vs):
        if s.upper() in vplus_keywords:
            newvs.append(s.upper())
        elif s.upper() in ["DX", "DY", "DZ"]:       # DX, DY, DZ sunt functii daca sunt urmate de paranteza; 
            if re.match("\ *\(", (vs[i+1]).upper()): # altfel, sunt variabile
                newvs.append(s.upper())
            else:
                newvs.append(s.lower())
        else:
            newvs.append(s.lower())
    
    vs = list(newvs)
    var = string.join(newvs, "")
    return var
    
    






_currentFile = ""
_currentLineNo = 0
def translate_program(file):
    
    global _currentFile, _currentLineNo
    _currentFile = file
    
    beautify_program(file)
    
    global programDict
    
    f = open(file)
    code = f.readlines()
    f.close()
    
    newcode = []
    for (i, line) in enumerate(code):
        _currentLineNo = i + 1
        spaces = re.match("(\ *)", line).groups()[0]
        line = line.strip()
        lt = translate_line(line, len(spaces))
        
        #print spaces + lt
        newcode.append(spaces + lt)
    
    newcode.append("#end of file\n")
    return string.join(newcode, "\n")

def translate_line(line, indent=None):
    (code, comment) = split_comment(line)
    code = translate_statement(code, indent)
    if len(comment.strip()):
        return code + " #" + comment
    else:
        return code
        

def parse_function_call(expr):
    #print expr
    m = re.match("^([^\(]+)\(([^\(]*)\)$", expr)
    #print m.groups()
    if m:
        func = m.groups()[0].strip()
        args = m.groups()[1].strip()
        try:
            args_ref = find_params_passable_by_ref(args)
        except:
            args_ref = []
        return (func, args, args_ref)
    else:
        if ("(" in expr) or (")" in expr):
            raise SyntaxError, "Error in function call declaration."
        else:
            return (expr, "", [])


_program_args = []
    
def translate_statement(var, indent):
    
    # argumentul contine o linie de program fara comentarii
    # primul cuvant este de obicei un cuvant cheie
    
    if len(var.strip()) == 0:
        return var
    
    
    # APPRO a, b    => APPRO(a, b)
    # adica ceea ce in vplus nu are nevoie de paranteze, dar are parametri
    vplus_functions = ['ACCEL', 'APPRO', 'APPROS', 'ATTACH', 
    'DELAY', 'DEPART', 'DEPARTS', 
    'DETACH', 'DISABLE', 'DRIVE',  'DURATION', # 'DX', 'DY', 'DZ', 
    'ENABLE', 'EXECUTE', 
    'JMOVE', 
    'KILL', 'MCS', 'MOVE', 'MOVES', 
    'MOVET', 'MOVEST', 
    'PAUSE', 'PROMPT', 
    'RUNSIG', 
    'SIGNAL', 'SPEED',
    'TOOL', 
    'TIMER', 
    'VAL']

    # OPENI => OPENI()
    # adica chestii fara parametri, care nu pot sa apara in expresii
    vplus_noarg_functions = ['ABORT', 'ABOVE', 'ALIGN', 
    'BELOW', 'BREAK', 'CALIBRATE',
    'CLOSE', 'CLOSEI', 'COARSE', 
    'DEST', 
    'FINE', 'FLIP',
    'LEFTY', 
    'NOFLIP', 'OPEN', 'OPENI', 
    'RELAX', 'RELAXI', 'RESET', 'RIGHTY', 
    'SEE', 'SINGLE',
    'STATUS', 'STOP']

    # PARAMETER HAND.TIME = 0.5
    # TIMER 1 = 0
    vplus_eq_functions = ['PARAMETER', 'TIMER']

    (kw, rest, vs) = split_after_keyword(var)
    global _program_args

    if kw[0] == '.':
        if indent != 0:
            raise IndentationError, "Missing END statement."
    if kw[0] != '.':
        if indent == 0:
            if kw == 'END':
                raise IndentationError, "Too many END statements."
            else:
                raise IndentationError, "Statements written outside .PROGRAM ... .END blocks are not allowed."
    
    if kw in vplus_eq_functions:
        (name, value) = split_at_equal_sign(rest)
        name = translate_expression(name)
        value = translate_expression(value)            
        vs = [kw.upper(), '("', name.strip(), '", ', value.strip(), ')']
    elif kw in vplus_functions:
        vs = [kw, "(", translate_expression(rest).strip(), ")"]
    elif kw in vplus_noarg_functions:
        vs = [kw.strip(), "()"]
    elif kw == "SET":
        (name, value) = split_at_equal_sign(rest)
        name = translate_expression(name)
        value = translate_expression(value)            
        vs = [name.strip(), ' = SET(', value.strip(), ')']
    elif kw == "CALL":                       
        
        # CALL func(a,b,c)   => (a,b,c) = func(a,b,c)
        # CALL func(a,b+1,c)   => (a,__,c) = func(a,b+1,c)
        vs = []
        callexpr = translate_expression(rest).strip()
        (func, args, args_ref) = parse_function_call(callexpr)
        (vplus_func, __, __) = parse_function_call(rest.strip())

        if len(args) > 0:
            arg_ref = find_params_passable_by_ref(args)
            vs = ["(", string.join(arg_ref, ", "), ") = CALL['", vplus_func, "'](", args, ")"]
        else:
            vs = ["CALL['", vplus_func, "']()"]

    elif kw == "EXIT":
        vs = ['break']
    elif kw == 'TYPE':
        vs = ["print ", translate_expression(rest)]
    elif kw == 'GLOBAL':
        vs = ["global ", translate_expression(rest)]
    elif kw in ['LOCAL', 'AUTO']:
        vars = string.split(rest, ",")
        newvars = []
        for v in vars:
            v = v.strip()
            v = translate_expression(v)
            m = re.match("([^\[\]]+)\[([^\[\]])\]$", v)
            if m: # e un vector
                variable = m.groups()[0].strip()
                size = m.groups()[1].strip()
                if len(size) == 0:
                    size = "100"      # fixme
                newvars.append(variable + "=[None]*(" + size + ")")
            else:
                newvars.append(v + "=None")
        vs = [ string.join(newvars, "; ") ]
    elif kw == ".PROGRAM":
            
        
        progdecl = translate_expression(rest).strip()
        (name, args, args_ref) = parse_function_call(progdecl)

        (name_vplus, __, __) = parse_function_call(rest.strip())

        programDict[name_vplus] = [args, _currentFile, _currentLineNo, None]
        programMangleP2V[name] = name_vplus
        programMangleV2P[name_vplus] = name
        
        if "__" in args_ref:
            raise SyntaxError, "Invalid .PROGRAM declaration"
        vs = ["def ", name, "(", args, "):"]
        
        _program_args = args_ref
        


    elif kw == "FOR":
        rest = translate_expression(rest)
        vs = split_keywords(rest)
        pos_to = vs.index("TO")
        (counter, ini_val) = split_at_equal_sign(string.join(vs[0:pos_to], ""))
        step = "1"
        if "STEP" in vs:
            pos_step = vs.index("STEP")
            fin_val = string.join(vs[pos_to+1 : pos_step], "")
            step = string.join(vs[pos_step+1 : ], "")
            vs = ['for ', counter.strip(), ' in range(', ini_val.strip(), ', ', '(', fin_val.strip(), ') + (', step.strip(), '), ', step.strip(), '):']
        else:
            fin_val = string.join(vs[pos_to+1 : ], "")
            vs = ['for ', counter.strip(), ' in ', ini_val.strip(), ' |TO| ', fin_val.strip(), ':']
            


    elif kw == "WHILE":
        rest = translate_expression(rest)
        vs = split_keywords(rest)
        if "DO" in vs:
            pos_do = vs.index("DO")
            cond = string.join(vs[0 : pos_do], "")
        else:
            cond = string.join(vs, "")
            
        vs = ['while ', cond.strip(), ':']
        
    elif kw == "IF":
        rest = translate_expression(rest)
        vs = split_keywords(rest)
        if "THEN" in vs:
            pos_then = vs.index("THEN")
            cond = string.join(vs[0 : pos_then], "")
        else:
            cond = string.join(vs, "")
            
        vs = ['if ', cond.strip(), ':']
    elif kw == "ELSEIF":
        vs = ['elif:']
    elif kw == "ELSE":
        vs = ['else:']
    elif kw == "WAIT":
        cond = translate_expression(rest)
            
        vs = ['while not (', cond.strip(), '): time.sleep(0.01)']
    elif kw == "WAIT.EVENT":
        args = translate_expression(rest).strip()
        print args
        if args[0] == ',':
            args = "0" + args
        vs = ['WAIT_EVENT(', args, ')']
    elif kw == "END":
        vs = ['#end']
    elif kw == ".END":
        vs = ['    return (', string.join(_program_args, ', '), ') # .END']
    elif kw == "RETURN":
        vs = ['return (', string.join(_program_args, ', '), ')']
    else:
        vs = [translate_expression(var)]


    var = string.join(vs, "")
    return var

def translate_expression(var):
    var = beautify_line(var)
    #print var

    stringsplit = split_strings(var)
    #print stringsplit
    newstr = []
    for block in stringsplit:
        if block[0] != '"':    # este ceva care nu e string, pot sa-l modific
            newstr.append(translate_block(block))
        else:
            newstr.append(block)
    
    return string.join(newstr, "")


def translate_block(var):    
    var = var.replace(":", "|")
    vs = re.split("([a-zA-Z\#\.][a-zA-Z0-9_\.]*)", var)
    newvs = []

    vs.append("")
    for i,s in enumerate(vs):
        if   s == 'BY'     : newvs.append(", ")
        elif s == 'HERE'   : newvs.append("HERE()")
        elif s == 'DEST'   : newvs.append("DEST()")
        elif s == 'TOOL'   : newvs.append("TOOL()")
        elif s == 'IPS'    : newvs.append(', "IPS"')
        elif s == 'MMPS'   : newvs.append(', "MMPS"')
        elif s == 'ALWAYS' : newvs.append(', "ALWAYS"')
        elif s == 'MONITOR': newvs.append(', "MONITOR"')
        elif s == 'MOD'    : newvs.append(" % ")
        else:
            newvs.append(s)

    vs = list(newvs)
    newvs = []
    # inlocuiesc punctul cu underscore
    for s in vs:
        if re.match("^[a-zA-Z\#][a-zA-Z0-9\.\_\#]*$", s): # nume de variabila
            newvs.append(s.replace(".", "_").replace("#", ""))
        else:
            newvs.append(s)
    
    var = string.join(newvs, "")
    return var

def split_keywords(line):
    reg_split = "([a-zA-Z\#\.][a-zA-Z0-9_\.]*)"
    vs = re.split(reg_split, line)
    return vs
    
def split_after_keyword(line):
    if len(line.strip()) == 0:
        return ("", "", [])
    
    
    vs = split_keywords(line)
    
    if len(vs[0].strip()) == 0:
        vs = vs[1:]

    keyword = vs[0].upper()
    rest = string.join(vs[1:], "")

    elements = vs
    return (keyword, rest, elements)
    
def split_strings(var):
    # sparg var in stringuri si non-stringuri
    
    if var.count('"') % 2:
        var = var + '"'
    
    str = '"[^"]*"'
    notstr = '[^"]*'
    block = "(" + str + "|" + notstr + "|" + ")"
    stringsplit = re.split(block, var)
    
    while "" in stringsplit:
        stringsplit.remove("")
        
    return stringsplit
    
def split_comment(var):
    
    stringsplit = split_strings(var)

    # acum caut primul comentariu
    for i,s in enumerate(stringsplit):
        if s[0] != '"':
            if ';' in s:
                split = s.index(';')
                code = string.join(stringsplit[:i], "") + s[:split]
                comment = s[split:] + string.join(stringsplit[i+1:], "")
                return (code, comment)
    return (var, "")

def split_at_equal_sign(var):
    m = re.match("^([^=]+)=([^=]+)$", var)
    if m:
        name = m.groups()[0]
        value = m.groups()[1]
        return (name, value)
    else:
        raise SyntaxError, "expected 'name = value' in '" + var + "' "
