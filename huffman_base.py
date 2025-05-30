import os
import sys
import getopt
import csv
from math import log2

#Parámetros de entrada y ayuda:
output_directory="salidas"
file_full_path = ""
file_split_path = []
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


file_huffman_comprimido =os.path.splitext(os.path.basename(file_full_path))[0]+".huffman"
ruta_diccionario = os.path.splitext(os.path.basename(file_full_path))[0]+"_diccionario.csv"
recovered_path = os.path.join(output_directory, "recovered_"+file_split_path[1])
#-----------------------------------------------------
# Algorithmo de compresión de huffman
#-----------------------------------------------------

#Apertura y lectura del archivo.
string=[]
with open(file_full_path, "rb") as f:
    while (byte := f.read(1)):
        # Do stuff with byte.
        int_val = int.from_bytes(byte, "big")
        string.append(int_val)

#Árbol binario.
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
            raiz.left = valor
        else:
            raiz.right = valor
    else:
        try:
            if( ruta[0]=='0'):
                if(raiz.left==None):
                    raiz.left = NodeTree(None,None)
                ruta = ruta[1:]
                insert_in_tree(raiz.left,ruta,valor)
            else:
                if(raiz.right==None):
                    raiz.right = NodeTree(None,None)
                ruta = ruta[1:]
                insert_in_tree(raiz.right,ruta,valor)
        except: 
            None


#Función principal del algoritmo de Huffman.
def huffman_code_tree(node, left=True, binString=''):
    if type(node) is int:
        return {node: binString}
    (l, r) = node.children()
    d = dict()
    d.update(huffman_code_tree(l, True, binString + '0'))
    d.update(huffman_code_tree(r, False, binString + '1'))
    return d
    

#Calculo de frecuencias y probabilidades.
prob_unit = 1/len(string)
freq = {}
for c in string:
    if c in freq:
        freq[c] += prob_unit
    else:
        freq[c] = prob_unit

freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)

nodes = freq #Lista de dulpas (símbolo,frecuencia)
while len(nodes) > 1:
    (key1, c1) = nodes[-1]
    (key2, c2) = nodes[-2]
    nodes = nodes[:-2]
    node = NodeTree(key1, key2)
    nodes.append((node, c1 + c2))
    nodes = sorted(nodes, key=lambda x: x[1], reverse=True)

huffmanCode = huffman_code_tree(nodes[0][0]) #Diccionario {símbolo:código}

print(' Char | Huffman code ')
print('----------------------')
for (char, frequency) in freq:
    print(' %-4r |%12s' % (char, huffmanCode[char]))

freq=dict(freq) #Diccionario {símbolo:frecuencia}

#Determinar e imprimir la entropía de la fuente:
information= lambda p:p*log2(1/p)
entropy=0
for code in freq:
    entropy+=information(freq[code])
print("Entropía de la Fuente: " + str(entropy))

#Determinar e imprimir el largo promedio de los códigos:
avg_length_new=0
for code in huffmanCode:
   avg_length_new+=len(huffmanCode[code])*freq[code]
print("Largo promedio: " + str(avg_length_new))

#Determinar e imprimir la varianza del nuevo código generado:
code_variance_new=0
for code in huffmanCode:
    code_variance_new+=freq[code]*((len(huffmanCode[code])-avg_length_new)**2)
print("Varianza del código original: " + str(code_variance_new))

#Determinar e imprimir la eficiencia del código original:
avg_length_old=entropy/8 #hardcoded a 8 bits en las codificaciones originales
print("Eficiencia del código original: " + str(avg_length_old))

#Determinar e imprimir la eficiencia del nuevo código generado:
try:
    new_code_efficiency=entropy/avg_length_new
    print("Eficiencia del nuevo código generado: " + str(new_code_efficiency))
except:
    print("Largo promedio igual a 0, todos los símbolos son iguales y no se genera diccionario de compresión.")

#Mostrar bytes del archivo original sin comprimir:
print("Cantidad de bytes en el archivo sin compresión: "+ str(len(string)))

#Compresión del archivo original.
binary_string = []
for c in string :
    binary_string += huffmanCode [c]

compressed_length_bit = len( binary_string )

if( compressed_length_bit %8>0):
    for i in range (8 - len( binary_string ) % 8) :
        binary_string += "0"

byte_string ="". join ([ str( i ) for i in binary_string ])
byte_string =[ byte_string [ i : i +8] for i in range (0 , len( byte_string ), 8) ]

#Mostrar bytes del archivo comprimido:
print("Cantidad de bytes en el archivo con compresión: "+ str(len(byte_string)))

try:
    #Mostrar tasa de compresion:
    print("Tasa de compresión: " + str(len(string)/len(byte_string)))
except:
    print("No se calcula la tasa de compresión debido a que no hay diccionario de compresión.")

#Escribir el archivo con los datos comprimidos.
compressed_file=open(f"{output_directory}/{file_huffman_comprimido}","wb")
byte_string=bytearray([int(i,2) for i in byte_string])
compressed_file.write(byte_string)
compressed_file.close()

#Generar archivo .csv del diccionario utilizado en la codificación.
csvfile = open(f"{output_directory}/{ruta_diccionario}","w")
writer = csv.writer ( csvfile )
writer.writerow ([ str ( compressed_length_bit ) ," bits "])

for entrada in huffmanCode:
    writer.writerow ([ str ( entrada ) , huffmanCode [ entrada ]])
csvfile.close()

#Abrir diccionario y descomprimir datos.
csvfile = open (f"{output_directory}/{ruta_diccionario}" , "r")
reader = csv . reader ( csvfile )
bits_a_leer = None 
diccionario = dict () 
for row in reader :
    if( bits_a_leer == None ) :
        bits_a_leer = int( row [0]) 
    else:
        diccionario.update ({ int( row [0]) : row [1]})
Decoding = NodeTree ( None , None ) 
for entrada in diccionario :
    insert_in_tree ( Decoding , diccionario [ entrada ] , entrada )
nodo = Decoding 
data_estimated = []
for i in range ( compressed_length_bit ) :
    (l , r ) = nodo . children () 
    if( binary_string [ i ]== "1") :
        nodo = r
    else:
        nodo = l
    if type ( nodo ) is int :
        data_estimated . append(nodo)
        nodo = Decoding

#Mostrar bytes del archivo original después de descomprimir:
print("Cantidad de bytes en el archivo descomprimido: "+ str(len(data_estimated)))

#Guardar archivo descomprimido
decompressed_file=open(recovered_path,"wb")
byte_decompress=bytearray(data_estimated)
decompressed_file.write(byte_decompress)
decompressed_file.close()
