class Nodo:

	def __init__(self, tipo, valor=None, hijos=None):
		self.tipo = tipo
		self.valor = valor
		self.visitado = False
		self.type = None
		self.arreglo = None
		self.lexeme = None
		if hijos:
			self.hijos = hijos
		else:
			self.hijos = []