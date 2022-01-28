from numpy.random import randint
from numpy.random import uniform 
from numpy.random import exponential
from population   import Individual
from population   import Population
from evfunctions  import Evaluation
from numpy        import array
from numpy        import loadtxt
from numpy        import savetxt
from heapq        import heappop
from heapq        import heappush
from time         import time
from sys          import exit

import os

class DifferentialEvolution:

	def __init__(self, np, cr, f, algorithm):
		self.__np         = np
		self.__cr         = cr
		self.__f          = f
		self.__algorithm  = None
		self.__evfunc     = Evaluation()
		self.__population = []
		self.__temporaryp = []
		self.__crosstype  = None
		self.__best_solution = None
		self.__all_solutions = []
		self.__all_best_solutions = []
		self.__total_time = None

		if callable(getattr(self, algorithm, None)):
			self.__algorithm = getattr(self, algorithm, None)
			self.__crosstype = algorithm.split('_')[-1]

		else:
			print('\nERROR:\n\tDE algorithm \'{}\' is not available.'.format(algorithm))
			exit(-1)

		
	def heap_sort(self):

		heap = []
		for individual in self.__population:
			heappush(heap, individual)

		ordered = []
		while heap:
			ordered.append(heappop(heap))

		self.__population = ordered
	

	def evaluate(self):
		
		for individual in self.__population:
			fit = self.__evfunc.compute(individual.get())
			individual.set_fit(fit)
		
		for t_individual in self.__temporaryp:
			fit = self.__evfunc.compute(t_individual.get())
			t_individual.set_fit(fit)

	def evolve(self):
		
		ti = time()

		self.__all_solutions = []
		self.__all_best_solutions = []

		population = Population(np=self.__np)

		self.__population = population.create() 


		for i, individual in enumerate(self.__population):
			# mutation
			mutated_vector = self.mutate(i)

			# crossover
			new_individual = Individual()
			new_individual.create()

			u = self.crossover(individual, mutated_vector)

			new_individual.set(array(u))
			self.__temporaryp.append(new_individual)

		self.__all_solutions = self.__temporaryp

		tf = time()	  
		self.__total_time =  tf - ti

	def mutate(self, i):
		return self.__algorithm(i)

	def crossover(self, individual, mutated_vector):

		call = None
		if self.__crosstype == 'exp':
			call = exponential
		elif self.__crosstype == 'bin':
			call = uniform 
		
		J = randint(0, self.__np)

		u = []
		for j, value in enumerate(individual.get()):
			r = float(format(call(), '.1f'))
			if r < self.__cr or j == J:
				u.append(mutated_vector[j])
			else:
				u.append(value)

		return u

	def get_best(self):

		best = self.__population[0]
		# for indv in self.__population:
		#     if indv.get_fit() < best.get_fit():
		#         best = indv

		return best
	
	def get_best_solution(self):
		return self.__best_solution

	def get_all_solutions(self):
		return self.__all_solutions

	def get_all_best_solutions(self):
		return self.__all_best_solutions

	def get_execution_time(self):
		return self.__total_time

	def rand_1_bin(self, i):

		''' Vi,G = Vr1,G + F (Vr2,G - Vr3,G) '''

		indexes = []
		indexes.append(i)     
		while len(indexes) <= 4:
			r = randint(0, self.__np)
			if not r in indexes:
				indexes.append(r)

		r1, r2, r3 = indexes[1], indexes[2], indexes[3]

		v = self.__population[r1].get() + self.__f * (self.__population[r2].get() - self.__population[r3].get())

		return v


	def rand_2_bin(self, i):

		''' Vi,G = Vr1,G + F (Vr2,G - Vr3,G + Vr4,G – Vr5,G) '''

		indexes = []
		indexes.append(i)     
		while len(indexes) <= 6:
			r = randint(0, self.__np)
			if not r in indexes:
				indexes.append(r)

		r1, r2, r3, r4, r5 = indexes[1], indexes[2], indexes[3], indexes[4], indexes[5]

		v = self.__population[r1].get() + self.__f * ((self.__population[r2].get() - self.__population[r3].get()) + (self.__population[r4].get() - self.__population[r5].get()))

		return v


	def randtobest_1_bin(self, i):
		
		''' Vi,G = Vr1,G + F (Vbest,G – Vr1,G + Vr2,G – Vr3,G) '''

		best = self.__population.index(self.get_best())

		indexes = []
		indexes.append(i)   
		indexes.append(best)  

		while len(indexes) <= 5:
			r = randint(0, self.__np)
			if not r in indexes:
				indexes.append(r)

		r1, r2, r3 = indexes[1], indexes[2], indexes[3]  

		v = self.__population[r1].get() + self.__f * (( self.__population[best].get() - self.__population[r1].get()) + (self.__population[r2].get() - self.__population[r3].get()))

		return v


	def rand_2_exp(self):
		pass

	def best_1_bin(self, i):
		
		''' Vi,G = Vbest,G + F (Vr2,G - Vr3,G) '''

		best = self.__population.index(self.get_best())

		indexes = []
		indexes.append(i)   
		indexes.append(best)  

		while len(indexes) <= 4:
			r = randint(0, self.__np)
			if not r in indexes:
				indexes.append(r)

		r2, r3 = indexes[2], indexes[3]  

		v = self.__population[best].get() + self.__f * (self.__population[r2].get() - self.__population[r3].get())

		return v


	def best_2_exp(self):
		pass

	def currenttobest_1_bin(self, i):

		''' Vi,G = Vi,G + F (Vbest,G – Vi,G + Vr2,G – Vr3,G) '''

		best = self.__population.index(self.get_best())
		current = i

		indexes = []
		indexes.append(current)   
		indexes.append(best)
		
		while len(indexes) <= 4:
			r = randint(0, self.__np)
			if not r in indexes:
				indexes.append(r)

		r2, r3 = indexes[2], indexes[3]
		
		v = self.__population[current].get() + self.__f * ((self.__population[best].get() - self.__population[current].get()) + (self.__population[r2].get() - self.__population[r3].get()))

		return v

	def currenttorand_1_bin(self, i):
		
		''' Vi,G = Vi,G + F (Vr1,G – Vi,G + Vr2,G – Vr3,G) '''
		
		current = i

		indexes = []
		indexes.append(current)   
		
		while len(indexes) <= 4:
			r = randint(0, self.__np)
			if not r in indexes:
				indexes.append(r)

		r1, r2, r3 = indexes[1], indexes[2], indexes[3]        

		v = self.__population[current].get() + self.__f * ((self.__population[r1].get() - self.__population[current].get()) + (self.__population[r2].get() - self.__population[r3].get()))

		return v



if __name__ == '__main__':


	de = DifferentialEvolution(
		np=10,
		cr=0.7, 
		f=0.8, 
		algorithm='rand_1_bin'
	)

	de.evolve()	
	new_individuals = de.get_all_solutions()

	population_data = loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), delimiter=' ', dtype=int)
	population_data = list(population_data[:-10])

	for new in new_individuals:
		population_data.append(array(new.get(), dtype=int))
	
	for i, indv in enumerate(population_data):
		population_data[i] = ' '.join(map(str, indv))

	savetxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), population_data, delimiter=' ', fmt='%s')

	