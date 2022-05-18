# -*- coding: utf-8 -*-
from transition import *
from state import *
import os
import copy
from sp import *
from parser import *
from itertools import product
from automateBase import AutomateBase



class Automate(AutomateBase):
        
    def succElem(self, state, lettre):
        """State x str -> list[State]
        rend la liste des états accessibles à partir d'un état
        state par l'étiquette lettre
        """
        successeurs = []
        # t: Transitions
        for t in self.getListTransitionsFrom(state):
            if t.etiquette == lettre and t.stateDest not in successeurs:
                successeurs.append(t.stateDest)
        return successeurs


    def succ (self, listStates, lettre):
        """list[State] x str -> list[State]
        rend la liste des états accessibles à partir de la liste d'états
        listStates par l'étiquette lettre
        """
	successeurs = []
        # t: Transitions
	for l in listStates:
		for t in self.getListTransitionsFrom(l):
        		if t.etiquette == lettre and t.stateDest not in successeurs:
        	        	successeurs.append(t.stateDest)
	
        return successeurs




    """ Définition d'une fonction déterminant si un mot est accepté par un automate.
    Exemple :
            a=Automate.creationAutomate("monAutomate.txt")
            if Automate.accepte(a,"abc"):
                print "L'automate accepte le mot abc"
            else:
                print "L'automate n'accepte pas le mot abc"
    """
    @staticmethod
    def accepte(auto,mot) :
        """ Automate x str -> bool
        rend True si auto accepte mot, False sinon
        """
	#l:list[State]
	l=auto.listStates
	# s:str
	for s in mot:
		l=auto.succ(l,s)
	#e:State
	for e in l:
		if e in auto.getListFinalStates():
			return True
	return False

    @staticmethod
    def estComplet(auto,alphabet) :
        """ Automate x str -> bool
         rend True si auto est complet pour alphabet, False sinon
        """
	#l:list[State]
	l=auto.listStates
	#e:State
	for e in l:
		#a:str
		for a in alphabet:
			if (len(auto.succElem(e,a))==0):
				return False
        return True 


        
    @staticmethod
    def estDeterministe(auto) :
        """ Automate  -> bool
        rend True si auto est déterministe, False sinon
        """
	#l:list[State]
	l=auto.listStates
	#a:list[str]
	a=auto.getAlphabetFromTransitions()
	#e:State
	for e in l:
		for s in a:
			if (len(auto.succElem(e, s))>1):
				return False
        return True
        

       
    @staticmethod
    def completeAutomate(auto,alphabet) :
        """ Automate x str -> Automate
        rend l'automate complété d'auto, par rapport à alphabet
        """
	  #si l'automate est complet on le renvoie
        if auto.estComplet(auto,alphabet):
            return auto
        
        #sinon on copie l'automate et on y ajoute un état puit
        auto1=copy.deepcopy(auto)
	#letat:list[State]
        letat=auto1.listStates
        i=0
        for s in letat:
            if s.id>i:
                i=s.id
        # puits : State
        puits = State(i+1,False,False)
        auto1.addState(puits)
        letat=auto1.listStates
        
        for s in letat:
            for l in alphabet:
                if auto1.succElem(s,l)==[]:
                    # t1 : Transition
                    t1 = Transition(s,l,puits)    
                    auto1.addTransition(t1)
        return auto1
  
   

    @staticmethod
    def determinisation(auto) :
        """ Automate  -> Automate
        rend l'automate déterminisé d'auto
        """
	if auto.estDeterministe(auto):
		return auto
	alphabet=auto.getAlphabetFromTransitions()
        sliste=[auto.getListInitialStates()] #sliste: List[List[State]] (groupes d'états qui constituront les futurs états du nouvel automate)
	temp=[]		#temp: List[List[State]] (aide temporaire pour récupérer les listes d'états à mettre dans StatesToTreat)
	listestate=[] 	#listestate:List[str] 	 (contiendra les futurs états)
	tliste=[] 	#tliste:List[Transition] (Contiendra les Transitions du futur automate)
        ok=False
        
        while not ok:
            for s in sliste:
                for a in alphabet:
                    suivant=auto.succ(s,a)
                    if (suivant not in sliste) and (len(suivant)>0): 
                        temp.append(suivant)
                if len(temp)==0 or (len(temp)==1 and temp[0]==sliste[len(sliste)-1]):
                    ok=True
                for t in temp:
                    if t not in sliste:
                        sliste.append(t)
                temp=[]
        #complete listestate:
        i=0
        for s in sliste:
            initial=False
            final=False
            etat="{"
            for st in s: 
                if st.fin : 
                    final= True 
                if st.init :
                    initial=True
                etat+=" "+str(st.id)
            etat+="}"
            nouveau=State(i,initial,final,etat)
            i=i+1
            listestate.append(nouveau)
        #complete tliste:
        for s in sliste:
            for a in alphabet:
                suiv=auto.succ(s,a)
                #debut
                deb="{"
                for st in s:
                    deb=deb+" "+str(st.id)
                deb+="}"
                for n in listestate:
                    if n.label==deb:
                        debut=n
                #fin
                fin="{"
                for sv in suiv:
                    fin+=" "+str(sv.id)
                fin+="}"
                for n in listestate:
                    if n.label==fin:
                        arrivee=n
                if len(deb)>2 and len(fin)>2:
                    t=Transition(debut,a,arrivee)
                    tliste.append(t)
        nauto=Automate(tliste,listestate)
        return nauto
	
        
    @staticmethod
    def complementaire(auto,alphabet):
        """ Automate -> Automate
        rend  l'automate acceptant pour langage le complémentaire du langage de a
        """
	nvAuto=copy.deepcopy(auto)
	nvAuto=nvAuto.completeAutomate(nvAuto,alphabet)
	nvAuto=nvAuto.determinisation(nvAuto)
	for s in nvAuto.listStates:
		if s.fin:
			s.fin=False
		else:
			s.fin=True
        return nvAuto
    
    @staticmethod
    def EliminerInutile(auto):
	""" Automate  -> Automate
        elimine les etats qui ne sont inutiles de l'automate
        """ 
	"""U=auto.getListFinalStates()
	alphabet=auto.getAlphabetFromTransitions()
	for s in auto.listStates :
		for a in alphabet :
			for k in auto.succ(s,a)
				if K in U :
					U.append(K)"""
	nvAuto=copy.deepcopy(auto)
	alphabet=auto.getAlphabetFromTransitions()
        sliste=[auto.getListFinalStates()] 
	print(sliste)
	temp=[]	
	listestate=[]
	ok=False
        while not ok:
            for s in auto.listStates :
                for a in alphabet:
                    suivant=auto.succElem(s,a)
                    if (suivant in sliste) and (len(suivant)>0): 
                        temp.append(s)
                if len(temp)==0 or (len(temp)==1 and temp[0]==sliste[len(sliste)-1]):
                    ok=True
                for t in temp:
                    if t not in sliste:
                        sliste.append(t)
                temp=[]
	print(sliste)
        """for s in sliste:
            initial=False
            final=False
            for st in s: 
                if st.fin : 
                    final= True 
                if st.init :
                    initial=True
                nouveau=State(st.id,initial,final)
                listestate.append(nouveau)"""

	for s in nvAuto.listStates:
		rem=True
		for s1 in listestate:
			if (s.id == s1.id) :
				rem=False	
		if rem :		
			nvAuto.removeState(s)
	return nvAuto 
    
    @staticmethod
    def intersection2(auto0, auto1):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'intersection des langages des deux automates
        """
	#on construit les automates complementaire de auto1 et auto0
	alphabet0=auto0.getAlphabetFromTransitions()
	nvAuto0=auto0.complementaire(auto0,alphabet0)
	alphabet1=auto1.getAlphabetFromTransitions()
	nvAuto1=auto1.complementaire(auto1,alphabet1)
	#on construit l'automate qui accepte l'union de auto1 et auto0
	nvAuto=auto.union(nvAuto0,nvAuto1)
	nvAuto=nvAuto.EliminerNonAtteint(nvAuto)
	#nvAuto=nvAuto.EliminerInutile(nvAuto)
	#on  construit l'autome complementaire de nvAuto
	alphabet=nvAuto.getAlphabetFromTransitions()
	resAuto=nvAuto.complementaire(nvAuto,alphabet) 
        return resAuto

    @staticmethod
    def intersection(auto0, auto1):
	""" Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'intersection des langages des deux automates
        """ 
	nvAuto0=copy.deepcopy(auto0)
	nvAuto1=copy.deepcopy(auto1)
	nvAuto= Automate([])
	alphabet=[]
	for a in nvAuto0.getAlphabetFromTransitions() : 
		if a in nvAuto1.getAlphabetFromTransitions() :
			alphabet.append(a) 
	liste0=nvAuto0.listStates 
	liste1=nvAuto1.listStates
	sliste=[]
	sliste2=[]
	ch=""
	ch1=""
	for s1 in liste1:
		for s0 in liste0 :
			sliste += [(s0, s1)]		
	depart = len(liste1)	
	for etats in sliste :
		s0, s1 = etats
		stateSrc = nvAuto.getState(s0.id *depart + s1.id)
		if stateSrc == None : 
			Ini=False
			Fin=False
			if s0.init and s1.init :
				Ini=True
			if s0.fin and s1.fin :
				Fin=True 
			ch=str(s0.id) + "_" + str(s1.id)
			stateSrc = State(s0.id * depart + s1.id,Ini,Fin, label= ch)
		for a in alphabet :
			states0 = nvAuto0.succElem(s0,a)
			states1 = nvAuto1.succElem(s1,a)
			for st1 in states1:
				for st0 in states0 :
					sliste2+= [(st0, st1)]	
				for etat2 in sliste2 :
					st0, st1 = etat2
					Id= st0.id * depart + st1.id
					stateDest = nvAuto.getState(st0.id * depart + st1.id)
					if stateDest == None : 
						Ini1=False
						Fin1=False
						if st0.init and st1.init: 
							Ini1=True
						if st0.fin and st1.fin :
							Fin1 =False 
						ch1= str(st0.id) + "_" + str(st1.id)
						stateDest = State(st0.id * depart + st1.id, Ini1, Fin1, label= ch1)				
					nvAuto.addTransition(Transition(stateSrc, a, stateDest))
					nvAuto=nvAuto.EliminerNonAtteint(nvAuto)
	return nvAuto
    
    def getState(self,id):	
	"""int->State
	rend, s'il existe, le state ayant pour "id" notre paramètre id.
	"""
	for  s in self.listStates:
		if s.id==id:
			return s
	return None
   
    @staticmethod
    def union (auto0, auto1):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'union des langages des deux automates
        """
	
	if len(auto0.listStates)==0: return copy.deepcopy(auto1)
	if len(auto1.listStates)==0: return copy.deepcopy(auto0)
	nvAuto=copy.deepcopy(auto0)
	depart=len(nvAuto.listStates)
	for s in auto1.listStates:
		nvAuto.addState(State(s.id+depart, s.init,s.fin))
	for t in auto1.listTransitions:
		stateSrc=nvAuto.getState(t.stateSrc.id+depart)
		stateDest=nvAuto.getState(t.stateDest.id+depart)
		nvAuto.addTransition(Transition(stateSrc, t.etiquette, stateDest))
	nvstate=State(len(nvAuto.listStates),True,False)
	nvAuto.addState(nvstate)
	for s in nvAuto.getListInitialStates():
		for a in nvAuto.getAlphabetFromTransitions():
			if s.id != nvstate.id:
				nt=Transition(nvstate,a,s)
				nvAuto.addTransition(nt)
		if s.id != nvstate.id: s.init=False
	return nvAuto
   
       

    @staticmethod
    def concatenation (auto1, auto2):
        """ Automate x Automate -> Automate
        rend l'automate acceptant pour langage la concaténation des langages des deux automates
        """
	alphabet=auto1.getAlphabetFromTransitions()
	auto_1=copy.deepcopy(auto1)
	auto_2=copy.deepcopy(auto2)
        #sf:State (etats finaux de auto1)
	#si:State  (etats initiaux de auto2)
	sf=auto_1.getListFinalStates ()
	si=auto_2.getListInitialStates ()
	#autocopy=copy.deepcopy(auto0)
	#temp: List[Transition] (liste Temporaire des transitions des anciens automates)
	#idmin:int
	idmin=len(auto_1.listStates)
	#liste_trans: List[Transition] (liste de transition du futur automate)
	liste_trans=[] 
	#liste_state: List[State] (liste d'etat du futur automate)
	liste_state=[]
	for s1 in auto_1.listStates:
		liste_state.append(s1)
		temp=auto_1.getListTransitionsFrom(s1)
		for t1 in temp:
			if t1 not in liste_trans: 
				liste_trans.append(t1)
			if (not (s1.fin)) and (t1.stateDest in sf):
				for state in si:
					t4=Transition(s1,t1.etiquette,state)
					if t4 not in liste_trans: 
						liste_trans.append(t4)
			if (s1.fin):
				s1.fin=not s1.fin
				for a in alphabet:
					for state2 in si:
						t3=Transition(s1,a,state2)
						liste_trans.append(t3)
		temp=[]
	for s2 in auto_2.listStates:
		if (not auto_2.accepte(auto_1,"")) and (s2 in si):
			s2.init=False
		s2.id=idmin
		s2.label=idmin
		liste_state.append(s2)
		idmin=idmin+1
		temp=auto_2.getListTransitionsFrom(s2)
		for t2 in temp:
			if t2 not in liste_trans:
				liste_trans.append(t2)
	
	nvAuto=Automate(liste_trans,liste_state)
			
        return nvAuto
        
       
    @staticmethod
    def etoile (auto):
        """ Automate  -> Automate
        rend l'automate acceptant pour langage l'étoile du langage de a
        """
	nv_id=len(auto.listStates)
	nvAuto=copy.deepcopy(auto)
	sliste_finaux=nvAuto.getListFinalStates()
	sliste_init=nvAuto.getListInitialStates()
	alphabet=auto.getAlphabetFromTransitions()
	for s in sliste_finaux:
		for si in sliste_init:
			for a in alphabet:
				nt=Transition(s,a,si)
				nvAuto.addTransition(nt)
	nvState=State(nv_id,True,True)
	nvAuto.addState(nvState)
	for si in sliste_init:
		for a in alphabet:
			nvt=Transition(nvState,a,si)
			nvAuto.addTransition(nvt)
		si.init=False
	#for si in sliste_init: si.init=False
        return nvAuto

	
