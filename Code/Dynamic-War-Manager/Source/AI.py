from logging import raiseExceptions
from random import uniform
from typing import Dict
from State import State
from Threat import Threat
from Resource import Resource
from Obstacle import Obstacle
from Action import Action
import General
from LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'AI')


class AI:

    # La AI è deputata esclusivamente alla valutazione delle informazioni ricevute dai sensori per 
    # l'aggiornamento dello stato dell'automa e del enviroment conosciuto dall'automa (env_state)
    # e per definire l'azione da compiere in base a queste informazioni
    

    def __init__(self, state = State(run = True), env_state = dict(), obj_memory = dict(), automaId = None  ):
        
        self._state = state #Class State 
        self._env_state = env_state
        self._obj_memory = obj_memory
        self._automaId = automaId# per evitare la circular reference e comunque avere un riferimento verso l'automa

        #env_state = ( obj.pos, obj1, type = unknow, direction = (8, nord_est_up), aspect = away, estimated_distance = 7),  
        
        # obj_memory = dict(key = IdObj, _class = threat/obstacle/food, _typ = shooter/catcher/solid/liquid/gas, 
        # eval_dangerous_range = (x.range, y.range, z.range), danger = 1..100)
        self._obj_memory = obj_memory#dict( [ ("dummyObjId", ["OBSTACLE", "SOLID", [10, 10, 10], 0] ) ] )

        if not self.checkProperty():
            raise Exception("Invalid parameters! Object not istantiate.")

        logger.logger.debug('AI Instantiate')

    # Methods

    def checkProperty(self):

        if not self._state or not isinstance(self._state, State) or not isinstance(self._obj_memory, dict) or not isinstance(self._env_state, dict) :#or not self._env_state or not self._obj_memory
            return False
            
        return True

    
    def evalutate(self, automa, percept_info, state):
        """Evalutate enviroments info from percept_info. Update internal and 
        enviroment state property of ai and return the action to execute. Raise an Generic Exception"""
        # Funzione principale (API), aggiorna lo stato interno dell'automa ()
        # updateInternalState( automa, percept_info )
        if automa._id != self._automaId:
            raiseExceptions("updateEnvState( self, automa, perception_info ): automa._id! = ai._automaId")

        # updateInternalState --> updateEnvState --> evalutation --> Action
        # Evalutate the Action to Automa execute. Return an istance of Action"""
        
        # eval_threat --> eval_resource --> eval_space --> eval_action
        
        #threats = self._ev_threat( self._state, self._env_state, state )
        #resources = self._ev_resource( self._state, self._env_state, state )
        #obstacles = self._ev_obstacle( self._state, self._env_state, state )
        #action = self._ev_action(threats, resources, obstacles, state) #action = Action(...) una classe
     
        action = None

        if not self.updateInternalState( automa, percept_info ): 
            raise Exception("evalutate method failed! updateInternalState Failed")
        # evaluate action using low-level cognitive functions in base alla memoria istintiva (azioni incondizionate)
        if not self.lowLevelEvalutation( automa, percept_info ): 
            raise Exception("evalutate method failed! updateEnvState Failed")
        # evaluate action using high-level cognitive functions
        action = self.highLevelEvalutation( self, automa ) #action = Action(...) una classe

        if not action:
            raise Exception("evalutate method failed! updateEnvState Failed")
        return action


    def updateInternalState( self, automa, perception_info ):
        """update the internal_state property"""
        # nota: l'internal state serve solo per valutare il livello di efficenza dell'ai nell'esecuzione delle sue funzioni
        return True

    def lowLevelEvalutation( self, automa, perception_info ):
        """evaluate action using low-level cognitive functions based on the information contained in the Enviroment State. Update Enviroments State and Internal Memory of Object"""
        # l'env_state è la porzione dell'intero enviroments (contesto) percepito dalla AI inn base ai suoi sensori. l'env_state è quindi quella memoria utilizzata dal 
        # "sistema nervoso periferico" per determinare le azioni incondizionate che per ragioni di velocità sono acquisite come schemi predefiniti, ottimizzati con l'esperienza
        # acquisita e che non coinvolgono elaborazioni più complesse,
        #        
        # Questa funzione implementa le funzioni dell'algoritmo di AI che simulano le risposte "incondizionate" anche acquisite
        # esperenzialmente, che non coinvolgono processi di analisi sofisticati. Utilizza la memoria degli oggetti (_memory_obj)
        # per eventualmente riconoscere oggetti già visti o inserirne di nuovi.
        # effettua l'update dell'env_state e della memory_obj
        #
        # utilizzare lo _env_state per valutare i vettori di spostamento degli obj già presenti utilizzando le nuove posizioni
        # rilevate nella preception_info. 
        #
        # Utilizzando la memory_obj (memoria degli oggetti conosciuti) classificare i nuovi obj presenti nella perception_info
        # aggiornare quindi l'_env_state.
        #               
        # (obj3, position = (x,y,z), class = food, type = boh, direction = (x,y,z), aspect = stopped, distance = 3, dimension = (1,1,1), threat_level = 0, )
        # )
        #
        # note: 
        # Nell'algoritmo AI basato su condizioni, si potrebbero valutare le azioni da eseguire considerando l'env_state        # L'env_state potrebbe essere rappresentato da una tabella in cui c'è l'obj, il vettore di spostamento (modulo = velocità presunta),
        # e la classificaione: pericolo (con magnitudo), cibo (con magnitudo), ostacolo (con dimensioni). Esempio
        # ( (obj1, "unknow", direction = (8, nord_est_up), aspect = away, best_direction_to_escape = (south_west_up), distance = 7, danger = 3), 
        # (obj2, "threat", vector = (10, south_west), aspect=approaching, best_direction_to_escape = (south_west_up), danger=10), (obj3, "food", vector=(10, north), aspect=away, danger=0)
        # In base a questa lista l'automa deve valutare la priorità di fuggire in una determinata direzione opposta all'eventuale pericolo, ovvero
        # in direzione di una preda ovvero aggirando un ostacolo. In una prima versione di AI basata su condizioni, possiamo valutare danger, pesando il tipo di minaccia (uno shooter è più pericoloso di un catcher),
        # la distanza della minaccia e l'aspect. Poi confrontando i valori di danger delle diverse minaccie insieme ai valori di obstacle_magnitudo e di food_magnitudo
        # stabiliere quale direzione prendere.
        
        if not automa or automa._id != self._automaId:
            raiseExceptions("updateEnvState( self, automa, perception_info ): automa._id! = ai._automaId")

        if not perception_info:
            raiseExceptions("updateEnvState( self, automa, perception_info ): perception_info not defined")

        for obj in perception_info:
            # la differenza tra i parametri ev_ e gli altri consiste nella valutazione come stima dei primi e l'esattezza dei secondi 
            # necessaria per calcolare in modo univoco l'impronta (l'impronta è utilizzata come obj_key nell'env_state e nella memory_obj)
            position = obj.getPosition()            
            category = None
            type = None
            dimension = None
            uei = None    
            direction = None
            aspect = None
            distance = None
            ev_speed = None
            ev_strenght = None
            ev_resilience = None
            ev_perceptiveness = None
            ev_intelligence = None
            ev_isAutoma = None
            ev_isObstacle = None
            ev_isFood = None
            ev_threat = None
            objectFootPrint, isAutoma = obj.getFootPrint()
            #env_position = self.searchObjectInEnvState( objectFootPrint )

            if self._env_state[obj._id]:# object presents in env_state
               # update aspect. direction and uei in env_state
                #category: "threat", "food", "enviroment", "unknow".  type: "automa", "object"
                #self._obj_memory[objectFootPrint] = { "category": category, "type": type, "dimension": dimension, "uei": uei, "speed": ev_speed, "strenght" : ev_strenght, "resilience": ev_resilience, "perceptiveness": ev_perceptiveness, "resilience": ev_resilience, "intelligence": ev_intelligence, "automa": ev_isAutoma }                
                #self._env_state[obj._id] = { "objectFootPrint" : objectFootPrint, "position" : position, "category" : category, "type" : type, "direction" : direction, "aspect" : aspect, "distance" : distance, "uei" : uei }
                direction, mod = obj._coord.getDirection( self._env_state[obj._id], position )
                #aspect of obj in realtionship with automa position (da rivedere)
                aspect, prod_scal, prod_vect = obj._coord.getVectorAspect( direction, position )
                uei = self.computeUei( obj, automa ) # uei = unconditionating emotion intensity: level of fear intensity
                
                if aspect == "approach":
                    ev_perceptiveness = True

                ev_speed = mod # non serve mettere direction (vettore velocità) in quanto è una info più coerente con env_state. In memory_obj la speed ha il significato di valutazione della capacità dell'oggetto di correre velocemente
                
                if uei > 1 and ( self._obj_memory[objectFootPrint]["category"]=="threat" or self._obj_memory[objectFootPrint]["category"]=="unknow" ) and aspect == "approach":
                    uei *= mod / General.calcVectorModule( self._obj_memory[objectFootPrint]["direction"] )

                    if self._obj_memory[objectFootPrint]["category"]=="unknow":
                        ev_threat = True
                    automa_suggested_direction = direction #escaping
                
                elif uei > 1 and ( self._obj_memory[objectFootPrint]["category"]=="threat" or self._obj_memory[objectFootPrint]["category"]=="unknow" ) and ( aspect == "away" or aspect == "tangent" ):
                    uei *= mod / General.calcVectorModule( self._obj_memory[objectFootPrint]["direction"] )
                    automa_suggested_direction = -direction #step away

                elif  self._obj_memory[objectFootPrint]["category"]=="threat" and self._obj_memory[objectFootPrint]["category"]=="enviroment":                    
                    automa_suggested_direction = automa._coord.getDirection(automa.getPosition, -obj.getPosition ) #step away
                                
                elif self._obj_memory[objectFootPrint]["category"]=="food" or ( self._obj_memory[objectFootPrint]["category"]=="enviroment" and not self._obj_memory[objectFootPrint]["category"]=="threat" ) or ( uei < 1 and self._obj_memory[objectFootPrint]["category"]=="unknow" ):#probably food
                     automa_suggested_direction = automa._coord.getDirection (automa.getPosition, obj.getPosition ) #approaching
                
                else:
                    raiseExceptions("lowLevelEvalutation( automa, perception_info ): object presents in env_state but not possible compute new direction ")

                # update obj_memory
                self._obj_memory[objectFootPrint]["uei"] = uei
                self._obj_memory[objectFootPrint]["speed"] = ev_speed# o direction per avere il vettore
                self._obj_memory[objectFootPrint]["perceptiveness"] = ev_perceptiveness 
                # update env_state
                #self._env_state[position] = { "objectFootPrint" : objectFootPrint, "obj_id" : obj._id, "position" : position, "category" : category, "type" : type, "direction" : direction, "aspect" : aspect, "distance" : distance, "uei" : uei }
                self._env_state[obj._id]["position"] = position                
                self._env_state[obj._id]["direction"] = direction
                self._env_state[obj._id]["aspect"] = aspect
                self._env_state[obj._id]["distance"] = General.calcVectorModule( position )
                self._env_state[obj._id]["uei"] = uei
        
            elif self._obj_memory[objectFootPrint]: # object presents in obj_memory
                # l'oggetto è già presente nella obj_memory (l'istanza)
                # compute aspect. direction and uei and other parameters and store in env_state
                #self._env_state[position] = { "objectFootPrint" : objectFootPrint, "obj_id" : obj._id, "position" : position, "category" : category, "type" : type, "direction" : direction, "aspect" : aspect, "distance" : distance, "uei" : uei }
                #self._obj_memory[objectFootPrint] = { "category": category, "type": type, "dimension": dimension, "uei": uei, "speed": ev_speed, "strenght" : ev_strenght, "resilience": ev_resilience, "perceptiveness": ev_perceptiveness, "resilience": ev_resilience, "intelligence": ev_intelligence, "automa": ev_isAutoma }                
                
                self._env_state[obj._id] = self._env_state[position]                
                self._env_state[obj._id]["direction"] = direction
                self._env_state[obj._id]["aspect"] = aspect
                self._env_state[obj._id]["distance"] = General.calcVectorModule( position )
                self._env_state[obj._id]["uei"] = uei

            else:# unknow obj
                # evalutate uei a initialize other parameter to store in env_state and memory obj
                automa_volume = automa.getValueVolume()                    
                factor_of_volume = 1.5# ratio volume obj/ volume automa to scare
                factor_of_escape = 2# ratio speed/distance to scare
                volume_ratio = obj.differenceWithValueVolume( automa_volume ) / automa_volume# obj_volume - automa_volume
                distance = obj.getDistance( automa._coord )# distance of obj from automa                                       
                uei = 1 # uei = unconditionating emotion intensity: level of fear intensity for unknow obj # fear: >1,  unfear: <=1                    
                position = obj.getPosition()                    
                dimension = obj.getDimension()
                category = "unknow"
                type = "unknow"
                
                if isAutoma:                                            
                    # nota: il codice cambia ad ogni nuova sessione di python. Quindi se si prevede il salvataggio di una sessione è necessario sostituire la funzione hash() utilizzata                                            
                    uei = self.computeUei( obj, automa)# uei = unconditionating emotion intensity: level of fear intensity

                    if uei > 1:
                        category = "threat"                        
                    else:
                        category = "food"

                else:
                    category = "no_automa"
                    uei = 0

                self._obj_memory[objectFootPrint] = { "category": category, "type": type, "dimension": dimension, "uei": uei, "speed": ev_speed, "strenght" : ev_strenght, "resilience": ev_resilience, "perceptiveness": ev_perceptiveness, "resilience": ev_resilience, "intelligence": ev_intelligence, "automa": ev_isAutoma, "obstacle" : ev_isObstacle, "food": ev_isFood }
                self._env_state[objectFootPrint] = { "obj_id" : obj._id, "position" : position, "category" : category, "type" : type, "direction" : direction, "aspect" : aspect, "distance" : distance, "uei" : uei }

        return True

        
    def _ev_threat( self, internal_state, env_state, state ):
        """Evalutate Threats with level of threath and position. Return an istance of Threat.
        Rise an Invalid Parameters Exception"""
        threats = Threat()
        return threats        

    def _ev_resource( self, internal_state, env_state, state ):
        """Evalutate Resource with level of resource and position. Return an istance of Resource.
        Rise an Invalid Parameters Exception"""
        resources = Resource()
        return resources

    def _ev_obstacle( self, internal_state, env_state, state ):
        """Evalutate Space enviroments with Obstacles. Return an istance of Obstacle.
        Rise an Invalid Parameters Exception"""
        obstacles = Obstacle()
        return obstacles

    def _ev_action(self, threaths, resources, space_env, state):
        """Evalutate action to execute considering threats, resources, space_env and state.
        Return an instance of Action. Rise an Invalid Parameters Exception"""
        action = Action()
        return action

    def setAutomaId( self, automaId ):
        """Set automaId"""
        if not automaId:
            raiseExceptions("setAutomsaId( automaId ): parameter not defined")
        
        self._automaId = automaId
        return True

    def getAutomaId():
        """get automaId"""
        return self._automaId

    def computeUei( self, distance, automa):
        automa_max_speed = automa.getActuator("mover").speed                
        escaping_range = automa_max_speed /distance # chance of escape
        uei = volume_ratio * factor_of_escape / ( factor_of_volume * escaping_range )
        return uei


    def searchObjectInEnvState( self, objectFootPrint ):
        """Return key (position) of env_state element with objectFootPrint value, otherwise None"""
        for element in self._env_state:
            if element["objectFootPrint"] == objectFootPrint:
                return element.key()
        return None