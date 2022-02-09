from operator import gt
from random import randrange
from numpy import array
from numpy import loadtxt
from warnings import warn
from copy import deepcopy

import os 

class Individual:

	def __init__(self):
		self.__fit   = None
		self.__gene  = []
		self.xwindow = 48
		self.ywindow = 48
		self.linf	 = -25
		self.lsup	 = 25

	def create(self):
	
		x1 = randrange(-self.xwindow, self.xwindow)%self.xwindow - self.xwindow/2
		y1 = randrange(-self.ywindow, self.ywindow)%self.ywindow - self.ywindow/2
		x2 = randrange(-self.xwindow, self.xwindow)%self.xwindow - self.xwindow/2
		y2 = randrange(-self.ywindow, self.ywindow)%self.ywindow - self.ywindow/2

		self.__gene = array([x1, y1, x2, y2], dtype=int)
		
		
	def get(self):
		return self.__gene
	
	def set(self, gen):
		self.__gene = gen

	def get_fit(self):
		return self.__fit

	def set_fit(self, f):
		self.__fit = f

	def __lt__(self, other):
		return self.get_fit() > other.get_fit()

	def __gt__(self, other):
		return other.__lt__(self)

	def __eq__(self, other):
		return self.get_fit() == other.get_fit()
	
	def __ne__(self, other):
		return not self.__eq__(other)  

class Population:

	def __init__(self, np):
		self.__np = np
		self.__individuals = []

	def create(self):
		
		population_data = loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'pair_stats.txt'), delimiter=' ', dtype=int)
		
		for i in population_data[-self.__np:]:    
			individual = Individual()
			individual.set(array(i[:-1]))
			individual.set_fit(i[-1])
			self.__individuals.append(individual)

		return self.__individuals

	def get(self):
		return self.__individuals

	def opposite(self, individuals):

		oppindividuals = []
		
		for i in individuals:
			
			gtemp = []
			for x in i.get():
				xx = (i.lsup + i.linf) - x
				gtemp.append(xx)

			oppindv = Individual()
			oppindv.set(array(gtemp))
			oppindv.set_fit(None)
			oppindividuals.append(oppindv)

		return oppindividuals
