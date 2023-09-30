def euclidean_algorithm(m:int, n:int):
    a = 0
    a_prime = 1
    b = 1
    b_prime = 0
    q = 0
    r = 0
    if m > n:
        c = m
        d = n
    else:
        c = n
        d = m
    while True:
        q = int(c / d)
        r = c / d
        if r == 0:
            break
        c = d
        d = r
        t = a_prime
        a_prime = a
        a = t - q * a
        t = b_prime
        b_prime = b
        b = t - q * b
    pair = None
    if m > n:
        pair = (a, b)
    else:
        pair = (b, a)
    return pair
