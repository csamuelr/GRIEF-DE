from configparser import ConfigParser
from de import DifferentialEvolution
import os


experiments_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'experiments'   ))
grief_path 		 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'grief_history' )) 
algorithms 		 = ['rand_1_bin', 'rand_to_best_1_bin']
# algorithms 		 = ['best_1_bin']
configs = ConfigParser()

ng = 3

for algorithm in algorithms:

	print("Running for {}\n".format(algorithm))
	
	path = os.path.join(experiments_path, algorithm)

	config_path = os.path.join(path, 'configs.conf')
	configs.read(config_path)

	for e, experiment in enumerate(configs):
		
		if e == 0: continue

		exp_path = os.path.join(path, experiment)
		os.mkdir(exp_path)

		for i in range(10):
			print("{} - execution number: {}".format(experiment, i+1))

			os.system('./scripts/resetGrief.sh >> /dev/null')
			# os.system('./tools/generate_eval.sh >> /dev/null')
			os.system('./tools/evaluate GRIEF-datasets/planetarium >> /dev/null')
		
			execution_path = os.path.join(path, experiment, str(i+1))
			os.mkdir(execution_path)
			
			print(experiment)
			algorithm       	=   str(configs[experiment].get('algorithm'))
			np              	=   int(configs[experiment].get('np'))
			cr              	= float(configs[experiment].get('cr'))
			f               	= float(configs[experiment].get('f'))
			change_criteria 	=   str(configs[experiment].get('change_criteria')).split(' ')
			obl             	=  configs[experiment].getboolean('obl')
			obl_gen_rate    	= float(configs[experiment].get('obl_gen_rate'))
			obl_aggressive  	=  configs[experiment].getboolean('obl_aggressive')
			obl_aggressive_rate = float(configs[experiment].get('obl_aggressive_rate'))

			change_criteria[1] = int(change_criteria[1])

			de = DifferentialEvolution(
				np=np,
				cr=cr, 
				f=f, 
				ng=ng,
				algorithm=algorithm,
				change=change_criteria,
				obl=obl,
				obl_gen_rate=obl_gen_rate,
				obl_aggressive=obl_aggressive,
				obl_aggressive_rate=obl_aggressive_rate
			)

			de.evolve()

			cmd = 'cp grief_history -r ' + os.path.join(execution_path, 'history')
			os.system(cmd)

			cmd = 'cp opposite_generations ' + os.path.join(execution_path, 'opposite_generations')
			os.system(cmd)
			
			cmd = "rm opposite_generations && touch opposite_generations" 
			os.system(cmd)

			cmd = "rm -rf grief_history/*" 
			os.system(cmd)
			

