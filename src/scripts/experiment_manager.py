import csv
from datetime import datetime
from os import getcwd, getpid, makedirs, path as path2
import os
import re
import shutil



""" This program cues up and executes multiple runs of PYGE. Results of runs
    are parsed and placed in a spreadsheet for easy visual analysis.

    Copyright (c) 2014 Michael Fenton
    Hereby licensed under the GNU GPL v3."""

from sys import path, executable
path.append("../src")

from utilities.algorithm.general import check_python_version

check_python_version()

from multiprocessing import Pool
from subprocess import call
import sys

from algorithm.parameters import params, set_params
from scripts.stats_parser import parse_stats_from_runs
# from scripts.CasosRegistrados import Registo 
from scripts.CasosRegistrados import getRegisto,actualizarFichero

from representation import grammar

def execute_run(seed):
    """
    Initialise all aspects of a run.

    :return: Nothing.
    """

    exec_str = executable + " ponyge.py " \
               "--random_seed " + str(seed) + " " + " ".join(sys.argv[1:])

    call(exec_str, shell=True)


def execute_runs():
    """
    Execute multiple runs in series using multiple cores.

    :return: Nothing.
    """

    # Initialise empty list of results.
    results = []

    # Initialise pool of workers.
    pool = Pool(processes=params['CORES'])

    for run in range(params['RUNS']):
        # Execute a single evolutionary run.
        results.append(pool.apply_async(execute_run, (run,)))

    for result in results:
        result.get()

    # Close pool once runs are finished.
    pool.close()

# registro = Registo()



def crear_teoria():
    """
    Execute multiple runs in series using multiple cores.

    :return: Nothing.
    """
    contador=1
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
    
    filename =registro.getRuta()+"teoria.txt"
    savefile = open(filename, 'a')
    savefile.write("Teoria generada:\n")
    savefile.close()

    ''' 
     Bucle para la generacion de la teoria, parara cuando:
     -se resuelvan todos los casos
     -el porcentaje pendiente sea aproximadamente cero
     -se ejecuten 5 evoluciones seguidas sin disminuir el porcentaje pendiente
    '''
    while round(nPorcen,10)>0 and casosResueltos!=nTotal and contador<5:
        # Lanzamos cada evolucion individual
        execute_run(runs)

        # Actualizamos el numero de experimentos generados 
        registro=getRegisto()
        registro.setnExperimentos(runs)
        actualizarFichero(registro)
        
        filename =registro.getRuta()+"proceso.txt"
        savefile = open(filename, 'a')
        savefile.write("\nN.Casos cubiertos:"+str(len(registro.getCasos()))+"\nPorcentaje pendiente:"+str(registro.getPorcen())+"\n\n")
        savefile.close()
        casosResueltos=len(set(registro.getCasos()))
        runs+=1
        
        if nPorcen==registro.getPorcen():            
            contador+=1
        else:
            contador=0
        nPorcen=registro.getPorcen()

def check_params():
    """
    Checks the params to ensure an experiment name has been specified and
    that the number of runs has been specified.

    :return: Nothing.
    """

    if not params['EXPERIMENT_NAME']:
        s = "scripts.run_experiments.check_params\n" \
            "Error: Experiment Name not specified.\n" \
            "       Please specify a name for this set of runs."
        raise Exception(s)

    if params['RUNS'] == 1:
        print("Warning: Only 1 run has been specified for this set of runs.")
        print("         The number of runs can be specified with the command-"
              "line parameter `--runs`.")


def main():
    """
    The main function for running the experiment manager. Calls all functions.

    :return: Nothing.
    """

    # Setup run parameters.
    set_params(sys.argv[1:], create_files=False)

    # Check the correct parameters are set for this set of runs.
    check_params()

    if params["TEORIA"]:
        #En caso de haber generado una teoria, borramos todo el contenido
        carpeta= path2.join("..", "results", params["EXPERIMENT_NAME"])
        if os.path.exists(carpeta):
            shutil.rmtree(carpeta)
        
        #Proceso para generar una teoria con clausulas de Horn
        crear_teoria()
    else:
        # Execute multiple runs.
        execute_runs()
        
    # Save spreadsheets and all plots for all runs in the 'EXPERIMENT_NAME'
    # folder.
    parse_stats_from_runs(params['EXPERIMENT_NAME'])


if __name__ == "__main__":
    main()