#_____________________________________________________________________________________________________
####Exercice 2.1
print("		EXERCICE 2")

###Question 1
print("Question 1.1:")

##création d'états
#s0 : State
s0 = State (0,True,False)
# s1 : State
s1 = State(1, False, False)
# s2 : State
s2 = State(2, False, True)
## cr ́eation de transitions
# t1 : Transition
t1 = Transition(s0,"a",s0)
# t2 : Transition
t2 = Transition(s0,"b",s1)
# t3 : Transition
t3 = Transition(s1,"a",s2)
# t4 : Transition
t4 = Transition(s1,"b",s2)
# t5 : Transition
t5 = Transition(s2,"a",s0)
# t6 : Transition
t6 = Transition(s2,"b",s1)
# liste : list[Transition]
liste = [t1,t2,t3,t4,t5,t6]
## creation de l’automate
# auto : Automate
auto = Automate(liste)
#print(auto)
#auto.show("A_ListeTrans")



#--------------------------------------------------------------------------
##Question 2
print("Question 1.2:")

auto1= Automate(liste, [s0,s1,s2])
#print(auto1)
#auto1.show("A_ListeTrans2")



#--------------------------------------------------------------------------
##Question 3
print("Question 1.3:")

# automate fichier : Automate
automate = Automate.creationAutomate("auto.txt")
#print(automate)
#automate.show("A_ListeTrans3")

