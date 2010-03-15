def pick_place(pick,place):
    z_pick = 100
    z_place = 100
    
    OPEN()
    APPRO(pick, 100)
    BREAK()
    SPEED(30)
    MOVES(pick)
    CLOSEI()
    SPEED(30)
    DEPARTS(100)
    BREAK()

    APPRO(place, 100)
    BREAK()
    SPEED(30)
    APPROS(place, 1)
    OPENI()
    SPEED(30)
    DEPARTS(100)
    BREAK()

def pal_back():
    # variabile globale: safe, st, pal, dx, dy, dz
    n = 12   # numarul de piese
    ang = -30
    nl = 2
    nc = 3
    nn = 2
    

    PARAMETER("HAND.TIME", 0.5)
    SPEED(100, ALWAYS)
    
    OPEN()
    MOVE(safe)
    BREAK()    
    
    for p in n |TO| 1:
        # ordinea L-C-N
        i = INT((p-1) / (nc * nn))
        j = INT((p-1) / nn) |MOD| nc
        k = (p-1) |MOD| nn
        
        print p, i, j, k
        
        place = SHIFT(st, 0, 0, dz * (n - p))
        pick = RZ(ang)*TRANS(i*dx, j*dy, k*dz)*RZ(-ang)*pal
        
        pick_place(pick, place)

    MOVE(safe)
    BREAK()

pal_back()
