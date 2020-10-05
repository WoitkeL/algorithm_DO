#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pulp
from libsbml import*
import sys
import itertools
import os
import re
import time
from colorama import Fore, Back, Style
from graphviz import Digraph
from contextlib import contextmanager
#import graphviz
@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout
#Reaktion-Klasse bildet Instanzen von Reaktionen mit allen benötigten Informationen
#eine Reaktion benötigt zur initialisierung folgende Parameter:
#Name, Reactantenliste,Produktliste und eine jeweilg zugehörige Stöchiometrie-liste  
class reaction:
    def __init__(self, name, reactants, products, extract_stoich_rea=[], extract_stoich_prod=[],listOfReactions=[]):
        self.always=False
        self.closed=True
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
        
             
        if len(self.listOfReactants)==0:
            self.always=True
            print(self.defined_name+"ist Input")

#Reaktion-Klasse bildet Instanzen von minimalen Reaktionsräumen einer Reaktion und trägt den Namen dieser.
#spezielles set von reaktionen, der dem Abschluss einer bestimmten Reaktion entspricht
#single-reaction-closure
#elementarer reactionsabschluss
#elementary reaction closure
class ERC:
    def __init__(self, lOR_solve, ERC_dict=[], reaction=[], solospecies=[],):
        self.joinable_ERCs=[]
        if reaction !=[]:
            self.defined_name=reaction.defined_name
            ERC_dict[self.defined_name]=self
            self.reactions=[reaction]
            self.species=set()
            for element in reaction.listOfReactants:
                self.species.add(element)
            for element in reaction.listOfProducts:
                self.species.add(element)
            self.eRC_aufstellung(lOR_solve)
            print("ERC erstellt:", end='')
            for element in self.reactions:
                print(element.defined_name, end=' ')
            print()
        else:
            self.defined_name=solospecies
            self.reactions=[]
            self.species={solospecies}
            self.eRC_aufstellung(lOR_solve)
            for reaction in self.reactions:
                print(reaction.defined_name)
                
#Funktion, die über alle Reaktionen iteriert und eine hinzufügt, wenn deren Reaktanten vollständig im ERC enthalten sind
#wenn eine Reaktion hinzugefügt wird, wird die Funktion erneut aufgerufen, um mit aktualisierter Speziesmenge zu vergleichen
    def eRC_aufstellung(self, lOR_solve):
        for checkreaction in lOR_solve:
            if checkreaction not in self.reactions:
                if set(checkreaction.listOfReactants).issubset(self.species):
                    
                    self.reactions.append(checkreaction)
                    self.species.update(checkreaction.listOfProducts)
                    self.eRC_aufstellung(lOR_solve)
                    
                    return
                
    def merge(self,ERC2, lOR_solve):
        self.defined_name=str(self.defined_name)+"+"+str(ERC2.defined_name)
        print(self.defined_name)
        self.species.update(ERC2.species)
        reactionsset=set(self.reactions).union(set(ERC2.reactions))
        self.reactions=list(reactionsset)
        #wenn im System aktive Reaktion getriggert wird, muss Funktion erneut aufgerufen werden mit Produkten der Reaktionen
        self.eRC_aufstellung(lOR_solve)
        
#Funktion die einen für einen ERC überprüft, welche Species nicht hinzugefügt werden dürfen. Dafür werden Zwei Listen 
#mit Specieskombinationen erstellt, die entweder eine im System bereits aktive oder eine im Sytem inaktive Reaktion triggern 
#würden. Da die Lösung der linearen Programierung das Maximum der aktiven Reaktionen liefert, würde das triggern einer inaktiven
#Reaktion, keine Lösung sein. 


#Es gibt 2 Möglichkeiten, die Reaktionen in das Programm einzuspeisen. Wird kein Dateipfad mit einer SBML-Datei gegeben, 
#greift es die im Programmtext manuell gegebenen Reaktionen ab.
def getReaction(path="manual"):
    

    listOfReactions_gR = []
    if path=="manual":
        x1= reaction("r1",["KinU","A"],["KinU","I"],[1,1],[1,1],listOfReactions_gR)
        
        x2=reaction("r2",["I"],["A"],[1],[1],listOfReactions_gR)
        
        x3= reaction("r3",[],["A"],[],[1],listOfReactions_gR)
        
        x4= reaction("r4",[],["A","D"],[],[1,1],listOfReactions_gR)
      
        x5= reaction("r5",["A","B","C"],["C"],[1,1,1],[1],listOfReactions_gR)
 
    else:
#SBML-Reader ist Reader aus LibSBML-Package, wird initialisert
        reader = SBMLReader()
        
        if not os.path.isfile(path):
            print("no file in path found")
            return()
        if reader == None:
            print("no object created")

        doc_extract = reader.readSBMLFromFile(path)
        if doc_extract.getNumErrors() > 0:
            if doc_extract.getError(0).getErrorId() == XMLFileUnreadable:
                print("XMLFileUnreadable")
            elif doc_extract.getError(0).getErrorId() == XMLFileOperationError:
                print("XMLFileOperationError")
                
                
#Im Folgenden, Anwendung einiger Funktionen und Klassen aus libsbml-package:
#Model wird wird aus Sbml-Datei gewonnen
        model_extr=doc_extract.getModel()
#Reaktionsliste wird aus Model gewonnen
        listrea_extract=model_extr.getListOfReactions()
#for schleife für jede einzelne Reaktion
        for i in range (len(listrea_extract)):
            name=listrea_extract.get(i).getId()
            
#sbml.ListOfReactions.get(x) extrahiert SBML.Reaktion mit Attributen ListOfReactants und ListOfProducts            
            extract_rea_list=listrea_extract.get(i).getListOfReactants()
            extract_pro_list=listrea_extract.get(i).getListOfProducts()
            extract_rea_list_species=[]
            extract_pro_list_species=[]
            extract_rea_list_species_stoich=[]
            extract_pro_list_species_stoich=[]
#aus diesen Listen wird die Species mit dem jeweiligen stöchiometrischen Faktor herausgeholt.            
            for j in range (len(extract_rea_list)):
                extract_rea_list_species.append(extract_rea_list[j].getSpecies())
                extract_rea_list_species_stoich.append(extract_rea_list[j].getStoichiometry())
                
            for j in range (len(extract_pro_list)):
                extract_pro_list_species.append(extract_pro_list[j].getSpecies())
                extract_pro_list_species_stoich.append(extract_pro_list[j].getStoichiometry())
                
#Initialisierung der extrahierten Daten via der eigens-implementierten Reaktion-Klasse            
            x= reaction(name,extract_rea_list_species,extract_pro_list_species,extract_rea_list_species_stoich,extract_pro_list_species_stoich,listOfReactions_gR)
            
    return(listOfReactions_gR)    


#Species können manuell als Set übergegeben werden, oder sind alle Species, die in den Reaktionen vorkommen.
#reduziert netzwerk auf entscheidende Funktionen und überprüft auf abgeschlossenheit
def setSpecies(listOfReactions, setspec=None):
    listOfReactions_sS=listOfReactions[:]
    setOfSpecies_sS=set()
#wenn keine Spezies gegeben werden, wird über alle Reaktionen iteriert und ein Species-set geupdated
    if setspec==None:
        for reaction in listOfReactions_sS:
            setOfSpecies_sS.update(reaction.listOfReactants)  
            setOfSpecies_sS.update(reaction.listOfProducts)

    else:
        if not type(setspec) is set:
            print("Speciesset muss Set sein")
            return()
        setOfSpecies_sS = setspec 
        listOfReactions_iterator= listOfReactions_sS.copy()
        
#es wird eine Kopie von listofreactions angefertigt, damit das Grundobjekt in der nächsten schleife
#verändert werden könnnen, ohne dass das schleifenverhalten verändert wird
        for reaction in listOfReactions_iterator:
            if set(reaction.listOfReactants).issubset(setOfSpecies_sS):
                if set(reaction.listOfProducts).issubset(setOfSpecies_sS):
                    reaction.closed=True
                    
                else:
                    reaction.closed=False
                    #setOfSpecies.update(reaction.listOfProducts)#setofSpecies wird um nicht gegebene Species erweitert, um korrekten Umgang für Pulp zu gewährleisten
                    
            else:
                listOfReactions_sS.remove(reaction)