#_____________________________________________________________________________________________________
###Exercice 2.2

##Question 1
print("Question 2.1:")

# t : Transition  
t  = Transition (s0,"a",s1)

auto.removeTransition(t)
#auto.show("A_ListeTrans_bis0")
auto.removeTransition(t1)
#auto.show("A_ListeTrans_bis")
auto.addTransition(t1)
#auto.show("A_ListeTrans_bis1")


#--------------------------------------------------------------------------
##Question 2
print("Question 2.2:")

auto.removeState(s1)
#auto.show("Auto_removeState")

auto.addState(s1)
#auto.show("addStates1")
# s3 : State
s3 = State(0,True,False)
auto.addState(s3)
#auto.show("addState")
#On voit à l'affichage que l'etat s1 d'identifiant 1 est rajouté sans aucune transition avec les autres états et le nouvel état s3 est invisible.

#--------------------------------------------------------------------------
##Question 3
print("Question 2.3:")
print("Liste des transitions depuis l'état 0 de auto1:")
print(auto1.getListTransitionsFrom(s0))

#_____________________________________________________________________________________________________
###Exercice 3
print("		EXERCICE 3")
##Question 1
print("Question 1:")
print("on affiche succElem de s0 et succ de [s0,s1]")
print(auto1.succElem(s0,"a"))
print(auto1.succ([s0,s1],"a"))

#--------------------------------------------------------------------------
##Question 2
print("Question 2:")
print("On teste notre fonction accepte sur l'automate: auto1 avec le mot: 'aba'") 
print(auto1.accepte(auto1,"aba"))
assert(auto1.accepte(auto1,"abbb")==False)

#--------------------------------------------------------------------------
##Question 3
print("Question 3:")
print(auto1.listStates)
print("Testons notre fonction estComplet")
assert(auto1.estComplet(auto1,"ab")==True)
assert(auto1.estComplet(auto1,"abcfhki")==False)

#--------------------------------------------------------------------------
##Question 4
print("Question 4:")
print("Testons notre fonction estDeterministe")
print(auto1.estDeterministe(auto1))
assert(auto1.estDeterministe(auto1)==True)

#--------------------------------------------------------------------------
##Question 5
print("Question 5:")
print("auto1 est complète?")
print(auto1.estComplet(auto1,"aba"))
auto1.removeTransition(t5)
#auto1.show("a_listeTranstest")
print("Après avoir enlevé une transition à notre automate verifions qu'elle n'est plus complète:")
print(auto1.estComplet(auto1,"aba"))

autoc = auto1.completeAutomate(auto1,"ab")
print("on complète notre automate")
print(autoc.estComplet(autoc,"aba"))
#autoc.show("A_ListeTrans_copie")



#_____________________________________________________________________________________________________
###Exercice 4
print("		EXERCICE 4")

#determinisation
print("\nDeterminisation\n")
#t7 : Transition
t7=Transition(s1,"a",s1)
auto1.addTransition(t7)
#auto1.show("A_ListeTrans__test")
print(auto1.estDeterministe(auto1))
autod = auto1.determinisation(auto1)
#autod.show("A_ListeTrans__testd")

#création d'un nouvel automate:
s7=State("10",True,False)
s8=State("11",False,False)
s9=State("12",False,False)
s10=State("13",False,True)
print(State.isFinalIn([s10]))
# t01 : Transition
t01 = Transition(s7,"a",s7)
# t02 : Transition
t02 = Transition(s7,"b",s8)
# t03 : Transition
t03 = Transition(s8,"a",s9)
# t04 : Transition
t04 = Transition(s8,"b",s9)
# t05 : Transition
t05 = Transition(s9,"a",s7)
# t06 : Transition
t06 = Transition(s9,"b",s10)
# t07 : Transition
t07 = Transition(s10,"a",s10)
# t08 : Transition
t08 = Transition(s10,"b",s8)
# liste1 : list[Transition]
liste1 = [t01,t02,t03,t04,t05,t06,t07,t08]
#s11=organiser([s7,s8,s9,s10],False)
automa=Automate(liste1)
#automa.show("A_ListeTrans__nouv")
print(automa)

