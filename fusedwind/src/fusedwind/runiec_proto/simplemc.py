
import operator
import numpy as np
from numpy.random import weibull
from scipy.stats import vonmises, gamma
from math import pi


class MultiIndex(object):
    # multi-index class, indexing goes left to right (as opposed to counting in 
    # base "maxval", which would go right to left).
    # length is "dimension"
    def __init__(self,length, maxvals):
        self.maxvals = maxvals
        self.length = length
        self.midx = [0 for i in range(length)]
        
    def incr(self):
        done = True
        for i in range(self.length):
            if self.midx[i] < self.maxvals[i] - 1:
                self.midx[i] += 1
                done = False
                break;
            else:
                self.midx[i] = 0
        return done

def prod(x):
    val = 1
    for v in x:
        val *= v
    return val

def fn(x):
    val = sum(x**2)
    return val

#-------------
def draw_weibull(shape, scale, nsamples):
    x = scale * weibull(shape, nsamples)
    return x
def prob_weibull(x, shape, scale):
    p = (shape/scale)*(x/scale)**(shape-1)*np.exp(-(x/scale)**shape) 
    return p

def draw_vonmises(kappa, loc, nsamples):
#    print "kappa, loc: ", kappa, loc
#    x = 180/pi * vonmises.rvs(kappa, loc=loc, size=nsamples)
    x = vonmises.rvs(kappa, loc=loc, size=nsamples)
#    fvm.write("%f\n" % x[0])
    return x
def prob_vonmises(x, kappa, loc):
#    print "kappa, loc: ", kappa, loc
#    p = vonmises.pdf(x*pi/180.0,kappa, loc=loc)
#    p = vonmises.pdf(x,kappa, loc=loc)
    p = np.array([vonmises.pdf(x+m,kappa, loc=loc) for m in [-2*pi,0,2*pi]])
    p = np.amax(p,axis=0)
    return p

def draw_gamma(shape, scale, nsamples):
    x = gamma.rvs(shape, loc=0, scale=scale, size=nsamples)
    return x
def prob_gamma(x, shape, scale):
    p = gamma.pdf(x,shape, loc=0, scale=scale)
    return p
#-------------


def pdf(x):
    prob = prob_weibull(x,shape, scale)
#    prob = prob_gamma(x,gshape, gscale)
#    prob = prob_vonmises(x,kappa, loc)
    prob = prod(prob)
    return prob

def pdf2(x):
    global kappa0
    p0 = prob_weibull(x[0],shape, scale)
#    prob = prob_gamma(x,gshape, gscale)
    kappa = kappa0 + 0.2 * x[0]
    p1 = prob_vonmises(x[1],kappa, loc)
    prob = p0*p1
    return prob

def sample():
    x = draw_weibull(shape, scale, dim)
#    x = draw_gamma(gshape, gscale, dim)
#    x = draw_vonmises(kappa, loc, dim)
    return x

def sample2():
    x0 = draw_weibull(shape, scale,1)
#    x = draw_gamma(gshape, gscale, dim)
    x1 = draw_vonmises(kappa, loc,1)
    return np.array([x0[0],x1[0]])


def int_det(nsample):
    dx = (xmax-xmin)/float(nsample-1)
    lsum = 0
    psum = 0
    done =False
    xmin_vec = xmin * np.ones(dim)
    midx = MultiIndex(dim, [nsample for i in range(dim)])
    while not done:
        x = xmin_vec + dx * np.array(midx.midx)
        val = fn(x)
        prob = pdf(x)
        psum += prob
        lsum += (val * prob * dx**dim)
#        print x, val, prob, lsum, psum, dx
        done = midx.incr()
    print "det int done, ", lsum, psum,  psum * dx**dim
    return lsum

def int_det2(nsample):
    ns = np.array(nsample)
    dx = np.divide((xmax-xmin),(ns-1.0))
    lsum = 0
    psum = 0
    done =False
    midx = MultiIndex(dim, nsample)
    while not done:
        x = xmin + np.multiply(dx, np.array(midx.midx))
        val = fn(x)
        prob = pdf2(x)
        psum += prob
        lsum += (val * prob * prod(dx))
#        print x, val, prob, lsum, psum, dx
        done = midx.incr()
    print "det int done, ", lsum, psum,  psum * prod(dx)
    return lsum


def int_det4(sctx,nsample,write,read):
    ns = np.array(nsample)
    dx = np.divide((xmax-xmin),(ns-1.0))
    lsum = 0
    psum = 0
    done =False
    midx = MultiIndex(dim, ns)
    idx = 0
    while not done:
        x = xmin + np.multiply(dx, np.array(midx.midx))
        if (write):
            for j in range(dim):
                fscan.write("%f " % x[j])
            fscan.write("\n")
        if (read):
            val = fscanlines[idx][20]  ### NOTE exact field of interest!
        else:
            val = fn(x)
        prob = sctx.calc_prob(x)
#        prob = pdf2(x)
        psum += prob
        lsum += (val * prob * prod(dx))
#        print x, val, prob, lsum, psum, dx
        done = midx.incr()
        idx += 1
    print "det int done, ", lsum, psum,  psum * prod(dx)
    return lsum


def int_mc(nsample_per_dim):
    nsample = nsample_per_dim ** dim
    lsum = 0
    for i in range(nsample):
        x = sample()
        val = fn(x)
        lsum += val
