
from Coordinate import Coordinate
import General
from State import State
from LoggerClass import Logger
import random
from Sensibility import Sensibility

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Sensor')

class Sensor:
    # Il sensore non è una specializzazione di Object

    # Unit test: ok
    def __init__(self, position, typ, _class, emissivity_perception = None, power = None, resilience = None, delta_t = None, accuracy = None, range_max = None,  strength = None, dimension = None, name = None ):

        self._name = name
        self._class = _class# la grandezza che il sensore misura (vedi General.SENSOR_TYPE)
        self._type = typ# il tipo di sensore
        self._id = General.setId('Sensor_ID', None) # Id generator automaticamente 
        self._state = State( run = True)
        self._position = position
        self._power = power# nota l'energia è gestita nello stato in quanto è variabile
        self._range = range_max# è rappresentato da una tupla di distanze (x_d:int, y_d:int, z_d:int)
        self._sensibility = None
        self._resilience = resilience# resistenza ad uno SHOT in termini di power (se shot power > resilence --> danno al sensore)
        self._delta_t = delta_t# Il tempo necessario per eseguire la detection serve per calcolare il consumo energetico. Puotrà essere utilizzato per gestire eventuali detection che necessitano di più cicli        
        self._emissivity_perception = emissivity_perception# il livello minimo di emessivity che il sensore rileva. Da confrontare con l'emmisivity di un oggetto da rilevare. Più piccolo è questo lavoro e più il sensore è capace di rilevare, 0: rileva tutto
        self._strength = strength
        self._accuracy = accuracy
        self._dimension = dimension        

        if not name or not isinstance(name, str):
            self._name = General.setName('Sensor_Name')
        else:
            self._name = name

        if not range_max:
            self._range = General.getSensorParam(self._class, self._type, "range")

        if not power:
            self._power = General.getSensorParam(self._class, self._type, "power")

        if not resilience:
            self._resilience = General.getSensorParam(self._class, self._type, "resilience")

        if not delta_t:
            self._delta_t = General.getSensorParam(self._class, self._type, "delta_t")
        
        if not emissivity_perception:
            self._emissivity_perception = General.getSensorParam(self._class, self._type, "emissivity_perception")

        if not strength:
            self._strength = General.getSensorParam(self._class, self._type, "strength")

        if not accuracy:
            self._accuracy = General.getSensorParam(self._class, self._type, "accuracy")

        if not dimension:
            self._dimension = General.getSensorParam(self._class, self._type, "dimension")

        self._sensibility = Sensibility( self._range, self._accuracy )

        if not self.checkParam( self._position, self._emissivity_perception, self._type, self._range, self._accuracy,  self._power, self._resilience, self._delta_t, self._class ):
            raise Exception("Invalid parameters! Sensor not istantiate.")


    def checkParam(self, position, emissivity_perception, typ, range_max, accuracy,  power, resilience, delta_t, _class):
        
        if not( range_max and range_max[0] >0 and range_max[1] >0 and range_max[2] >0 and delta_t and delta_t <= 1 and delta_t >= 0 and power and power <= 100 and power >= 0 and  resilience and  resilience <= 100 and resilience >= 0 and  emissivity_perception and  emissivity_perception <= 100 and emissivity_perception > 0):
            return False
        
        if accuracy and accuracy <=0:
            return False
        
        if not typ or not _class or not ( General.checkSensorTypeAndClass( typ, _class ) and General.checkPosition( position ) ):
            return False

        return True

    def getSensorFootPrint( self ):
        """Return an integer FootPrint for this sensor"""
        #
        # nota: il codice cambia ad ogni nuova sessione di python. Quindi se si prevede il salvataggio di una sessione è necessario sostituire la funzione hash() utilizzata
        #
        dim_str = '.'.join(str(p) for p in self._dimension )
        return hash( self._class + "-" + self._type + "-" + dim_str )


    # Unit test: 0k
    def evalutateSelfDamage(self, power):
        """Evalutate the damage on sensor and update state"""
        if power > self._resilience:
            damage = power - self._resilience# in realtà il danno dovrebbe essere proporzionale all'energia
            return self._state.decrementHealth( damage )
        
        return self._state.getHealth()


    def setId(self, id = None):

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

    # test: ok    
    def perception(self, posMng, request_perception = None):
        """Return percept_info: (energy_sensor, detected_objs) detected. detected_objs = { ( x, y, z): obj }"""
        # Attiva il sensore in base alle info contenute in request_perception, se request_perception è None utilizza i parametri di default
        # Restituisce le informazioni sulle azioni effettuate quali stato, posizione degli attuatori

        percept_info = None
        # la perception individua gli oggetti presenti nel volume di scansione in base alla probabilità nel
        # punto di scansione dove è presente l'oggetto. Per quanto riguarda la perception dell'enviroment tenere
        # presente che una zona a temperatura pericolosa è rappresentata da un oggetto di volume pari alla zona
        # interessata con proprietà temperatura. Quindi durante la perception, individutato, l'oggetto
        # obj.isGas() ---> automa.MaxTemp >= obj._temperature
        
        scanning_volumes = self._sensibility.get_probability_of_perception( self._position ) # scanning_volume = (volume, probability)
        detected_objs = dict()

        for item in scanning_volumes:   
            scan_vol = item[0]        
            _, low_vertex, high_vertex, _, _ = posMng.volumeInLimits( scan_vol )

            if not low_vertex:
                #vertici minimi volume fuori i limiti interrompe l'iterazione e l'esecuzione della scansione del volume di ricerca
                break

            if not high_vertex:
                #vertici massimi volume superiori ai limti scaltatura volume di ricerca 
                scan_vol = posMng.volumeNormalization(scan_vol)    
            
            logger.logger.debug("scanning volume {0} to detect object".format( scanning_volumes.index( item ) ))
            prob = random.randint( 1, 100 ) / 100
            volume_prob = item[ 1 ] * self._state.getEfficiency()            
            logger.logger.debug( "prob:{0}, volume_prob:{1}, scanning volume:{2}".format( prob, volume_prob, prob < volume_prob ) )

            if prob < volume_prob:
                detected = posMng.getObjectInVolume( scan_vol )# detected: {  (x,y,z), obj }
                                            
                if detected:
                    logger.logger.debug( "exists {0} objects in sub-volume".format( len(detected) ) )
                    num_object_detected = 0

                    for elem in detected.values():# elem: obj

                        object_emissivity_level = elem.getEmissivityForClass( self._class )
                        
                        if object_emissivity_level >= self._emissivity_perception:
                            detected_objs.update( { elem.getPosition(): elem } )
                            num_object_detected = num_object_detected + 1
                            logger.logger.debug("detected object: {0}  with emissivity type, level: {1}, {2} using intensity sensor: {3}, and inserted in detected object list".format( elem.getId(), self._type, object_emissivity_level, self._emissivity_perception ))
                                                
                    logger.logger.debug( "detected {0} objects and inserted in detected object list".format( num_object_detected ) )

        energy_sensor = self._state.updateEnergy( self._power, self._delta_t )
        
        # l'energia è presente nello stato del sensore, tuttavia è l'automa che fornisce energia al sensore quindi ha senso 
        # restituire all'automa la info sul consumo energetico relativo alla perception
        # In questa prima versione decremento solo l'energia del sensore, quando questa diventa 0 l'automa deve provveedere
        # a ricaricare l'energia del sensore tramite la propria energia (con un fattore di  moltiplicazione: 1 energia automa = x energia sensore)

        #enviroment perception:  temp, emc, gas ecc

        percept_info = (energy_sensor, detected_objs)
        logger.logger.debug("detected {0} objects and consumed {1} energy. Sensor energy avalaible: {2}".format( len( detected_objs ), self._power * self._delta_t, energy_sensor ))
        return percept_info




    # test: ok
    def checkSensorClass(self, sensor):
        """Return True if sensors is a Sensor object otherwise False"""
        if not sensor or not isinstance(sensor, Sensor):
            return False
        
        return True

    def checkSensorList(self, sensors):

        """Return True if sensors is a list of Sensor object otherwise False"""
        if sensors and isinstance(sensors, list) and all( isinstance(sensor, Sensor) for sensor in sensors ):
            return True

        return False

    def isOperative(self):
        """Return true if sensor state is running"""
        return self._state.isRunning()