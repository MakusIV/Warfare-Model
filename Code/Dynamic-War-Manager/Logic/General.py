### General Methods

import random
import logging
import os
import math

# LOGGING --
# non èpossibile usare la classe Logger per evitare le circular dependencies: Logger importa General e Geneal imprta Logger

logging.basicConfig( level = logging.DEBUG )
# Create a custom logger
logger = logging.getLogger( __name__ )

log_dir = os.path.join(os.path.normpath(os.getcwd()), 'logs')
log_fname = os.path.join(log_dir, 'log_General.log')


# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler( log_fname )
c_handler.setLevel( logging.DEBUG )
f_handler.setLevel( logging.ERROR )

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(funcName)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)


# VALUES

MAX_SPEED = 10 # velocità max in numero di posizioni percorribili in un singolo task. NOTA da sosituire conle speed specificate in ACTUATOR_TYPE che rappresentan le spedd_max per il tipo di attuatore

#SENSOR_TYPE = ( "radio", "thermal", "optical", "nuclear", "electric", "acoustics", "chemist" )

ACTUATOR_CLASS = ( "object_manipulator", "mover", "plasma_launcher", "projectile_launcher", "object_catcher", "object_assimilator", "object_hitter" )

ACTION_TYPE = ( "move", "run", "translate", "catch", "eat", "attack", "nothing", "shot", "hit" )

EVENT_TYPE = ( "PUSH", "POP", "HIT", "ASSIMILATE", "MOVE" ) # la differenza tra PUSH e HIT è nell'energia-potenza impressa, mentre tra POP e ADSORB è che con EAT l'oggetto "preso" dovrebbe essere eliminato