#unmögliche Reaktionen werden aus listOfReactions entfernt

    
    return(listOfReactions_sS,setOfSpecies_sS)

    
def solve_problem(lOR_solve,job="solve", parameter=""):
    ERC_dict={}
    speciesdict={}
    setOfSpecies=set()
        
    for reaction in lOR_solve:
        setOfSpecies.update(reaction.listOfReactants)  
        setOfSpecies.update(reaction.listOfProducts)
    
    for species in setOfSpecies:
        speciesdict[species+'_r']=[]
        speciesdict[species+'_p']=[]    
        
#verlinkt species auf Reaktionen
    for reaction in lOR_solve:
        for species in reaction.listOfReactants:
            speciesdict[species+'_r'].extend([reaction])
        for species in reaction.listOfProducts:
            speciesdict[species+'_p'].extend([reaction])  
#erschafft ERC-Instanz von Reaktionen
    for reaction1 in lOR_solve:
        ERC(lOR_solve, ERC_dict , reaction1) 

    
    if job=="getminimumcircle":
        solve_dist_org=pulp.LpProblem("Solver Dist Org",pulp.LpMinimize)
    else:
        solve_dist_org=pulp.LpProblem("Solver Dist Org",pulp.LpMaximize)
        
    # Initialisierung der benötigten Variablen: Rbool beschreibt, ob eine Reaktion ausgeführt wird(rbool_r=1) oder nicht(rbool_r2=0)
    # reac und spec beschreiben die Stöchiometrie der Reaktionen und  der Überschüssigen Species
    # die Dictionaries verweisen von den Reaktions- und Speciesnamen auf die jeweiligen Pulp-Objekte
   
    
    listOfReactionsname = [i.defined_name for i in lOR_solve]
    Rbool=pulp.LpVariable.dicts("Rbool",listOfReactionsname,lowBound=0, upBound=1,cat="Integer")
    reac=pulp.LpVariable.dicts("r",listOfReactionsname,lowBound=0)
    spec=pulp.LpVariable.dicts("s",setOfSpecies,lowBound=0)
    
    #check
    print(Rbool)
    print(reac)
    print(spec)

    #objective Funktion
    objectfunction_vektor=[]
    

    #hier wird nach der maximalen Reaktivität des Systems optimiert
    revenue=pulp.lpSum(Rbool.values())
    
    #doch wenn nach minimum_circle gesucht wird, wird Zielfunktion überschrieben
    if job=="getminimumcircle":
        try:
            solve_dist_org+=Rbool[parameter]==1
        except KeyError: 
            print("gegebene Reaktion existiert nicht")
            return
    
    #gewünschte Zielfunktion wird in pulp integriert
    solve_dist_org+=revenue

    

    #constraints
    
    # die Reaktionen werden durch die Änderung der Speciesanzahl für jede Species eingegeben. Eine Reaktion a->b wird eingeben als: 
    # a=-R und b=R dafür werden 2 Listen(edukt, produkt) für jede Species angelegt, welche am ende mit summiert und eingefügt werden
    for key, element in spec.items():
        educt=[]
        product=[]
        
        for einzelreaktion in speciesdict[key+'_r']:
            index_st=einzelreaktion.listOfReactants.index(key)
            stoich=einzelreaktion.reac_stoich[index_st]    
            for i in range (int(stoich)): 
                educt.append(reac[einzelreaktion.defined_name])
                
        for einzelreaktion in speciesdict[key+'_p']:
            index_st=einzelreaktion.listOfProducts.index(key)   #da stöchiometrie des stoffes nicht in speciesdict übergeben 
            stoich=einzelreaktion.prod_stoich[index_st]    #wird, greift man index des stoffes in der Reaktion ab und greift
            for i in range (int(stoich)):                       #dann auf die stöchiometrie dieses Index für die Reaktion zu
                product.append(reac[einzelreaktion.defined_name])
        
        
            
            
        #lpSum fasst Elemente der Liste als Ausdruck für pulp zusammen
        educt_sum=pulp.lpSum(educt)
        product_sum=pulp.lpSum(product)
        
        #einzelne Aufstellungen aller Gleichungen für Speziesänderung
        solve_dist_org+= element==product_sum-educt_sum     


    # um das Problem nicht als mixed-LP-Problem mit Integer-cuts aufzulösen, wird Rbool <= Reaktion <= Rbool*1000 gesetzt
    for key, element in reac.items():
        solve_dist_org+=Rbool[key]<=element
        solve_dist_org+=element<=Rbool[key]*1000


    #mit den Rbool-werten, werden die minimalen ERC's als Constraints eingefügt. Wenn eine Reaktion R1 mit all seinen 
    # enthaltenen Species eine Reaktion R2 triggered, so muss Rbool_R1<= Rbool_R2 sein
    for reaction1 in lOR_solve:
        separable_reactants=len(reaction1.listOfReactants)
        
    #wird eine Reaktion immer überall ausgeführt, so kommen die Produkte überall vor -> trennbare Reaktanten=-1        
        for reactant in reaction1.listOfReactants:
            for reaction in speciesdict[reactant+"_p"]:
                if reaction.always:
                    separable_reactants-=1
                    break

        if not job=="getminimumcircle":
            if (separable_reactants<2) and (set(reaction1.listOfReactants).issubset(setOfSpecies)):
                if not reaction1.closed:
                    print("stop solve_problem: speciesset is not closed, reaction "+reaction1.defined_name+" happens")
                    return(([0],{0}))
                solve_dist_org+= Rbool[reaction1.defined_name]==1
        
        if not reaction1.closed:
            solve_dist_org+= Rbool[reaction1.defined_name]==0
            
