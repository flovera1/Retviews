"""
Implementación de un analizador sintactico para el lenguaje BasicTran

Autores:
Constanza Abarca
Pedro Maldonado

Fecha:
05/06/2018
"""

import ply.yacc as yacc
from Lex import tokens
from sys import argv
import sys
from arbol import *
from contexto import *
from evaluacion import *

# Lista de precedencias 
precedence = (
	('nonassoc', 'TkMayor', 'TkMenor', 'TkMayorIgual', 'TkMenorIgual'),
	('left', 'TkSuma', 'TkResta'),
	('left', 'TkMult', 'TkDiv', 'TkMod'),
	('right', 'uminus'),
	('left', 'TkConcatenacion'),
	('left', 'TkShift'),
	('left', 'TkCorcheteAbre', 'TkCorcheteCierra'),
	('left', 'TkPunto'),
	('left', 'TkSiguienteCar'),
	('left', 'TkAnteriorCar'),
	('left', 'TkValorAscii'),
	('left', 'TkIgual', 'TkDesigual'),
	('left', 'TkConjuncion', 'TkDisyuncion'),
	('right', 'TkNot'),
	('nonassoc', 'TkNum', 'TkId')
)

# Regla principal, define un bloque de instrucciones
def p_programa(p):
	'''
	bloque : TkBegin cuerpo TkEnd
		   | TkWith declaracion TkBegin cuerpo TkEnd
	'''
	if (len(p) == 4):
		p[0] = Nodo('BLOQUE', None, [p[2]])

	else:
		p[0] = Nodo('BLOQUE', None, [p[2], p[4]])


# Regla para declaraciones de variables y su tipo
def p_declaracion(p):
	'''
	declaracion : TkVar variables TkDosPuntos TkInt
			    | TkVar variables TkDosPuntos TkBool
			    | TkVar variables TkDosPuntos TkChar
			    | TkVar variables TkDosPuntos arreglo
			    | TkVar variables TkDosPuntos TkInt declaracion
			    | TkVar variables TkDosPuntos TkBool declaracion
			    | TkVar variables TkDosPuntos TkChar declaracion
			    | TkVar variables TkDosPuntos arreglo declaracion

	'''
	if (len(p)==6):
		if (p[4] == 'int' or p[4] == 'char' or p[4] == 'bool'):
			p[0] = Nodo('DECLARACION', p[4], [p[2], p[5]])
		else:
			p[0] = Nodo('DECLARACION', 'arreglo', [p[4],p[2], p[5]])

	else:
		if (p[4] == 'int' or p[4] == 'char' or p[4] == 'bool'):
			p[0] = Nodo('DECLARACION', p[4], [p[2]])
		else:
			p[0] = Nodo('DECLARACION', 'arreglo', [p[4],p[2]])


# Definicion de arreglos
def p_arreglo(p):
	'''
	arreglo : TkArray TkCorcheteAbre terminal TkCorcheteCierra TkOf TkChar
		    | TkArray TkCorcheteAbre terminal TkCorcheteCierra TkOf TkInt
		    | TkArray TkCorcheteAbre terminal TkCorcheteCierra TkOf TkBool
		    | TkArray TkCorcheteAbre terminal TkCorcheteCierra TkOf arreglo
		    | TkArray TkCorcheteAbre opAritm TkCorcheteCierra TkOf TkChar
		    | TkArray TkCorcheteAbre opAritm TkCorcheteCierra TkOf TkInt
		    | TkArray TkCorcheteAbre opAritm TkCorcheteCierra TkOf TkBool
		    | TkArray TkCorcheteAbre opAritm TkCorcheteCierra TkOf arreglo
		    | TkArray TkCorcheteAbre indice TkCorcheteCierra TkOf TkChar
		    | TkArray TkCorcheteAbre indice TkCorcheteCierra TkOf TkInt
		    | TkArray TkCorcheteAbre indice TkCorcheteCierra TkOf TkBool
		    | TkArray TkCorcheteAbre indice TkCorcheteCierra TkOf arreglo
	'''
	if (p[6] == 'int' or p[6] == 'bool' or p[6] == 'char'):
		p[0] = Nodo('ARREGLO', p[6], None)
		p[0].arreglo = p[3]
	else:
		p[0] = Nodo('ARREGLO', None, [p[6]])
		p[0].arreglo = p[3]


