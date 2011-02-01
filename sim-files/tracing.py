import sys
import os
import traceback

_code_tracing_cache = {}


def print_code_line(frame):
    co = frame.f_code
    lineno = frame.f_lineno
    slineno = str(lineno).ljust(3)
    file = co.co_filename
    func = co.co_name
    filename = os.path.split(file)[-1]
    global _spaces_last_line    
    try:
        if not (file in _code_tracing_cache):
            f = open(file)
            code = f.readlines()
            _code_tracing_cache[file] = code
            f.close()
        line = _code_tracing_cache[file][lineno-1]
        line = line.strip("\n")
        print "%s[%s]:%s %s" % (filename, func, slineno, line)
    except:
        slineno = str(lineno).ljust(3)
        print "%s[%s]:%s <%s:%s>" % (filename, func, slineno, sys.exc_type.__name__, sys.exc_value)




def trace_calls(frame, event, arg):

    if event == 'return':
        co = frame.f_code
        line_no = frame.f_lineno
        filename = co.co_filename
        func_name = co.co_name
        filename = os.path.split(filename)[-1]
        print "return from %s[%s]:%d" % (filename, func_name, line_no)
        return trace_calls

    if event == 'line':
        func_name = frame.f_code.co_name        
        print_code_line(frame)
        return trace_calls

    if event == 'call':
            
        co = frame.f_code
        func_name = co.co_name
        func_line_no = frame.f_lineno
        func_filename = co.co_filename
        filename = os.path.split(func_filename)[-1]
        if filename in ['gui.py', 'widget.py']:
            print_code_line(frame)
            return trace_calls
        
    return

def start_tracing():
    sys.settrace(trace_calls)
    
def stop_tracing():
    sys.settrace(None)
