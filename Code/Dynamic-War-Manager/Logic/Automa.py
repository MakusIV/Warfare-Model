# Automa
from logging import raiseExceptions
from Object import Object
from Actuator import Actuator
from Sensor import Sensor
from AI import AI
from Action import Action
from State import State
import General
import random
from LoggerClass import Logger


# LOGGING --
 
logger = Logger( module_name = __name__, set_consolle_log_level = 30, set_file_log_level = 10, class_name = 'Automa' )


class Automa(Object):
    """Automa derived from Object. """

    # TEST: OK
    def __init__( self, name = 'Automa', dimension = [1, 1, 1], mass = 100, maxLoad = 500, resilience = 100, power = 100, emissivity = {"radio": 50, "thermal": 50, "optical": 100, "nuclear": 0, "electric": 50, "acoustics": 100, "chemist": 0}, coord = None, sensors= None, actuators = None ):

        Object.__init__( self, name = name, dimension = dimension, mass = mass, resilience = resilience, emissivity = emissivity, coord = coord )

        self._ai = AI( automaId = self._id ) #AI Engine: 
        self._power = power # nota l'energia è gestita nello stato in quanto è variabile        
        self._state = State( run = True ) #Class State        
        self._sensors = sensors# list of Sensor objects
        self._actuators = actuators# list of Actuator objects. NO DEVE ESSERE UNA CLASSE CHE CONTIENE LA LISTA DEGLI ATTUATORI. QUESTA CLASSE DEVE IMPLEMENTARE IL METODO PER VALUTARE QUALI ATTUATORI ATTIVARE IN BASE AL COMANDO RICEVUTO
        self.action_executed = None
        self._actionsQueue = {} #  {key: event id, value = action}
        self._objectCatched = []
        self._maxLoad = maxLoad

        if not self.checkParamAutoma( power, sensors, actuators, maxLoad ):
            raise Exception( "Invalid properties! Automata not istantiate." )

        logger.logger.info( "Automa {0} created".format( self._id ) )
    
    # Methods


    # La sequenza è update --> percept --> evalutate --> action. 
    # update: aggiorna lo stato dell'automa in base agli eventi contenuti nella coda degli eventi
    # percept: utilizza i sensori per conoscere l'enviroment locale e aggiorna lo stato dell'automa



    # La AI è deputata esclusivamente alla valutazione delle informazioni ricevute dai sensori per 
    # l'aggiornamento dello stato dell'automa per definire l'azione da compiere in base a queste informazioni.
    # la proprietà 'env_state che rappresenta l'enviromets conosciuto dall'automa è interna e gestita nella AI
    
    def runTask( self, posManager ):
        
        self.update( posManager ) #Evalutate effect of events in eventsQueue and update state. Inherit from Object
        list_obj = self.percept( posManager )   #Scan space with sensor and returns objects detected
        
        if not self._ai:
            logger.logger.debug("Automa: {0} Exception: _ai not defined".format( self._id ))
            raise Exception( "Automa: {0} Exception: _ai not defined".format( self._id ) )                
        self._actionsQueue = self._ai.evalutate( list_obj ) # define task actions and insert in Queue action
        logger.logger.debug("Automa: {0} execute evalutate percept_info: created actionQueue with {1} items".format( self._id, len( self._actionsQueue ) ))
        logger.logger.info( "Automa: {0} running task: update internal state, execute perception and detected {1} object, evalutate and executed action()".format( self._id, len( list_obj ) ))
        return self.action( posManager ) # execute and return action task in Queue Action



    # TEST: OK
    def percept(self, posMng):
        """Percepts the enviroments with sensors, update the automa state and return percept informations."""
        #percept_info: le informazioni dopo l'attivazione dei sensori: (energy_consumption, list_obj_detected)
        #request_percept: le informazioni riguardo tipo di sensori e modalità di attivazione
        list_obj = list()
        operative_sensors = [ sensor for sensor in self._sensors if sensor.isOperative() ]# Lista dei sensori attivi
        percept_infos = [ sensor.perception( posMng, self.getPosition() ) for sensor in operative_sensors ]# lista delle perception info ottenuta interrogando tutti i sensori operativi. La percept_info: percept_info: (energy_sensor, detected_objs) detected. detected_objs = { ( x, y, z): obj }
        list_item =  [ percept_info[ 1 ].values() for percept_info in percept_infos ]# lista degli object    
        
        for item in list_item:
            for obj in item:
                if obj._id != self._id:
                    list_obj.append( obj )# lista degli object dictionary (pos, obj) creati dai diversi sensori
        energy_consume = [ percept_info[ 0 ] for percept_info in percept_infos ]
        self.updateStateForEnergyConsume( energy_consume )# aggiorna lo stato dell'automa
        logger.logger.debug("Automa: {0} execute perception: activated {1} sensor, detected {2} object, energy consumed: {3}".format( self._id, len( operative_sensors ), len( list_obj ), energy_consume  ))
        return list_obj # ( obj1, ob2, ...) NEXT UPDATE: si potrebbe utilizzare un dict = {id_obj: obj} per una ricerca immediata tramite id


    # TEST: OK
    def action(self, posManager ):
        """Activates Actuators for execution of Action. Return action informations."""
        #action_info: le informazioni dopo l'attivazione degli attuatori e lo stato degli stessi( classe)
        actions_info = [] # (action_type, energy_consume, position, object)
        active_actions = self.getActionActive()

        for action in active_actions:           
            # actuators_activation: [ actuator,  [ position or obj, ..other params ] ]
            actuator_activation = self.select_actuators( action.getActionParam() ) # questa funzione deve anche valutare gli attuatori attivi e se questi sono sufficienti per compiere l'atto altrimenti deve restituire false o un atto ridotto            
            action_info = actuator_activation[0].exec_command( self, posManager, actuator_activation[ 1 ] )
            actions_info.append( action_info )            
            self.updateStateForAction( action, actuator_activation[0], action_info )

        logger.logger.debug("Automa: {0} executed action: created action_info with {1} items".format( self._id, len( actions_info ) ))
        return actions_info

    
    # vedi il libro
    def checkParamAutoma( self, power, sensors, actuators, maxLoad ):            
        """Return True if conformity of the parameters is verified"""
        
        if not maxLoad or not isinstance(maxLoad, int) or maxLoad < 0 or not power or not isinstance(power, int) or not( power <= 100 and power >= 0 ) or not sensors or not isinstance(sensors[0], Sensor) or not Sensor.checkSensorList(sensors[0], sensors) or not actuators or not isinstance(actuators[0], Actuator) or not Actuator.checkActuatorList(actuators[0], actuators):
            return False
        return True

     # TEST: OK (indirect from percept method)
    def updateStateForEnergyConsume(self, energy_consume):
        """Update state, Sensor, Actuator states for Percept  info"""                
        total_sensor_consume = sum( energy_consume )
        self._state.decrementEnergy( total_sensor_consume )
        logger.logger.debug("Automa: {0} update state for energy consume: total_sensor_consume: {1}, self._state._energy: {2}".format( self._id, total_sensor_consume, self._state._energy ))
        return True

    # TEST: OK (indirect from action method)
    def updateStateForAction(self, action, actuator, action_info):
        """Update state, Sensor, Actuator states for Action info"""

        if not action_info[2]:# l'azione è non stata completata nell'iterazione
            # action.setDuration(2)# ripristina la durata della action. L'ho eliminato in quanto, a differenza della move,  ci potrebbero essere action utilizzano la duration per la loro esecuzione in più task 
            logger.logger.debug("Automa: {0}. Actuator: {1}, execute action: {2}, action not complete".format( self._id, actuator.getId(), action_info[2] ))
            
        else:# l'azione è stata completata nell'iterazione
            action.setDuration( 0 )# imposta ad 0 la durata della action affinchè venga eliminata nella successiva scansione della queue
            logger.logger.debug("Automa: {0}. Actuator: {1}, execute action: {2}, action complete: removed from queue".format( self._id, actuator.getId(), action_info[2] ))           
    
        return True

    # TEST: OK (indirect from action method)
    def insertAction( self, action ):

        if not action or not isinstance( action, Action ):
            return False
        self._actionsQueue[ action._id  ] = action
        logger.logger.debug("Automa: {0} inserted new action in queue, action id: {1}, actions in queue: {2}".format( self._id, action._id, len( self._actionsQueue ) ))
        return True

    # TEST: OK (indirect from action method)
    def removeAction( self, action ):
        """remove action in eventsQueue"""
        if not isinstance(action._id, int) :
            return False

        self._actionsQueue.pop( action._id )        
        logger.logger.debug("Automa: {0} removed action in queue, action id: {1}, actions in queue: {2}".format( self._id, action._id, len( self._actionsQueue ) ))
        return True

    # TEST: OK (indirect from action method)
    def resetActionQueue( self ):
        """Reset the Action Queue"""
        self._actionsQueue.clear()

    # TEST: OK (indirect from action method)
    def getActionActive( self ):
        """Return a list with activable actions for a single task. Update the event Queue"""
        active = [] # list of active actions
        
        for act in list( self._actionsQueue.values() ):

            if act.isAwaiting(): # event not activable in this task
                act.decrTime2Go() # decrement time to go
                self._actionsQueue[ act.getId() ] = act # update actions queue

            elif act.isActivable(): # action activable
                act.decrDuration() # decrement duration
                self._actionsQueue[ act.getId() ] = act # update actions queue
                active.append( act ) # insert the action in action events list

            else: # expired action
                self._actionsQueue.pop( act.getId() ) #remove element from events queue 

        return active




    def evalutateHit( self, posManager, power, random_hit = True ):
        """" evalutate event hit effect """
        
        if random_hit:
            automa_energy_hit_power = int( power * random.uniform(0, 1) )
            sensor_energy_hit_power = int( ( power - automa_energy_hit_power ) * random.uniform(0, 1) )
            actuator_energy_hit_power = int( ( power - sensor_energy_hit_power ) * random.uniform(0, 1) )

        else:
            automa_energy_hit_power = power
            sensor_energy_hit_power = int( power * 0.5 )
            actuator_energy_hit_power = int( power * 0.8 )

        logger.logger.debug("Automa: {0} - automa_energy_hit_power: {1}, sensor_energy_hit_power: {2}, actuator_energy_hit_power: {3}".format( self._id, automa_energy_hit_power, sensor_energy_hit_power, actuator_energy_hit_power ))

        for sensor in self._sensors:
            health = sensor.evalutateSelfDamage( sensor_energy_hit_power )
            
            if health == 0: # valutazione del danno per il sensore. Se restituisce 0 il sensore è dsitrutto
                self._sensors.pop( sensor ) # elimina il sensore dalla lista sensori dell'automa
                logger.logger.debug("Automa: {0} deleted sensor: {1} for damage".format( self._id, sensor._name ))
            
            resilience = sensor._resilience                    
            active = sensor._state.isActive()
            critical = sensor._state.isCritical()
            anomaly = sensor._state.isAnomaly()
            destroyed = sensor._state.isDestroyed()                                                
            remove = sensor._state.isRemoved()
            logger.logger.debug("Automa: {0} Evalutate Sensor ( name: {1} ) Hit damage with power: {2}. resilience: {3}, health: {4}, active: {5}, critical: {6}, anomaly: {7}, destroyed: {8}, removed: {9}".format( self._id, sensor._name, power, resilience, health, active, critical, anomaly, destroyed, remove ) )
        

        for actuator in self._actuators:
            health = actuator.evalutateSelfDamage( actuator_energy_hit_power )
            
            if health  == 0: # valutazione del danno per l'attuatore. Se restituisce 0 l'attuatore è dsitrutto
                self._actuators.pop( actuator ) # elimina il attuatore dalla lista attuatori dell'automa
                logger.logger.debug("Automa: {0} deleted actuator: {1} for damage".format( self._id, actuator._name ))
            
            resilience = actuator._resilience                    
            active = actuator._state.isActive()
            critical = actuator._state.isCritical()
            anomaly = actuator._state.isAnomaly()
            destroyed = actuator._state.isDestroyed()                                                
            remove = actuator._state.isRemoved()
            logger.logger.debug("Automa: {0} Evalutate Actuator ( name: {1} ) Hit damage with power: {2}. resilience: {3}, health: {4}, active: {5}, critical: {6}, anomaly: {7}, destroyed: {8}, removed: {9}".format( self._id, actuator._name, power, resilience, health, active, critical, anomaly, destroyed, remove ) )
        
        health = self.evalutateDamage( automa_energy_hit_power )
        resilience = self._resilience                    
        active = self._state.isActive()
        critical = self._state.isCritical()
        anomaly = self._state.isAnomaly()

        if health == 0: # valutazione del danno per l'automa. Se restituisce 0 l'automa è dsitrutto
            self.destroy()
            logger.logger.debug("Automa: {0} health = 0, Automa destroyed".format( self._id ))           
            destroyed = self._state.isDestroyed()                                                
            remove = self._state.isRemoved()
            logger.logger.debug("Automa: {0} Evalutate Hit damage with power: {1}. resilience: {2}, health: {3}, active: {4}, critical: {5}, anomaly: {6}, destroyed: {7}, removed: {8}".format( self._id, power, resilience, health, active, critical, anomaly, destroyed, remove ) )
        
            if destroyed:
        
                if posManager.removeObject( self ):                                
                    logger.logger.debug("Object: {0} object removed from position manager".format( self._id ) )
                    # valutare se è opportuno inviare un evento da inviare ... a chi? (l'eventuale esecutore del HIT non è conosciuto da object)
                    return True
        
                else:                
                    raise Exception("Object: {0} was destructed but not removed from position manager".format( self._id ) )
                            
        logger.logger.debug("Object: {0} object was hit but not destructed. Health = {0}, resilience: {1}, active: {2}, critical: {3}, anomaly: {4}".format( self._id, health, resilience, active, critical, anomaly ) )            
        return True

    
    # TEST: OK parziale
    def select_actuators( self, act ):
        """Select the actuators for activation with act parameter and define parameter for execute action"""
        # act: (action_type, position or object)
        # return: # actuators_activation: [ actuators,  [ position or obj, ..other params, self ] ]
        
        if not act or not isinstance(act, list) or not General.checkActionType( act[0] ) or not( isinstance( act[1], Object) or General.checkPosition( act[1] ) ):
            raise Exception("action not found!")

        action_type = act[0]

        # actuators:  { key: actuator_type, value: actuator }
        if action_type == 'move' or action_type == 'run': # OK
            actuator = self.getActuator( actuator_class = 'mover' )            

            if action_type == 'move': # OK                
                speed_perc = act[2] #0.7 # % della speed max. Il consumo di energia è calcolato applicando questa % al dt*power
            
            else:
                speed_perc = 1 # % della speed max. Il consumo di energia è calcolato applicando questa % al dt*power
                        

            target_position = act[ 1 ]            
            logger.logger.debug("Automa: {0}, created actuators_activation, action_type: {1}, target_position: {2} and speed_perc: {3}".format( self._id, action_type, target_position, speed_perc ))
            # NOTA!!!: L'esecuzione dell'azione move da parte di un attuatore, comporta lo spostamento effettivo dell'automa, quindi n attutori effettueranno complessivamente n move -> SBAGLIATO
            # Ciò significa che per l'esecuzione della action_type move deve essere azionato un solo attuatore che rappresenta l'insieme dei dispositivi dedicati a questo tipo di azione
            # nella actuators lista sarà quindi composta da un solo attuatore
            return [ actuator,  [ target_position, speed_perc ] ]            
            
        elif action_type == 'translate': # OK
            actuator = self.getActuator( actuator_class = 'object_manipulator' )
            obj = act[ 1 ]    
            destination = act[ 2 ]        
            logger.logger.debug("Automa: {0}, created actuators_activation with included: action_type: {1}, object: {2}".format( self._id, action_type, obj._id ))
            return [ actuator, [ obj, destination ] ]

        elif action_type == 'catch': # OK
            actuator = self.getActuator( actuator_class = 'object_catcher' )
            obj = act[ 1 ]
            logger.logger.debug("Automa: {0}, created actuators_activation with included: action_type: {1}, object: {2}".format( self._id, action_type, obj._id ))
            return [ actuator, [ obj ] ]
        
        elif action_type == 'eat':
            actuator = self.getActuator( actuator_class = 'object_assimilator' )
            obj = act[ 1 ]
            logger.logger.debug("Automa: {0}, created actuators_activation with included: action_type: {1}, object: {2}".format( self._id, action_type, obj._id ))
            return [ actuator, [ obj ] ]

        elif action_type == 'shot':
            actuators = []
            plasma_actuators = self.getActuator( actuator_class = 'plasma_launcher' )
            projectile_actuators = self.getActuator( actuator_class = 'projectile_launcher' )
            
            if plasma_actuators:                                
                actuators.append( plasma_actuators )
            
            if projectile_actuators:
                actuators.append( projectile_actuators )

            actuator = actuators[ 0 ] #self.eval_best_actuators( actuators ) # Qui logica per decidere quale attuatore è meglio utilizzare

            obj = act[ 1 ]
            logger.logger.debug("Automa: {0}, created actuators_activation with included: action_type: {1}, object: {2}".format( self._id, action_type, obj._id ))
            return [ actuator, [ obj ] ]

        elif action_type == 'hit':
            actuator = self.getActuator( actuator_class = 'object_hitter' )
            obj = act[ 1 ]
            logger.logger.debug("Automa: {0}, created actuators_activation with included:  action_type: {1}, object: {2}".format( self._id, action_type, obj._id ))
            return [ actuator, [ obj ] ]
        
        elif action_type == 'attack':
            actuators = []
            catcher_actuators = self.getActuator( actuator_class = 'object_catcher' ) 
            projectile_actuators = self.getActuator( actuator_class = 'projectile_launcher' )
            plasma_actuators = self.getActuator( actuator_class = 'plasma_launcher' )
            hitter_actuators = self.getActuator( actuator_class = 'object_hitter' )

            if plasma_actuators:
                actuators.append( plasma_actuators )
            
            if projectile_actuators:
                actuators.append( projectile_actuators )

            if catcher_actuators:
                actuators.append( catcher_actuators )
            
            if hitter_actuators:
                actuators.append( hitter_actuators )
            
            actuator = actuators[ 0 ] #self.eval_best_actuators( actuators ) # Qui logica per decidere quale attuatore è meglio utilizzare

            obj = act[ 1 ]
            logger.logger.debug("Automa: {0}, created actuators_activation with included: list of {1} acutators, action_type: {2}, object: {3}".format( self._id, len( actuators ), action_type, obj._id ))
            return [ actuator, [ obj ] ]
        
        else:
            logger.logger.error("Automa: {0}, raised exception: 'action_type not found!!' ".format( self._id, len( actuators ), action_type, obj._id ))
            raise Exception("action_type not found!!")

        return

    def getActuator( self, actuator_class ):
        """Return actuator with actuator_class propriety. If actuator doesn't exists or is not operative return False """

        for actuator in self._actuators:

            if actuator.isClass( actuator_class ) and actuator.isOperative():        
                return actuator

        return False

    def setActuator( self, actuator):
        """Insert an Actuator in actuators list"""
        if not actuator or not isinstance(actuator, Actuator):
            return False
        self._actuators.append( actuator )
        return True

    def setSensor( self, sensor):
        """Insert an Sensor in sensors list"""
        if not sensor or not isinstance(sensor, Sensor):
            return False
        self._sensors.append( sensor )
        return True

    def checkLoadObject( self, obj):
        """ Check if obj can load in object catched list. Return True if possible, otherwise False"""
        loaded = 0
        
        for obj_ in self._objectCatched:
            loaded = loaded + obj_.getMass()

        return ( self._maxLoad - loaded ) >= obj.getMass()


    def catchObject( self, obj):
        """Inserted obj in object catched list and set id automa in object take_from property"""
        if not obj or not self.checkLoadObject( obj ):
            return False

        obj.setCaught_from( self._id )
        self._objectCatched.append( obj )

        return True

    def checkCaught( self, obj):
        """Return True if obj exist in object catched list, otherwise False"""
        for obj_ in self._objectCatched:
            if obj == obj_:
                return True
        return False

    def checkClass( self, automa):
        """Check if Class automa is Automa"""
        if automa and isinstance(automa, Automa):
            return True

        return False

    def destroy( self ):
        """Destroy this automa"""

        for obj in self._objectCatched:
            obj.destroy()
        self._ai = None
        self._sensors = None
        self._actuators = None
        self._actionsQueue = None
        self._objectCatched = None   
        Object.destroy( self )     
        return True

        

    def setAI( self, ai ):
        """Set AI association"""                 
        if ai or not isinstance(ai, AI):
            raiseExceptions("setAI( ai ): ai not defined or not istance of AI class")      
        self._ai = ai        
        ai._automaId = self._id
        return True


    def getAI( self ):
        """Get AI association"""         
        return self._ai
    # deprecated
    def calcOptimumDistanceDetection( self ):
        """"Return the distance for optimal detection of automa"""
        # check all sensor for evalutate optimum distance according with detection max range
        # this value must not be random
        operative_sensors = [ sensor for sensor in self._sensors if sensor.isOperative() ]        
        range_media = 0

        if operative_sensors:
            
            for sensor in operative_sensors:
                range_media += General.calcVectorModule( sensor._range )
        return range_media

    def getFootPrint( self ):
        """Return hash code for Automa"""        
        isAutoma = False
        sensorFootPrint = self.getDetectableSensorsFootPrint()        
        actuatorFootPrint = self.getDetectableActuatorsFootPrint()  
        
        if sensorFootPrint + actuatorFootPrint != 0:
            isAutoma = True       
        # Automa footprint depends from actuators and sensors footprint and automa propriety (dimensions and mass)
        automaFootPrint = hash( General.calcVectorModule( self._dimension ) + sensorFootPrint + actuatorFootPrint + self._mass )
        return automaFootPrint, isAutoma

    def getDetectableSensorsFootPrint( self ):
        """Return hash code for detectable sensors"""
        # detectable_sensor_list_code = è codice hash che rappresenta univocamente i sensori visibili (opticalDet, radioDet, thermalDet, chemistDet)
        # 
        # la sensibilità del sensore è già considerata durante il rilevamento dell'oggetto. 
        # perciò la visibilità dei suoi componenti: sensori e attuatori, dipende dalla distanza, 
        # e dal rapporto tra le dimensioni dell'oggetto e quelle del sensore
        #
        # nota: il codice cambia ad ogni nuova sessione di python. Quindi se si prevede il salvataggio di una sessione è necessario sostituire la funzione hash() utilizzata
        #   
        sensorsFootPrint = 0        
        operative_sensors = [ sensor for sensor in self._sensors if sensor.isOperative() ]        

        if operative_sensors:
            automa_dimension_module = General.calcVectorModule( self._dimension )             
            detectable_ratio = 3 # ratio of minimum dimension of a detectable sensor at max distance for full object detection (dimension_sensor / dimension_autom ) 
            # valuta se considerare le singole componenti x,y,x per il calcolo della detectable. Per il momento considero il modulo                    

            for sensor in operative_sensors:
                sensor_dimension_module = General.calcVectorModule( sensor._dimension )            
                detectable = ( sensor_dimension_module * detectable_ratio ) / ( automa_dimension_module )
                #att: con distance (1,1,1) e max distance (100, 100, 100 )--> detected è 0.7!!!
                #detected = General.calcProbability( detectable )  non và bene in quanto non può essere aleatorio perchè utilizzato per creare impronte di oggetto usate come chiavi

                if detectable > 0.5:                
                    sensorsFootPrint = hash( sensorsFootPrint + sensor.getSensorFootPrint() )# sommo i due numeri per evitare che liste con ordine contenenti gli stessi sensori ma in diverso ordine possano generare hash diversi (la somma è sempre uguale proprietà commutativa della somma)
 
        return sensorsFootPrint 

    def getDetectableActuatorsFootPrint( self ):
        """Return hash code for detectable actuators"""
        # detectable_actuator_list_code = è codice hash che rappresenta univocamente gli attuatori visibili (opticalDet, radioDet, thermalDet, chemistDet)
        # 
        # la sensibilità dell'attuatore è già considerata durante il rilevamento dell'oggetto. 
        # perciò la visibilità dei suoi componenti: actuatori e attuatori, dipende dalla distanza, 
        # e dal rapporto tra le dimensioni dell'oggetto e quelle dell'attuatore
        #
        # nota: il codice cambia ad ogni nuova sessione di python. Quindi se si prevede il salvataggio di una sessione è necessario sostituire la funzione hash() utilizzata
        #        
        actuatorsFootPrint = 0
        operative_actuators = [ actuator for actuator in self._actuators if actuator.isOperative() ]        

        if operative_actuators:    
            automa_dimension_module = General.calcVectorModule( self._dimension )            
            detectable_ratio = 3 # ratio of minimum dimension of a detectable actuator at max distance for full object detection (dimension_actuator / dimension_autom ) 
            # valuta se considerare le singole componenti x,y,x per il calcolo della detectable. Per il momento considero i moduli                            

            for actuator in operative_actuators:
                actuator_dimension_module = General.calcVectorModule( actuator._dimension )            
                detectable = ( actuator_dimension_module * detectable_ratio ) / ( automa_dimension_module )
                #att: con distance (1,1,1) e max distance (100, 100, 100 )--> detected è 0.7!!!
                
                #detected = #General.calcProbability( detectable ) non và bene in quanto non può essere aleatorio perchè utilizzato per creare impronte di oggetto usate come chiavi

                if detectable > 0.5:                
                    actuatorsFootPrint = hash( actuatorsFootPrint + actuator.getActuatorFootPrint() )# sommo i due numeri per evitare che liste con ordine contenenti gli stessi actuatori ma in diverso ordine possano generare hash diversi (la somma è sempre uguale proprietà commutativa della somma)
    
        return actuatorsFootPrint            