# Regla de valores terminales
def p_terminal(p):
	'''
	terminal : TkId
			  | TkCaracter
			  | TkNum
			  | TkTrue
			  | TkFalse
			  | TkTab
			  | TkSalto
			  | TkComilla
			  | TkBarra
			  | TkParAbre terminal TkParCierra
	'''
	if (len(p) == 5):
		# Termnino con corchetes
		p[0] = Nodo("TERMINO", p[1]+p[2]+str(p[3])+p[4], [p[3]])
				
			

	elif(len(p)== 4):

		# Termino entre parentesis
		p[0] = Nodo("TERMINO", p[1]+str(p[2])+p[3], [p[2]])

		if ((str(p[2].lexeme)).isdigit()):
			p[0].type = "int"
			p[0].lexeme = p[1] + str(p[2].lexeme) + p[3]
		elif (p[2].lexeme == "true" or p[2].lexeme == "false"):
			p[0].type = "bool"
			p[0].lexeme = p[1] + p[2].lexeme + p[3]
		elif (p[2].lexeme[0]=="\'"):
			p[0].type = "char"
			p[0].lexeme = p[1] + p[2].lexeme + p[3]	
		else:
			p[0].type = "var"
			p[0].lexeme = p[1] + p[2].lexeme + p[3]		

	else:

		p[0] = Nodo('TERMINO', p[1], None)

		if ((str(p[1])).isdigit()):
			p[0].type = "int"
			p[0].lexeme = p[1]
		elif (p[1] == "true" or p[1] == "false"):
			p[0].type = "bool"
			p[0].lexeme = p[1]
		elif (p[1][0]=="\'"):
			p[0].type = "char"
			p[0].lexeme = p[1]
		else:
			p[0].type = "var"
			p[0].lexeme = p[1]

# Regla para definir el cuerpo de un bloque (conjunto de instrucciones)
def p_cuerpo(p):
	'''
	cuerpo : instruccion
		   | instruccion cuerpo
		   | bloque cuerpo
		   | bloque
	'''
	p[0] = Nodo("CUERPO", None, [p[1]])
	if (len(p) == 2):
		p[0] = Nodo("CUERPO", None, [p[1]])
		#p[0] = (p[1])
	else:
		p[0] = Nodo("CUERPO", None, [p[1], p[2]])


# Definicion de una instruccion
def p_instruccion(p):
	'''
	instruccion : expresion TkPuntoYComa
				| condicional
				| iterDeter
				| iterInd
				| asignacion TkPuntoYComa
				| input TkPuntoYComa
				| output TkPuntoYComa

	'''
	
	p[0] = Nodo("INSTRUCCION", None, [p[1]])


# Definicion de instrucciones condicionales
def p_condicional(p):
	'''
	condicional : TkIf expresion TkHacer cuerpo TkEnd
			    | TkIf expresion TkHacer cuerpo TkOtherwise TkHacer cuerpo TkEnd


	'''
	if (len(p) == 9):
		p[0] = Nodo("CONDICIONAL", None, [p[2], p[4], p[7]])
	else:
		p[0] = Nodo("CONDICIONAL", None, [p[2], p[4]])

# Definicion de asignaciones
def p_asignacion(p):
	'''
	asignacion : TkId TkAsignacion expresion
			   | indice TkAsignacion expresion
			   
	'''
	if (len(p) == 7):
		p[0] = Nodo("ASIGNACION", p[1], [p[6]])
		p[0].arreglo = p[3]
	else:
		p[0] = Nodo("ASIGNACION", p[1], [p[3]])
		p[0].arreglo = p[3]

