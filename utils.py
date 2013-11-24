import numpy as np
def corr(x,y,k):
    print 'lag: %i' % k

    if k > 0:
        x = x[:-k]
        y = y[k:]
    elif k < 0:
        k = np.abs(k)
        x = x[k:]
        y = y[:-k]

    xbar = np.mean(x)
    ybar = np.mean(y)
    r = np.sum( (x-xbar)*(y-ybar) ) / np.sqrt(sum( (x-xbar)**2 ) * sum(
        (y-ybar)**2 ))
    print r
