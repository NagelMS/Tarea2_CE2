import os
import sys
import getopt
import csv
from math import log2

# Parametros de entrada y ayuda:
file_full_path = ""
file_split_path = [];
def myfunc(argv):
    global file_full_path, file_split_path
    arg_output = ""
    arg_user = ""
    arg_help = "{0} -i <input>".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hi:", ["help", "input="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  
            sys.exit(2)
        elif opt in ("-i", "--input"):
            file_full_path = arg
            file_split_path = os.path.normpath(file_full_path)
            file_split_path = os.path.split(file_split_path)


if __name__ == "__main__":
    myfunc(sys.argv)

# Definición de archivos posteriores

file_huffman_comprimido = file_full_path+".huffman"
ruta_diccionario = file_full_path+".diccionario.csv"
recovered_path = os.path.join(file_split_path[0], "recovered_"+file_split_path[1]);

#-----------------------------------------------------
# Algorithmo de compresión de huffman
#-----------------------------------------------------
#Apertura y lectura del archivo
string=[];
with open(file_full_path, "rb") as f:
    while (byte := f.read(1)):
        # Do stuff with byte.
        int_val = int.from_bytes(byte, "big")
        string.append(int_val)

# Árbol binario
class NodeTree(object):
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
    def children(self):
        return (self.left, self.right)
    def nodes(self):
        return (self.left, self.right)
    def __str__(self):
        return '%s_%s' % (self.left, self.right)

def insert_in_tree(raiz, ruta, valor):
    if(len(ruta)==1):
        if(ruta=='0'):
            raiz.left = valor;
        else:
            raiz.right = valor;
    else:
        if(ruta[0]=='0'):
            #if type(raiz.left) is int:
            if(raiz.left==None):
                raiz.left = NodeTree(None,None);
            ruta = ruta[1:];
            insert_in_tree(raiz.left,ruta,valor);
        else:
            #if type(raiz.right) is int:
            if(raiz.right==None):
                raiz.right = NodeTree(None,None);
            ruta = ruta[1:];
            insert_in_tree(raiz.right,ruta,valor);


# Función principal del algoritmo de Huffman
def huffman_code_tree(node, left=True, binString=''):
    if type(node) is int:
        return {node: binString}
    # Se asigna a l el hijo izquierdo y r el hijo derecho del nodo
    (l, r) = node.children()
    d = dict()
    # Se actualiza el código en el arbol
    d.update(huffman_code_tree(l, True, binString + '0'))
    d.update(huffman_code_tree(r, False, binString + '1'))
    return d
    

# Calculo de frecuencias y probabilidades
prob_unit = 1/len(string)
# Tupla de frecuencias: Guarda el caracter y la probabilidad.
freq = {}
for c in string:
    #print("Char",c)
    if c in freq:
        freq[c] += prob_unit
    else:
        freq[c] = prob_unit

# Ordena los códigos según la probabilidad, de forma descendente
freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

# Se crea una tupla nodes igual a freq
nodes = freq

# Mientras que el largo de nodes sea mayor a 1
while len(nodes) > 1:
    # Se asignan los valores de las menores probabilidades
    (key1, c1) = nodes[-1]
    (key2, c2) = nodes[-2]
    # nodes se convierte en una tupla más pequeña
    nodes = nodes[:-2]
    # Se genera un node los hijos de menor probabilidad
    node = NodeTree(key1, key2)
    # Se añada a la tupla el nodo generado con la suma de las dos probabilidades
    nodes.append((node, c1 + c2))
    #print(nodes)
    # Se ordenan de forma descendente
    nodes = sorted(nodes, key=lambda x: x[1], reverse=True)

huffmanCode = huffman_code_tree(nodes[0][0])

# Imprimiendo códigos generados
print(' Char | Huffman code ')
print('----------------------')
for (char, frequency) in freq:
    print(' %-4r |%12s' % (char, huffmanCode[char]))

# Calculo de la entropía de la fuente

entropy = 0

for _,p in freq:
    entropy -=  p*log2(p)

print("\nEntropía de la fuente:", entropy ,"bits/símbolo")

# Longitud media del código generado

len_media = 0

for (char,p) in freq:
    len_media += p*len(huffmanCode[char])

print("\nLongitud media del código generado:", len_media ,"bits/símbolo")

# Varianza 

varianza = 0

for (char, p) in freq:
    longitud = len(huffmanCode[char])
    varianza += p * (longitud - len_media) ** 2

print("\nVarianza de la longitud del código:", varianza)

# Calculo de eficiencias

eff_orig = entropy/8; # Se divide entre 8 ya que originalmente cada simbolo estaba representado por 8 bits

eff_huffman = entropy/len_media; 

print("\nEficiencia del código original:", eff_orig)
print("\nEficiencia del código de huffman:", eff_huffman)