# inserire mass
ACTUATOR_TYPE = {  
    
    "mover":                {   "2-legs": { "power": 40, "speed": 70, "accuracy": 100, "resilience":20, "strength": 30, "range": None, "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "4-legs": { "power": 60, "speed": 60, "accuracy": 70, "resilience": 40, "strength": 60, "range": None, "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "2-wheels": { "power": 20, "speed": 80, "accuracy": 50, "resilience": 30, "strength": 20, "range": None, "delta_t": 0.01, "mass": 20, "dimension": (2,1,1) },
                                "4-wheels": { "power": 30, "speed": 70, "accuracy": 40, "resilience": 60, "strength": 40, "range": None, "delta_t": 0.01, "mass": 20, "dimension": (2,2,1) },
                                "crawler": { "power": 80, "speed": 40, "accuracy": 30, "resilience": 100, "strength": 100, "range": None, "delta_t": 0.01, "mass": 20, "dimension": (2,2,2) },
                                "hoover": { "power": 100, "speed": 100, "accuracy": 10, "resilience": 30, "strength": 70, "range": None, "delta_t": 0.01, "mass": 20, "dimension": (2,2,2) }  },                    

    "object_manipulator":   {   "hand": { "power": 20, "speed": 70, "accuracy": 100, "resilience":20, "strength": 40, "range": (8, 8, 8), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "clamp": { "power": 80, "speed": 50, "accuracy": 60, "resilience": 80, "strength": 100, "range": (10, 10, 10), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "tentacle": { "power": 50, "speed": 80, "accuracy": 40, "resilience": 50, "strength": 80, "range": (15, 15, 15), "delta_t": 0.01, "mass": 20 }, "dimension": (2,2,4)  },

    "projectile_launcher":  {   "heavy_cannon": { "power": 80, "speed": 10, "accuracy": 100, "resilience":100, "strength": 100, "range": (1000, 1000, 1000), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "medium_cannon": { "power": 60, "speed": 30, "accuracy": 85, "resilience": 85, "strength": 85, "range": (700, 700, 700), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "light_cannon": { "power": 40, "speed": 60, "accuracy": 70, "resilience": 70, "strength": 70, "range": (500, 500, 500), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "heavy_machine_gun": { "power": 60, "speed": 70, "accuracy": 60, "resilience":50, "strength": 60, "range": (300, 300, 300), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "medium__machine_gun": { "power": 40, "speed": 85, "accuracy": 50, "resilience": 30, "strength": 50, "range": (150, 150, 150), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "light__machine_gun": { "power": 20, "speed": 100, "accuracy": 30, "resilience": 10, "strength": 30, "range": (100, 100, 100), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) }  },

    "plasma_launcher":      {   "flamethrower": { "power": 50, "speed": 50, "accuracy": 20, "resilience":80, "strength": 70, "range": (20, 20, 20), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "laser": { "power": 70, "speed": 100, "accuracy": 100, "resilience": 50, "strength": 80, "range": (300, 300, 300), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "plasma": { "power": 80, "speed": 80, "accuracy": 60, "resilience": 50, "strength": 100, "range": (100, 100, 100), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) }  },

    "object_catcher":       {   "harpoon": { "power": 40, "speed": 100, "accuracy": 70, "resilience":40, "strength": 80, "range": (100, 100, 100), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "clamp": { "power": 70, "speed": 70, "accuracy": 40, "resilience": 70, "strength": 80, "range": (10, 10, 10), "delta_t": 0.01, "mass": 20, "dimension": (2,2,4) },
                                "hand": { "power": 50, "speed": 50, "accur acy": 90, "resilience": 55, "strength": 50, "range": (8, 8, 8), "delta_t": 0.01, "mass": 20, "dimension": (2,2,1) }  },

    "object_assimilator":   {   "jaw": { "power": 70, "speed": 60, "accuracy": 70, "resilience":80, "strength": 90, "range": (5, 5, 5), "delta_t": 0.01, "mass": 20, "dimension": (2,1,2) },                            
                                "sucker": { "power": 40, "speed": 80, "accuracy": 90, "resilience": 30, "strength": 30, "range": (10, 10, 10), "delta_t": 0.01, "mass": 20, "dimension": (4,1,1) }  },

    "object_hitter":        {   "hammer": { "power": 50, "speed": 100, "accuracy": 60, "resilience":100, "strength": 90, "range": (10, 10, 10), "delta_t": 0.01, "mass": 20, "dimension": (3,2,4) },
                                "chainsaw":  { "power": 80, "speed": 50, "accuracy": 40, "resilience": 70, "strength": 70, "range": (7, 7, 7), "delta_t": 0.01, "mass": 20, "dimension": (5,2,2) },
                                "drill": { "power": 70, "speed": 70, "accuracy": 80, "resilience": 55, "strength": 75, "range": (5, 5, 5), "delta_t": 0.01, "mass": 20, "dimension": (3,1,1) }  }
                    
                    }


SENSOR_TYPE = {  
    
    "radio":                {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } },                                

    "thermal":              {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } },                                

    "optical":              {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } },                                

    "nuclear":              {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } },                                

    "electric":             {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } },                                
    
    "acoustics":            {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } },                                

    "chemist":              {   "simple": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) },
                                "medium": { "power": 100, "emissivity_perception":1, "accuracy": 5, "resilience":100, "strength": 30, "range": (50, 50, 50), "delta_t": 0.01, "mass": 20, "dimension": (2,1,4) } }                                
                    
                    }


# METHODS


def getActuatorParam(_class, _type, param):
    """Return power, speed, accuracy, resilience, strenght for actuator of that _class and _type, otherwise False"""
    
    #if not checkActuatorTypeAndClass(_type, _class) non serve in quanto il controllo viene effettuato al momento della creazione dell'istanza dell'Actuator
    #    return False
    return ACTUATOR_TYPE.get( _class ).get( _type )[param]#values()

def getSensorParam(_class, _type, param):
    """Return power, speed, accuracy, resilience, strenght for actuator of that _class and _type, otherwise False"""
    
    #if not checkActuatorTypeAndClass(_type, _class) non serve in quanto il controllo viene effettuato al momento della creazione dell'istanza dell'Actuator
    #    return False
    return SENSOR_TYPE.get( _class ).get( _type )[param]#values()

def checkActionType(_type):
    """Return True if _type is compliance with standard type defined for ACTION_TYPE in General.py"""
    return _type != None and isinstance(_type, str) and any( [ True for el in ACTION_TYPE if el == _type ] )


def checkSensorType(_type):
    """Return True if _type is compliance with standard type defined for Sensor in General.py"""
    return _type != None and isinstance(_type, str) and any( [ True for el in SENSOR_TYPE if el == _type ] )




def checkEventType(_type):
    """Return True if _type is compliance with standard type defined for Event in General.py"""
    return _type != None and isinstance(_type, str) and any( [ True for el in EVENT_TYPE if el == _type ] )

def checkSensorTypeAndClass(_type, _class):
    """Return True if _type and _class are compliance with standard type and class defined for Sensor in General.py"""
    return _type != None and _class != None and isinstance(_type, str) and isinstance(_class, str) and any( [True for key in SENSOR_TYPE.keys() if key == _class] ) and any( [True for key in SENSOR_TYPE[ _class ].keys() if key == _type ] )

def checkActuatorTypeAndClass(_type, _class):
    """Return True if _type and _class are compliance with standard type and class defined for Actuator in General.py"""
    return _type != None and _class != None and isinstance(_type, str) and isinstance(_class, str) and any( [True for key in ACTUATOR_TYPE.keys() if key == _class] ) and any( [True for key in ACTUATOR_TYPE[ _class ].keys() if key == _type ] )


def checkDimension(dimension):
    """ Return True if dimension is a list normalized as dimension:  dimension: [int dim_x, int dim_y, int dim_z]"""

    if not dimension or not ( isinstance(dimension, list) or isinstance(dimension, tuple) ) and not len(dimension) == 3 or not isinstance( dimension[0], int) or not  isinstance( dimension[1], int) or not  isinstance( dimension[2], int):
        return False
    
    return True

def checkPosition(position):
    """ Return True if position is a tuple normalized as dimension:  dimension: ( int dim_x, int dim_y, int dim_z)"""

    if not position or not ( isinstance(position, tuple) and len(position) == 3 ) or not isinstance( position[0], int) or not  isinstance( position[1], int) or not  isinstance( position[2], int):
            return False
    
    return True


def checkVolume(volume):
    """ Return True if volume is an list normalized as volume:  volume: [ [ int x_low, int y_low, int z_low ], [ int x_high, int y_high, int z_high ] ]"""

    if not volume or not isinstance( volume, list ) or len(volume) != 2 or len(volume[0]) != 3  or len(volume[1]) != 3:
         return False
    
    elif not isinstance( volume[0][0], int ) or not isinstance( volume[0][1], int ) or not isinstance( volume[0][2], int ) or not isinstance( volume[1][0], int ) or not isinstance( volume[1][1], int ) or not isinstance( volume[1][2], int ):
             return False

    # LO ESCLUDO DAL TEST IN QUANTO IN UN CONTESTO RELATIVO CON COOORDINATE NEGATIVE I LIMITI SUPERIORI E INFERIORI DEL VOLUME SI INVERTONO ANCHE UTILIZZANDO ABS NON E' POSSIBILE GARANTIRE COERENZA (VEDI Sensibility.get_probability_of_perception)
    #if abs( volume[0][0] ) > abs( volume[1][0] ) and abs( volume[0][1] ) > abs( volume[1][1] ) and abs( volume[0][2] ) > abs( volume[1][2] ):
    #    return False
    
    return True


def setId(name, id):
    """Return string name plus random int 6 digit"""                    
    if not id or not isinstance(id, int):
        id = str( name ) + '_#' + str( random.randint( 1, 999999 ) )  # hashing or radInt
    else:
        id = str( name ) + '_#' + str( id )    
    return id

def setName(name):
    """Return string with name plus random int 4 digit"""            
    if not name or not isinstance( name, str ):
        name = 'unamed_#' + str( random.randint( 1, 9999 ) ) # hashing or radInt
    else:
        name = name + '_#' + str( random.randint( 1, 9999 ) ) # hashing or radInt        
    return name

def calcVectorModule( vect ):
    """Return module of vect"""
    return math.sqrt( vect[0]**2 + vect[1]**2 + vect[2]**2 )

def calcVectorDiff( vect1, vect2):
    """Return vector diff"""
    return ( ( vect2[0] - vect1[0] ), ( vect2[1] - vect1[1] ), ( vect2[1] - vect1[2] ) )

def calcVectorSum( vect1, vect2):
    """Return vector sum"""
    return ( ( vect2[0] + vect1[0] ), ( vect2[1] + vect1[1] ), ( vect2[1] + vect1[2] ) )

def calcScalProd( vect1, vect2):
    # se perpendicolari: prod_scal = 0, se alfa>0, <=90 prod scal > 0, se alfa>90, <=180 prod scal < 0
    """Return scalar product"""
    return vect1[0]*vect2[0] + vect1[1]*vect2[2] + vect1[2]*vect2[2]

def calcVectProd( vect1, vect2):
    """Return scalar product"""
    # ha il modulo proporzionale all'area del parallelogramma formato dai due vettori. Quindi se sono allineati(paralleli) il prod_vect = 0
    # (y1*z2 - z1*y2), (z1*x2 - x1*z2), (x1*y2 - y1*x2)
    return ( ( vect1[1]*vect2[2] - vect1[2]*vect2[1] ), ( vect1[2]*vect2[0] - vect1[0]*vect2[2] ), ( vect1[0]*vect2[1] - vect1[1]*vect2[0] ) )

def calcProbability( probability ):
    """Return true if random number is greater of probability"""
    num = random.uniform(0, 1)
    return num < probability
    