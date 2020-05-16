"""
Created on Thu May 14 16:34:22 2020

@author: Harshil
"""

import numpy as np
import scipy.signal as sp

# Leaky integrator
class LeakyIntegrator:
    def __init__(self, lmb):
        self.lmb = lmb
        self.y   = 0
    
    def compute(self, x):
        res = []
        for v in x:
            self.y = self.lmb * self.y + (1 - self.lmb) * v
            res.append(self.y)
        return res


# Simple Moving Average
class SimpleMovingAverage:
    def __init__(self, navg, items):
        self.navg  = navg
        self.items = items
    
    def calculate(self):
        av = []
        for i in range(1, len(self.items)):
            if i < self.navg:
                av.append(0)
            else:
                av.append(sum(self.items[i+1-self.navg:i+1]) / self.navg)
        return av


# Minimax Optimal Filter 
class MinimaxOptimalFilter:
    def __init__(self, order, A, B, Aweight, iters):
        self.A       = A
        self.B       = B
        self.Aweight = Aweight
        self.order   = order
        self.iters   = iters
    
    def weigh(self, x):
        if np.isscalar(x):
            return 1.0/self.Aweight if x <= self.A else 1
        else:
            return [1.0/self.Aweight if v <= self.A else 1 for v in x]
    
    def find_error_extrema(self, p):
        intervals = {
            (0, self.A): 1,
            (self.B, 1): 0
        }
        loc = []
        err = []
        for rng, val in intervals.items():
            t = np.linspace(rng[0], rng[1], 100)
            y = val - p(t)
            ix = np.diff(np.sign(np.diff(y))).nonzero()[0] + 1
            loc = np.hstack((loc, t[0], t[ix], t[-1]))
            err = np.hstack((err, y[0], y[ix], y[-1]))
        return loc, err

    def RemezFit(self):
        pts = self.order + 2
        ptsA = int(pts*self.A / (self.A-self.B+1))
        if ptsA <= 2:
            ptsA = 2
        ptsB = pts - ptsA

        x = np.concatenate((np.arange(1, ptsA+1) * (self.A / (ptsA+1)),
                            self.B + np.arange(1, ptsB+1) * ((1 - self.B) / (ptsB+1))
                            ))

        y = np.concatenate((np.ones(ptsA), np.zeros(ptsB)))        

        data = {}

        for n in range(self.iters):
            data['prev_x'] = x
            data['prev_y'] = y

            V = np.vander(x, increasing=True)
            V[:-1] = pow(-1, np.arange(0, len(x))) * self.weigh(x)
            v = np.linalg.solve(V, y)
            p = np.poly1d(v[-2::-1])
            e = np.abs(v[-1])
            
            data['Aerr'] = e / self.Aweight
            data['Berr'] = e

            loc, err = self.find_error_extrema(p)
            alt = []
            for n in range(len(loc)):
                c = {
                    'loc'    : loc[n],
                    'sign'   : np.sign(err[n]),
                    'err_mag': np.abs(err[n])
                }

                if c['err_mag'] >= e - 1e-3:
                    if alt == [] or alt[-1]['sign'] != c['sign']:
                        alt.append(c)
                    elif alt[-1]['err_mag'] < c['err_mag']:
                        alt.pop()
                        alt.append(c)

            while len(alt) > self.order+2:
                if alt[0]['err_mag'] > alt[-1]['err_mag']:
                    alt.pop(-1)
                else:
                    alt.pop(0)
            
            x = [c['loc'] for c in alt]
            y = [1 if c <= self.A else 0 for c in x]
            
            data['new_x'] = x       
        
        return p, data


class Butterworth:
    def __init__(self, order, lowcut, highcut, fs):
        self.lowcut    = lowcut
        self.highcut   = highcut
        self.fs        = fs
        self.order     = order
        self.nyq       = fs / 2
        self.low       = self.lowcut / self.nyq
        self.high      = self.highcut / self.nyq
    
    def filter(self, data):
        b, a = sp.butter(self.order, [self.low, self.high], btype='band')
        y    = sp.lfilter(b, a, data)
        return y

class ChebyshevType1:
    def __init__(self, order, ripple, fcut, fs):
        self.order  = order
        self.ripple = ripple
        self.fcut   = fcut
        self.fs     = fs
    
    def filter(self):
        wn = self.fcut / (0.5 * self.fs)
        b, a = sp.cheby1(self.order, self.ripple, wn, fs=self.fs)
        return b, a


class EllipticLowpass:
    def __init__(self, order, ripple, attenuation, fcut, fs):
        self.order       = order
        self.ripple      = ripple
        self.attenuation = attenuation
        self.fcut        = fcut
        self.fs          = fs
    
    def filter(self):
        wn = self.fcut / (0.5 * self.fs)
        b, a = sp.ellip(self.order, self.ripple, self.attenuation, wn, fs=self.fs)
        return b, a