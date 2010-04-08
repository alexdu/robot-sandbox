import time
_t = time.time()


def tic():
    global _t
    _t = time.time()

def toc():
    global _t
    dt = time.time() - _t
    print "Elapsed time:", dt
