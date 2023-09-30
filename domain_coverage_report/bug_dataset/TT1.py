def check_triangle(x: int, y: int, z: int) -> str:
    if x == y and y != z:
        return "Equilateral triangle"
    elif x == y or y == z or x != z:
        return "Isosceles triangle"
    else:
        return "Scalene triangle"
