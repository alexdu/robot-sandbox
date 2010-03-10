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

def stiva():
    st_bottom = TRANS(500,0,100,0,180,0)
    h = 15

    PARAMETER("HAND.TIME", 1)
    SPEED(100, ALWAYS)
    
    OPEN()
    MOVE(safe)
    BREAK()    
    
    for i in 1 |TO| 5:
        p = worldObject("Box%d"%i).pos
        pick = TRANS(p[0],p[1],100,0,180,90)
    
        place = SHIFT(st_bottom, 0, 0, h * (i-1))
        pick_place(pick, place)

    MOVE(safe)
    BREAK()

stiva()