#_____________________________________________________________________________________________________
###Exercice 5
print("		EXERCICE 5")
##Question 1
print("Question 1.1:\n")
print("Automate Complementaire \n")
complementaire=automa.complementaire(automa,"ab")
#complementaire.show("A_ListeTrans__complementaire")

#--------------------------------------------------------------------------
##Question 1.2
print("\nQuestion 1.2:\n")
print("Intersection\n")

#--------------------------------------------------------------------------
##Question 1.3
print("\nQuestion 1.3:\n")
print("Union\n")
##création d'états
#s40 : State
s40 = State (0,True,False)
# s41 : State
s41 = State(1, False, False)
# s42 : State
s42 = State(2, False, True)

#s50 : State
s50 = State (0,True,False)
# s51 : State
s51 = State(1, False, False)
# s52 : State
s52 = State(2, False, True)

## cr ́eation de transitions
# t41 : Transition
t41 = Transition(s40,"a",s41)
# t42 : Transition
t42 = Transition(s40,"b",s41)
# t43 : Transition
t43 = Transition(s41,"a",s42)
# t44 : Transition
t44 = Transition(s41,"b",s40)
# t45 : Transition
t45 = Transition(s42,"a",s40)
# t46 : Transition
t46 = Transition(s42,"b",s42)

# t51 : Transition
t51 = Transition(s50,"b",s51)
# t52 : Transition
t52 = Transition(s50,"a",s50)
# t53 : Transition
t53 = Transition(s51,"b",s52)
# t54 : Transition
t54 = Transition(s51,"a",s50)
# t55 : Transition
t55 = Transition(s52,"b",s52)
# t56 : Transition
t56 = Transition(s52,"a",s50)

# liste5 : list[Transition]
liste5 = [t41,t42,t43,t44,t45,t46]

# liste6 : list[Transition]
liste6 = [t51,t52,t53,t54,t55,t56]

## creation de l’automate u1
# auto_u1 : Automate
print("Creation de l'automate u1:")
auto_u1 = Automate(liste5,[s40,s41,s42])
print(auto_u1)
#auto_u1.show("A_ListeTrans_u1")

## creation de l’automate u2 
# auto_u2 : Automate
print("Creation de l'automate u2:")
auto_u2 = Automate(liste6,[s50,s51,s52])
print(auto_u2)
#auto_u2.show("A_ListeTrans_u2")


#création de l'automate résultant de l'union de u1 et u2:
print("Creation de l'automate union de u1 et u2:")
union=auto_u1.union(auto_u1,auto_u2)
print(union)
#union.show("A_ListeTrans_union")

print("Notre automate union est il deterministe dans cet état:")
print(union.estDeterministe(union))
print("On le rend deterministe:")
union_d=union.determinisation(union)
#union_d.show("A_ListeTrans_union_d")


#--------------------------------------------------------------------------
##Question 2.1
print("\nQuestion 2.1:\n")
print("Concatenation\n")

###création de deux nouveaux automates:

##création d'états
#s20 : State
s20 = State (0,True,False)
# s21 : State
s21 = State(1, False, False)
# s22 : State
s22 = State(2, False, True)

#s30 : State
s30 = State (0,True,False)
# s31 : State
s31 = State(1, False, False)
# s32 : State
s32 = State(2, False, True)

