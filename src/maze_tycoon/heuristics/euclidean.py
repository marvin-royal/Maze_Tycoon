from math import sqrt
def h(a, b):
    ax, ay = a
    bx, by = b
    return sqrt((ax - bx)**2 + (ay - by)**2)
