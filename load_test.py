from numpy import loadtxt
import numpy as np
import os
from matplotlib import pyplot as plt
import random
media_dez_melhores = []
media_dez_piores = []
media = []


for i in range(3030):
    pop = loadtxt(os.path.join(os.getcwd(), 'evaluations_GRIEF', str(i+1).zfill(5)+'.txt'), delimiter=' ', dtype=int)
    idx_ordem = np.argsort(pop[:,4])
    media_dez_melhores.append(np.mean(pop[idx_ordem[-10:],4]))
    media_dez_piores.append(np.mean(pop[idx_ordem[:10],4]))
    media.append(np.mean(pop[:,4]))

print(media[1557])
plt.plot(media, label='media')
plt.plot(media_dez_melhores, label='media dez melhores')
plt.plot(media_dez_piores, label='media dez piores')
plt.legend()
plt.show()
