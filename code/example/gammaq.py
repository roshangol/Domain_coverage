import math

def gammaq(a: float, x: float):
    eps=3.e-7
    if (x < 0.0 or a <= 0.0):
        return'Bad value for a or x'
    if (x < a + 1.0):
        gln = gammln(a)
        itmax = 700
        if (x < 0.0):
            return 'Bad value for x'
        if (x == 0.0):
            return(0.0, 0.0)
        ap = a
        total = 1.0 / a
        delta = total
        n = 1
        while n <= itmax:
            ap = ap + 1.0
            delta = delta * x / ap
            total = total + delta
            if (abs(delta) < abs(total) * eps):
                a = total * math.exp(-x + a * math.log(x) - gln)
            n = n + 1
        return 1.0 - a
    else:
        gln = gammln(a)
        itmax = 200
        gold = 0.0
        a0 = 1.0
        a1 = x
        b0 = 0.0
        b1 = 1.0
        fac = 1.0
        n = 1
        while n <= itmax:
            an = n
            ana = an - a
            a0 = (a1 + a0 * ana) * fac
            b0 = (b1 + b0 * ana) * fac
            anf = an * fac
            a1 = x * a0 + anf * a1
            b1 = x * b0 + anf * b1
            if (a1 != 0.0):
                fac = 1.0 / a1
                g = b1 * fac
                if (abs((g - gold) / g) < eps):
                    a = g * math.exp(-x + a * math.log(x) - gln)
                gold = g
            n = n + 1
        return a


def gammln(n):
    gammln_cof = [76.18009173, -86.50532033, 24.01409822,-1.231739516e0, 0.120858003e-2, -0.536382e-5]
    x = n - 1.0
    tmp = x + 5.5
    tmp = (x + 0.5) * math.log(tmp) - tmp
    ser = 1.0
    for j in range(6):
        x = x + 1.
        ser = ser + gammln_cof[j] / x
    return tmp + math.log(2.50662827465 * ser)