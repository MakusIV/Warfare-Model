import random
from Coordinate import Coordinate
import General
from State import State
from Event import Event
from LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Actuator')


class Actuator:
    #position, range_max, typ, emissivity_perception = 1, power = 100, resilience = 100, delta_t = 0.01, accuracy = 5, name = None, state = None 
    def __init__(self, position, class_, typ, mass = 10, range_max = None, power = None,  resilience = None, delta_t = None, name = None, speed = None, strength = None, accuracy = None, dimension = None  ):

        
        self._name = name
        self._id = General.setId('Actuator_ID', None) # Id generator automaticamente
        self._power = power# nota l'energia è gestita nello stato in quanto è variabile  
        self._range = range_max# è rappresentato da una tupla di distanze (x_d:int, y_d:int, z_d:int)
        self._state = State( run = True )
        self._resilience = resilience # resistenza ad uno SHOT in termini di power (se shot power > resilence --> danno al actuatore)
        self._delta_t = delta_t # Il tempo necessario per eseguire l'attuazione serve per calcolare il consumo energetico. Potrà essere utilizzato per gestire eventuali attuazioni che necessitano di più cicli
        self._type = typ # il tipo di attuazione (vedi General.ACTUATOR_TYPE)
        self._class = class_ # la classe dell'attuatore (vedi General.ACTUATOR_TYPE)
        self._position = position
        self._mass = mass
        self._speed = speed
        self._strength = strength               
        self._accuracy = accuracy
        self._dimension = dimension                       

        if not name:
            self._name = General.setName('Actuator_Name')

        if not range_max:
            self._range = General.getActuatorParam(self._class, self._type, "range")

        if not power:
            self._power = General.getActuatorParam(self._class, self._type, "power")

        if not resilience:
            self._resilience = General.getActuatorParam(self._class, self._type, "resilience")

        if not delta_t:
            self._delta_t = General.getActuatorParam(self._class, self._type, "delta_t")
        
        if not speed:
            self._speed = General.getActuatorParam(self._class, self._type, "speed")

        if not strength:
            self._strength = General.getActuatorParam(self._class, self._type, "strength")

        if not accuracy:
            self._accuracy = General.getActuatorParam(self._class, self._type, "accuracy")

        if not dimension:
            self._dimension = General.getActuatorParam(self._class, self._type, "dimension")

        if not self.checkParam( position, class_, typ, self._power, self._resilience, self._delta_t, self._range ):
            raise Exception("Invalid parameters! Actuator not istantiate.")




    #TEST: OK
    def checkParam( self, position, class_, typ, power, resilience, delta_t, range_max ):
        """Return True if conformity of the parameters is verified"""
        if not( ( range_max and range_max[0] >0 and range_max[1] >0 and range_max[2] >0 ) and ( delta_t and delta_t <= 1 and delta_t >= 0 ) and ( power and power <= 100 and power >= 0 ) and  ( resilience and  resilience <= 100 and resilience >= 0 )):
            return False
        
        if not typ or not class_ or not ( General.checkActuatorTypeAndClass( typ, class_ ) and General.checkPosition( position ) ):
            return False

        return True

    def setStandardParam( self ):
        #"power": 40, "speed": 70, "accuracy": 100, "resilience":20, "strength": 30, "range": None, "delta_t": 0.01
        param = General.getActuatorParam(self._class, self._type)
        self._power = param.power
        self._range = param.range
        self._resilience = param.resilience               
        self._delta_t = param.delta_t
        self._strength = param.strength               
        self._accuracy = param.accuracy               
        self._speed = param.speed               
        

    def isType( self, actuator_type ):
        """Return True if actuator have self._type == actuator_type"""
        return self._type == actuator_type
                        
    

    def isClass( self, actuator_class ):
        """Return True if actuator have self._class == actuator_class"""   
        return self._class == actuator_class
    

    #TEST: OK
    def isClassAndType( self, actuator_class, actuator_type ):
        """Return True if actuator have self._class == actuator_class and self._type == actuator_type """   
        return self._type == actuator_type and self._class == actuator_class

    #TEST: OK
    def exec_command( self, automa, posManager, param ):
        # param: [ position or obj, ..other params ]
        # ACTION_TYPE = ( "move", "run", "take", "catch", "eat", "attack", "escape", "nothing", "shot", "hit" )
        # return actions_info = [boolean for execute action, energy level of actuator]
        # il controllo e la scelta dell'attuatore da utilizzare per un determinato comando viene
        # fatta in automa quindi qui dovresti eseguire l'azione indipendentemente dall'interpretazione del comando
        # l'eventuale movimento, colpo, e conseguenze varie è valutato in automa
        # qui dovresti considerare solo gli effetti sull'attuatore
        # due possibilità o crei specializzazioni di attuatori con exec_command in override
        # oppure inserisci nei parametri del metodo il tipo di attuatore e il comando e qui selezioni
        # il metodo di esecuzione specifico per quell'attuatore. Quindi qui dovrai definire i varii metodi per 
        # ogni attuatore. Forse è meglio utilizzare l'ereditarietà. No definisco qui le diverse funzioni da utilizzare per ogni attuatore       

        if self._class == "object_manipulator":                        
            return self.object_manipulating( automa, posManager, param )

        elif self._class == 'mover':                 
            return self.moving( automa, posManager, param )

        elif self._class == "plasma_launcher" or self._class == "projectile_launcher" or self._class == "object_hitter":
            return self.shooting( automa, posManager, param )

        elif self._class == "object_catcher":
            return self.object_catching( automa, posManager, param )

        elif self._class == "object_assimilator":
            return self.object_assimilating( automa, posManager, param )
        
        else:
            raise Exception("Actuator class not defined")

        return


    # TEST: OK
    def object_manipulating( self, automa, posManager, param ):
        #param[0] = object, param[1]= destination
        obj = param[ 0 ]
        destination = param[ 1 ]
        manipulation_terminated = False# serve per implementare la gestione di manipolazioni che richiedono più task per essere completate

        energy_actuator = self._state.updateEnergy( self._power, self._delta_t )
        # verifica se param[1] destinazione dello spostamento, range attuatore e posizione dell'automa sono idonei per l'esecuzione della attuaione
        if not self.isInRange( destination ):
            logger.logger.debug("Actuator: {0} not executed manipulate action because destination is out of range. destination: {1}, range: {2}, energy_actuator: {3}".format( self._id, destination, self._range, energy_actuator ))
            return [ False, energy_actuator, False ]
    
        # devi considerare che la prima volta inserisce l'evento: l'evento deve poi essere rigestito includendo la fase finale di catch e isnerimento nell'automa
        #duration = 3 # qui valutare la durata in base a l tipo di Hit (es. un plasma può avere una durata di più cicli
        #time2go = 1 # valutare il tempo necessario affinchè il colpo e i sui effetti raggiungano il targe (es: time2go = distanza /velocita qui distanza / power o altro)        
        self.setEvent( automa, obj = obj, typ = "PUSH", duration = 3, time2go = 1, energy = None, volume = None, destination = destination) # duration = 0 -> effetti evento già applicati su object

        return [ True, energy_actuator, manipulation_terminated ]

        

    # TEST: OK
    def object_assimilating( self, automa, posManager, param ):
        """Execute catching action and return action_info"""
        # action_type: object_assimilting
        #param[0] = object, param[1]= destination                    
        obj = param[ 0 ]       
        energy_actuator = self._state.updateEnergy( self._power, self._delta_t )
        # verifica se param[1] destinazione dello spostamento, range attuatore e posizione dell'automa sono idonei per l'esecuzione della attuaione
        if not self.isInRange( obj.getPosition() ):
            logger.logger.debug("Actuator: {0} not executed assimilate action because object not in range. automa: {1}, object position: {2}, range: {3}, energy_actuator: {4}".format( self._id, obj.getCaught_from(), obj.getPosition(), self._range, energy_actuator ) )
            return [ False, energy_actuator, True ]# imposto assimilating_terminated = True per consentire l'eliminazione della action nella coda delle action
       
        # devi considrare che la prima volta inserisce l'evento: l'evento deve poi essere rigestito includendo la fase finale di catch e isnerimento nell'automa
        #duration = 1 # qui valutare la durata in base a l tipo di Hit (es. un plasma può avere una durata di più cicli
        #time2go = 1 # valutare il tempo necessario affinchè il colpo e i sui effetti raggiungano il targe (es: time2go = distanza /velocita qui distanza / power o altro)
        self.setEvent( automa, obj = obj, typ = "ASSIMILATE", duration = 1, time2go = 1, energy = None, volume = None, destination = None) # duration = 0 -> effetti evento già applicati su object
        
        return [ True, energy_actuator, False ]


                
    
    # TEST: OK
    def moving( self, automa, posManager, param ):
        """Execute move action and return action_info"""
        # action_type: move
        # param: [target_position, speed_perc], position è la posizione verso cui muovere[ action_type, position or obj, ..other params ]
        # direction: 
        # foward, foward_left. foward_right, foward_up_left, foward_up_right, foward_down_left, foward_down_right, foward_up, foward_down
        # backward, backward_left. backward_right, backward_up_left, backward_up_right, backward_down_left, backward_down_right, bacward_up, backward_down       
        # _left, _up_left, _down_left
        # _right, _up_right, _down_right
        # _up, _down
        position_reached = False
        automa_position = automa.getPosition()
        automa_coord = Coordinate( automa_position )
        next_position = param[ 0 ]
        speed_perc = param[ 1 ]
        direction = automa_coord.eval_direction( automa_position, next_position)
        logger.logger.debug("Actuator: {0} from: {1} to: {2} -  Evalutate direction: {3}".format( self._id, automa_position, next_position, direction ))
        energy_actuator = self._state.getEnergy()
        max_dist_for_single_iteration = int( speed_perc * self._speed ) # int( speed_perc * General.MAX_SPEED )
        min_dist_from_pos_to_dest = min( abs( automa_position[ 0 ] - next_position[ 0 ] ), abs( automa_position[ 1 ] - next_position[ 1 ] ), abs( automa_position[ 2 ] - next_position[ 2 ] ) )
        num_iteration = min( max_dist_for_single_iteration,  min_dist_from_pos_to_dest) # min_dist_from_pos_to_dest determina il massimo numero di posizioni che è possibile percorrere limitando di fatto lo spostamento possibile nelle altre dimensioni: sarebbe necessario gestire il movimento distinguendo ogni lo spostamento in ogni dimensione

        if max_dist_for_single_iteration >= min_dist_from_pos_to_dest:
            position_reached = True

        logger.logger.debug("Actuator: {0} -  max_dist_for_single_iteration: {1},  min_dist_from_pos_to_dest: {2},  num Iteration: {3} ".format( self._id, max_dist_for_single_iteration,  min_dist_from_pos_to_dest, num_iteration ))

        for i in range( num_iteration ):# la velocità determina il numero di iterazioni
            automa_coord.move( direction )
            automa_position = automa_coord.getPosition()
            
            if not posManager.moveObject( automa_coord.getPosition(), automa ):
                logger.logger.debug("Actuator: {0} not executed move action. Iteration: {1} Energy_actuator {2}  position_reached {3}".format( self._id, i, energy_actuator, position_reached ))
                return False, energy_actuator, position_reached
            # l'energia è presente nello stato dell'attuatore, tuttavia è l'automa che fornisce energia all'attuatore quindi ha senso 
            # restituire all'automa la info sul consumo energetico relativo alla perception
            # In questa prima versione decremento solo l'energia dell'attuatore, quando questa diventa 0 l'automa deve 
            # ricaricare l'energia dell'attuatore tramite la propria energia (con un fattore di  moltiplicazione: 1 energia automa = x energia sensore)
            energy_actuator = self._state.updateEnergy( self._power * speed_perc, self._delta_t )
            logger.logger.debug("Actuator: {0} executed move action. Iteration: {1} Energy_actuator {2} position_reached {3}".format( self._id, i, energy_actuator, position_reached ))
        
            if automa_position[ 0 ] == next_position[ 0 ] and automa_position[ 1 ] == next_position[ 1 ] and automa_position[ 2 ] == next_position[ 2 ]:
                logger.logger.debug("Actuator: {0} executed move action. Iteration: {1} Energy_actuator {2}  position_reached {3}".format( self._id, i, energy_actuator, position_reached ))            
                return True, energy_actuator, position_reached
            # nota: non registri l'evento in quanto questa manovra non coinvolge altri oggetti        
        return True, energy_actuator, position_reached

    # TEST: OK
    def object_catching( self, automa, posManager, param ):
        """Execute catching action and return action_info"""
        # action_type: catch
        #param[0] = object, param[1]= destination
        catch_terminated = False# serve per implementare la gestione di catture che richiedono più task per essere completate
        obj = param[ 0 ]       
        
        energy_actuator = self._state.updateEnergy( self._power, self._delta_t )

        # verifica se param[1] destinazione dello spostamento, range attuatore e posizione dell'automa sono idonei per l'esecuzione della attuaione
        if not self.isInRange( obj.getPosition() ):
            logger.logger.debug("Actuator: {0} not executed catch action because object not in range. automa catcher: {1}, object position: {2}, range: {3}, energy_actuator: {4}".format( self._id, obj.getCaught_from(), obj.getPosition(), self._range, energy_actuator ) )
            return [ False, energy_actuator, True ]
       
        # devi considrare che la prima volta inserisce l'evento: l'evento deve poi essere rigestito includendo la fase finale di catch e isnerimento nell'automa
        #duration = 3 # qui valutare la durata in base a l tipo di Hit (es. un plasma può avere una durata di più cicli
        #time2go = 1 # valutare il tempo necessario affinchè il colpo e i sui effetti raggiungano il targe (es: time2go = distanza /velocita qui distanza / power o altro)
        self.setEvent( automa, obj = obj, typ = "POP", duration = 3, time2go = 1, energy = None, volume = None, destination = None) # duration = 0 -> effetti evento già applicati su object
    
        return [ True, energy_actuator, catch_terminated ]

        


    # TEST: OK
    def shooting( self, automa, posManager, param):
        """Execute projectile launching action and return action_info"""
        # action_type: shot
        #param[0] = object, param[1]= destination

        #NOTA: lo shooting è imèplementato iin modo da applicare immediatamente gli effetti dell'HIT utilizzando il Position_manager per gestire l'eventuale eliminazione
        # del target. Nello sviluppo successivo posso considerare la valutazione degli effetti dell'HIT nel Task (ciclo) del target mediante l'evento. In questo modo gli elementi da 
        # considerare sono: cosa deve sapere l'automa degli effetti del HIT subiti dal target e come (se l'oggetto viene distrutto viene eliminato e quindi non sarà più visibile dall'Automa nella fase Perception del suo successivo task)
        # eventualmente un eventuale danno può aumentatare l'impronta infrarossa o radio o altro ....
        # Nota: deve essere quantificato il tempo (in task -cicli) necessario affinchè l'HIT colpisca il target e inserito nell'evento come time2go (la duration è 1). Questo tempo deve essere differenziato in base al tipo di shooting
        
        firing_terminated = True
        obj = param[ 0 ]# cambiare param[0] dovrebbe riportare solo la posizione dell'oggetto       
        energy_actuator = self._state.updateEnergy( self._power, self._delta_t )
        # verifica se param[1] destinazione del proiettile, range attuatore e posizione dell'automa sono idonei per l'esecuzione della attuaione
        if not self.isInRange( obj.getPosition() ):
            logger.logger.debug("Actuator: {0} not executed projectile launch action because object not in range. automa: {1}, object position: {2}, range: {3}, energy_actuator: {4}".format( self._id, automa.getId(), obj.getPosition(), self._range, energy_actuator ) )
            return [ False, energy_actuator, firing_terminated ]
       
        # creazione evento e inserimento nella lista degli eventi dell'oggetto: quinndi anche un semplice object deve avere una lista degli eventi
        # oppure è il position manager che deve gestire l'applicazione degli effetti dell'evento ed come viene fatto qui cioè nl mommento di creazione dell'evento da parte dell'auttuatore
        # ma in questo caso non viene considerato il tempo necessario per l'esecuzione dell'attuazione
        # si 
        # può fre in questo modo: se il taret è un automa si crea l'evento e lo si inserisce nella event queue, se invece è un object si applicano direttamente gli effetti (trascurando il tempo di attuazione)
        # no deve essere realizzata una event queue anche per l'object

        #duration = 1 # qui valutare la durata in base al tipo di Hit (es. un plasma può avere una durata di piiiù cicli
        #time2go = 1 # valutare il tempo necessario affinchè il colpo e i sui effetti raggiungano il targe (es: time2go = distanza /velocita qui distanza / power o altro)
        self.setEvent( automa, obj = obj, typ = "HIT", duration = 1, time2go = 1, energy = None, volume = None, destination = None) # duration = 0 -> effetti evento già applicati su object
    
        return [ True, energy_actuator, firing_terminated ]


    def setId( self, id = None ):

        if not id:
            return False
        else:
            self._id = id        
            
        return True

    def getId( self ):
        return self._id

    def setName(self, name):

        if not name:
            return False
        else:
            self._name = name

        return True

    def eval_command(self, request_action):
        # Valuta quali attuatori attivare e come attivarli in base alle info contenute in request_action (class Action)
        # Restituisce le informazioni sulle azioni effettuate quali stato, posizione degli attuatori
        action_info = None
        return action_info


    #TEST: OK
    def checkActuatorClass(self, actuator):
        """Return True if actuators is a actuator object otherwise False"""
        if not actuator or not isinstance(actuator, Actuator):
            return False
        
        return True


    #TEST: OK
    def checkActuatorList(self, actuators):

        """Return True if actuators is a list of Actuator object otherwise False"""
        if actuators and isinstance(actuators, list) and all( isinstance(actuator, Actuator) for actuator in actuators ):
            return True

        return False


    def isOperative(self):
        """Return true if actuator state is running"""
        return self._state.isRunning()


    # TEST: OK
    def evalutateSelfDamage(self, power):
        """Evalutate the damage on actuator and update state"""
        if power > self._resilience:
            damage = power - self._resilience# in realtà il danno dovrebbe essere proporzionale all'energia
            return self._state.decrementHealth( damage )
        
        return self._state.getHealth()


    def isInRange(self, destination):
        """Return True if abs( destination - position) <= range"""
        return ( abs( destination[ 0 ] - self._position[ 0 ] ) <= self._range[ 0 ] ) and ( abs( destination[ 1 ] - self._position[ 1 ] ) <= self._range[ 1 ] ) and ( abs( destination[ 2 ] - self._position[ 2 ] ) <= self._range[ 2 ] ) 


    def setEvent(self, automa, obj, typ, duration = 1, time2go = 0, energy = None, volume = None, destination = None):
        """Set event in Object's Event Queue if object is an istance of Automa"""
        power = self._power
        mass = self._mass 

        if automa.checkObjectClass( obj ):
            #(self, typ, volume,  time2go = 1, duration = 1, energy = None, power = None, mass = None  
            event = Event( typ = typ, volume = volume, duration = duration, time2go = time2go, energy = energy, power = power, mass = mass, obj = automa, destination = destination ) # duration = 0 -> effetti evento già applicati su object
            obj.insertEvent( event ) 
            logger.logger.debug("Actuator: {0} set event = {1}. Inserted event in object's event queue: event._id: {2}, event._typ: {3}, event._volume: {4}, event._time2go: {5}, event._duration: {6}, event._energy: {7}, event._power: {8}, event._mass: {9}".format( self._id, typ, event._id, event._type, event._volume, event._time2go, event._duration, event._energy, event._power, event._mass ))        

        return True

    
    def getActuatorFootPrint( self ):
        """Return an integer FootPrint for this actuator"""
        #
        # nota: il codice cambia ad ogni nuova sessione di python. Quindi se si prevede il salvataggio di una sessione è necessario sostituire la funzione hash() utilizzata
        #
        dim_str = '.'.join(str(p) for p in self._dimension )
        return hash( self._class + "-" + self._type + "-" + dim_str )