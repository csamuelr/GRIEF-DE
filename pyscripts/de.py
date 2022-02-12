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
import numpy
from time         import time
from sys          import exit,argv
import random
import os

class DifferentialEvolution:

	def __init__(self, np, cr, f, algorithm):
		
		self.__np         = np
		self.__cr         = cr
		self.__f          = f
		self.__algorithm  = None
		self.__evfunc     = Evaluation()
		self.execution = 0
		self.__population = Population(np=self.__np).create()
		self.__temporaryp = []
		self.__crosstype  = None
		self.__best_solution = None
		self.__all_solutions = []
		self.__all_best_solutions = []
		self.__total_time = None
		self.__population_data = []
		prev_pop_with_eval = loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'pair_stats.txt'), delimiter=' ', dtype=int)
		idx_prev_worst_ind = numpy.argsort(prev_pop_with_eval[:,4])[:10]
		self.__selected_to_change = idx_prev_worst_ind

		for individual in self.__population:
			self.__population_data.append(individual.get())
		self.__new_population_data = self.__population_data

		self.__previous_fit = self.evaluate(0, self.__population_data[0])

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
	
	def evaluate(self, i, u):
		
		aux = self.__population_data[i]
		self.__population_data[i] = u
		savetxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), self.__population_data, delimiter=' ', fmt='%s')

		

		#Função de avaliação
		cmd = "./tools/evaluate GRIEF-datasets/planetarium > /dev/null"
		os.system(cmd)
	
		evaluation = loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'evaluation.txt'), delimiter=' ', dtype=int)
		return int(evaluation)

	def evaluate_select(self):
		os.system("cp ./tools/grief/pair_stats.txt ./tools/grief/pair_stats.bak")
		os.system("cp store.tmp store.bak")

		
		
		savetxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), self.__new_population_data, delimiter=' ', fmt='%s')
		
		os.system("./tools/generate_eval.sh")

		#Função de avaliação
		cmd = "./tools/evaluate GRIEF-datasets/planetarium| grep fitness > store.tmp"
		os.system(cmd)


		evaluation = int(loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'evaluation.txt'), delimiter=' ', dtype=int))
		
		
		if(0):
			os.system("cp store.bak store.tmp")
			counter = 0
			
			os.system("cp ./tools/grief/pair_stats.bak ./tools/grief/pair_stats.txt")
			savetxt(os.path.join(os.getcwd(), 'tools', 'grief', 'test_pairs.txt'), self.__population_data, delimiter=' ', fmt='%s')
			self.__new_population_data = self.__population_data#faltou essa
			os.system("./tools/generate_eval.sh  > /dev/null")
			
			self.__population = Population(np=self.__np).create()
			print(f'a anterior foi {self.__previous_fit} e a nova  foi {evaluation} não mudou')

			##Função de avaliação
			#cmd = "./tools/evaluate GRIEF-datasets/planetarium| grep fitness > store.tmp"
			#os.system(cmd)
			
		else:
			print(f'a anterior foi {self.__previous_fit} e a nova  foi {evaluation} mudou')
			self.__previous_fit = evaluation
			self.__population_data = self.__new_population_data
			self.__population = Population(np=self.__np).create()

		

	def evolve(self, generations):
		for g in range(generations):
			ti = time()

			self.__all_solutions = []
			self.__all_best_solutions = []

			for i in self.__selected_to_change:
				# mutation
				mutated_vector = self.mutate(i)

				u = self.crossover(self.__population[i], mutated_vector)
				self.__new_population_data[i] = u


			# selection
			self.evaluate_select()

			self.__all_solutions = self.__temporaryp

			tf = time()	  
			self.__total_time =  tf - ti
			fitness = int(os.popen("cat store.tmp|cut -f 3 -d ' '").read())
			error = float(os.popen("cat store.tmp|cut -f 4 -d ' '").read())
			os.system("cp tools/grief/pair_stats.txt grief_history"+str(self.execution)+"/"+str(g+1).zfill(5)+"_"+str(fitness)+".txt")
			prev_pop_with_eval = loadtxt(os.path.join(os.getcwd(), 'tools', 'grief', 'pair_stats.txt'), delimiter=' ', dtype=int)
			idx_prev_worst_ind = numpy.argsort(prev_pop_with_eval[:,4])[:10]
			self.__selected_to_change = idx_prev_worst_ind

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

	generations = int(argv[1])
	executions = int(argv[2])
	
	for execution in range(2, executions):
		os.system("./scripts/resetGrief.sh > /dev/null")
		os.system("./tools/evaluate GRIEF-datasets/planetarium| grep fitness > store.tmp")
		os.system("mkdir grief_history"+str(execution))
		de = DifferentialEvolution(
		np=512,
		cr=0.7, 
		f=0.8, 
		algorithm='rand_1_bin'
		)
		de.execution = execution
		de.evolve(generations)
	