#folgender Befehl gibt die Constraints für die ERC's. gibt ein
#da erstes Element mit sich selbst verglichen werden würde, muss es aus der Iteration entfernt werden, deswegen wird x+1 
#benutzt und die Iterationslänge um ein verringert
        for x in range (len(ERC_dict[reaction1.defined_name].reactions)-1):
            solve_dist_org+= Rbool[reaction1.defined_name]<= Rbool[ERC_dict[reaction1.defined_name].reactions[x+1].defined_name]
    
    solve_dist_org.solve()
        
    #mit diesem Befehl, kann man sich alle gegebenen Daten des LpProblems ausgeben lassen
    if job=="see_constraints":
        print(solve_dist_org)
    
    #statusanzeige des problems:
    print(pulp.LpStatus[solve_dist_org.status])
    
    if (pulp.LpStatus[solve_dist_org.status]=="Infeasible"):
        print("no Solution for Problem")
        return([0],{0})
    
    #wandelt daten in liste mit namen von aktiven Reaktionen
    p2 = re.compile("Rbool")
    bool_reaction_list=[]
    for variable in solve_dist_org.variables():
        print("{} = {}".format(variable.name,variable.varValue))
        if p2.match(variable.name) and variable.varValue==1:
            bool_reaction_list.append(variable.name[6:])
    
    
    return(bool_reaction_list, ERC_dict)
        
   


    ##naives clustern von elementaren ERC's
