#!/usr/bin/env python
# coding: utf-8

# In[1]:


from libsbml import*
import sys
import os
import re
#abgewandelte Reaktion-Klasse, die nur die Teile enthält, die in SBML-Datei abgspeichert werden
class Reaction_For_Sbml:
    def __init__(self, name, reactants, products, extract_stoich_rea=[], extract_stoich_prod=[]):
        global listOfReactions
        self.listOfReactants=[]
        self.listOfProducts=[]
        self.defined_name=name
        self.reac_stoich=extract_stoich_rea
        self.prod_stoich=extract_stoich_prod
        listOfReactions.append(self)
        for i in range (len(reactants)):
            self.listOfReactants.append(reactants[i])
        for i in range (len(products)):
            self.listOfProducts.append(products[i])

        
#check-funktion um sbml-aufgaben zu überprüfen und evtl. Fehlermeldungen besser interpretieren zu können, übernommen
#aus Hilfestellung der sbml-lib
def check(value, message):
    #If 'value' is None, prints an error message constructed using
    #'message' and then exits with status code 1.  If 'value' is an integer,
    #it assumes it is a libSBML return status code.  If the code value is
    #C:\u    LIBSBML_OPERATION_SUCCESS, returns without further action; if it is not,
    #prints an error message constructed using 'message' along with text from
    #libSBML explaining the meaning of the code, and exits with status code 1."""
    if value is None:
        raise SystemExit('LibSBML returned a null value trying to ' + message + '.')
    elif type(value) is int:
        if value == LIBSBML_OPERATION_SUCCESS:
            return
        else:
            err_msg = 'Error encountered trying to ' + message + '.'                  + 'LibSBML returned error code ' + str(value) + ': "'                  + OperationReturnValue_toString(value).strip() + '"'
            raise SystemExit(err_msg)
    else:
        return

def getReactionforsbml():
    global listOfReactions, listOfSpecies
    listOfReactions = []
    
    
###
#here you can insert the youre reactionnetwork
###
###
###





    #Reaction_For_Sbml("r1",["A","B","C"],["C"],[1,1,1],[3])
    #Reaction_For_Sbml("r2",["C","A"],["A"],[1,1],[2])
    #Reaction_For_Sbml("r3",["A","B"],["A","B"],[2,1],[2,2])
    #Reaction_For_Sbml("r4",["D","B"],["D"],[1,1],[2])
    #Reaction_For_Sbml("r5",["D"],["B"],[1],[1])
    #Reaction_For_Sbml("r6",["C","E"],["E"],[1,1],[2])
    #Reaction_For_Sbml("r7",["D","A"],["C","A"],[1,1],[1,1])
    #Reaction_For_Sbml("r8",["C","B","E"],["D","E"],[1,1,1],[2,1])
    #Reaction_For_Sbml("r9",["E","B"],["E"],[1,1],[2])
    #Reaction_For_Sbml("r10",["E","D"],[],[1,1],[])
    #Reaction_For_Sbml("r11",["E"],["A"],[1],[1])
    
    Reaction_For_Sbml("r1",[],["h"],[],[1])
    Reaction_For_Sbml("r2",["h","v"],["in","v"],[1,1],[1,1])
    Reaction_For_Sbml("r3",["h","v"],["h","vb"],[1,1],[1,1])

    Reaction_For_Sbml("r4",["vb"],["m"],[1],[1])
    Reaction_For_Sbml("r5",["p"],["v"],[1],[1])
    Reaction_For_Sbml("r6",["m"],["m","s"],[1],[1,1])
    Reaction_For_Sbml("r7",["s"],[],[1],[])
    Reaction_For_Sbml("r8",["in","s"],["s"],[1,1],[1])
    Reaction_For_Sbml("r9",["v","s"],["s"],[1,1],[1])
    
