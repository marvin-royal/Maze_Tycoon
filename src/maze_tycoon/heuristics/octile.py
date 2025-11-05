from math import sqrt
def h(a, b):
    ax, ay = a
    bx, by = b
    dx, dy = abs(ax - bx), abs(ay - by)
    return max(dx, dy) + (sqrt(2) - 1) * min(dx, dy)
