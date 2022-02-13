from numpy.random import randint
from numpy.random import uniform 
from numpy.random import exponential
from population   import Individual
from population   import Population
from numpy        import array
from numpy        import loadtxt
from numpy        import savetxt
from heapq        import heappop
from heapq        import heappush
from time         import time
from sys          import exit, argv
from copy 		  import deepcopy
from random		  import sample
import os


class DifferentialEvolution:

	def __init__(self, np, cr, f, ng, algorithm, change, obl, obl_gen_rate, obl_aggressive, obl_aggressive_rate):
	
		self.__np         		   = np
		self.__cr         		   = cr
		self.__f         		   = f
		self.__ng		  		   = ng
		self.__algorithm  		   = None
		self.__population 		   = []
		self.__crosstype  		   = None
		self.__total_time 		   = None
		self.__obl		  		   = obl
		self.__obl_gen_rate	  	   = obl_gen_rate
		self.__obl_aggressive 	   = obl_aggressive
		self.__obl_aggressive_rate = obl_aggressive_rate
		self.__aux_population 	   = []
		self.__criteria_of_change  = change
		self.__selected_to_change  = {'indv': [], 'indexes': []}
	
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

		self.__population = deepcopy(ordered)


	def evaluate(self):

		population_data = []
		for individual in self.__population:
			population_data.append(individual.get())

		savetxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), population_data, delimiter=' ', fmt='%s')
		
		#Função de avaliação
		cmd = "./tools/evaluate GRIEF-datasets/planetarium"
		os.system(cmd)
	
		evaluation = loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'evaluation.txt'), delimiter=' ', dtype=int)
		return int(evaluation)


	def evaluate_new_population(self, op=False):

		population_data = []
		for individual in self.__population:
			population_data.append(individual.get())

		# os.system("cp ./tools/grief/pair_stats.txt ./tools/grief/pair_stats.bak")
		# os.system("cp store.tmp store.bak")
		savetxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), population_data, delimiter=' ', fmt='%s')
		
		os.system("./tools/generate_eval.sh ")

		#Função de avaliação
		cmd = "./tools/evaluate GRIEF-datasets/planetarium| grep fitness > store.tmp"
		os.system(cmd)

		if op:
			return int(loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'evaluation.txt'), delimiter=' ', dtype=int))
		
		return

	def select_individuals(self, aggressive=False):

		key, n = self.__criteria_of_change
		
		if aggressive:
			n = int((self.__np * self.__obl_aggressive_rate)/100)
			
		self.__selected_to_change['indv']    = []
		self.__selected_to_change['indexes'] = []

		if key == 'worst':
			
			indexes = [i for i in range(self.__np)][-n:]
			self.__selected_to_change['indexes'] = indexes
			
			for i in indexes:
				self.__selected_to_change['indv'].append(self.__population[i])

		
		elif key == 'rand':

			indexes = sample(range(0, 511), n)
			self.__selected_to_change['indexes'] = indexes

			for i in indexes:
				self.__selected_to_change['indv'].append(self.__population[i])


	def evolve(self):
		
		ti = time()

		population = Population(np=self.__np)
		self.__population = population.create()

		opposite_positions = []

		if self.__obl:

			p = int((self.__ng * self.__obl_gen_rate)/100)
			for i in range(1, self.__ng, p):
				opposite_positions.append(i)

		for g in range(self.__ng):

			###########################
			# Opposite-Based Learning #
			###########################

			if self.__obl  and  g in opposite_positions:	

				with open("opposite_generations", "a") as f:
					f.write(str(g)+"\n")

				self.heap_sort()

				if self.__obl_aggressive and ((100*g)/self.__ng) > 50:
					self.select_individuals(aggressive=True)
				
				# select individuals who will be used as opposite
				self.select_individuals()

				opposite_individuals = population.opposite(self.__selected_to_change['indv'])

				for index, individual in zip(self.__selected_to_change['indexes'], opposite_individuals):
					self.__population[index] = individual

				self.evaluate_new_population()

			
			else:

				###################################
				# Differential Evolution Process #
				###################################
								
				self.select_individuals()

				for index, individual in zip(self.__selected_to_change['indexes'], self.__selected_to_change['indv']):
					
					############
					# mutation #
					############

					mutated_vector = self.mutate(index)

					#############
					# crossover #
					#############

					new_individual = Individual()
					new_individual.create()

					u = self.crossover(individual, mutated_vector)
					new_individual.set(array(u))

					self.__aux_population.append(new_individual)
					

				#############
				# selection #
				#############

				# replace individuals by new ones generated by DE in the original population
				for index, individual in zip(self.__selected_to_change['indexes'], self.__aux_population):
					self.__population[index] = individual

				self.evaluate_new_population()
				
				
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
				u.append(int(mutated_vector[j]))
			else:
				u.append(int(value))

		return u

	def get_best(self):

		self.heap_sort()
		best = self.__population[0]

		return best
	

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

		for j, a in enumerate(v):
			
			if a >= 0:
				v[j] = a%25
			else:
				v[j] = -(abs(a)%25)

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

		for j, a in enumerate(v):
			
			if a >= 0:
				v[j] = a%25
			else:
				v[j] = -(abs(a)%25)

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
		
		for j, a in enumerate(v):
			
			if a >= 0:
				v[j] = a%25
			else:
				v[j] = -(abs(a)%25)

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
		
		for j, a in enumerate(v):
			
			if a >= 0:
				v[j] = a%25
			else:
				v[j] = -(abs(a)%25)

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

		for j, a in enumerate(v):
			
			if a >= 0:
				v[j] = a%25
			else:
				v[j] = -(abs(a)%25)

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

		for j, a in enumerate(v):
			
			if a >= 0:
				v[j] = a%25
			else:
				v[j] = -(abs(a)%25)
				
		return v


if __name__ == '__main__':
	

	ng = 100
	p = int((ng * 5)/100)
			
	change_criteria = ['worst', 10]
	
	de = DifferentialEvolution(
		np=512,
		cr=0.8, 
		f=0.7, 
		ng=ng,
		algorithm='rand_1_bin',
		change=change_criteria,
		obl=False,
		obl_gen_rate=0,
		obl_aggressive=False,
		obl_aggressive_rate=0
	)

	de.evolve()	
	