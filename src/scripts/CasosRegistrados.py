from os import path
import os
from algorithm.parameters import params


class Registo:
  def __init__(self):
    
    filename =path.join("..","results",params["EXPERIMENT_NAME"], "registro.txt")
    carpeta= path.join("..", "results", params["EXPERIMENT_NAME"])
    
    if not os.path.exists(carpeta):
      os.makedirs(carpeta)

    reg={}
    self.__ruta = carpeta+"/"
    self.__fichero = filename    
    if os.path.exists(filename):

      with open(filename, 'r') as parameters:
        
        content = parameters.readlines()
        
        for line in [l for l in content if not l.startswith("#")]:
          split = line.find(":")

          key, value = line[:split], line[split + 1:].strip()
          reg[key] = value

        self.__porcenSinCubrir  = float(reg["porcenSinCubrir"])
        self.__nExperimentos    = int(reg["nExperimentos"])
        self.__nColumnas        = int(reg["nColumnas"])
        self.__nFilas           = int(reg["nFilas"])
        self.__consecuente      = reg["consecuente"]
        
        if reg["casos"]!="":
          componentes = reg["casos"].split(",")
          self.__casos = [int(valor) for valor in componentes if valor]
        else:
          self.__casos = []   

        if reg["antedecentes"]!="":
          componentes = reg["antedecentes"].split(",")
          self.__antedecentes = [valor for valor in componentes if valor]
        else:
          self.__antedecentes = []   

    else:

      self.__porcenSinCubrir = 100.00  
      self.__nExperimentos = 0
      self.__nColumnas=0
      self.__nFilas=0
      self.__consecuente=""    
      self.__casos = []
      self.__antedecentes = []
      actualizarFichero(self)
    
  def getRuta(self):
    return self.__ruta 
  
  def getFichero(self):
    return self.__fichero 
  
  def getPorcen(self):
    return self.__porcenSinCubrir 
  
  def getnExperimentos(self):
    return self.__nExperimentos
 
  def setnExperimentos(self,nExp):
    self.__nExperimentos=nExp

  def getnColumnas(self):
    return self.__nColumnas

  def setnColumnas(self,nExp):
    self.__nColumnas=nExp

  def getnFilas(self):
    return self.__nFilas
  
  def setnFilas(self,nExp):
    self.__nFilas=nExp
  

  def getConsecuente(self):
    return self.__consecuente
  
  def setConsecuente(self,nExp):
    self.__consecuente=nExp
  
  def getCasos(self):
    return self.__casos
    
  def setCaso(self,caso,ntotal):
    self.__casos.append(caso) 
    self.__actualizarPorcen(ntotal)

    
  def getAntedecentes(self):
    return self.__antedecentes
    
  def setAntedecentes(self,variable):
    self.__antedecentes.append(variable) 


  def vecesCaso(self,caso):
    return self.__casos.count(caso)
  
  def __actualizarPorcen(self,nExp):
    self.__porcenSinCubrir=self.__porcenSinCubrir-nExp 
    
def actualizarFichero(reg):
    savefile = open(reg.getFichero(), 'w')
    savefile.write("nColumnas:"+str(reg.getnColumnas()))
    savefile.write("\nnFilas:"+str(reg.getnFilas()))
    savefile.write("\nporcenSinCubrir:"+str(reg.getPorcen()))
    savefile.write("\nnExperimentos:"+str(reg.getnExperimentos()))
    savefile.write("\nconsecuente:"+reg.getConsecuente())
    
    savefile.write("\ncasos:")
    for caso in reg.getCasos():
      savefile.write(str(caso)+",")

    savefile.write("\nantedecentes:")
    for antecedente in reg.getAntedecentes():
      savefile.write(antecedente+",")

    savefile.close()

def getRegisto():
  registro = Registo()
  actualizarFichero(registro)
  return registro