def minimalERCs(bool_reaction_list_mERC, ERC_dict ,lOR_mERC, setOfSpecies="all"):
    #funktion gibt Booleanwert, ob inaktive Reaktionen durch zusammenfügen aktiviert werden. True= keine neuen Reaktionen, die
    #nicht im System vorkommen
    def checktrigger(species_vereint,gem_reactions,checkERC):
        global vereinigung_ende
        for reaction in lOR_mERC:
            
            if reaction not in gem_reactions:
                if set(reaction.listOfReactants).issubset(species_vereint):
                    if reaction not in bool_reactions:
                        return(False)
                        
                    else:
        #wenn im System aktive Reaktion getriggert wird, muss Funktion erneut aufgerufen werden mit Produkten der Reaktionen
                        species_vereint.update(set(reaction.listOfProducts))
                        
                        gem_reactions.add(reaction)
                        return(checktrigger(species_vereint,gem_reactions,checkERC))
        
        vereinigung_ende=len(species_vereint)
        return(True)
    
    def search_join():
        #negativer bester Join-wert wird initialisiert
        bestjoin_value=-10
        for element in min_ERClist: 
            global vereinigung_ende
            vereinigung_ende=0
            #Kopie wird angefretigt, da durch min_ERClist iteriert wird und beim zusammenbringen/mergen von 2 ERC's einer 
            #entfernt wird. (keine Indexfehler)
            min_ERClist_copy=min_ERClist.copy()
            #muss nicht mit sich selbst verglichen werden, deswegen wird element aus der Kopie entfernt
            min_ERClist_copy.remove(element)
            print()
            print(Style.RESET_ALL)
            print(element.defined_name)
            
            #für Heuristik wird im normal nach folgendem Optimiert: die geringste Anzahl and Spaces wird erzielt, wenn beim zusammen-
            #bringen mit den unkompliziertesten merge-operationen begonnen wird. Ein kleinerer ERC ist meistens weniger kompliziert
            # als ein großer ERC, deswegen wird bei der Überprüfung das mergen von 2 ERC's mit vielen gemeinsamen Species als
            #positiv bewertet(+1 pro gemeinsame species) und das entstehen von species, die vorher in keiner der beiden ERC's war, als
            #negativ (-1 pro weitere species)
            
            for checkERC in min_ERClist_copy:
                
                species_vereint=element.species.union(checkERC.species)
                summe_species=len(element.species)+len(checkERC.species)
                gem_reactions=set(element.reactions).union(set(checkERC.reactions))
                
                #printed mögliche merges grün und unmögliche merges rot
                if checktrigger(species_vereint,gem_reactions,checkERC):
                    element.joinable_ERCs.append(checkERC)
                    print(Fore.GREEN +element.defined_name+" + "+checkERC.defined_name+"  ", end='')
                    
                    #berechung der werte für positvies und negatives bewerten
                    value=summe_species-vereinigung_ende
                    print(value)
                   
                    #merkt sich besten wert und dazugehörige Spaces über alle möglichen merge-operationen
                    if bestjoin_value<value:
                        bestjoin_value=value
                        bestERC1=element
                        bestERC2=checkERC
                else:
                    print(Fore.RED +element.defined_name+" + "+checkERC.defined_name)
            print(len(element.joinable_ERCs))
        #wenn es keine möglichen merge-operationen gibt, verlässt es die Schleife, ansonsten wiederholt es "search_join()"
        if bestjoin_value!=-10:
            bestERC1.merge(bestERC2, lOR_mERC)
            print("merge"+ bestERC2.defined_name+ "and"+ bestERC1.defined_name)
            min_ERClist.remove(bestERC2)
            search_join()
        else: 
            #Ausgabe der Lösung
            for element in min_ERClist:
                print(Style.RESET_ALL)
                print("merged ERC's:",end='')
                print(element.defined_name)
                print("active reactions:",end='')
                for reaction in element.reactions:
                    print(reaction.defined_name+", ", end='')
                print()
                print("species in space:",end='')
                print(element.species)
            
    #Funktion muss getrennt angelegt werden, um danach zu sortieren
    def sortfunction(elem):
        return len(elem.reactions)
    
    
    #min_ERClist ist Objekt, auf dem die merge-Operationen ausgeführt werden und der zum Ende ausgegeben wird
    min_ERClist=[]
    bool_reactions=set()
    
    
    #wandelt liste von string zu geeigneten objekten um
    for element in bool_reaction_list_mERC:
        min_ERClist.append(ERC_dict[element])
        bool_reactions.update(ERC_dict[element].reactions)
    
    
    #vorüberprüfung, ob aktive ERC's Teilelemente anderer aktiver ERC's sind.
    #dabei werden Kopien der ERC-Liste angefertigt um durch diese zu iterieren und dabei Elemente zu entfernen ohne dass 
    #Indexfehler entstehen
    min_ERClist.sort(key=sortfunction, reverse=False)
    min_ERCiterator1=min_ERClist.copy()
    min_ERCiterator2=min_ERClist.copy()
    for element1 in min_ERCiterator1:
        if len(element1.reactions)>1:
            print("compare if ERC's are subset of ERC " +str(element1.defined_name))
            for element2 in min_ERCiterator2:
                if element2 != element1:
                    #print("vergleich: ERC "+str(element2.defined_name)+"<= ERC "+str(element1.defined_name))
                    if element2.reactions[0] in element1.reactions:
                        print("remove "+element2.defined_name)
                        try:
                            min_ERClist.remove(element2)
                            min_ERCiterator1[min_ERCiterator1.index(element2)].reactions=[]
                        except ValueError:
                            pass
            #2ter iterator wird aktualisiert um bereits gelöschte ERC nicht doppelt zu überprüfen
            min_ERCiterator2=min_ERClist
            
    #überprüfung, ob alle species in ERC's enthalten sind. Falls eine Species in keinem ERC vorkommt, wird jweils ein ERC
    #mit dieser Species erstellt
    new_ERCs=[]
    if setOfSpecies=="all":
        setOfSpecies=set()
        for reaction in lOR_mERC:
            setOfSpecies.update(reaction.listOfReactants)  
            setOfSpecies.update(reaction.listOfProducts)
        
    for species in setOfSpecies:
        check=False
        for element in min_ERClist:
            if species in element.species:
                check=True
        if check==False:
            #Einzelspezies-ERC werden in liste eingefügt und am ende der hauptliste hinzugefügt
            new_ERCs.append(ERC(lOR_mERC, solospecies=species))
    
    min_ERClist.extend(new_ERCs)
            
    for element in new_ERCs:  
        print("Einzelspecies ERC:"+element.defined_name)
    print("active ERC's are:", end='')
    for element in min_ERClist:
        print(element.defined_name, end=', ')
    print()
    #alle inaktiven Reaktionen angeben
    print("not active reactions:", end='')
    for reaction in lOR_mERC:
        if reaction not in bool_reactions:
            print(reaction.defined_name, end=', ')
    print()
    
    search_join()