def p_indice(p):
	'''
	indice : TkId TkCorcheteAbre terminal TkCorcheteCierra
	       | TkId TkCorcheteAbre opAritm TkCorcheteCierra
	       | TkId TkCorcheteAbre indice TkCorcheteCierra
	       | opArr TkCorcheteAbre terminal TkCorcheteCierra
	       | opArr TkCorcheteAbre opAritm TkCorcheteCierra
	       | opArr TkCorcheteAbre indice TkCorcheteCierra
	'''
	if (isinstance(p[1],str)):
		p[0] = Nodo("VAR_ARREGLO", p[1], [p[3]])
	else:
		p[0] = Nodo("VAR_ARREGLO", p[1].hijos[0], [p[3]])
	p[0].arreglo = p[1]

# Entrada
def p_input(p):
	'''
	input : TkRead TkId
	'''
	p[0] = Nodo("ENTRADA", p[2], None)

#Salida
def p_output(p):
	'''
	output : TkPrint expresion
	'''
	p[0] = Nodo("SALIDA", p[1], [p[2]])

# Cliclos while
def p_iteracionind(p):
    '''
    
    iterInd : TkWhile expresion TkHacer cuerpo TkEnd
    '''
    
    p[0] = Nodo("ITERACION INDETERMINADA", p[2], [p[4]])

# Ciclos for
def p_iterDeter(p):
	'''
	iterDeter : TkFor TkId TkFrom opAritm TkTo opAritm TkStep opAritm TkHacer cuerpo TkEnd
			  | TkFor TkId TkFrom opAritm TkTo terminal TkStep opAritm TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom terminal TkTo opAritm TkStep opAritm TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom terminal TkTo terminal TkStep opAritm TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom opAritm TkTo opAritm TkStep terminal TkHacer cuerpo TkEnd
			  | TkFor TkId TkFrom opAritm TkTo terminal TkStep terminal TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom terminal TkTo opAritm TkStep terminal TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom terminal TkTo terminal TkStep terminal TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom opAritm TkTo opAritm TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom opAritm TkTo terminal TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom terminal TkTo opAritm TkHacer cuerpo TkEnd
	          | TkFor TkId TkFrom terminal TkTo terminal TkHacer cuerpo TkEnd
	'''
	if (len(p) == 12):
		p[0] = Nodo("ITERACION DETERMINADA", [p[2], p[4], p[6], p[8]], [p[10]])
	else:
		p[0] = Nodo("ITERACION DETERMINADA", [p[2], p[4], p[6], "1"], [p[8]])

# Exoresiones generales
def p_expresion(p):
	'''
	expresion : opAritm
              | terminal
              | opRel
              | opCar
              | opBool
              | indice
              | opArr

	'''

	if (len(p) == 5):
		p[0] = Nodo("EXPRESION", p[1]+p[2]+str(p[3])+p[4], [p[3]])
	else:
		p[0] = Nodo("EXPRESION", None, [p[1]])

def p_opAritm(p):
	'''
	opAritm : expresion TkResta expresion
		    | expresion TkSuma expresion
		    | expresion TkDiv expresion
	        | expresion TkMult expresion
	        | expresion TkMod expresion
	        | expresion TkPunto expresion
			| TkParAbre expresion TkResta expresion TkParCierra
		    | TkParAbre expresion TkSuma expresion TkParCierra
		    | TkParAbre expresion TkDiv expresion TkParCierra
	        | TkParAbre expresion TkMult expresion TkParCierra
	        | TkParAbre expresion TkMod expresion TkParCierra
	        | TkParAbre expresion TkPunto expresion TkParCierra
	        | TkResta expresion %prec uminus
	        | TkParAbre TkResta expresion TkParCierra %prec uminus

	'''
	if (len(p) == 6):
		p[0] = Nodo("BIN_ARITMETICA", p[3], [p[2], p[4]])
	elif (len(p) == 3):
		p[0] = Nodo("OPERACION UNARIA", p[1], [p[2]])
	elif (len(p) == 5):
		p[0] = Nodo("OPERACION UNARIA", p[2], [p[3]])
	else:
		p[0] = Nodo("BIN_ARITMETICA", p[2], [p[1], p[3]])
	#p[0] = (p[1], p[2], p[3])

def p_opArr(p):
	'''
	opArr : TkId TkConcatenacion TkId
          | TkParAbre TkId TkConcatenacion TkId TkParCierra
          | TkShift TkId
		  | TkParAbre TkShift TkId TkParCierra
	'''
	if (len(p) == 4):
		p[0] = Nodo("OPERACION ARREGLO", p[2], [p[1], p[3]])
	elif (len(p) == 6):
		p[0] = Nodo("OPERACION ARREGLO", p[3], [p[2], p[4]])
	elif (len(p) == 3):
		p[0] = Nodo("OPERACION ARREGLO", p[1], [p[2]])
	else:
		p[0] = Nodo("OPERACION ARREGLO", p[2], [p[3]])


def p_opCar(p):
	'''
	opCar : terminal TkSiguienteCar
		  | terminal TkAnteriorCar
	      | TkValorAscii terminal
	      | TkValorAscii terminal TkSiguienteCar
	      | TkValorAscii terminal TkAnteriorCar
	      | indice TkSiguienteCar
		  | indice TkAnteriorCar
	      | TkValorAscii indice
	      | TkValorAscii indice TkSiguienteCar
	      | TkValorAscii indice TkAnteriorCar

	'''
	if (p[1] == '#'):
		if (len(p) == 3):
			p[0] = Nodo("OPERACION CARACTER", p[1], [p[2]])
		else:
			p[0] = Nodo("OPERACION CARACTER", p[1], [Nodo("OPERACION CARACTER", p[3], [p[2]])])
	else:
		p[0] = Nodo("OPERACION CARACTER", p[2], [p[1]])


def p_opRel(p):
	'''
	opRel : expresion TkMayor expresion
		  | expresion TkMenor expresion
		  | expresion TkMayorIgual expresion
		  | expresion TkMenorIgual expresion
		  | expresion TkIgual expresion
		  | expresion TkDesigual expresion
		  | TkParAbre expresion TkMayor expresion TkParCierra
		  | TkParAbre expresion TkMenor expresion TkParCierra
		  | TkParAbre expresion TkMayorIgual expresion TkParCierra
		  | TkParAbre expresion TkMenorIgual expresion TkParCierra
		  | TkParAbre expresion TkIgual expresion TkParCierra
		  | TkParAbre expresion TkDesigual expresion TkParCierra
	'''
	if (len(p) == 6):
		p[0] = Nodo("RELACIONAL", p[3], [p[2], p[4]])
	else:
		p[0] = Nodo("RELACIONAL", p[2], [p[1], p[3]])

# Definicion de las variables que corresponden a una declaracion
def p_variables(p):
	'''
	variables : TkId TkComa variables
			  | TkId TkAsignacion expresion TkComa variables
			  | TkId 
			  | TkId TkAsignacion expresion
	'''
	if (len(p) == 4):
		p[0] = Nodo('VARIABLE', p[1], [p[3]])
	elif (len(p) == 6):
		p[0] = Nodo('VARIABLE', p[1], [p[3], p[5]])
	else:
		p[0] = Nodo('VARIABLE', p[1], None)

# Definicion de operaciones booleanas
def p_opBool(p):
	'''
	opBool : expresion TkConjuncion expresion
           | expresion TkDisyuncion expresion
           | TkParAbre expresion TkConjuncion expresion TkParCierra
           | TkParAbre expresion TkDisyuncion expresion TkParCierra
           | TkNot expresion
           | TkParAbre TkNot expresion TkParCierra

	'''
	if (len(p) == 4):
		p[0] = Nodo("BOOLEANA", p[2], [p[1], p[3]])
	elif (len(p) == 3):
		p[0] = Nodo("BOOLEANA UNARIA", p[1], [p[2]])
	elif (len(p) == 5):
		p[0] = Nodo("BOOLENA UNARIA", p[2], [p[3]])
	elif(len(p) == 2):
		p[0] = Nodo("TERMINO", p[1], [])
	else:
		p[0] = Nodo("BOOLEANA", p[3], [p[2], p[4]])

# Regla para errores
def p_error(p):
	print("\nError de sintaxis en la linea ", p.lineno + 1)
	sys.exit(0)

def imprimirTermino(nodo, tabs):
	# Tipo de expresion

	if (len(nodo.hijos) == 0):
		print(tabs + nodo.tipo)
		print(tabs + " - Identificador: " + str(nodo.lexeme))
		print(tabs + " - Tipo: " + str(nodo.type))
	else:
		imprimirTermino(nodo.hijos[0], tabs)


# Imprimir las expresiones aritmeticas
def imprimirAritm(nodo, tabs):
	# Tipo de expresion
	print(tabs + nodo.tipo)
	# Tipo de operacion
	print(tabs + "- Operacion: " + nodo.valor)

	# Si hay un nodo (disitinto de None)
	if (nodo):
		# Si el nodo tiene hijos 
		if (len(nodo.hijos) > 0):
			# Los hijos son los operadores de la expresion
			izq = nodo.hijos[0]
			der = nodo.hijos[1]

			# Operador izquierdo
			print(tabs + "- Operador izquierdo: ")
			if (izq.tipo == "EXPRESION"):
				imprimirExp(izq, tabs + "\t")
			elif (izq.tipo == "TERMINO"):
				imprimirTermino(izq, tabs)

			# Operador derecho
			print(tabs + "- Operador derecho: ")
			if (der.tipo == "EXPRESION"):
				imprimirExp(der, tabs + "\t")
			elif (der.tipo == "TERMINO"):
				imprimirTermino(der, tabs)

# Funcion general para imprimir cualquier expresion
def imprimirExp(nodo, tabs):
	hijo = nodo.hijos[0]
	# Los hijos del nodo son cualquier tipo de expresion
	if (hijo.tipo == "BIN_ARITMETICA"):
		imprimirAritm(hijo, tabs)
	elif (hijo.tipo == "EXPRESION"):
		imprimirExp(hijo, tabs)
	elif (hijo.tipo == "TERMINO"):
		imprimirTermino(hijo, tabs)
	elif (hijo.tipo == "OPERACION UNARIA"):
		imprimirUnaria(hijo, tabs)
	elif (hijo.tipo == "RELACIONAL"):
		imprimirRelacional(hijo, tabs)
	elif (hijo.tipo == "OPERACION CARACTER"):
		imprimirCaracter(hijo, tabs)
	elif (hijo.tipo == "BOOLEANA" or hijo.tipo == "BOOLEANA UNARIA"):
		imprimirBool(hijo, tabs)
	elif(hijo.tipo == "OPERACION ARREGLO"):
		imprimirArr(hijo, tabs)

def imprimirArr(nodo, tabs):
	print(tabs + nodo.tipo)
	if (len(nodo.hijos) > 0):
		print(tabs + "- Operacion: " + nodo.valor)
		for i in nodo.hijos:
			print(tabs + '- Operador: ' + i)

# Para imprimir exp booleanas
def imprimirBool(nodo, tabs):

	print(tabs + nodo.tipo)

	if (len(nodo.hijos) > 0):
		print(tabs + "- Operacion: " + nodo.valor)
		if (len(nodo.hijos) == 2):
			# Sus hijos son los operadores
			print(tabs + "- Operador izquierdo: ")
			imprimirExp(nodo.hijos[0], tabs+"\t")
			print(tabs + "- Operador derecho: ")
			imprimirExp(nodo.hijos[1], tabs+"\t")
		else:
			print(tabs + "- Operador: ")
			imprimirExp(nodo.hijos[0], tabs+"\t")
	else:
		print(tabs + "- Valor:")
		print(tabs+"\t" + nodo.valor)

# Para imprimir declaracion de variables
def imprimirDeclaracion(nodo, tabs):
	if (nodo.tipo == "DECLARACION"):
		print(tabs + "TIPO: " + nodo.valor)
	if (nodo):
		if (len(nodo.hijos) > 0):
			for i in nodo.hijos:
				if (i.tipo == "VARIABLE"):
					print(tabs + i.tipo)
					print(tabs + "- Identificador: " + i.valor)
					if (len(i.hijos) >0):
						for j in i.hijos:
							if (j.tipo == "EXPRESION"):
								print(tabs + "- Valor: ")
								imprimirExp(j, tabs+"\t")
							else:
								print(tabs + "- Valor: no asignado")
					else:
						print(tabs + "- Valor: no asignado")
					
				imprimirDeclaracion(i, tabs)

# Para imprimir expresiones con caracteres
def imprimirCaracter(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "- Operacion: " + nodo.valor)

	hijo = nodo.hijos[0]

	if (hijo.tipo == "OPERACION CARACTER"):
		print(tabs + "- Operador")
		imprimirCaracter(hijo, tabs+"\t")
	elif (hijo.tipo == "TERMINO"):
		print(tabs + "- Operador")
		imprimirTermino(hijo, tabs+"\t")

# Para imprimir expresiones relacionales
def imprimirRelacional(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "- Operacion: " + nodo.valor)

	if (nodo):
		if (len(nodo.hijos) > 0):
			izq = nodo.hijos[0]
			der = nodo.hijos[1]

			if (izq.tipo == "EXPRESION"):
				print(tabs + "- Operador izquierdo: ")
				imprimirExp(izq, tabs + "\t")
			elif (izq.tipo == "TERMINO"):
				print(tabs + "- Operador izquierdo: ")
				imprimirTermino(izq, tabs+"\t")

			if (der.tipo == "EXPRESION"):
				imprimirExp(der, tabs + "\t")
			elif (der.tipo == "TERMINO"):
				print(tabs + "- Operador derecho: ")
				imprimirTermino(der, tabs+"\t")

# Para imprimir ciclos for
def imprimirIterDeter(nodo, tabs):
	print(tabs + nodo.tipo)
	inf = nodo.valor[1]
	sup = nodo.valor[2]
	step = nodo.valor[3]
	print(tabs + "- Identificador: " + nodo.valor[0])
	print(tabs + "- Limite inferior: ")
	if (inf.tipo == "TERMINO"):
		imprimirTermino(inf, tabs+"\t")
	elif (inf.tipo == "BIN_ARITMETICA"):
		imprimirAritm(inf, tabs + "\t")
	print(tabs + "- Limite superior: ")
	if (sup.tipo == "TERMINO"):
		imprimirTermino(sup, tabs+"\t")
	elif (sup.tipo == "BIN_ARITMETICA"):
		imprimirAritm(sup, tabs + "\t")
	print(tabs + "- Step: ")
	if (step == "1"):
		print(tabs + "\t" + "TERMINO")
		print(tabs + "\t" + step)
	else:	
		if (step.tipo == "TERMINO"):
			imprimirTermino(step, tabs+"\t")
		elif (step.tipo == "BIN_ARITMETICA"):
			imprimirAritm(step, tabs + "\t")
	print(tabs + "- Operaciones")
	imprimirArbol(nodo.hijos[0], tabs + "\t")

# Para imprimir expresiones unarias
def imprimirUnaria(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "Operacion: " + nodo.valor)
	print(tabs + "Operador: ")
	if (nodo.hijos[0].tipo == "TERMINO"):
		imprimirTermino(nodo.hijos[0], tabs+"\t")
	elif (nodo.hijos[0].tipo == "OPERACION UNARIA"):
		imprimirUnaria(nodo.hijos[0], tabs + "\t")
	elif (nodo.hijos[0].tipo == "EXPRESION"):
		imprimirExp(nodo.hijos[0], tabs + "\t")
	else:
		imprimirAritm(nodo.hijos[0], tabs + "\t")

# Para asignaciones
def imprimirAsig(nodo, tabs):
	print(tabs + nodo.tipo)
	if (isinstance(nodo.valor, str)):
		print(tabs + "Identificador: " + nodo.valor)
	else:
		print(tabs + "Identificador: " + nodo.valor.valor)


	print(tabs + "Valor: ")

	imprimirExp(nodo.hijos[0], tabs + "\t")

# Para condicionales
def imprimirCond(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "- Guardia")
	imprimirArbol(nodo.hijos[0], tabs + "\t")
	if (len(nodo.hijos) == 3):
		print(tabs + "- Exito")
		imprimirArbol(nodo.hijos[1], tabs + "\t")
		print(tabs + "- Otherwise")
		imprimirArbol(nodo.hijos[2], tabs + "\t")
	else:
		print(tabs + "- Exito")
		imprimirArbol(nodo.hijos[1], tabs + "\t")

# Para entradas
def imprimirEntrada(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "- Operador: read")
	print(tabs + "-Identificador: " + nodo.valor)

# Para salidas
def imprimirSalida(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "- Operador: " + nodo.valor)
	print(tabs + "-Salida: ")
	imprimirExp(nodo.hijos[0], tabs + "\t")

# Para imprimir while loop
def imprimirIndeter(nodo, tabs):
	print(tabs + nodo.tipo)
	print(tabs + "- Guardia: ")
	imprimirExp(nodo.valor, tabs + "\t")
	print(tabs + "- Exito: ")
	imprimirArbol(nodo.hijos[0], tabs + "\t")

# Para imprimir todo el arbol de expresiones
def imprimirArbol(nodo, tabs):
	if (nodo):
		if (len(nodo.hijos) > 0):
			for i in nodo.hijos:
				if (i.tipo == "BLOQUE"):
					tabs = tabs + "\t"
					print("\n")
					print(tabs + i.tipo)
				
				if (i.tipo == "EXPRESION"):
					print("\n")
					imprimirExp(i, tabs)

				elif (i.tipo == "DECLARACION"):
					print("\n")
					print(tabs + i.tipo)
					imprimirDeclaracion(i, tabs)

				elif(i.tipo == "ITERACION DETERMINADA"):
					print("\n")
					imprimirIterDeter(i, tabs)

				elif (i.tipo == "ITERACION INDETERMINADA"):
					print("\n")
					imprimirIndeter(i, tabs)					

				elif (i.tipo == "ASIGNACION"):
					print("\n")
					imprimirAsig(i, tabs)

				elif (i.tipo == "CONDICIONAL"):
					print("\n")
					imprimirCond(i, tabs)
				elif (i.tipo == "SALIDA"):
					print("\n")
					imprimirSalida(i, tabs)
				elif (i.tipo == "ENTRADA"):
					print("\n")
					imprimirEntrada(i, tabs)
				else:
					imprimirArbol(i, tabs)
				

def main():
	# Leer nombre del archivo de la entrada estandar
	filename = argv[1]

	# String con todas las lineas del archivo
	program = ""

	# Numero total de lienas en el archivo
	n = 0
	parser = yacc.yacc()

	with open(filename, 'r') as fd:

		for line in fd:
			program = program + line
			n = n + 1

	p = parser.parse(program)


	c = context()
	c.contextCheck(p)
	c.imprimirTabla()
	print("SECUENCIACION")
	s = "\t"
	imprimirArbol(p, s)
	e = evaluacion(c.scopes)
	e.evalArbol(p)

main()