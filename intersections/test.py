import numpy as np

def CCW(a,b,c):
    a11 = 1
    a21 = 1
    a31 = 1
    a12 = a[0]
    a13 = a[1]
    a22 = b[0]
    a23 = b[1]
    a32 = c[0]
    a33 = c[1]

    det = a11*(a22*a33 - a23*a32) - a12*(a21*a33 - a23*a31) + a13*(a21*a32 - a22*a31)
    return det > 0

def intersect(l1,l2):
    x1 = l1[0:2]
    y1 = l1[2:4]
    x2 = l2[0:2]
    y2 = l2[2:4]
    if CCW(x1, x2, y2) == CCW(y1, x2, y2):
        return False
    elif CCW(x1, y1, x2) == CCW(x1, y1, y2):
        return False
    return True

n = 100000000
sample = np.random.randn(n,8)
for i in np.arange(n):
    draw = sample[i]
    intersect(draw[0:4], draw[4:8])