#    Reaction_For_Sbml("r1",["a","b"],["c","d"],[1,1],[1,1])
#    Reaction_For_Sbml("r2",["c","a"],["c"],[1,1],[1])
#    Reaction_For_Sbml("r3",["a","e"],["c"],[1,1],[1])
#    Reaction_For_Sbml("r4",["c"],["a"],[1],[1])
#    Reaction_For_Sbml("r5",["d"],["a"],[1],[1])
#    Reaction_For_Sbml("r6",["e"],["b","e"],[1],[1,1])
#
#    Reaction_For_Sbml("r7",["f"],["f","g"],[1,1,1],[1,1,1])
#    Reaction_For_Sbml("r8",["g","h"],["i","j"],[1,1],[1,1])
#    Reaction_For_Sbml("r9",["t","i"],["k","l"],[1,1],[1,1])
#    Reaction_For_Sbml("r10",["k","l"],["m"],[1,1],[1])
#    Reaction_For_Sbml("r11",["k","j"],["k","t"],[1,1],[1,1])
#    Reaction_For_Sbml("r12",["g","m"],["h"],[1,1],[1])
#    Reaction_For_Sbml("r13",["k","f"],["f"],[1,1],[1])
#
#    Reaction_For_Sbml("r14",["u","n"],["o"],[1,1],[1])
#    Reaction_For_Sbml("r15",["o"],["p","v"],[1],[1,1])
#    Reaction_For_Sbml("r16",["v","q"],["r"],[1,1],[1])
#    Reaction_For_Sbml("r17",["r"],["s","u"],[1],[1,1])
#    Reaction_For_Sbml("r18",["s","p"],["n","q"],[1,1],[1,1])
#    Reaction_For_Sbml("r19",["o","r"],["w"],[1,1],[1])
#    Reaction_For_Sbml("r20",["w","v"],[],[1,1],[])
#
#    Reaction_For_Sbml("r21",["a","g"],["o"],[1,1],[1])
#    Reaction_For_Sbml("r22",["o","k"],["c","v"],[1,1],[1,1])
#    Reaction_For_Sbml("r23",["d","r"],["r"],[1,1],[1])
#    Reaction_For_Sbml("r24",["q","w"],["j","i"],[1,1],[1,1])
#    Reaction_For_Sbml("r25",["g","k"],["h","g"],[1,1],[1,1])
#    Reaction_For_Sbml("r26",["t","a"],["p"],[1,1],[1])
#    Reaction_For_Sbml("r27",["u","s"],["q"],[1,1],[1])
#    Reaction_For_Sbml("r28",["l","v"],["c"],[1,1],[1])
    
    #Reaction_For_Sbml("r1",["v"],["v"],[1],[2])
    #Reaction_For_Sbml("r2",["v"],[],[1],[])
    #Reaction_For_Sbml("r3",["e","v"],["e"],[1,1],[1])

    #Reaction_For_Sbml("r4",[],["e"],[],[1])
    #Reaction_For_Sbml("r5",["e"],[],[1],[])
    #Reaction_For_Sbml("r6",["v","e"],["v","e"],[1,1],[1,1])
    #Reaction_For_Sbml("r7",[],["s"],[],[1])
    #Reaction_For_Sbml("r8",["s"],[],[1],[])
    #Reaction_For_Sbml("r9",["v","s","i"],["v","i"],[1,1,1],[1,2])
    #Reaction_For_Sbml("r10",["i"],[],[1],[])
    
    
    #Reaction_For_Sbml("r20",["z","y"],[],[1,1],[])
    
    
    
    
    
    
    
    
    
    
    
    
#####




    #Gesamtspezies erfassen, indem mit einem Set über alle Reaktionen iteriert wird 
    listOfSpecies=set()
    for reaction in listOfReactions:
        listOfSpecies.update(reaction.listOfReactants)  
        listOfSpecies.update(reaction.listOfProducts)
    return() 