#funktion legt alle elemente zusammen und überprüft, ob Lösung der DO auch Organisation ist.
#Funktion "minimalERCs" kommt auch auf die Lösung, wenn dies vorliegt, doch benötigt deutlich mehr Zeit
def isorg(lOR_iterator, bool_reaction_list_isorg, ERCdic_isorg, species_isorg):
    if bool_reaction_list_isorg!=[0]:
        allreactants=set(species_isorg).copy()
        bool_reactions_isorg=set()
        for element in bool_reaction_list_isorg:
            bool_reactions_isorg.update(set(ERCdic_isorg[element].reactions))
        for reaction in lOR_iterator:
            if reaction not in bool_reactions_isorg:
                if set(reaction.listOfReactants).issubset(allreactants):
                    return(False)
        return(True)        
    else: return("no Solution")       
    

    
def gethasse(info, given_species=None):
    #funktion für kanten eines knoten, als argument wird der knoten oder ein zu untersuchendes subset eines knotens gegeben.
    def create_edges(knot, species_to_cover, checked=set()):
        if len(species_to_cover)>1:
            for checkset in itertools.combinations(species_to_cover ,len(species_to_cover)-1):
                def inner():
                
                    diff=len(knot)-len(checkset)       
                    if diff==1:
                        if checkset in nodedict.keys():
                            dot.edge('node'+str(number_of_nodes), nodedict[checkset], arrowhead = "none")
                        else:
                            create_edges(knot, checkset,checked)

                    else:
                        for x in range (diff-1):
                            y=len(knot)-(x+1)
                            for checkset2 in itertools.combinations(knot ,y):
                                
                                if checkset2 in nodedict.keys():

                                    if set(checkset).issubset(set(checkset2)):
                                        return


                        if checkset in nodedict.keys():
                            dot.edge('node'+str(number_of_nodes), nodedict[checkset], arrowhead = "none") 

                        else:


                            create_edges(knot, checkset, checked)
                    
                inner()
        else:
            if len(species_to_cover)==1:
                
                if () in nodedict.keys():
                    dot.edge('node'+str(number_of_nodes), nodedict[()], arrowhead = "none")
            return()
       
    lOR_sS=[]   
    setOfSpecies=set()
    if type(info)==str:
        lOR_gh=getReaction(info)
    else:
        lOR_gh=info[:]
        
    if given_species==None:
        lOR_gh2,setOfSpecies= setSpecies(lOR_gh)
    else:
        if type(given_species)==set:
            lOR_gh2, setOfSpecies= setSpecies(lOR_gh,given_species)
        else: print("speciesset is wrong")    

    
    number_of_nodes=0
    dot = Digraph(strict=True,comment='Hasse_Diagram')
    
    #dictionary wird eingeführt: hat unter key von specieskombination den verweis auf knoten-objekt
    nodedict={}

    for x in range(len(setOfSpecies)+1):
        for element in itertools.combinations(setOfSpecies, x):
