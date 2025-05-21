### data type

import random 
import logging
import os
#import sys
import math
import hashlib
import uuid
import inspect
from Code.Dynamic_War_Manager.Source.DataType.Sphere import Sphere
from Code.Dynamic_War_Manager.Source.DataType.Hemisphere import Hemisphere
from sympy import Point, Line, Point3D, Point2D, Line3D, symbols, solve, Eq, sqrt, And
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import numpy as np

# LOGGING --
# non è possibile usare la classe Logger per evitare le circular dependencies: Logger importa Utility e Utility imprta Logger
# tuttavia, considerando che Logger importa utility solo per utilizzare il metodo setName(), elimina la questo utilizzo ed implementa qui logger

logging.basicConfig( level = logging.DEBUG )
# Create a custom logger
logger = logging.getLogger( __name__ )

log_dir = os.path.join(os.path.normpath(os.getcwd()), 'logs')
log_fname = os.path.join(log_dir, 'log_Utility.log')


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


# GLOBAL DATA



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


def checkEventType(_type):
    """Return True if _type is compliance with standard type defined for Event in General.py"""
    return _type != None and isinstance(_type, str) and any( [ True for el in EVENT_TYPE if el == _type ] )


def setId(name: str, id = None ):
    """Return string name plus random int 6 digit"""                    
    if not id or not isinstance(id, int):
        # Genera un identificativo univoco basato su codifica hash e generazione casuale di numeri
        hash_object = hashlib.sha256((name + str(uuid.uuid4())).encode())
        id = str( name ) + '_#' + str( int(hash_object.hexdigest(), 16) % 10**6 )  # hashing or radInt
    else:
        id = str( id )    
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
    
def enemySide(side):
    """Return enemy side"""
    if side == 'Blue':
        return 'Red'
    elif side == 'Red':
        return 'Blue'
    else:
        return "Neutral"


# FUZZY LOGIC METHODS

# Conversione dell'output in stringa usando le funzioni di appartenenza Funzione privata di calcProductionTargetPriority, calcStorageTargetPriority, calcTransportLineTargetPriority
def get_membership_label(output_value, variable):
    """
    Conversione dell'output in stringa usando le funzioni di appartenenza 
    Funzione privata di:
    calcProductionTargetPriority, calcStorageTargetPriority, calcTransportLineTargetPriority
    
    """
    max_membership = 0
    label = None
    for term in variable.terms:
        membership_value = fuzz.interp_membership(variable.universe, variable[term].mf, output_value)
        if membership_value > max_membership:
            max_membership = membership_value
            label = term
    return label


def calc_Production_Target_Priority(target_priority, production_efficiency):
    """
    Calculate Priority of Production Target using Fuzzy Logic.

    input param: 
    target_priority (string): ['L', 'M', 'H', 'VH'] oppure float: [0,1], da utilizzare come parametro di condizionamento oppure per un altra variabile d'influenza
    production_efficiency (float): [0,1]

    return (string): ['L', 'M', 'H', 'VH'] 

    TEST:  OK CON JUPITER NOTEBOOK
    """

    # Variabili di input
    t_p = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 't_p')  # target priority  0=L, 0.33=M, 0.66=H, 1=VH    
    p_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_e')  # production efficiency Valori continui [0, 1]

    # Variabile di output
    t_p_p = ctrl.Consequent(np.arange(0, 1.01, 0.01), 't_p_p')  # target production priority Valori: 0=L, 0.33=M, 0.66=H, 1=VH

    # Funzioni di appartenenza target production efficiency
    # t_p.automf(names=['L', 'M', 'H', 'VH'])    
    if isinstance(target_priority, str):
        t_p['L'] = 0
        t_p['M'] = 0.33
        t_p['H'] = 0.66
        t_p['VH'] = 1

    t_p['L'] = fuzz.trimf(t_p.universe, [0, 0, 1/3])
    t_p['M'] = fuzz.trimf(t_p.universe, [0, 1/3, 2/3])
    t_p['H'] = fuzz.trimf(t_p.universe, [1/3, 2/3, 1])
    t_p['VH'] = fuzz.trimf(t_p.universe, [2/3, 1, 1])

    p_e['L'] = fuzz.trapmf(p_e.universe, [0, 0, 0.3, 0.35])
    p_e['M'] = fuzz.trapmf(p_e.universe, [0.3, 0.35, 0.6, 0.65])
    p_e['H'] = fuzz.trapmf(p_e.universe, [0.6, 0.65, 0.85, 0.95])
    p_e['VH'] = fuzz.trapmf(p_e.universe, [0.9, 0.95, 1, 1])
   
    t_p_p.automf(names=['L', 'M', 'H', 'VH'])

    # Definizione delle regole
    rules = [
        ctrl.Rule(t_p['VH'] & p_e['VH'], t_p_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['H'], t_p_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['M'], t_p_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['L'], t_p_p['M']),
        ctrl.Rule(t_p['H'] & p_e['VH'], t_p_p['VH']),
        ctrl.Rule(t_p['H'] & p_e['H'], t_p_p['H']),
        ctrl.Rule(t_p['H'] & p_e['M'], t_p_p['M']),
        ctrl.Rule(t_p['H'] & p_e['L'], t_p_p['M']),
        ctrl.Rule(t_p['M'] & p_e['VH'], t_p_p['H']),
        ctrl.Rule(t_p['M'] & p_e['H'], t_p_p['M']),
        ctrl.Rule(t_p['M'] & p_e['M'], t_p_p['M']),
        ctrl.Rule(t_p['M'] & p_e['L'], t_p_p['L']),
        ctrl.Rule(t_p['L'] & p_e['VH'], t_p_p['M']),
        ctrl.Rule(t_p['L'] & p_e['H'], t_p_p['M']),
        ctrl.Rule(t_p['L'] & p_e['M'], t_p_p['L']),
        ctrl.Rule(t_p['L'] & p_e['L'], t_p_p['L']),        
    ]


    # Aggiunta delle regole al sistema di controllo
    t_p_p_ctrl = ctrl.ControlSystem(rules)
    t_p_p_sim = ctrl.ControlSystemSimulation(t_p_p_ctrl)

    # Mappa per convertire i valori stringa in interi per t_p
    #string_to_value = {'L': 0, 'M': 0.33, 'H': 0.66, 'VH': 1}

    # Esempio di input e calcolo
    # t_p_value = string_to_value[target_priority]  # Cambia qui con 'L', 'M', 'H', o 'VH'
    t_p_p_sim.input['t_p'] = target_priority# t_p_value    
    t_p_p_sim.input['p_e'] = production_efficiency #0.9

    # Calcolo dell'output
    t_p_p_sim.compute()
    output_numeric = t_p_p_sim.output['t_p_p']

    output_string = get_membership_label(output_numeric, t_p_p)

    return output_string, output_numeric
    #print("Valore numerico di t_p_p:", output_numeric)
    #print("Valore stringa di t_p_p:", output_string)


def calc_Storage_Target_Priority(target_priority, production_efficiency, storage_efficiency):
    """
    Calculate Priority of Transport Line Target using Fuzzy Logic.

    input param: 
    target_priority (string): ['L', 'M', 'H', 'VH'] o float: [0,1], da utilizzare come parametro di condizionamento oppure per un altra variabile d'influenza
    transport_line_efficiency, storage_efficiency (float): [0,1]

    return (string): ['L', 'M', 'H', 'VH'] 

    TEST: OK CON JUPITER NOTEBOOK
    """

    # Variabili di input
    t_p = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 't_p')  # target priority 0=L, 0.33=M, 0.66=H, 1=VH
    p_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'p_e')  # production efficiency Valori continui [0, 1]
    s_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 's_e')  # storage efficiency Valori continui [0, 1]

    # Variabile di output
    t_s_p = ctrl.Consequent(np.arange(0, 1.01, 0.01), 't_s_p')  # target storage priority Valori continui [0, 1]

    # Funzioni di appartenenza
    #t_p.automf(names=['L', 'M', 'H', 'VH'])
    if isinstance(target_priority, str):
        
        if target_priority not in ['L', 'M', 'H', 'VH']: 
            raise ValueError("Invalid target priority value. Must be 'L', 'M', 'H', or 'VH'.")
        
        if target_priority == 'L': t_p['L'] = 0
        elif target_priority == 'M': t_p['M'] = 0.33
        elif target_priority == 'H': t_p['H'] = 0.66
        else: t_p['VH'] = 1

    t_p['L'] = fuzz.trimf(t_p.universe, [0, 0, 1/3])
    t_p['M'] = fuzz.trimf(t_p.universe, [0, 1/3, 2/3])
    t_p['H'] = fuzz.trimf(t_p.universe, [1/3, 2/3, 1])
    t_p['VH'] = fuzz.trimf(t_p.universe, [2/3, 1, 1])

    p_e['L'] = fuzz.trapmf(p_e.universe, [0, 0, 0.3, 0.35])
    p_e['M'] = fuzz.trapmf(p_e.universe, [0.3, 0.35, 0.6, 0.65])
    p_e['H'] = fuzz.trapmf(p_e.universe, [0.6, 0.65, 0.85, 0.95])
    p_e['VH'] = fuzz.trapmf(p_e.universe, [0.9, 0.95, 1, 1])
    
    s_e['L'] = fuzz.trapmf(s_e.universe, [0, 0, 0.2, 0.3])
    s_e['M'] = fuzz.trapmf(s_e.universe, [0.25, 0.4, 0.5, 0.6])
    s_e['H'] = fuzz.trapmf(s_e.universe, [0.55, 0.75, 0.85, 0.95])
    s_e['VH'] = fuzz.trapmf(s_e.universe, [0.85, 0.95, 1, 1])
    
    t_s_p.automf(names=['L', 'M', 'H', 'VH'])

    # Definizione delle regole
    rules = [
        ctrl.Rule(t_p['VH'] & p_e['VH'] & s_e['VH'], t_s_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['VH'] & s_e['H'], t_s_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['VH'] & s_e['M'], t_s_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['VH'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['VH'] & p_e['H'] & s_e['VH'], t_s_p['VH']),
        ctrl.Rule(t_p['VH'] & p_e['H'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['H'] & s_e['M'], t_s_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['H'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['VH'] & p_e['M'] & s_e['VH'], t_s_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['M'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['VH'] & p_e['M'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['VH'] & p_e['M'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['VH'] & p_e['L'] & s_e['VH'], t_s_p['L']),
        ctrl.Rule(t_p['VH'] & p_e['L'] & s_e['H'], t_s_p['L']),
        ctrl.Rule(t_p['VH'] & p_e['L'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['VH'] & p_e['L'] & s_e['L'], t_s_p['L']),
        
        ctrl.Rule(t_p['H'] & p_e['VH'] & s_e['VH'], t_s_p['VH']),
        ctrl.Rule(t_p['H'] & p_e['VH'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['VH'] & s_e['M'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['VH'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['H'] & s_e['VH'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['H'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['H'] & s_e['M'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['H'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['M'] & s_e['VH'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['M'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['H'] & p_e['M'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['M'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['L'] & s_e['VH'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['L'] & s_e['H'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['L'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['H'] & p_e['L'] & s_e['L'], t_s_p['L']),
        
        ctrl.Rule(t_p['M'] & p_e['VH'] & s_e['VH'], t_s_p['H']),
        ctrl.Rule(t_p['M'] & p_e['VH'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['M'] & p_e['VH'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['VH'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['H'] & s_e['VH'], t_s_p['H']),
        ctrl.Rule(t_p['M'] & p_e['H'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['M'] & p_e['H'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['H'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['M'] & s_e['VH'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['M'] & s_e['H'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['M'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['M'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['L'] & s_e['VH'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['L'] & s_e['H'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['L'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['M'] & p_e['L'] & s_e['L'], t_s_p['L']),
        
        ctrl.Rule(t_p['L'] & p_e['VH'] & s_e['VH'], t_s_p['H']),
        ctrl.Rule(t_p['L'] & p_e['VH'] & s_e['H'], t_s_p['H']),
        ctrl.Rule(t_p['L'] & p_e['VH'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['VH'] & s_e['L'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['H'] & s_e['VH'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['H'] & s_e['H'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['H'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['H'] & s_e['L'], t_s_p['L']),
        ctrl.Rule(t_p['L'] & p_e['M'] & s_e['VH'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['M'] & s_e['H'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['M'] & s_e['M'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['M'] & s_e['L'], t_s_p['L']),
        ctrl.Rule(t_p['L'] & p_e['L'] & s_e['VH'], t_s_p['M']),
        ctrl.Rule(t_p['L'] & p_e['L'] & s_e['H'], t_s_p['L']),
        ctrl.Rule(t_p['L'] & p_e['L'] & s_e['M'], t_s_p['L']),
        ctrl.Rule(t_p['L'] & p_e['L'] & s_e['L'], t_s_p['L']),
    ]


    # Aggiunta delle regole al sistema di controllo
    t_s_p_ctrl = ctrl.ControlSystem(rules)
    t_s_p_sim = ctrl.ControlSystemSimulation(t_s_p_ctrl)

    # Mappa per convertire i valori stringa in interi per t_p
    #string_to_value = {'L': 0, 'M': 0.33, 'H': 0.66, 'VH': 1}

    # Esempio di input e calcolo
    #t_p_value = string_to_value[target_priority]  # Cambia qui con 'L', 'M', 'H', o 'VH'
    t_s_p_sim.input['t_p'] = target_priority # t_p_value
    t_s_p_sim.input['p_e'] = production_efficiency #0.95
    t_s_p_sim.input['s_e'] = storage_efficiency #0.9

    # Calcolo dell'output
    t_s_p_sim.compute()
    output_numeric = t_s_p_sim.output['t_s_p']

    output_string = get_membership_label(output_numeric, t_s_p)

    return output_string, output_numeric
    #print("Valore numerico di t_s_p:", output_numeric)
    #print("Valore stringa di t_s_p:", output_string)


def calc_Transport_Line_Target_Priority(target_priority, transport_line_efficiency, storage_efficiency):
    """
    Calculate Priority of Transport Line Target using Fuzzy Logic.

    input param: 
    target_priority (string): ['L', 'M', 'H', 'VH'] oppure float: [0,1], rappresenta la target priority riferita alla military base connessa alle Transport Line
    transport_line_efficiency, storage_efficiency (float): [0,1]

    return (string): ['L', 'M', 'H', 'VH'] 

    TEST: OK CON JUPITER NOTEBOOK
    """

    # Variabili di input
    t_p = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 't_p')  # target priority  0=L, 0.33=M, 0.66=H, 1=VH 
    l_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'l_e')  # transport line efficiency Valori continui [0, 1]
    s_e = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 's_e')  # storage efficiency Valori continui [0, 1]

    # Variabile di output
    t_l_p = ctrl.Consequent(np.arange(0, 1.01, 0.01), 't_l_p')  # target trasnsport line priority Valori continui [0, 1]

    # Funzioni di appartenenza    
    #t_p.automf(names=['L', 'M', 'H', 'VH'])
    if isinstance(target_priority, str):
        t_p['L'] = 0
        t_p['M'] = 0.33
        t_p['H'] = 0.66
        t_p['VH'] = 1
    
    t_p['L'] = fuzz.trimf(l_e.universe, [0, 0, 1/3])
    t_p['M'] = fuzz.trimf(l_e.universe, [0, 1/3, 2/3])
    t_p['H'] = fuzz.trimf(l_e.universe, [1/3, 2/3, 1])
    t_p['VH'] = fuzz.trimf(l_e.universe, [2/3, 1, 1])

    l_e['L'] = fuzz.trapmf(l_e.universe, [0, 0, 0.2, 0.35])
    l_e['M'] = fuzz.trapmf(l_e.universe, [0.3, 0.4, 0.6, 0.7])
    l_e['H'] = fuzz.trapmf(l_e.universe, [0.65, 0.75, 0.8, 0.85])
    l_e['VH'] = fuzz.trapmf(l_e.universe, [0.8, 0.95, 1, 1])

    s_e['L'] = fuzz.trapmf(s_e.universe, [0, 0, 0.2, 0.3])
    s_e['M'] = fuzz.trapmf(s_e.universe, [0.25, 0.4, 0.5, 0.6])
    s_e['H'] = fuzz.trapmf(s_e.universe, [0.55, 0.75, 0.85, 0.95])
    s_e['VH'] = fuzz.trapmf(s_e.universe, [0.85, 0.95, 1, 1])
    
    t_l_p.automf(names=['L', 'M', 'H', 'VH'])

    # Definizione delle regole
    rules = [
        ctrl.Rule(t_p['VH'] & l_e['VH'] & s_e['VH'], t_l_p['VH']),
        ctrl.Rule(t_p['VH'] & l_e['VH'] & s_e['H'], t_l_p['VH']),
        ctrl.Rule(t_p['VH'] & l_e['VH'] & s_e['M'], t_l_p['H']),
        ctrl.Rule(t_p['VH'] & l_e['VH'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['VH'] & l_e['H'] & s_e['VH'], t_l_p['VH']),
        ctrl.Rule(t_p['VH'] & l_e['H'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['VH'] & l_e['H'] & s_e['M'], t_l_p['H']),
        ctrl.Rule(t_p['VH'] & l_e['H'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['VH'] & l_e['M'] & s_e['VH'], t_l_p['H']),
        ctrl.Rule(t_p['VH'] & l_e['M'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['VH'] & l_e['M'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['VH'] & l_e['M'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['VH'] & l_e['L'] & s_e['VH'], t_l_p['L']),
        ctrl.Rule(t_p['VH'] & l_e['L'] & s_e['H'], t_l_p['L']),
        ctrl.Rule(t_p['VH'] & l_e['L'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['VH'] & l_e['L'] & s_e['L'], t_l_p['L']),
        
        ctrl.Rule(t_p['H'] & l_e['VH'] & s_e['VH'], t_l_p['VH']),
        ctrl.Rule(t_p['H'] & l_e['VH'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['VH'] & s_e['M'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['VH'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['H'] & s_e['VH'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['H'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['H'] & s_e['M'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['H'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['M'] & s_e['VH'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['M'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['H'] & l_e['M'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['M'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['L'] & s_e['VH'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['L'] & s_e['H'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['L'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['H'] & l_e['L'] & s_e['L'], t_l_p['L']),
        
        ctrl.Rule(t_p['M'] & l_e['VH'] & s_e['VH'], t_l_p['H']),
        ctrl.Rule(t_p['M'] & l_e['VH'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['M'] & l_e['VH'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['VH'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['H'] & s_e['VH'], t_l_p['H']),
        ctrl.Rule(t_p['M'] & l_e['H'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['M'] & l_e['H'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['H'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['M'] & s_e['VH'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['M'] & s_e['H'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['M'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['M'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['L'] & s_e['VH'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['L'] & s_e['H'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['L'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['M'] & l_e['L'] & s_e['L'], t_l_p['L']),
        
        ctrl.Rule(t_p['L'] & l_e['VH'] & s_e['VH'], t_l_p['H']),
        ctrl.Rule(t_p['L'] & l_e['VH'] & s_e['H'], t_l_p['H']),
        ctrl.Rule(t_p['L'] & l_e['VH'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['VH'] & s_e['L'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['H'] & s_e['VH'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['H'] & s_e['H'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['H'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['H'] & s_e['L'], t_l_p['L']),
        ctrl.Rule(t_p['L'] & l_e['M'] & s_e['VH'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['M'] & s_e['H'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['M'] & s_e['M'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['M'] & s_e['L'], t_l_p['L']),
        ctrl.Rule(t_p['L'] & l_e['L'] & s_e['VH'], t_l_p['M']),
        ctrl.Rule(t_p['L'] & l_e['L'] & s_e['H'], t_l_p['L']),
        ctrl.Rule(t_p['L'] & l_e['L'] & s_e['M'], t_l_p['L']),
        ctrl.Rule(t_p['L'] & l_e['L'] & s_e['L'], t_l_p['L']),
    ]


    # Aggiunta delle regole al sistema di controllo
    t_l_p_ctrl = ctrl.ControlSystem(rules)
    t_l_p_sim = ctrl.ControlSystemSimulation(t_l_p_ctrl)

    # Mappa per convertire i valori stringa in interi per t_p
    #string_to_value = {'L': 0, 'M': 0.33, 'H': 0.66, 'VH': 1}

    # Esempio di input e calcolo
    #t_p_value = string_to_value[target_priority]  # Cambia qui con 'L', 'M', 'H', o 'VH'
    t_l_p_sim.input['t_p'] = target_priority #t_p_value
    t_l_p_sim.input['l_e'] = transport_line_efficiency #0.95
    t_l_p_sim.input['s_e'] = storage_efficiency #0.9

    # Calcolo dell'output
    t_l_p_sim.compute()
    output_numeric = t_l_p_sim.output['t_l_p']

    output_string = get_membership_label(output_numeric, t_l_p)

    return output_string, output_numeric
    #print("Valore numerico di t_l_p:", output_numeric)
    #print("Valore stringa di t_l_p:", output_string)


def calc_Threat_Level(pointDistance2D: float, threatRadius: float, pointHeight: float, maxThreatHeight: float):
    """
    Calculate anti-aircraft threat Level using Fuzzy Logic

    input param:     
    pointDistance2D: planar distance from point to center of threath - float, 
    threatRadius: radius of threath - float, 
    pointHeight: height of point - float, 
    maxThreatHeight: height of threath - float
    
    

    return (string): ['L', 'M', 'H', 'VH'] 

    TEST:
    """

    if pointDistance2D <= 0 or threatRadius <= 0 or pointHeight <= 0 or maxThreatHeight <= 0:
        raise ValueError("Input values must be positive and non-zero.")
        
    if pointDistance2D > threatRadius or pointHeight > maxThreatHeight:
        return 'L', 1

    # Variabili di input
    kd = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'kd')  # kd = pointDistance2D / threatRadius Valori continui [0, 1]
    kh = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'kh')  # kh = pointHeight / maxThreatHeight Valori continui [0, 1]

    # Variabile di output
    t_l_p = ctrl.Consequent(np.arange(0, 1.01, 0.01), 't_l_p')  # target trasnsport line priority Valori continui [0, 1]

    # Funzioni di appartenenza
    kd['L'] = fuzz.trapmf(kd.universe, [0.85, 0.9, 1, 1])
    kd['M'] = fuzz.trapmf(kd.universe, [0.7, 0.8, 0.85, 0.9])
    kd['H'] = fuzz.trapmf(kd.universe, [0.4, 0.5, 0.7, 0.8])
    kd['VH'] = fuzz.trapmf(kd.universe, [0, 0, 0.3, 0.6])

    kh['L'] = fuzz.trapmf(kh.universe, [0.85, 0.9, 1, 1])
    kh['M'] = fuzz.trapmf(kh.universe, [0.7, 0.75, 0.8, 0.9])
    kh['H'] = fuzz.trapmf(kh.universe, [0.3, 0.4, 0.7, 0.75])
    kh['VH'] = fuzz.trapmf(kh.universe, [0, 0, 0.35, 0.5])
    
    t_l_p.automf(names=['L', 'M', 'H', 'VH'])

    # Definizione delle regole
    rules = [
        ctrl.Rule(kd['VH'] & kh['VH'], t_l_p['VH']),
        ctrl.Rule(kd['VH'] & kh['H'], t_l_p['VH']),
        ctrl.Rule(kd['VH'] & kh['M'], t_l_p['H']),
        ctrl.Rule(kd['VH'] & kh['L'], t_l_p['M']),
        ctrl.Rule(kd['H'] & kh['VH'], t_l_p['VH']),
        ctrl.Rule(kd['H'] & kh['H'], t_l_p['H']),
        ctrl.Rule(kd['H'] & kh['M'], t_l_p['H']),
        ctrl.Rule(kd['H'] & kh['L'], t_l_p['M']),
        ctrl.Rule(kd['M'] & kh['VH'], t_l_p['H']),
        ctrl.Rule(kd['M'] & kh['H'], t_l_p['H']),
        ctrl.Rule(kd['M'] & kh['M'], t_l_p['M']),
        ctrl.Rule(kd['M'] & kh['L'], t_l_p['L']),
        ctrl.Rule(kd['L'] & kh['VH'], t_l_p['M']),
        ctrl.Rule(kd['L'] & kh['H'], t_l_p['M']),
        ctrl.Rule(kd['L'] & kh['M'], t_l_p['L']),
        ctrl.Rule(kd['L'] & kh['L'], t_l_p['L']),
    ]


    # Aggiunta delle regole al sistema di controllo
    t_l_p_ctrl = ctrl.ControlSystem(rules)
    t_l_p_sim = ctrl.ControlSystemSimulation(t_l_p_ctrl)

    # Esempio di input e calcolo
    t_l_p_sim.input['kd'] = pointDistance2D / threatRadius #0.95
    t_l_p_sim.input['kh'] = pointHeight / maxThreatHeight #0.9

    # Calcolo dell'output
    t_l_p_sim.compute()
    output_numeric = t_l_p_sim.output['t_l_p']

    output_string = get_membership_label(output_numeric, t_l_p)

    return output_string, output_numeric
    #print("Valore numerico di t_l_p:", output_numeric)
    #print("Valore stringa di t_l_p:", output_string)


def getClassName(obj):
    return obj.__class__.__name__


def mean_point(points: list) -> Point:
    if not points:
        raise ValueError("None value, points must be a list of Points")
    
    if not isinstance(points, list) or any([no_point for no_point in points if not isinstance(no_point, Point)]):
        raise ValueError("points must be a list of Points: {points!r}")
    
    if isinstance(points[0], Point3D) and any([no_point3D for no_point3D in points if not isinstance(no_point3D, Point3D)]):
        raise ValueError("points must have only Point3D or only Point2D: {points!r}")
    
    if isinstance(points[0], Point2D) and any([no_point2D for no_point2D in points if not isinstance(no_point2D, Point2D)]):
        raise ValueError("points must have only Point3D or only Point2D: {points!r}")


    if isinstance(points[0], Point3D):
        x_mean = np.mean([point.x for point in points])
        y_mean = np.mean([point.y for point in points])
        z_mean = np.mean([point.z for point in points])
        return Point3D(x_mean, y_mean, z_mean)
    
    elif isinstance(points[0], Point2D):
        x_mean = np.mean([point.x for point in points])
        y_mean = np.mean([point.y for point in points])
        return Point2D(x_mean, y_mean)
    
    else:
        raise TypeError("Unknow anomaly in points {points!r}")

def evaluateMorale(success_ratio: float, efficiency: float):
    """
    Calculate Morale using Fuzzy Logic

    input param:     
    success_ratio: success ratio of the activity block: Military -> mission_success_ratio, Production, Storage, Transport, Urban succes_ratio = = random_anomaly (anomalie di produzione, trasporto ecc generate casualmente in funzione del livello di goods (ricambi):  random(0, rcp_goods / acp _goods))
    
    return (string): ['L', 'M', 'H', 'VH'] 

    TEST:
    """

    if success_ratio <= 0 or efficiency <= 0:
        raise ValueError("Input values must be positive and non-zero.")
            
    # Variabili di input
    kd = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'kd')  # kd = success_ratio_set Valori continui [0, 1]
    kh = ctrl.Antecedent(np.arange(0, 1.01, 0.01), 'kh')  # kh = efficiency set Valori continui [0, 1]

    # Variabile di output
    t_l_p = ctrl.Consequent(np.arange(0, 1.01, 0.01), 't_l_p')  # morale set Valori continui [0, 1]

    # Funzioni di appartenenza
    kd['L'] = fuzz.trapmf(kd.universe, [0.0, 0.0, 0.5, 1.0])
    kd['M'] = fuzz.trapmf(kd.universe, [0.75, 1.0, 1.25, 2])
    kd['H'] = fuzz.trapmf(kd.universe, [1.25, 2, 10, 10])

    kh['L'] = fuzz.trapmf(kh.universe, [0.0, 0.0, 0.5, 0.55])
    kh['M'] = fuzz.trapmf(kh.universe, [0.5, 0.66, 0.75, 0.85])
    kh['H'] = fuzz.trapmf(kh.universe, [0.66, 0.85, 1.0, 1.0])
    
    
    t_l_p.automf(names=['L', 'M', 'H'])

    # Definizione delle regole
    rules = [
    
        ctrl.Rule(kd['H'] & kh['H'], t_l_p['H']),
        ctrl.Rule(kd['H'] & kh['M'], t_l_p['H']),
        ctrl.Rule(kd['H'] & kh['L'], t_l_p['M']),    
        ctrl.Rule(kd['M'] & kh['H'], t_l_p['H']),
        ctrl.Rule(kd['M'] & kh['M'], t_l_p['M']),
        ctrl.Rule(kd['M'] & kh['L'], t_l_p['L']),
        ctrl.Rule(kd['L'] & kh['H'], t_l_p['M']),
        ctrl.Rule(kd['L'] & kh['M'], t_l_p['L']),
        ctrl.Rule(kd['L'] & kh['L'], t_l_p['L']),
    ]


    # Aggiunta delle regole al sistema di controllo
    t_l_p_ctrl = ctrl.ControlSystem(rules)
    t_l_p_sim = ctrl.ControlSystemSimulation(t_l_p_ctrl)

    # Esempio di input e calcolo
    t_l_p_sim.input['kd'] = success_ratio #0.95
    t_l_p_sim.input['kh'] = efficiency #0.9

    # Calcolo dell'output
    t_l_p_sim.compute()
    output_numeric = t_l_p_sim.output['t_l_p']

    output_string = get_membership_label(output_numeric, t_l_p)

    return output_string, output_numeric
    #print("Valore numerico di t_l_p:", output_numeric)
    #print("Valore stringa di t_l_p:", output_string)


def getFormattedPoint(point, decimal_places=2):
    return tuple(f"{float(coord):.2f}" for coord in point)


def rotate_vector(v, angle):
        """
        Ruota un vettore 2D di un dato angolo (in radianti)
        """
        cos_ang = math.cos(angle)
        sin_ang = math.sin(angle)
        return (v[0] * cos_ang - v[1] * sin_ang,  v[0] * sin_ang + v[1] * cos_ang)

def normalize_vector(v):
    """
    Normalizza un vettore 2D
    """
    length = math.sqrt(v[0]**2 + v[1]**2)
    if length == 0:
        return (0, 0)
    return (v[0] / length, v[1] / length)

def get_direction_vector(start, end):
    """
    Calcola il vettore direzione da un punto di partenza a un punto di arrivo
    """
    dir = normalize_vector((end[0] - start[0], end[1] - start[1]))
    return dir
    
def validate_class(obj, class_name: str) -> bool:    
    """return True if class_name is a class name of object's class gerarchy"""    
    if not isinstance(class_name, str):
        raise ValueError(f"class_name must be a string")

    return class_name in tuple(cls.__name__ for cls in inspect.getmro(obj.__class__))