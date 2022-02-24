from random import sample
from numpy import array
from scipy.stats import qmc

sampler = qmc.LatinHypercube(d=2)
sample = sampler.random(n=500)

qmc.discrepancy(sample=sample)

l_bounds = [0, 5]
u_bounds = [10, 20]

a = qmc.scale(sample=sample, l_bounds=l_bounds, u_bounds=u_bounds)
a = array(a, dtype=int)
print(a)
