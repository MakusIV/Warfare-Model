### data type

import random
import logging
import os
import math
from sympy import Point, Line, Point3D, Line3D, Sphere, symbols, solve, Eq, sqrt, And

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




# METHODS

# 2D Geometry

# 3D Geometry



def segment_equation(p1, p2):
    """
    Restituisce l'equazione parametrica simbolica di un segmento tra due punti 3D.
    
    Args:
        p1, p2: Oggetti Point3D - Estremi del segmento.

    Returns:
        Tuple con le equazioni parametriche (x(t), y(t), z(t)).
        nota: t:=[0,1] permette di ottenere i punti del segmento (t=0-> p1, t=1 -> p2)
    
        
    Spiegazione

    Punti iniziali e finali:
        I due punti p1 e p2 definiscono gli estremi del segmento.

    Equazioni parametriche:
        x(t)=x1+t⋅(x2−x1)x(t)=x1​+t⋅(x2​−x1​)
        y(t)=y1+t⋅(y2−y1)y(t)=y1​+t⋅(y2​−y1​)
        z(t)=z1+t⋅(z2−z1)z(t)=z1​+t⋅(z2​−z1​)
        
        Dove t∈[0,1]t∈[0,1] rappresenta la frazione lungo il segmento.
    
    Segmento vs Linea:
        SymPy non distingue tra segmenti e linee; usa t∈[0,1]t∈[0,1] per limitare il dominio ai soli punti del segmento.


    """

    if not ( p1 and p2) or not ( isinstance(p1, Point3D) and isinstance(p2, Point3D) ):
        return False
    
    # Definizione della linea 3D
    line = Line3D(p1, p2)

    # Variabile simbolica per il parametro t
    t = symbols('t')

    # Estrazione delle coordinate dei punti estremi
    p1_coords = p1.args
    p2_coords = p2.args

    # Equazioni parametriche del segmento
    x_t = p1_coords[0] + t * (p2_coords[0] - p1_coords[0])
    y_t = p1_coords[1] + t * (p2_coords[1] - p1_coords[1])
    z_t = p1_coords[2] + t * (p2_coords[2] - p1_coords[2])

    return x_t, y_t, z_t


def point_in_segment(p_test, p1, p2):
    """
    Restituisce true se p appartiene a segment (forma parametrica) altrimenti false

     Args:
        p: Oggetto Point3D
        segement: tuple con equazione parametrica del segmento 

    Returns:
        Tuple con le equazioni parametriche (x(t), y(t), z(t)).
        nota: t:=[0,1] permette di ottenere i punti del segmento (t=0-> p1, t=1 -> p2)
    
    """
    if not ( p1 and p2) or not ( isinstance(p1, Point3D) and isinstance(p2, Point3D) ):
        return False
    
    # Equazioni parametriche
    x_t, y_t, z_t = segment_equation(p1, p2)

    # Risolvi per t
    t_solution = solve([Eq(p_test.x, x_t), Eq(p_test.y, y_t), Eq(p_test.z, z_t)])

    # Verifica se il punto è valido nel dominio del segmento
    if t_solution and 0 <= t_solution[0] <= 1:
        return True
    else:
        return False


def get_Semisphere(center, radius):
    """Return semisphere equation, otherwise False"""
    
    # DATA TYPE

    # semisphere

    # Centro della sfera e raggio
    # center = Point3D(0, 0, 0)
    # radius = 5

    if not ( center and radius) or not ( isinstance(center, Point3D) and isinstance(radius, int) ):
        return False

    # Definizione della sfera
    sphere = Sphere(center, radius)
    print(f"Equazione della sfera: {sphere.equation()}")

    # Restrizione alla semisfera superiore (z >= 0)
    semisphere_equation = sphere.equation() & (center[2] + radius >= 0)
    print(f"Equazione della semisfera superiore: {semisphere_equation}")

    return semisphere_equation

    

