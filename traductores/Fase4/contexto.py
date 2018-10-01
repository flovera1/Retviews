import sys

class context:

	def __init__(self):
		# Inicializar pila de scopes (variables declaradas para cada bloque)
		self.scopes = []
		self.auxScopes = []
		self.linea = 1

	def contextCheck(self, ast):

		# Tomamos un arbol y recorremos sus hijos
		if (ast):
			if (len(ast.hijos) > 0): 

				for nodo in ast.hijos:

					if (nodo.tipo == 'BLOQUE'):
						self.linea += 1
						self.contextCheck(nodo)

						# Removemos el top de la pila al terminar con este bloque
						self.scopes.pop(0)

					elif (nodo.tipo == 'DECLARACION'):
						self.linea += 1
						# Creamos nuevo scope (por ahora vacio)
						scope = {}
						# Insertamos nuevo scope en la cabeza de la pila
						self.scopes.insert(0, scope)
						self.nuevoScope(nodo)
						self.auxScopes.append(self.scopes[0])


					elif (nodo.tipo == 'ASIGNACION'):
						self.linea += 1
						# Si encontramos una operacion de tipo Asignacion, chequear que
						# la variable ha sido declarada y que el tipo concuerde

						#Obtengamos id
						if (isinstance(nodo.valor, str)):
							var = self.checkVar(nodo.valor)
							if (var.contador):
								print("Error linea " + str(self.linea) + ". Se trata de modificar la variable" + nodo.valor + "que pertenece a una iteracion.")
								sys.exit(0)
							var = var.tipo
						else:
							var = self.getTipoId(nodo.valor)
							# chequear si el hijo tambien es un arreglo
						

						# Si la var es de un arreglo chequear que el indice es de tipo entero
						tpe = self.checkExp(nodo.hijos[0])

						if (var != tpe):
							print("Error linea " + str(self.linea) + ". Las variables son de tipos distintos.")
							sys.exit(0)

					
					elif(nodo.tipo == 'CONDICIONAL'):
						self.linea += 1

						for h in nodo.hijos:

							# Recorrer el cuerpo de forma recursiva
							if (h.tipo == 'CUERPO'):
								self.contextCheck(h)
							# Chequear que la condicion sea de tipo booleana
							else:
								t = self.checkExp(h)

								if (t != 'bool'):
									print("Error linea " + str(self.linea) + ". Las variables son de tipos distintos.")
									sys.exit(0)

					elif (nodo.tipo == 'ITERACION INDETERMINADA'):
						self.linea += 1

						guardia = self.checkExp(nodo.valor)
						if (guardia != 'bool'):
							print("Error linea " + str(self.linea) + ". Las variables en la guardia son de tipo incorrecto.")
							sys.exit(0)

						
						self.contextCheck(nodo.hijos[0])

					elif (nodo.tipo == 'ITERACION DETERMINADA'):
						self.linea += 1

						# agregar atributo a la var de iteracion, set to true 
						# al salir de los hijos del ciclo set to false

						cont = nodo.valor[0]
						scope = {}
						scope[cont] = simbolo(cont, 'int')
						scope[cont].contador = True

						# Chequear que los rangos sean enteros
						limInf = nodo.valor[1]
						tipoInf = self.checkExp(limInf)
						limSup = nodo.valor[2]
						tipoSup = self.checkExp(limSup)

						if (tipoSup != tipoInf != 'int'):
							print("Error linea " + str(self.linea) +'. Rangos del ciclo no son enteros.')
							sys.exit(0)

						step = nodo.valor[3]

						if (step != '1'):
							if (step.tipo == 'TERMINO'):
								if (len(step.hijos)>0):
									t = self.checkExp(step)
								else:
									t = step.type
							else:
								t = self.checkExp(step)

							if (t != 'int'):
								print("Error linea " + str(self.linea) + ". Las variables son de tipo incorrecto.")
								sys.exit(0)

						# Insertamos nuevo scope en la cabeza de la pila
						self.scopes.insert(0, scope)

						self.contextCheck(nodo.hijos[0])
						self.auxScopes.append(self.scopes[0])
						self.scopes.pop(0)
					else:
						if (nodo.tipo=='ENTRADA' or nodo.tipo=='SALIDA'):
							self.linea += 1
						self.contextCheck(nodo)

	def checkIfArray(self, var):
		if (len(var.hijos)>0):
			for h in var.hijos:
				self.checkIfArray(h)
		else:
			t = self.checkVar(var.lexeme)
			if (t.arreglo):
				return True
			else:
				return False

	def imprimirTabla(self):
		print('TABLA DE SIMBOLOS')
		tabs = ''
		for scope in self.auxScopes:
			for var in scope:
				print(tabs + var + ': ' + scope[var].tipo)
			tabs = tabs + '\t'


	def checkTipoArrOfArr(self,arr):
		# Cheuqear tipo del indice
		if (arr.arreglo == None):
			print("Error linea " + str(self.linea) +'. no es un arreglo.')
			sys.exit(0)
		t = self.getTipoId(arr.arreglo)
		if (t != 'int'):
			print("Error linea " + str(self.linea) +'. Tipo incorrecto para indice del arreglo.')
			sys.exit(0)
		if (len(arr.hijos)>0):
			for i in arr.hijos:
				self.checkTipoArrOfArr(i)


	def getTipoId(self, indice):
		# Chequea tipo del indice y lo retorna si es correcto
		# var -> nombre de la variable que contiene el arreglo
		# indice -> indice a acceder del arreglo


		# Obtengamos tipo del indice
		if (indice.tipo == 'BIN_ARITMETICA'):
			hijo1 = indice.hijos[0]
			hijo2 = indice.hijos[1]
			if (hijo1.tipo == 'TERMINO'):
				tipo1 = hijo1.type
			else:
				tipo1 = self.checkExp(hijo1)
			if (hijo2.tipo == 'TERMINO'):
				tipo2 = hijo2.type
			else:
				tipo2 = self.checkExp(hijo2)
			
			if (tipo1 != 'int' or tipo2 != 'int'):
				print("Error linea " + str(self.linea) +'. Tipo incorrecto para indice del arreglo.')
				sys.exit(0)
			else:
				return tipo1

		elif (indice.tipo == 'TERMINO'):
			if (len(indice.hijos) > 0):
				for hijo in indice.hijos:
					tipoIndex = self.getTipoId(hijo)

					if (tipoIndex != 'int'):
						print("Error linea " + str(self.linea) +'. Tipo incorrecto para indice del arreglo.')
						sys.exit(0)
					return tipoIndex
			else:
				if (indice.type == 'var'):
					tipoIndex = self.checkVar(indice.lexeme).tipo
				else:
					tipoIndex = indice.type
				return tipoIndex
		elif (indice.tipo == 'VAR_ARREGLO'):

			t = self.checkVar(indice.valor)
			if (not t.arreglo):
				print("Error linea " + str(self.linea) +'.' + t.valor + ' no es un arreglo')
				sys.exit(0)

			for hijo in indice.hijos:
				tipoIndex = self.getTipoId(hijo)

			if (t.tipo != tipoIndex != 'int'):
				print("Error linea " + str(self.linea) +'. Tipo incorrecto para indice del arreglo.')
				sys.exit(0)

			return t.tipo


	def nuevoScope(self, dec):

		# Tipo de la declaracion
		tipo = dec.valor
		arreglo = False
		if (tipo == 'arreglo'):
			arreglo = True

		tam = None
		# Los hijos de una variable pueden ser un conjunto de variables, un arreglo
		# u otra declaracion
		for k in dec.hijos:

			if (k.tipo == 'ARREGLO'):
				# Si la variable es un arreglo entonces necesitamos hallar
				# el tipo de los elementos del arreglo
				tipo = self.getTipo(k)
				# Si es un arreglo tambien hay que chequear el tamaño
				# sea de tipo entero
				self.checkTipoArrOfArr(k)

				tam = k.arreglo
				

			elif (k.tipo == 'DECLARACION'):
				self.linea += 1
				self.nuevoScope(k)

			elif (k.tipo == 'VARIABLE'):
				self.agregarSimbolo(k, tipo, arreglo, tam)
	

	def getTipo(self, arr):
		# Recorremos los hijos del arreglo
		# (pues puede ser un arreglo de arreglos)
		if (len(arr.hijos) > 0):
			for i in arr.hijos:
				tipo = self.getTipo(i)
				return tipo
		# Cuando el arreglo no tenga mas hijos, en valor estara guardado el tipo
		else:
			return arr.valor
		
	def agregarSimbolo(self, var, tipo, arr, tam=None):
		
		# scope actual
		top = self.scopes[0]
		# chequeeemos que la variable no esta siendo redeclarada

		if var.valor in top:
			print("Error linea " + str(self.linea) +'. Variable ya declarada.')
			sys.exit(0)
		# Construimos objeto simbolo
		variable = simbolo(var.valor, tipo, tam)
		variable.arreglo = arr
		# Agregamos simbolo a la tabla
		top[var.valor] = variable

		# Recorremos arbol
		if ((len(var.hijos))>0):
			for i in var.hijos:
				if (i.tipo == 'VARIABLE'):
					self.agregarSimbolo(i, tipo, arr, tam)
				elif (i.tipo == 'EXPRESION'):
					t = self.checkExp(i)
					if (t != tipo):
						print("Error linea " + str(self.linea) + 'Los tipos de la variables y la asignacion no coinciden.')
						sys.exit(0)
					else:
						top[var.valor].asignado = i


	def checkExp(self, exp):
		# Chequea si las operaciones de la expr son correctas
		# y retorna el tipo resultante 
		# Usarla de forma recursiva con cada subexpresion
		# retorna error si se obtiene tipos distintos

		for hijo in exp.hijos:
			if (hijo.tipo == 'BOOLEANA'):
				op1 = hijo.hijos[0]
				op2 = hijo.hijos[1]
				tipo1 = self.checkExp(op1)
				tipo2 = self.checkExp(op2)
				if (tipo1 != tipo2 != 'bool'):
					print("Error linea " + str(self.linea) + '. Tipo incorrecto operacion booleana.')
					sys.exit(0)
				else:
					return 'bool'

			elif (hijo.tipo == 'RELACIONAL'):

				op1 = hijo.hijos[0]
				op2 = hijo.hijos[1]

				tipo1 = self.checkExp(op1)
				tipo2 = self.checkExp(op2)

				if (hijo.valor != '/=' and hijo.valor != '='):
					if (tipo1 != 'int' or tipo2 != 'int'):
						print("Error linea " + str(self.linea) +'. Tipo incorrecto operacion relacional.')
						sys.exit(0)


				if (tipo1 != tipo2):
					print("Error linea " + str(self.linea) +'. Tipo incorrecto operacion relacional.')
					sys.exit(0)
				else:
					return "bool"

			elif(hijo.tipo == 'BIN_ARITMETICA'):
				op1 = hijo.hijos[0]
				op2 = hijo.hijos[1]
				tipo1 = self.checkExp(op1)
				tipo2 = self.checkExp(op2)


				if (tipo1 != tipo2):
					print("Error linea " + str(self.linea) +'. Tipo incorrecto operacion aritmetica.')
					sys.exit(0)
				elif (tipo1 != 'int'):
					print("Error linea " + str(self.linea) +'. Tipo incorrecto operacion aritmetica.')
					sys.exit(0)
				else:
					return 'int'
			elif(hijo.tipo == 'BOOLEANA UNARIA'):
				op = hijo.hijos[0]
				tipo = self.checkExp(op)
				if (tipo != 'bool'):                    
					print("Error linea " + str(self.linea) +'. Tipo incorrecto booleana unaria.')
				else:
					return "bool"

			elif(hijo.tipo == 'OPERACION UNARIA'):
				op = hijo.hijos[0]
				tipo = self.checkExp(op)
				if (tipo != 'int'):
					print("Error linea " + str(self.linea) +'. Tipo incorrecto aritmetica unaria.')
				else:
					return 'int'

			elif(hijo.tipo == "OPERACION CARACTER"):
			
				t = self.checkExp(hijo)
				if (t != 'char'):
					print("Error linea " + str(self.linea) +'. Tipo incorrecto caracter.')
					sys.exit(0)
				else:
					if (hijo.valor == '#'):
						return 'int'
					else:
						return 'char'
			elif (hijo.tipo == 'OPERACION ARREGLO'):
				
				# puedo tener 1 o 2 hijos
				# chequear que los hijos sean del mismo tipo
				if (len(hijo.hijos)>1):
					op1 = hijo.hijos[0]
					op2 = hijo.hijos[1]

					tipo1 = self.checkVar(op1)
					tipo2 = self.checkVar(op2)
					if (not tipo1.arreglo or not tipo2.arreglo):
						print("Error linea " + str(self.linea) +'. No son arreglos')
						sys.exit(0)

					if (tipo1.tipo != tipo2.tipo):
						print("Error linea " + str(self.linea) +'. Tipo incorrecto operacion con arreglos')
						sys.exit(0)
					else:
						return tipo1.tipo
				else:
					h = hijo.hijos[0]
					t = self.checkVar(h)
					if (not t.arreglo):
						print("Error linea " + str(self.linea) +'. Tipo incorrecto operacion con arreglos')
						sys.exit(0)
					return t.tipo

			elif(hijo.tipo == 'TERMINO'):
				if (len(hijo.hijos)>0):
					for h in hijo.hijos:
						t = self.checkExp(h)
						return t
				else:
					if (hijo.type == 'var'):
						
						t = self.checkVar(hijo.lexeme)

						return t.tipo
					else:
						return hijo.type
			
			elif(hijo.tipo == 'VAR_ARREGLO'):
				# Chequear que indices son correctos
				index = self.getTipoId(hijo.hijos[0])
				if (index != 'int'):
					print("Error linea " + str(self.linea) +'. El indice de un arreglo debe ser entero.')
					sys.exit(0)
				#retorna tipo del arreglo
				t = self.checkVar(hijo.valor)

				if (not t.arreglo):
					print("Error linea " + str(self.linea) +'.' + t.valor + ' no es un arreglo')
					sys.exit(0)

				return t.tipo




	def checkVar(self, var):
		# chequea que una variable exista en los scopes y devuelve su tipo
		# si no retorna, none

		if (len(self.scopes) > 0):

			for i in range(len(self.scopes)):
				if var in self.scopes[i]:
					return self.scopes[i][var]
		
		print("Error linea " + str(self.linea) +'. Variable ' + var + ' no declarada.')
		sys.exit(0)



class simbolo():
	def __init__(self, val, t, tam=None):
		self.tipo = t # tipo de la variable
		self.valor = val # identificador o valor de la variable
		self.asignado = None # valor del simbolo en caso de que se trate de una var
		self.contador = None # para chequear si una variable esta siendo usada como contador
		self.arreglo = False
		self.res = None # valor de la variable
		if (tam):
			self.size = tam
			self.res = []

