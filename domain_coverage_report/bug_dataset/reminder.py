def reminder(a: int, b: int):
    r = -1
    cy = 0
    ny = 0
    if a == 0:
        return 0
    elif b == 0:
        return 0
    elif a > 0:
        if b > 0:
            while (a - ny) >= b:
                ny = ny - b
                r = a - ny
                cy = cy + 1
        elif b < 0:
            while (a + ny) >= abs(b):
                ny = ny + b
                r = a + ny
                cy = cy - 1
    elif b > 0:
        while abs(a + ny) >= b:
            ny = ny + b
            r = a + ny
            cy = cy - 1
    elif a < 0 and b < 0:
        while(b >= (a - ny)):
            ny = ny + b
            r = abs(a - ny)
            if a - ny >= 0:
                r = a - ny
            else:
                r = -(a - ny)
            cy = cy + 1
    return r
