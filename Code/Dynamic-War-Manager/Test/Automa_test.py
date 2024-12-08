# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, 'project')

import General
from State import State
from Automa import Automa
from Sensor import Sensor
from Actuator import Actuator
from Coordinate import Coordinate
from Position_manager import Position_manager
from Object import Object
from Event import Event
from Action import Action

from LoggerClass import Logger


# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Automa_test')




def testClassAutoma():

    result = True
    message = 'MESSAGE: '
    # actuator(position, range_max, typ, power = 100,  resilience = 100, delta_t = 0.01, name = None, state = None)
    #name = 'Automa', dimension = [1, 1, 1], resilience = 10, state = State(run = True), ai = AI(), coord = None, sensors= None, actuators = None       
    coord = Coordinate( 0, 0, 0 )
    sensors = [ Sensor(  _class = "radio", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100) ), Sensor( _class = "optical", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100) ), Sensor( _class = "thermal", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100) )]
    actuators = [ Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "mover", typ = "crawler", power = 100,  resilience = 100, delta_t = 0.01, speed = 10 ), Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "mover", typ = "2-legs", power = 100,  resilience = 100, delta_t = 0.01, speed = 10 ) ]
    automa = Automa(coord = coord, sensors = sensors, actuators = actuators, mass = 30)
    
    
    if automa.checkClass( automa ) == False or automa._name != 'Automa' or automa._dimension != [1, 1, 1] or automa._resilience != 100 or automa._power != 100 or not automa._state or not isinstance(automa._state, State) or not automa._state.isRunning() or automa._ai._automaId != automa._id:
        message = message +'\n' + 'Automa Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, automa._dimension, automa._resilience, automa._state )                         
        result = False 
        
    
    state = automa._state    
    automa.destroy()

    if not state.isDestroyed() or not automa._state.isDestroyed():
        message = message +'\n' + 'Automa.destroy() Failed!!!<------------------------------------------------------------------------------ '
        print( message , state, automa )
        return False



    # test: automa.select_actuators( action )
    #
    automa = Automa(coord = coord, sensors = sensors, actuators = actuators, mass = 30)    
    action = [ 'move', (10, 10, 10), 0.7 ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != ( 10, 10, 10 ) or actuators_activation[1][1] != 0.7:
        message = message +'\n' + 'Automa.select_actuators( action ) move Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 

    action = [ 'run', (10, 10, 10) ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != ( 10, 10, 10 ) or actuators_activation[1][1] != 1:
        message = message +'\n' + 'Automa.select_actuators( action ) run Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 

    automa.setActuator( Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "object_manipulator", typ = "clamp", power = 100,  resilience = 100, delta_t = 0.01 ) )
    obj = Object( coord = Coordinate( 5, 5, 5 ) )
    action = [ 'translate', obj, ( 8, 8, 8) ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != obj or actuators_activation[1][1] != (8, 8, 8):
        message = message +'\n' + 'Automa.select_actuators( action ) translate Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 

    automa.setActuator( Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "object_catcher", typ = "clamp", power = 100,  resilience = 100, delta_t = 0.01 ) )
    obj = Object( coord = Coordinate( 10, 10, 10 ) )
    action = [ 'catch', obj ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != obj:
        message = message +'\n' + 'Automa.select_actuators( action ) catch Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 

    automa.setActuator( Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "object_assimilator", typ = "jaw", power = 100,  resilience = 100, delta_t = 0.1 ) )
    obj = Object( coord = Coordinate( 10, 10, 10 ) )
    action = [ 'eat', obj ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != obj:
        message = message +'\n' + 'Automa.select_actuators( action ) eat Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 

    automa.setActuator( Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "plasma_launcher", typ = "laser", power = 100,  resilience = 100, delta_t = 0.01 ) )
    obj = Object( coord = Coordinate( 10, 10, 10 ) )
    action = [ 'shot', obj ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != obj:
        message = message +'\n' + 'Automa.select_actuators( action ) shot Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 
    

    automa.setActuator( Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "object_hitter", typ = "drill", power = 100,  resilience = 100, delta_t = 0.01 ) )
    obj = Object( coord = Coordinate( 10, 10, 10 ) )
    action = [ 'hit', obj ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != obj:
        message = message +'\n' + 'Automa.select_actuators( action ) hit Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 

    
    automa.setActuator( Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "projectile_launcher", typ = "medium__machine_gun", power = 100,  resilience = 100, delta_t = 0.01 ) )
    obj = Object( coord = Coordinate( 10, 10, 10 ) )
    action = [ 'attack', obj ] #(action_type, position or object) 
    actuators_activation = automa.select_actuators( action )

    if not actuators_activation or not isinstance(actuators_activation, list) or not isinstance(actuators_activation[0], Actuator) or actuators_activation[1][0] != obj:
        message = message +'\n' + 'Automa.select_actuators( action ) attack Failed!!<------------------------------------------------------------------------------'
        print( message ,actuators_activation[0], actuators_activation[1] )                         
        result = False 
    

    # test: automa.action( request_action = move )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None 
    action = Action( typ = 'move', time2go = 0, duration = 1, position = (10, 10, 10), param = 0.7 ) #(action_type, position or object) 
    automa.insertAction( action )
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 93:
        message = message +'\n' + 'Automa.action(posMng) move Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )                         
        result = False 
    

    # test: automa.action( request_action = run )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None 
    automa.resetActionQueue()
    action = Action( typ = 'run', time2go = 0, duration = 1, position = (10, 10, 10), param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 83:
        message = message +'\n' + 'Automa.action(posMng) run Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )                         
        result = False 


    
    # test: automa.action( request_action = translate )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ) )
    posMng.insertObject( ( 5, 5, 5 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'translate', time2go = 0, duration = 1, obj = obj, param = (7, 7, 7) ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 99 or len( obj._eventsQueue ) != 1:
        message = message +'\n' + 'Automa.action(posMng) translate -1: Automa Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )                         
        result = False 


    # test: automa.action( request_action = translate )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Automa( coord = Coordinate( 5, 5, 5 ), sensors = sensors, actuators = actuators, mass = 300 )
    posMng.insertObject( ( 5, 5, 5 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'translate', time2go = 0, duration = 1, obj = obj, param = (7, 7, 7) ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 98 or len( obj._eventsQueue ) != 1:
        message = message +'\n' + 'Automa.action(posMng) translate-2 Automa Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )                         
        result = False 
    
    # test: automa.action( request_action = catch )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ) )
    posMng.insertObject( ( 5, 5, 5 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'catch', time2go = 0, duration = 1, obj = obj, param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 99:
        message = message +'\n' + 'Automa.action(posMng) catch Failed!! ' + str( action_info[0][0] ) +" " + str( action_info[0][1] ) + " "  + str( automa.getId() ) + "<------------------------------------------------------"
        print( message )                 
        result = False 


    # test: automa.action( request_action = shot )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ), resilience = 90 )
    obj._state._health = 80
    posMng.insertObject( ( 9, 9, 9 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'shot', time2go = 0, duration = 1, obj = obj, param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 99:
        message = message +'\n' + 'Automa.action(posMng) shot Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )         
        result = False 

    
    # test: automa.action( request_action = shot )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ), resilience = 90 )
    obj._state._health = 80
    posMng.insertObject( ( -8, -8, -8 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'shot', time2go = 0, duration = 1, obj = obj, param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 98:
        message = message +'\n' + 'Automa.action(posMng) shot Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )         
        result = False 


    
    # test: automa.action( request_action = shot )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ), resilience = 90 )
    obj._state._health = 80
    posMng.insertObject( ( -8, -8, -8 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'hit', time2go = 0, duration = 1, obj = obj, param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 99:
        message = message +'\n' + 'Automa.action(posMng) hit Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )         
        result = False 


    # test: automa.action( request_action = shot )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ), resilience = 50, mass = automa.getMass() )
    obj._state._health = 50
    posMng.insertObject( ( -8, -8, -8 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'eat', time2go = 0, duration = 1, obj = obj, param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 90: # or obj.getHealth() != 0 or automa._state.getEnergy() != 200:
        message = message +'\n' + 'Automa.action(posMng) eat Failed!!<------------------------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )         
        result = False 



    # test: automa.action( request_action = shot )
    #   action_info: result of action, actuator's energy state
    #typ, time2go = 1, duration = 1, position = None, obj = None, param = None     
    posMng = Position_manager()
    posMng.insertObject( ( 0, 0, 0 ), automa )
    obj = Object( coord = Coordinate( 5, 5, 5 ), resilience = 50, mass = automa.getMass() )
    obj._state._health = 50
    posMng.insertObject( ( -8, -8, -8 ), obj )
    automa.resetActionQueue()
    action = Action( typ = 'attack', time2go = 0, duration = 1, obj = obj, param = None ) #(action_type, position or object) 
    automa.insertAction( action )
    action_info = automa.action(posMng)

    if not action_info or not isinstance(action_info, list) or not action_info[0][0] or action_info[0][1] != 97:
        message = message +'\n' + 'Automa.action(posMng) attack Failed!!<----------------------------------------------------------------'
        print( message ,action_info[0][0], action_info[0][1], automa.getId() )         
        result = False 


    

    print("------------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------------------")
    print( action_info )
    print("------------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------------------")
    print("------------------------------------------------------------------------------------------------------------")


    # test: automa.percept( pm )
    #     
    # create positione manager for manage enviroments, create object and populate pm
    num_objects = 100
    num_objects_for_linear = int( (num_objects)**(1/3) )    
    object_dimension = (3, 2, 1)
    separation_from_objects = 7
    incr = ( object_dimension[0] + separation_from_objects, object_dimension[2] + separation_from_objects, object_dimension[2] + separation_from_objects )
    dim_linear = ( num_objects_for_linear * incr[0], num_objects_for_linear * incr[2], num_objects_for_linear * incr[2] )
    bound = ( int( dim_linear[0]/2 ), int( dim_linear[1]/2 ), int( dim_linear[2]/2 ) )
    logger.logger.info( "num_objects:{0},  num_objects_for_linear:{1},  object_dimension:{2},  separation_from_objects:{3},  incr:{4},  dim_linear:{5},  bound:{6}".format( num_objects,  num_objects_for_linear, object_dimension, separation_from_objects, incr, dim_linear, bound ) )

    pm = Position_manager( name ='position manager', limits = [ [ -bound[0] , -bound[1], -bound[2]], [ bound[0], bound[1], bound[2] ] ] )

    for z in range(-bound[2], bound[2], incr[2]):
        for y in range(-bound[1], bound[1], incr[1]):
            for x in range(-bound[0], bound[0], incr[0]):
                
                if z == -bound[2] and y == -bound[1] and x == -bound[0]:
                    pm.insertObject( position = (x, y, z), obj = automa )    
                else:
                    pm.insertObject( position = (x, y, z), obj = Object(name = 'New_'+str( int(  ((bound[0] + x)%dim_linear[0])/incr[0] + num_objects_for_linear*((bound[1] + y)%dim_linear[1])/incr[1] + num_objects_for_linear*num_objects_for_linear*((bound[2] + z)%dim_linear[2])/incr[2] ) ), dimension = ( object_dimension[0], object_dimension[1], object_dimension[2]) , emissivity = {"radio": 5, "thermal": 0, "optical": 5, "nuclear": 0, "electric": 0, "acoustics": 0, "chemist": 0 } ) )
    
    
    obj_list = automa.percept( pm )

    if len( obj_list ) == 0 or not isinstance( obj_list, list) or any( False for obj in obj_list if not isinstance( obj, Object ) ):
        print('Automa.percept() Failed len(object_list) = 0 !! ', automa._id, obj_list)
        result = False 
    

    # test getDetectableSensors getDetectableActuators
    # actuator(position, range_max, typ, power = 100,  resilience = 100, delta_t = 0.01, name = None, state = None)
    #name = 'Automa', dimension = [1, 1, 1], resilience = 10, state = State(run = True), ai = AI(), coord = None, sensors= None, actuators = None       
    coord = Coordinate( 0, 0, 0 )
    sensors = [ Sensor(  _class = "radio", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100) ), Sensor( _class = "optical", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100), dimension = (1, 2, 2 ) ), Sensor( _class = "thermal", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100), dimension = (1, 1, 2 ) ) ]
    actuators = [ Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "mover", typ = "crawler", power = 100,  resilience = 100, delta_t = 0.01, speed = 10 ), Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "mover", typ = "2-legs", power = 100,  resilience = 100, delta_t = 0.01, speed = 10 ) ]
    automa = Automa(coord = coord, sensors = sensors, actuators = actuators, mass = 30, dimension = (1, 1, 1))
    
    automaFootPrint, isAutoma = automa.getFootPrint()
    sensorsFootPrint = automa.getDetectableSensorsFootPrint()
    actuatorsFootPrint = automa.getDetectableActuatorsFootPrint()
    #print("automa.getDetectableSensorsFootPrint: ", sensorsFootPrint )   

    if  not automaFootPrint or not isAutoma:
        message = message +'\n' + 'Automa.getFootPrint - Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, automaFootPrint )                         
        result = False 

    if not sensorsFootPrint:
        message = message +'\n' + 'Automa.getDetectableSensorsFootPrint - Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, sensorsFootPrint )                         
        result = False 

    if not actuatorsFootPrint:
        message = message +'\n' + 'Automa.getDetectableActuatorsFootPrint - Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, actuatorsFootPrint )                         
        result = False 

    automa = Automa(coord = coord, sensors = sensors, actuators = actuators, mass = 30, dimension = (100, 100, 100))
    automaFootPrint, isAutoma = automa.getFootPrint()
    sensorsFootPrint = automa.getDetectableSensorsFootPrint()
    actuatorsFootPrint = automa.getDetectableActuatorsFootPrint()
    #print("automa.getDetectableSensorsFootPrint: ", sensorsFootPrint )  

    if  automaFootPrint != hash( General.calcVectorModule( automa._dimension ) + automa._mass ):
        message = message +'\n' + 'Automa.getFootPrint - A Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, automaFootPrint )                         
        result = False 

    if sensorsFootPrint != 0:
        message = message +'\n' + 'Automa.getDetectableSensorsFootPrint - A Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, sensorsFootPrint )                         
        result = False 

    if actuatorsFootPrint != 0:
        message = message +'\n' + 'Automa.getDetectableActuatorsFootPrint - A Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, actuatorsFootPrint )                         
        result = False 
    
    sensors = [ Sensor( _class = "optical", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100), dimension = (1, 2, 2 ) ), Sensor( _class = "thermal", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100), dimension = (1, 1, 2 ) ), Sensor(  _class = "radio", typ = "simple", position = coord.getPosition(), range_max = (100, 100, 100) ) ]
    actuators = [ Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "mover", typ = "2-legs", power = 100,  resilience = 100, delta_t = 0.01, speed = 10 ), Actuator( position = coord.getPosition(), range_max = ( 10, 10, 10 ), class_ = "mover", typ = "crawler", power = 100,  resilience = 100, delta_t = 0.01, speed = 10 ) ]
    automa = Automa(coord = coord, sensors = sensors, actuators = actuators, mass = 30, dimension = (100, 100, 100))
    automaFootPrint1, isAutoma = automa.getFootPrint()
    sensorsFootPrint1 = automa.getDetectableSensorsFootPrint()
    actuatorsFootPrint1 = automa.getDetectableActuatorsFootPrint()

    if  automaFootPrint != automaFootPrint1:
        message = message +'\n' + 'Automa.getFootPrint - B Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, automaFootPrint )                         
        result = False 
    
    if sensorsFootPrint != sensorsFootPrint1:
        message = message +'\n' + 'Automa.getDetectableSensorsFootPrint - B Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, sensorsFootPrint, sensorsFootPrint1 )                         
        result = False 

    if actuatorsFootPrint != actuatorsFootPrint1:
        message = message +'\n' + 'Automa.getDetectableActuatorsFootPrint - B Failed!!<------------------------------------------------------------------------------'
        print( message ,automa._name, actuatorsFootPrint )                         
        result = False 
        


    print( message )
    return result

print("Automa class test result:", testClassAutoma() )