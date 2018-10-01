"""
Fase 4 del proyecto

"""
import sys
from collections import deque
from contexto import *

class evaluacion():
	# Usamos tabla de simbolos para obtener las variables del programa
	def __init__(self, tablaSim):
		self.tabla = tablaSim
		
		
	def evalArbol(self,ast):

		if (ast):
				if (len(ast.hijos) > 0): 
					for nodo in ast.hijos:

						if (nodo.tipo == 'ASIGNACION'):
							# Nombre de la variable
							var = nodo.valor
							# Valor a asignar
							value = self.evalExp(nodo.hijos[0])
							# Si la variable es un id
							if (isinstance(var, str)):
								self.setValor(var, value)
							# Si la variable es un indice de un arreglo
							else:
								indice = self.evalExp(var.hijos[0])
								self.setValor(var.valor, value, indice)

						elif (nodo.tipo == 'VARIABLE'):
							for i in nodo.hijos:
								# Para el caso es que se haga una asignacion dentro
								# de una declaracion
								if (i.tipo == 'EXPRESION'):
									var = nodo.valor
									value = self.evalExp(i)
									self.setValor(var, value)
								else:
									self.evalArbol(nodo)

						elif (nodo.tipo == 'DECLARACION'):
							# Evaluamos lo que hay dentro de la declaracion
							self.evalArbol(nodo)

						elif (nodo.tipo == 'SALIDA'):
							# Calcular valor a imprimir
							val = self.evalExp(nodo.hijos[0])
							print(val)

						elif (nodo.tipo == 'ENTRADA'):
							# Leer
							val = input()
							var = nodo.valor
							# Si leemos un digito convertirlo a entero
							if (val.isdigit()):
								val = int(val)
							# Si leemos un booleano
							if (val == 'false'):
								val = False
							elif (val == 'true'):
								val = True
							# Chequeemos que lo leido es de tipo correcto
							for i in self.tabla:
								if var in i:
									# tipo de la variable donde se va a guardar
									t = i[var].tipo
									# cheuqear que tipo de la variable y lo leido coincidan
									if (isinstance(val,str) and t!='char'):
										print("Error. Tipo incorrecto")
										sys.exit(0)
									elif(isinstance(val,bool) and t!='bool'):
										print("Error. Tipo incorrecto")
										sys.exit(0)
									elif(isinstance(val, int) and t!= 'int'):
										print("Error. Tipo incorrecto")
										sys.exit(0)
							# guardar valor leido en la variable
							self.setValor(var, val)

						elif (nodo.tipo == 'CONDICIONAL'):
							# evaluar guardia
							guardia = self.evalExp(nodo.hijos[0])
							# instrucciones dentro del bloque
							cuerpo = nodo.hijos[1]
							# si la guardia es true ejecutar cuerpo
							if (guardia):
								self.evalArbol(cuerpo)
							else:
								# si no se cumple la guardia verificar si existe un otherwise
								if (len(nodo.hijos)==3):
									# ejecutar other wise
									other = nodo.hijos[2]
									self.evalArbol(other)

						elif (nodo.tipo == 'ITERACION DETERMINADA'):
							# guardar valor del contador antes de ejecutar el for
							val = self.getValor(nodo.valor[0],None,True)
							# creamos nuevo objeto simbolo para guardarlo en la tabla
							contador = simbolo(self.getValor(nodo.valor[0],None,True),'int')
							self.tabla.insert(0,{})
							self.tabla[0][nodo.valor[0]]=contador
							# calcular lim inferior
							liminf = self.evalExp(nodo.valor[1])
							# el nuevo valor del contador sera el limite inferior
							self.setValor(nodo.valor[0], liminf)
							# calcular limite superior
							limsup = self.evalExp(nodo.valor[2])
							step = nodo.valor[3]
							# convertir step a entero
							if (isinstance(step,str)):
								step = int(step)
							# calcular valor de step si es una expresion
							else:
								step = self.evalExp(step)
							# error si step es 0
							if (step == 0):
								print("Error. El paso en la iteracion determinada no puede ser 0.")
								sys.exit(0)
							# ejecutar for
							for i in range(liminf, limsup, step):
								# actualizar valor del contador en cada iteracion
								self.setValor(nodo.valor[0], i)
								self.evalArbol(nodo.hijos[0])
							# guardar valor original
							self.setValor(nodo.valor[0], val)
							self.tabla.pop(0)
									
						elif (nodo.tipo == 'ITERACION INDETERMINADA'):
							# calcular valor de la guardia
							exp = self.evalExp(nodo.valor)
							# ejecutar instruciones
							while (exp):
								self.evalArbol(nodo.hijos[0])
								# evaluar guardia en cada iteracion
								comprobarexp = self.evalExp(nodo.valor)
								if (comprobarexp):
									continue
								else:
									break

						else:
							self.evalArbol(nodo)

	def evalExp(self, exp):
		# Para obtener valor de cada expresion

		if (exp.tipo == 'TERMINO'):
			# evaluar termino recursivamente
			if (len(exp.hijos)>0):
				t = self.evalExp(exp.hijos[0])
				return t
			else:
				if (exp.type == 'var'):
					# si es una variable retornar su valor
					t = self.getValor(exp.lexeme)
					return t
				else:
					if (exp.lexeme == 'true'):
						return True
					elif (exp.lexeme == 'false'):
						return False
					else:
						return exp.lexeme

		elif (exp.tipo == 'BOOLEANA'):
			operacion = exp.valor
			# hallar valor de los operadores
			op1 = self.evalExp(exp.hijos[0])
			op2 = self.evalExp(exp.hijos[1])
			# calcular expresion
			if (operacion == '\/'):
				res = op1 or op2
			elif (operacion == '/\\'):
				res = op1 and op2
			return res

		elif (exp.tipo == 'BOOLEANA UNARIA'):
			op = self.evalExp(exp.hijos[0])
			return not op

		elif (exp.tipo == 'RELACIONAL'):
			operacion = exp.valor
			# hallar valor de los operador
			op1 = self.evalExp(exp.hijos[0])
			op2 = self.evalExp(exp.hijos[1])
			# calcular la expresion
			if (operacion == '<'):
				res = op1 < op2
			elif (operacion == '>'):
				res = op1 > op2
			elif (operacion == '<='):
				res = op1 <= op2
			elif (operacion == '>='):
				res = op1 >= op2
			elif (operacion == '='):
				res = op1 == op2
			elif (operacion == '/='):
				res = op1 != op2

			return res

		elif (exp.tipo == 'OPERACION CARACTER'):
			operacion = exp.valor
			# hallar operador
			op = self.evalExp(exp.hijos[0])
			op = op.strip('\'')
			# calcular expresion
			if (operacion == '#'):
				return ord(op)
			elif (operacion == '++'):
				if(ord(op)==127):
					return chr(0)
				else:	
					return chr(ord(op)+1)
			elif (operacion == '--'):
				if (ord(op)==0):
					return chr(127)
				else:
					return chr(ord(op)-1)

		elif (exp.tipo == 'BIN_ARITMETICA'):
			operacion = exp.valor
			# hallar operadores
			op1 = self.evalExp(exp.hijos[0])
			op2 = self.evalExp(exp.hijos[1])
			# calcular expresion
			if (operacion == '+'):
				res = op1 + op2
			elif (operacion == '-'):
				res = op1 - op2
			elif (operacion == '*'):
				res = op1 * op2
			elif (operacion == '/'):
				if (op2 == 0):
					print("Error division por cero")
					sys.exit(0)
				else:
					res = op1 / op2
			elif (operacion == '%'):
				res = op1 % op2
			# redondear a entero
			return int(res)
		
		elif (exp.tipo == 'OPERACION UNARIA'):
			op = self.evalExp(exp.hijos[0])
			return -op

		elif(exp.tipo == 'EXPRESION'):
			t = self.evalExp(exp.hijos[0])

		elif(exp.tipo == 'VAR_ARREGLO'):
			indice = self.evalExp(exp.hijos[0])
			v = self.getValor(exp.valor, indice)
			return v

		elif (exp.tipo == 'OPERACION ARREGLO'):
			if (len(exp.hijos)==2):
				# hallar operadores y concatenarlos
				op1 = self.getValor(exp.hijos[0])
				op2 = self.getValor(exp.hijos[1])
				res = op1+op2
				return res
			else:
				# halalr arreglo
				op = self.getValor(exp.hijos[0])
				# shift del arreglo
				temp = []
				temp.append(op[len(op)-1])
				for i in range(len(op)-1):
					temp.append(op[i])
				return temp

		return t

	def isArray(self, var):
		# Chequear si una variable es un arreglo
		if (isinstance(var, str) and len(var)==1):
			if (len(self.tabla) > 0):
				for i in range(len(self.tabla)):
					if var in self.tabla[i]:
						if (self.tabla[i][var].arreglo):
							return True
		if (isinstance(var, list)):
			return True
		return False

	def setValor(self, var, val, index=None):

		# Guardar valor en un variable en la tabla
		if (len(self.tabla) > 0):
			for i in range(len(self.tabla)):
				if var in self.tabla[i]:
					# Chequeamos si se estan asignando arreglos a cosas que no lo son
					if (self.tabla[i][var].arreglo and not self.isArray(val) and index==None):
						print("Error. No se puede asignar un arreglo.")
						sys.exit(0)
					elif (not self.tabla[i][var].arreglo and self.isArray(val)):
						print("Error. No se puede asignar un arreglo.")
						sys.exit(0)
					# Si estamos accediendo a un arreglo
					if (index!=None):
						# Chequear que indice no sea mas grande
						if (index >= self.evalExp(self.tabla[i][var].size)):
							print("Error. Indice excede tamaño del arreglo.")
							sys.exit(0)
						elif (index < 0):
							print("Error. Indice no puede ser negativo.")
							sys.exit(0)
						else:
							# Si no hay nada en el arreglo inicializar
							if (len(self.tabla[i][var].res)==0):
								for n in range(self.evalExp(self.tabla[i][var].size)):
									self.tabla[i][var].res.append(None)
							# si asignaos arreglo a algo que no lo es
							if (isinstance(val, list)):
								if (not self.tabla[i][var].arreglo):
									print("Error. No se puede asignar arreglo a entero.")
									sys.exit(0)
							self.tabla[i][var].res[index] = val

					else:
						# si asignamos arreglo a algo que no lo es
						if (isinstance(val, list)):
							if (not self.tabla[i][var].arreglo):
								print("Error. No se puede asignar arreglo a variable que no es arreglo.")
								sys.exit(0)
							if (len(val) > self.evalExp(self.tabla[i][var].size)):
								print("Error. Arreglo excede el tamaño de la variable.")
								sys.exit(0)
						# guardar valor
						self.tabla[i][var].res = val

	def getValor(self, var, index=None, itera=None):
		# Valor a buscar
		val = None
		# Recorremos tabla
		if (len(self.tabla) > 0):
			for i in range(len(self.tabla)):
				# Si encontramos variable en la tabla
				if var in self.tabla[i]:
					# Si estamos buscando indice
					if (index!=None):
						# Si la variable es un arreglo
						if (self.tabla[i][var].arreglo):
							# Indice negativo reporta error
							if (index < 0):
								print("Error. Indice no puede ser negativo.")
								sys.exit(0)
							# Indice mayor que el tamaño del arreglo reporta error
							elif (index >= self.evalExp(self.tabla[i][var].size)):
								print("Error. Indice excede tamaño del arreglo.")
								sys.exit(0)
							# Si la variable esta inicializada
							if (self.tabla[i][var].res!=None):
								if (len(self.tabla[i][var].res)!=0):
									val = self.tabla[i][var].res[index]
						else:
							print("Error. Variable no es un arreglo.")
							sys.exit(0)
					else:	
						val = self.tabla[i][var].res
		# Si variable esta inicializada retornar su valor
		if (val != None):
			return val
		# SI la variable no esta inicializada pero es un arreglo
		elif (val==None and index!=None):
			return val
		# Si se trata de un contador
		elif(itera!=None):
			return val
		# Si no esta inicializada
		else:
			if (index != None):
				print("Error. Variable " + var + "[" + str(index) +"] no inicializada.")
				sys.exit(0)
			else:
				print("Error. Variable " + var + " no inicializada.")
				sys.exit(0)




