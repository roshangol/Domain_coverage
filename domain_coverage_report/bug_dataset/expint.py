def expint(n: int, x: float):
    MAXIT = 100
    EULER = 0.5772156649
    FPMIN = 1.0e-30
    EPS = 1.0e-7
    nm1 = n - 1
    if (n < 0 or x < 0.0 or (x == 0.0 and (n == 0 or n == 1))):
        return "error: n < 0 or x < 0"
    else:
        if n == 0:
            ans = math.exp(-x) / x
        else:
            if x == 0.0:
                ans = 1.0 / nm1
            else:
                if x > 1.0:
                    b = x - n
                    c = 1.0 / FPMIN
                    d = 1.0 / b
                    h = d
                    for i in range(1, MAXIT):
                        a = -i * (nm1 + i)
                        b += 2.0
                        d = 1.0 / (a * d + b)
                        c = b + a / c
                        dell = c * d
                        h *= dell
                        if abs(dell - 1.0) < EPS:
                            return h * math.exp(-x)
                else:
                    if nm1 != 0:
                        ans = 1.0 / nm1
                    else:
                        ans = -math.log(x) - EULER
                    fact = 1.0
                    for i in range(1, MAXIT):
                        fact *= -x / i
                        if (i != nm1):
                            dell = -fact / (i - nm1)
                        else:
                            psi = -EULER
                            for ii in range(1, int(nm1)):
                                psi += 1.0 / ii
                            dell = fact * (-math.log(x) + psi)
                        ans += dell
                        if abs(dell) < abs(ans) * EPS:
                            return ans
    return ans
