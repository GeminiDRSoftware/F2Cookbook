#!/usr/bin/env python
# shaw@noao.edu: 2015-Aug-12

import numpy as np

def getNormCoords(pMin, pMax, nPix):
   '''Generate coordinates normalized to the interval [-1,1].
   '''
   return np.array([(2.*p - (pMax + pMin))/((pMax - pMin)) \
       for p in np.arange(1,nPix+1)])

def evDispersion(dispFunc, c, n, z=0.):
   '''Evaluate the named dispersion function over the normalized coordinates.
   '''
   disp = 0
   for i in range(len(c)):
       disp += c[i] * dispFunc(i+1,n)
   return disp / (1.+z)

def evLegendre(i,n):
   '''Evaluate the Legendre polynomial function for order term "i" over the 
      normalized coordinates.
   '''
   if i <= 1:
       return 1
   elif i == 2:
       return n
   else:
       return ((2*i-3)*n*evLegendre(i-1,n) - (i-2)*evLegendre(i-2,n)) / (i-1)

def evCheby(i,n):
   '''Evaluate the Chebyshev polynomial function for order term "i" over the 
      normalized coordinates.
   '''
   if i <= 1:
       return 1
   elif i == 2:
       return n
   else:
       return 2*n*evCheby(i-1,n) - evCheby(i-2,n)