#        print x,val, lsum
    lsum /= nsample
    return lsum

def int_mc2(ns):
    nsample = prod(ns)
    lsum = 0
    for i in range(nsample):
        x = sample2()
        val = fn(x)
        lsum += val
#        print x,val, lsum
    lsum /= nsample
    return lsum

def int_mc4(sctx,ns,write,read):
    nsample = prod(ns)
    sctx.sample(nsample)
    if (dim == 1):
        xx = sctx.Vhub
    elif (dim == 2):
        xx = zip(sctx.Vhub, sctx.WaveDir)
    elif(dim == 4):
        xx = zip(sctx.Vhub, sctx.WaveDir, sctx.Hs, sctx.Tp)
    lsum = 0
    for i in range(nsample):
        x = np.array(xx[i])
        if (dim == 1):
            x = np.array([x])
        if (write):
            for j in range(dim):
                fsamp.write("%f " % x[j])
            fsamp.write("\n")
        if (read):
            val = fsamplines[i][20]  ### NOTE exact field of interest!
        else:
            val = fn(x)
        lsum += val
#        print x,val, lsum
    lsum /= nsample
    return lsum


def simple_test():
    fvm = file("vm.dat", "w")

    xmin = 0
    xmax = 10
    shape = 2.120
    scale = 9.767
    gshape = 10
    gscale = .2
#    xmin = -pi
#    xmax = pi
    kappa = 1
    loc = -0.1
    
    dim = 3
    allns = [11,21,41,81]

    dim = 1
    allns = [11,21,41,81,161,321,641,1281,2561,5121,10241]

#    dim = 4
#    allns = [5,9,17,33]

    dim = 1
    allns = [5,11,21,41,81,161,321,641,1281,2561,5121]
#    dim = 2
#    allns = [5,11,21,41,81]

    for ns in allns:
        lsum1 = int_det(ns)
        lsum2 = int_mc(ns)
        print ns, lsum1, lsum2


    fvm.close()

def less_simple_test():
    global xmin, xmax, shape, scale, gshape, gscale, kappa, loc, dim, kappa0
    xmin = np.array([4,-pi])
    xmax = np.array([24,pi])
    shape = 2.120
    scale = 9.767
    gshape = 10
    gscale = .2
    kappa = 1
    kappa0 = 1
    loc = -0.1

    dim = 2
    allns = [5,11,21,41,81]
    for ns in allns:
        ns = [ns for i in range(dim)]
        lsum1 = int_det2(ns)
        lsum2 = int_mc2(ns)
        print ns, lsum1, lsum2

def real_test(write=False, read=False):
    import sampler
    global xmin, xmax, shape, scale, gshape, gscale, kappa, loc, dim, kappa0
    global fsamp
    global fscan
    global fsamplines
    global fscanlines


    shape = 2.120
    scale = 9.767
    gshape = 10
    gscale = .2
    kappa = 1
    kappa0 = 1
    loc = -0.1

    dim = 1
    xmin = np.array([0])
    xmax = np.array([50])
    allns = [[20] ]

#    dim = 2
#    xmin = np.array([0,-pi+0.001])
#    xmax = np.array([30,pi-0.001])
#    allns = [[5,9],[11,9],[21,9] , [100,100]  ]

    dim = 4
    xmin = np.array([1,-pi,0,0])
    xmax = np.array([30,pi,6,6])
    allns = [  [2,2,3,3], [3,3,3,3],  [4,4,3,3], [4,4,4,4], [8,8,6,6] ,[10,10,8,8] ]
#    allns = [   [4,4,3,3], [8,8,6,6] , [16,16,12,12]    ]
#    allns = [[2,2,3,3]  ]
#    allns = [ [3,3,3,3], [4,4,4,4] ]
#    allns = [ [10,10,8,8] ]
    allns = [[6,6,4,4], [6,6,6,6]]
    sctx = sampler.Context(dim)

    for ns in allns:
        if (write):
            fname = "mc_samples"
            for d in ns:
                fname += "%d" % d
            fname += ".txt"
            fsamp = file(fname,"w")
            fsamp.write("Vhub WaveDir Hs Tp\n");
            fname = "int_samples"
            for d in ns:
                fname += "%d" % d
            fname += ".txt"
            fscan = file(fname, "w")
            fscan.write("Vhub WaveDir Hs Tp\n");
        if (read):
            fname = "mc_samples"
            for d in ns:
                fname += "%d" % d
            fname += ".out"
            fsamplines = file(fname).readlines()
            fsamplines = fsamplines[1:]
            fsamplines = [[float(x) for x in ln.split()] for ln in fsamplines]
            fname = "int_samples"
            for d in ns:
                fname += "%d" % d
            fname += ".out"
            fscanlines = file(fname).readlines()
            fscanlines = fscanlines[1:]
            fscanlines = [[float(x) for x in ln.split()] for ln in fscanlines]
    
        lsum1 = int_det4(sctx,ns,write,read)
        lsum2 = int_mc4(sctx,ns,write,read)
        print ns, lsum1, lsum2
#        print ns,  lsum2
        if (write):
            fsamp.close()
            fscan.close()

    

if __name__=="__main__":
#    simple_test()
#    less_simple_test()
#    real_test(write=True, read=False)
    real_test(write=False, read=True)
