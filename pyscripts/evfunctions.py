
class Evaluation:

	# def __init__(self, delta, pc, pf):
	# 	self.delta = delta
	# 	self.pc = pc
	# 	self.pf = pf

	def __init__(self):
		pass

	def compute(self, individual):
		# di (a, b) = |bi (Ia , ax , ay ) − bi(Ib , bx , by )|
		# f (δi, PC , PF ) = ∑ p∈PC (1 − 2 di (p)) + ∑ p∈PF (2 di (p) − 1)

		x1, y1, x2, y2 = individual
		dx = x1 - x2
		dy = y1 - y2

		pass

	def dissimilarity(self, p):
		
		a, b = p
		