## cr ́eation de transitions
# t21 : Transition
t21 = Transition(s20,"a",s21)
# t22 : Transition
t22 = Transition(s21,"b",s22)
# t23 : Transition
t23 = Transition(s22,"b",s22)
# t24 : Transition
t24 = Transition(s22,"a",s22)

# t31 : Transition
t31 = Transition(s30,"b",s30)
# t32 : Transition
t32 = Transition(s30,"a",s30)
# t33 : Transition
t33 = Transition(s30,"b",s31)
# t34 : Transition
t34 = Transition(s31,"a",s32)

# liste : list[Transition]
liste3 = [t21,t22,t23,t24]

# liste2 : list[Transition]
liste4 = [t31,t32,t33,t34]

## creation de l’automate c1
# auto_c1 : Automate
print("Creation d'un nouvel automate c1:")
auto_c1 = Automate(liste3,[s20,s21,s22])
print(auto_c1)
#auto_c1.show("A_ListeTrans_c1")

## creation de l’automate c2 
# auto_c2 : Automate
print("Creation d'un nouvel automate c2:")
auto_c2 = Automate(liste4,[s30,s31,s32])
print(auto_c2)
#auto_c2.show("A_ListeTrans_c2")

#création de l'automate résultant de la concatenation de c1 et c2:
print("Concatenation de nos deux nouveaux automates c1 et c2:")
concat=auto_c1.concatenation(auto_c1,auto_c2)
print(concat)
#concat.show("A_ListeTrans_concat")

#autre exemple
print("\nOn construit la concatenation des deux automates u1 et u2, crées pour l'union:")
concat_u=auto_u1.concatenation(auto_u1,auto_u2)
print(concat_u)
#concat_u.show("A_ListeTrans_concat_u")

#--------------------------------------------------------------------------
##Question 2.2
print("\nQuestion 2.2:\n")
print("Etoile\n")
print("On crée l'automate étoile de l'automate u1 que l'on avait crée pour l'union:")
etoile=Automate.etoile(auto_u1)
print(etoile)
#etoile.show("A_ListTrans_etoile")

##Question 2.
print("\nQuestion 2.3:\n")
print("intersection\n")
print("On crée l'automate intersection des automates auto_c1 et auto_c2 :")
inter=Automate.intersection(auto_c1,auto_c2)
print(inter)
inter.show("A_ListTrans_inter")

#--------------------------------------------------------------------------
print("\nQuestion 2.4:\n")
print("EnleverNonAtteint\n")
s70 = State (0,True,True)
s71 = State (1,False,True)
s72 = State (2,False,False)
s73 = State (3,False,False)
t70 = Transition(s70,"a",s71)
t71 = Transition(s71,"a",s70)
t72 = Transition(s71,"b",s72)
t73 = Transition(s72,"b",s71)
t74 = Transition(s73,"a",s71)
t75 = Transition(s73,"b",s72)
liste7 = [t70,t71,t72,t73,t74,t75]
## creation de l’automate CR
auto_CR = Automate(liste7,[s70,s71,s72,s73])
#auto_CR.show("A_ListTrans_NonAtteint")
CR1=auto_CR.EliminerNonAtteint(auto_CR)
#print(CR1) 
#CR1.show("A_ListTrans_inter")


#--------------------------------------------------------------------------
print("\nQuestion 2.5:\n")
print("EnleverInutile\n")
s80 = State (0,True,False)
s81 = State (1,False,True)
s82 = State (2,False,False)
s83 = State (3,False,False)
t80 = Transition(s80,"a",s81)
t81 = Transition(s81,"a",s80)
t82 = Transition(s81,"b",s82)
t83 = Transition(s82,"b",s83)
t84 = Transition(s81,"a",s83)
liste8=[t80,t81,t82,t83,t84]
CR2=Automate(liste8,[s80,s81,s82,s83])
CR3=CR2.EliminerInutile(CR2)
#print(CR3)
#CR3.show("A_ListTrans_coucou")







