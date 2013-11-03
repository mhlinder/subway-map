import numpy as np

def CCW(a,b,c):
    n = np.shape(a)[0]
    a11 = np.ones(n)
    a21 = np.ones(n)
    a31 = np.ones(n)
    a12 = a[:,0]
    a13 = a[:,1]
    a22 = b[:,0]
    a23 = b[:,1]
    a32 = c[:,0]
    a33 = c[:,1]

    det = a11*(a22*a33 - a23*a32) - a12*(a21*a33 - a23*a31) + a13*(a21*a32 - a22*a31)
    return det > 0

def intersect(l1,l2):
    n = np.shape(l1)[0]
    result = np.ones(n)
    p11 = l1[:,0:2]
    p12 = l1[:,2:4]
    p21 = l2[:,0:2]
    p22 = l2[:,2:4]
    result[CCW(p11, p21, p22) == CCW(p12, p21, p22)] = 0
    result[CCW(p11, p12, p21) == CCW(p11, p12, p22)] = 0
    return result
n = 100000000
# n = 1000
sample = np.random.randn(n,8)
result = intersect(sample[:,0:4], sample[:,4:8])