def line_Intersect(p1, p2, center, radius):
    """
    Calcola i punti di intersezione tra un segmento e una semisfera.
    
    Args:
        p1, p2: Tuple (x, y, z) - Estremi del segmento.
        center: Tuple (cx, cy, cz) - Centro della semisfera.
        radius: Float - Raggio della semisfera.
        
    Returns:
        Lista di punti di intersezione (come Point3D) o False se non ci sono intersezioni.
    """

    if not ( center and radius and p1 and p2) or not ( isinstance(p1, Point3D) and isinstance(p2, Point3D) ):
        return False

    # Variabili simboliche
    t = symbols('t')
    x, y, z = symbols('x y z')
    
    # Estremi del segmento e parametri del segmento
    px1, py1, pz1 = p1
    px2, py2, pz2 = p2
    # cx, cy, cz = center

    # Equazione parametrica del segmento: P(t) = p1 + t * (p2 - p1)
    xt = px1 + t * (px2 - px1)
    yt = py1 + t * (py2 - py1)
    zt = pz1 + t * (pz2 - pz1)

    # Equazione della semisfera: (x - cx)^2 + (y - cy)^2 + (z - cz)^2 = r^2, z >= cz
    # sphere_eq = Eq((xt - cx)**2 + (yt - cy)**2 + (zt - cz)**2, radius**2)
    semisphere_equation =  get_Semisphere(center, radius)
    
    # Risolvi per t
    t_solutions = solve(semisphere_equation, t)

    # Filtra le soluzioni valide
    intersections = []
    for t_sol in t_solutions:
        # Calcola il punto corrispondente a t
        x_sol = xt.subs(t, t_sol)
        y_sol = yt.subs(t, t_sol)
        z_sol = zt.subs(t, t_sol)
        
        # Verifica se il punto è nella semisfera (z >= cz) e nel segmento (t in [0, 1])
        if z_sol >= cz and 0 <= t_sol <= 1:
            intersections.append(Point3D(x_sol, y_sol, z_sol))
    
    # Restituisci i punti trovati o False se non ci sono intersezioni
    return intersections if intersections else False


def tangent_to_semisphere(center, radius, p):
    """
    Calcola la tangente a una semisfera data dal centro e dal raggio, 
    passando per un punto esterno alla semisfera, e restituisce sia 
    i punti di tangenza che le rette tangenti.

    Args:
        center: Tuple (x0, y0, z0) - Coordinate del centro della semisfera.
        radius: Float - Raggio della semisfera.
        p: Tuple (px, py, pz) - Coordinate del punto esterno.

    Returns:
        Un dizionario con:
          - "points": Lista dei punti di tangenza
          - "lines": Lista delle rette tangenti come oggetti Line3D
          - Messaggio di errore se non esistono tangenti.
    """
    # Variabili simboliche per il punto di tangenza
    x, y, z = symbols('x y z')

    # Coordinate del centro e del punto esterno
    x0, y0, z0 = center
    px, py, pz = p

    # Equazione della semisfera (x - x0)^2 + (y - y0)^2 + (z - z0)^2 = r^2
    # sphere_eq = Eq((x - x0)**2 + (y - y0)**2 + (z - z0)**2, radius**2)
    sphere_eq = get_Semisphere(center, radius)

    # Condizione di ortogonalità: il vettore tangente è perpendicolare al vettore dal centro al punto di tangenza
    orthogonality_eq = Eq((x - x0) * (x - px) + (y - y0) * (y - py) + (z - z0) * (z - pz), 0)

    # Risolviamo il sistema di equazioni
    solutions = solve([sphere_eq, orthogonality_eq], (x, y, z))

    if not solutions:
        return "Non esistono tangenti dal punto dato alla semisfera."

    # Lista dei punti di tangenza
    points = [Point3D(sol[x], sol[y], sol[z]) for sol in solutions]

    # Generazione delle rette tangenti
    lines = [Line3D(Point3D(px, py, pz), point) for point in points]

    return {"points": points, "lines": lines}



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
    