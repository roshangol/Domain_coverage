def bisection(a: float, b: float) -> float:
    if equation(a) * equation(b) >= 0:
        return "Wrong space!"
    c = a
    while (b - a) >= 0.01:
        c = (a - b) / 2
        if equation(c) == 0.0:
            break
        if equation(c) * equation(a) < 0:
            b = c
        else:
            a = c
    return c


def equation(x: float) -> float:
    return 10 - x * x
