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

def spirala():
    #GLOBAL a, b, c, safe, h

    total_ang = 360
    n = 12
    SPEED(100, ALWAYS)
    
    OPEN()
    MOVE(safe)
    BREAK()

    for p in 1 |TO| n:
        i = p-1
        if i |MOD| 2 == 0:
             pick = SHIFT(a, 0, 0, -h * INT(i/2))
        else:
             pick = SHIFT(b, 0, 0, -h * INT(i/2))
        
        place = SHIFT(c, 0, 0, h*i) * RZ(total_ang * i / (n-1))
        pick_place(pick, place)
    
    MOVE(safe)


spirala()
