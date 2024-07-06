import csv
import re
import shutil
import numpy as np
from os import path
import os
from fitness.base_ff_classes.base_ff import base_ff
from algorithm.parameters import params
from scripts.CasosRegistrados import getRegisto,actualizarFichero
from representation import grammar

# from scripts.CasosRegistrados import registro


class clausula_horn(base_ff):
    """
    Fitness para generar una clausula de horn
    """

    #Para maximizar
    maximise = True  # True as it ever was.

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()
        if params["TEORIA"]:
        
            runs=1
            fieldnames=[]
            nTotal=0

            with open(os.path.join("..", "datasets", params["DATASET_TRAIN"])) as csvfile:
                # Crea un lector CSV para leer nuestro datraset
                # Itera sobre las filas del archivo CSV
                reader = csv.DictReader(csvfile)
                nTotal=sum(1 for _ in reader)
                # Se obtiene el nombre de las cabeceras
                fieldnames = reader.fieldnames 


            gramaticaHorn = grammar.Grammar(os.path.join("..", "grammars", params['GRAMMAR_FILE']))

            cumpleGramatica=None
            consecuenteGramatica=None
            antecedentesGramatica=None
            '''
            Comprobamos que la gramatica tenga nuest 
            R → O I 
            O → nombre_consecuente(posibles_valores) 
            I → <nombre_antecedente_1>⋯<nombre_antecedente_t>    
            
            '''
            for lin in gramaticaHorn.non_terminals.values():
                
                if lin['id']=="<R>":
                    cumpleGramatica=''.join([elem['symbol'][1:-1] for elem in lin['min_path'][0]['choice']])
                
                if lin['id']=="<O>":
                    consecuenteGramatica=re.sub(r'\(.*$', '', lin['min_path'][0]['choice'][0]['symbol'])
                
                if lin['id']=="<I>":
                    antecedentesGramatica= [elem['symbol'][1:-1] for elem in lin['min_path'][0]['choice']]
                
                if consecuenteGramatica!=None and antecedentesGramatica!=None and cumpleGramatica!=None:
                    break

            if cumpleGramatica==None or cumpleGramatica!="OI":
                raise ValueError("No cumple la gramatica R -> OI ")
            
            if consecuenteGramatica==None or fieldnames.count(consecuenteGramatica)==0:
                raise ValueError("No encuentro la columna objetivo.")
            
            if not all(elem in fieldnames for elem in antecedentesGramatica):
                raise ValueError("No coinciden las columnas de partida.")
            
                
            # Inicializamos nuestra clase de registro
            registro=getRegisto()
            registro.setnColumnas(len(fieldnames))
            registro.setnFilas(nTotal)

            nPorcen=registro.getPorcen()
            casosResueltos=len(set(registro.getCasos()))

            registro.setConsecuente(consecuenteGramatica)  
            
            for columna in antecedentesGramatica:
                registro.setAntedecentes(columna)

            actualizarFichero(registro)
        

    def evaluate(self, ind, **kwargs):
      
        lRegistro=False
        for key, value in kwargs.items():
            if key=="REGISTRO":
                lRegistro=True
                break

        # Convierte la representación del individuo en una cadena ejecutable
        expr = str(ind.phenotype)
        # print(f"Evaluating expression: {expr}")

        # try:
            # Evalúa la expresión generada por el individuo

        registro = getRegisto()

        # valores = re.findall(r'\((.*?)\)', expr)

        # # Creamos un diccionario con los nombres de las variables y sus valores
        # variables = []

        consecuente=registro.getConsecuente()

        # variables.append(consecuente)

        # for nvariables in registro.getAntedecentes():
        #     variables.append(nvariables)
            
        # diccionario = dict(zip(variables, valores))
       
        valores = re.findall(r'([^\(\)]+)\((\d+)\)', expr)
        diccionario={clave: valor for clave, valor in valores}

        # filename2 =registro.getRuta()+"comprobar.txt"
        # savefile2 = open(filename2, 'a')
        # savefile2.write("\n\n"+expr+"\n")
        # Si el resultado es una columna del dataset, sumamos los valores absolutos
        if diccionario[consecuente]!="" and any(clave != consecuente and valor != "" for clave, valor in diccionario.items()):
            # Calcula la suma de los valores absolutos de la columna
        
            fitness = 1
            nFilas=0

            # Abre el archivo CSV en modo lectura
            with open(path.join("..", "datasets", params["DATASET_TRAIN"])) as csvfile:
                # Crea un lector CSV
                # Itera sobre las filas del archivo CSV
                reader = csv.DictReader(csvfile)
                # Itera sobre las filas del archivo CSV
                nTotal=sum(1 for _ in reader)

                aCalculo ={}
                csvfile.seek(1)

                for numero_fila, fila in enumerate(reader, start=1):

                    lOK = False

                    if fila[consecuente]==diccionario[consecuente]:
                        for clave, valor in diccionario.items():
                            if clave == consecuente:
                                continue 
                            elif valor == "" or fila[clave] == valor:
                                lOK = True
                            else:
                                lOK = False
                                break  # Si una condición no se cumple, salir del bucle
                
                    if lOK:
                        nFilas+=1
                        # Cuantas veces encuentro la linea en el registro
                        nPeso=registro.vecesCaso(numero_fila)
                        
                        if lRegistro:

                            filename =registro.getRuta()+"proceso.txt"
                            savefile = open(filename, 'a')

                            if nPeso==0:

                                savefile.write(str(numero_fila)+" (Nuevo) ")
                                savefile.close()

                                registro.setCaso(numero_fila,round(1/nTotal,10)*100)

                            else:
                                
                                savefile.write(str(numero_fila)+" (ya cubierto) ")
                                savefile.close()

                                registro.setCaso(numero_fila,0)

                            actualizarFichero(registro)

                        else:

                            if nPeso==0:
                               nPorcen=100
                               nSuma=1 
                            else:
                                nPorcen=registro.getPorcen()
                                nSuma=1/nPeso

                            if nPorcen in aCalculo:
                                aCalculo[nPorcen]+=nSuma                               
                            else:
                                aCalculo[nPorcen]=nSuma
                        
                            # savefile2.write(str(numero_fila)+"_"+str(nPorcen)+"_"+str(nPeso)+"_"+str(registro.getPorcen())+"_"+str(nTotal)+"___"+str(aCalculo[nPorcen])+"\n")
                       
            
            nCalulo = sum(clave * valor for clave, valor in aCalculo.items()) / nTotal
            #  nPeso=registro.porcenCaso(numero_fila)

            #                 if nPeso==0:

            #                     aCalculo.append([numero_fila,100])
                                
            #                 else:
            #                     aCalculo.append([numero_fila,registro.porcenSinCubrir])
                        
            #                 savefile2.write(str(numero_fila)+"-"+str(nPeso)+"-"+str(registro.porcenSinCubrir))
                       
            # nCalulo = sum(item[0] * item[1] for item in aCalculo)/nTotal
            fitness = nCalulo
            # savefile2.write("\n"+str(fitness))
            # savefile2.close()
            
        else:
            # Si el resultado no es un array, establece el fitness a infinito
            fitness = -1
            # savefile2.write("\n"+str(fitness))
            # savefile2.close()
   
        return fitness
