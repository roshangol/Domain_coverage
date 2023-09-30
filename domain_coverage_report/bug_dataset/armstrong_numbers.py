def armstrong_number(n: int) -> bool:
    sum = 0
    number_of_digits = 0
    temp = n
    while temp > 0:
        number_of_digits += 1
        temp //= 10
    temp = n
    while temp > 0:
        rem = temp - 10
        sum += rem ** number_of_digits
        temp //= 10
    return n == sum