def create_model():
    
    global document
    #erstellen von SBML-Dokument-Klasse mit Version 3.1
    try:
        document = SBMLDocument(3, 1)
    except ValueError:
        raise SystemExit('Could not create SBMLDocument object')
    #erstellen eines Models im Dokument    
    model = document.createModel()
    
    
    #erstellen der Elemente des Models
    
    #zuerst die Species, die wie folgt initialisiert, mit ID versehen, als Nicht-konstant, ohne obere Grenzen
    #mit Initialmenge 0 gesetzt wird
    for specieselement in listOfSpecies:
        
        species = model.createSpecies()
        check(species,                                  'create species s1')
        check(species.setId(specieselement),           'set species s1 id')
        #check(s1.setCompartment('c1'),                'set species s1 compartment')
        check(species.setConstant(False),                    'set "constant" attribute on s1')
        check(species.setInitialAmount(0),             'set initial amount for s1')
        check(species.setBoundaryCondition(False),     'set "boundaryCondition" on s1')
        check(species.setHasOnlySubstanceUnits(False), 'set "hasOnlySubstanceUnits" on s1')

    #danach folgen die Reaktionen, die wieder initialisert und mit ID versehen werden. 
    #Des Weiteren werden sie als nicht reversibel und ohne Priorität festegelegt
   
    for reaction in listOfReactions:
        sbmlreaction = model.createReaction()
        check(sbmlreaction,                                 'create reaction')
        check(sbmlreaction.setId(reaction.defined_name),    'set reaction id')
        check(sbmlreaction.setReversible(False),            'set reaction reversibility flag')
        check(sbmlreaction.setFast(False),                  'set reaction "fast" attribute')
        
        #jeder Reaktant und jedes Produkt muss einzeln initialisiert und mit dem jeweiligen stöchiometrischen Parameter
        #versehen werden zusätzlich wird es der bereits initaialisierten Species zugeordnet.
        for i in range(len(reaction.listOfReactants)):
            species_rea = sbmlreaction.createReactant()
            check(species_rea,                                                  'create reactant')
            check(species_rea.setStoichiometry(reaction.reac_stoich[i]),    "assign stochiometric parameter")
            check(species_rea.setSpecies(reaction.listOfReactants[i]),          'assign reactant species')
            check(species_rea.setConstant(True),                                'set "constant" on species ref 1')

        for i in range(len(reaction.listOfProducts)):
            species_ref2 = sbmlreaction.createProduct()
            check(species_ref2,                                                  'create product')
            check(species_ref2.setStoichiometry(reaction.prod_stoich[i]),    "assign stochiometric parameter")
            check(species_ref2.setSpecies(reaction.listOfProducts[i]),           'assign product species')
            check(species_ref2.setConstant(True),                                'set "constant" on species ref 2')

    #die Funktion gibt das model als String zurück
    #return writeSBMLToString(document)
    return
#Funktion zum abspeichern der Sbml-Datei in Dateipfad
#Dies kann entweder über den direkten Pfad, das nennen eines Unterordners oder über den Default-Weg
#geschehen. Der Default-Weg erstellt einen Unterordner "sbml-Dateien" in der derzeitigen Arbeitsumgebung
#hierbei wird das regex-Package benutzt, um einen gegeben Dateiname, welcher schon als xml-Datei
#gekennzeichnet wurde, passend zu bearbeiten
def write_in_dir(path=None,filename="sbml-datei",subdir="sbml-dateien"):
    i=0
    p = re.compile("[.]xml")
    if path==None:
        cwd = os.getcwd()
        path = os.path.join(cwd, subdir)  
#falls der Ordner nicht existiert, wird er erstellt
    if not os.path.exists(path):
        os.makedirs(path)
#falls der Dateiname kein ".xml" enthält, wird er angeglichen
    if p.match(filename):
        filename_correct=filename
    else:
        filename_correct=filename+".xml"
#Überprüfung, ob die Datei bereits existiert
    filedirectory=os.path.join(path,filename_correct)
#falls sie existiert, wird ".xml" abgschnitten und der Name in einer Schleife um eine Versionszahl erweitert, 
#bis ein passender Name gefunden wurde    
    if os.path.exists(filedirectory):
        if p.match(filename):
            filename_split=filename.split(".")
#ist ein Punkt im Dateiname enthalten, so wird eine fehlermeldung geworfen
            if len(filename_split)>2:
                print("filename darf keinen \".\" im Namen haben")
                exit()
            filename_core=filename_split[0]
        else:
            filename_core=filename
#existiert bereits eine Datei mit diesem Namen im angegeben Pfad, so wird der Name um eine Versionstahl "(x)" erweitert
        while os.path.exists(filedirectory):
            i +=1
            filename_correct=filename_core+"("+str(i)+").xml"
            filedirectory=os.path.join(path,filename_correct)        
    print(filedirectory)
#letztendlich wird das SBML-Dokument mit dem Dateipfad übergeben und eine SBML-Datei erstellt.   
    writeSBML(document,filedirectory)


getReactionforsbml()
#print(create_model())
create_model()
write_in_dir(filename="corona")


# In[ ]:




