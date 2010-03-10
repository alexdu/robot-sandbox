def pick_place(pick,place):
    z_pick = 100
    z_place = 100
    
    OPEN()
    APPRO(pick, 100)
    BREAK()
    SPEED(30)
    MOVE(pick)
    CLOSEI()
    SPEED(30)
    DEPART(100)
    BREAK()

    APPRO(place, 100)
    BREAK()
    SPEED(30)
    MOVE(place)
    OPENI()
    SPEED(30)
    DEPART(100)
    BREAK()

def palet():
    pal = TRANS(500,-100,100,0,180,-20)
    h = 15

    PARAMETER("HAND.TIME", 1)
    SPEED(100, ALWAYS)
    
    OPEN()
    MOVE(safe)
    BREAK()    
    
    for p in 1 |TO| 5:
        pos = worldObject("Box%d"%p).pos
        pick = TRANS(pos[0],pos[1],100,0,180,90)
        
        
        place = RZ(20) * TRANS(((p-1) |MOD| 2)*120, INT((p-1)/2)*120, 0) * RZ(-20) * pal
        pick_place(pick, place)

    MOVE(safe)
    BREAK()

palet()
