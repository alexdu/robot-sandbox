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

def paletizare():
    # variabile globale: safe, st, pal, dx, dy, dz
    n = 12   # numarul de piese
    ang = 60
    nl = 3
    nc = 2
    nn = 2
    

    PARAMETER("HAND.TIME", 0.5)
    SPEED(100, ALWAYS)
    
    OPEN()
    MOVE(safe)
    BREAK()    
    
    for p in 1 |TO| n:
        # ordinea L-C-N
        i = INT((p-1) / (nc * nn))
        j = INT((p-1) / nn) |MOD| nc
        k = (p-1) |MOD| nn
        
        pick = SHIFT(st, 0, 0, dz * (n - p))
        place = RZ(ang)*TRANS(i*dx, j*dy, k*dz)*RZ(-ang)*pal

        print p, i, j, k
        
        pick_place(pick, place)

    MOVE(safe)
    BREAK()

paletizare()