#output wird supressed um anzeige einfacher zu machen
            with suppress_stdout():
                lOR_iterator,setOfSpecies_iterator=setSpecies(lOR_gh2,set(element))
            with suppress_stdout():
                bool_reaction_list_iterator, ERC_dict_iterator=solve_problem(lOR_iterator)
            if bool_reaction_list_iterator!=[0]:
                print(element, end='') 
                print("has reactions:", end=' ') 
                for reaction in bool_reaction_list_iterator:
                    print(reaction, end='')
                print()    
                    
                number_of_nodes+=1    
                name=repr(element)
                name=name.replace(",)",")")
                name=name
                
                #je nach dem ob do auch O ist, wird knoten markiert
                if isorg(lOR_iterator,bool_reaction_list_iterator, ERC_dict_iterator,element):
                    dot.node('node'+str(number_of_nodes), name, shape='box')
                else:
                    dot.node('node'+str(number_of_nodes), name)

                nodedict[element]=str('node'+str(number_of_nodes))
                speciesdiff=1
                #funktionsaufruf für knoten
                create_edges(element, element,set())
                
    
    print(nodedict)
    dot.render('test-output/Hasse_Diagram.gv', view=True)      
    print(dot.source)  
    

    #zusammenfassung der wichtigsten befehle um zu erkennen ob set eine do ist
def isDO(info, species=None, job="solve", parameter=""):    
    if type(info)==str:
        lOR_isDO=getReaction(info)
    else:
        lOR_isDO=info[:]
        
    if species==None or species=="all":
        lOR_sS,setOfSpecies= setSpecies(lOR_isDO)
        bool_reaction_list, ERC_dict=solve_problem(lOR_isDO, job, parameter)
    else:
        if type(species)==set:
            lOR_sS,setOfSpecies= setSpecies(lOR_isDO, species)
            bool_reaction_list, ERC_dict=solve_problem(lOR_sS, job, parameter)
        else: print("speciesset is wrong")
            
    if bool_reaction_list!=[0]:
        print("is DO")
        if isorg(lOR_isDO,bool_reaction_list, ERC_dict,setOfSpecies):
            print("is O")
            
    #zusammenfassung der wichtigsten befehle um zu erkennen ob set eine do ist und nach der minimalen anzahl von 
    #compartments zu suchen
def FindDO(info, species=None, job="solve", parameter=""):
    if type(info)==str:
        lOR_findDO=getReaction(info)
    else:
        lOR_findDO=info[:]
        
    if species==None or species=="all":
        lOR_sS,setOfSpecies= setSpecies(lOR_findDO)
        bool_reaction_list, ERC_dict=solve_problem(lOR_sS, job, parameter)
    else:
        if type(species)==set:
            lOR_sS,setOfSpecies= setSpecies(lOR_findDO,species)
            bool_reaction_list, ERC_dict=solve_problem(lOR_sS,job, parameter)
        else: 
            print("speciesset is wrong")
            return()
            
    if bool_reaction_list!=[0]:
        print("is DO")
        minimalERCs(bool_reaction_list, ERC_dict, lOR_findDO, setOfSpecies)


    
#Orders for simple execute:                   
#lOR=getReaction("path")   
#give the path for sbmldata like this on windows: "C:/uni/python/sbml-dateien/final_daten(7).xml"
#lOR,setOfSpecies=setSpecies(lOR)     
#you can alter the speciesset like this: lOR,setOfSpecies=setSpecies(lOR,{"a","b","l","m"})
#bool_reaction_list, vektordict=solve_problem()
#benutzt die Werte:bool_reaction_list,vektordict,setOfSpecies
#minimalVektors()

#using isdo and finddo: with either path or lor and either speciesset or none
#you can also directly put parameters for solve-Problem() in FindDO
#isDO(lOR,{"a","b","e","e2","f","g","h","i","j","k","l","m"})

#gethasse with path or lor and either speciesset or none
#gethasse(path)


# In[ ]:




