"""
Implementación de un analizador lexicográfico para el lenguaje BasicTran

"""

import ply.lex as lex
from sys import argv

# Tokens
tokens = [
	'TkComa',
	'TkPunto',
	'TkPuntoYComa',
	'TkDosPuntos',
	'TkParAbre',
	'TkParCierra',
	'TkCorcheteAbre',
	'TkCorcheteCierra',
	'TkLlaveAbre',
	'TkLlaveCierra',
	'TkHacer',
	'TkAsignacion',
	'TkSuma',
	'TkResta',
	'TkMult',
	'TkDiv',
	'TkMod',
	'TkConjuncion',
	'TkDisyuncion',
	'TkMenor',
	'TkMenorIgual',
	'TkMayor',
	'TkMayorIgual',
	'TkIgual',
	'TkDesigual',
	'TkSiguienteCar',
	'TkAnteriorCar',
	'TkValorAscii',
	'TkConcatenacion',
	'TkShift',
	'TkId',
	'TkNum',
	'TkError',
	'TkErrorSol',
	'TkCaracterError',
	'TkCarEspecial',
	'TkCarError',
	'TkTab',
	'TkSalto',
	'TkCaracter',
	'TkComilla',
	'TkBarra'
]

# Palabras reservadas
reservadas = {
	'with': 'TkWith',
	'begin': 'TkBegin',
	'var': 'TkVar',
	'int': 'TkInt',
	'bool': 'TkBool',
	'char': 'TkChar',
	'array': 'TkArray',
	'of': 'TkOf',
	'true': 'TkTrue',
	'false': 'TkFalse',
	'if': 'TkIf',
	'otherwise': 'TkOtherwise',
	'while': 'TkWhile',
	'for': 'TkFor',
	'from': 'TkFrom',
	'to': 'TkTo',
	'step': 'TkStep',
	'read': 'TkRead',
	'print': 'TkPrint',
	'not': 'TkNot',
	'end': 'TkEnd'
}

tokens = tokens + list(reservadas.values())

# Ignorar espacios y tabuladores
t_ignore = ' \t'

# Expresiones regulares ordenadas de forma decreciente
t_TkConcatenacion = r'[:][:]'
t_TkDesigual = r'[/][=]'
t_TkSiguienteCar = r'[+][+]'
t_TkAnteriorCar = r'[-][-]'
t_TkConjuncion = r'\/\\'
t_TkDisyuncion = r'\\/'
t_TkMayorIgual = r'\>='
t_TkMenorIgual = r'\<='
t_TkHacer = r'\->'
t_TkAsignacion = r'\<-'
t_TkComa = r'\,'
t_TkPuntoYComa = r'\;'
t_TkPunto = r'\.'
t_TkDosPuntos = r'\:'
t_TkParAbre = r'\('
t_TkParCierra = r'\)'
t_TkCorcheteAbre = r'\['
t_TkCorcheteCierra = r'\]'
t_TkLlaveAbre = r'\{'
t_TkLlaveCierra = r'\}'
t_TkSuma = r'\+'
t_TkResta = r'\-'
t_TkMult = r'\*'
t_TkDiv = r'\/'
t_TkMod = r'\%'
t_TkMenor = r'\<'
t_TkMayor = r'\>'
t_TkIgual = r'\='
t_TkValorAscii = r'\#'
t_TkShift = r'\$'
t_TkErrorSol = r'.'

#Expresiones regulares especificadas como funciones

# Actualizar numero de lineas cada vez que se encuentra un salto
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)




# Cualquier otro tipo de error
def t_error(t):
	t.lexer.skip(1)

# Para detectar caracteres
def t_TkCaracter(t):
	r'[\'][^\'\\]{1}[\']'
	t.type = 'TkCaracter'
	return t

def t_TkTab(t):
	r'[\']\\t{1}[\']'
	t.type = 'TkTab'
	return t

def t_TkSalto(t):	
	r'[\']\\n{1}[\']'
	t.type = 'TkSalto'
	return t

def t_TkComilla(t):
	r'[\']\\\'{1}[\']'
	t.type = 'TkComilla'
	return t

def t_TkBarra(t):
	r'[\']\\\\{1}[\']'
	t.type = 'TkBarra'
	return t

def t_TkCarError(t):
	r'[\'](\'|\\){1}[\']'
	t.value = t.value[1]
	t.type = 'TkCaracterError'
	return t

# Para detectar un char especial seguido de un error
def t_TkCarEspecial(t):
	r'[\'](\\n.|\\t.|\\\'.|\\\\.)[\']'
	t.value = t.value[3]
	t.type = 'TkCaracterError'
	return t
	

# Para detectar un char erroneo(largo mayor de 1)
def t_TkCaracterError(t):
	r'[\'].{2,}[\']'
	t.value = t.value[2]
	t.type = 'TkCaracterError'
	return t

#Expresion regular que maneja las palabras reservadas.
def t_ID(t):
	r'[a-zA-Z][a-zA-Z_0-9]*'
	t.type = reservadas.get(t.value, 'TkId')
	return t

# Para detectar numeros
def t_TkNum(t):
	r'\d+'
	t.value = int(t.value)
	return t

# Para obtener el numero de columna de un token
def get_column(entrada, token):
	# El atributo lexpos es un entero que contiene la posicion actual en el texto de
	# entrada (justo despues del ultimo texto matcheado)
	# Con rfind hallamos el index del ultimo salto de linea antes de la posicion actual
	# y le sumamos 1 para obtener el index del inicio de la linea actual
	inicio = entrada.rfind('\n', 0, token.lexpos) + 1
	# Al index de la posicion actual con respecto a todo el texto le restamos el index
	# del inicio de la linea actual (con respecto a todo el texto) y asi obtenemos la
	# posicion actual con respecto a la linea
	column = (token.lexpos - inicio) + 1
	return column

############ Main ############

# Construimos el lexer
lexer = lex.lex()

# Leer nombre del archivo de la entrada estandar
filename = argv[1]

# String con todas las lineas del archivo
program = ""

# Numero total de lienas en el archivo
n = 0

with open(filename, 'r') as fd:

	for line in fd:
		program = program + line
		n = n + 1


# Pasamos programa al lexer
lexer.input(program)

# Booleano para chequear si ocurrio un error
error = False

# Recorremos los tokens para ver si ocurre un error
for tok in lexer:
	if tok.type == 'TkError' or tok.type == 'TkErrorSol' or tok.type == 'TkCaracterError':
		# Si se encuentra un token error cambiamos el estatus de error
		error = True
		break

# Reiniciamos posiciones del lexer
lexer.lexpos = 0
lexer.lineno = 0

# Diccionario de los token, las llaves son los numeros de las filas
# Para cada fila hay un arreglo, donde cada elemento es un string que representa
# un token de la linea
lines = {}

# Si se encontro un token error, solo imprimimos los errores
if (error):

	for tok in lexer:
		if tok.type == 'TkError' or tok.type == 'TkErrorSol' or tok.type == 'TkCaracterError':
			print("Error: Caracter inesperado \"" + tok.value + "\" en la fila " + str(lexer.lineno+1) + ", columna " + str(get_column(lexer.lexdata, tok)))

# # Si no ocurrio un error, añadimos los tokens al diccionario 
# else:

# 	for tok in lexer:
# 		# Numero del fila
# 		col = str(tok.lineno+1)
# 		# Si el numero de la fila ya esta en el diccionario, añadimos el token a la lista
# 		if (col in lines):
# 			# Cada string que representa un token tiene un formato distinto
# 			if (tok.type == 'TkId' ):
# 				lines[col].append(tok.type + "(\"" + tok.value + "\") " + col + " " + str(get_column(lexer.lexdata, tok)))
# 			elif (tok.type == 'TkCaracter' or tok.type == 'TkTab' or tok.type == 'TkSalto' or tok.type == 'TkBarra' or tok.type == 'TkComilla'):
# 				lines[col].append(tok.type + "(" + tok.value + ") " + col + " " + str(get_column(lexer.lexdata, tok)))
# 			elif (tok.type == 'TkNum'):
# 				lines[col].append(tok.type + "(" + str(tok.value) + ") " + col + " " + str(get_column(lexer.lexdata, tok)))

# 			else:
# 				lines[col].append(tok.type + " " + col + " " + str(get_column(lexer.lexdata, tok)))
# 		# Si el numero que representa la fila no esta en el dict, creamos su arreglo
# 		else:
# 			if (tok.type == 'TkId'):
# 				lines[col] = [tok.type + "(\"" + tok.value + "\") " + col + " " + str(get_column(lexer.lexdata, tok))]
# 			elif (tok.type == 'TkCaracter' or tok.type == 'TkTab' or tok.type == 'TkSalto' or tok.type == 'TkBarra' or tok.type == 'TkComilla'):
# 				lines[col] = [tok.type + "(" + tok.value + ") " + col + " " + str(get_column(lexer.lexdata, tok))]
# 			elif (tok.type == 'TkNum'):
# 				lines[col] = [tok.type + "(" + str(tok.value) + ") " + col + " " + str(get_column(lexer.lexdata, tok))]
# 			else:
# 				lines[col] = [tok.type + " " + col + " " + str(get_column(lexer.lexdata, tok))]
	
# 	# Recorremos las llaves (numero de lineas) del diccionario en orden ascendente
# 	for val in range(1,n+1):
# 		# Contador para chequear si hemos llegado al final de una linea
# 		i = 0
# 		# Si el numero de la linea esta en el diccionario (contiene tokens)
# 		if str(val) in lines:
# 			# Imprimimos todos los tokens de la linea
# 			for j in lines[str(val)]:
# 				# Si llegamos a la ultima columna de la linea imprimos sin coma
# 				if (i == len(lines[str(val)])-1):
# 					print(j)

# 				else:
# 					print(j + ", ", end = '')
# 				# Aumentar contador
# 				i = i + 1