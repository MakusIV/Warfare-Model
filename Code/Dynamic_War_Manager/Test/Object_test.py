
# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, 'project')

from Object import Object 
from Coordinate import Coordinate



def testClassObject():

    result = True
    message = 'MESSAGE: '

    coord = Coordinate (3, 4, 7)

    obj = Object( coord=coord, name='Tullio', dimension=[10, 8, 6]  )

    if obj._name!='Tullio' or obj._dimension != [10, 8, 6] or obj._coord != coord:
        print('Object.__Initit__ Failed!! ', obj._name, obj._id, obj._dimension, obj._coord)
        result = False 

    obj = Object()

    if not obj._name or not obj._id or not obj._dimension or not isinstance(obj._name,str) or not isinstance(obj._id,str) or not ( isinstance(obj._dimension,list) or isinstance(obj._dimension, tuple) ):
        print('Object.__Initit__ Failed!! ', obj._name, obj._id, obj._dimension)
        result = False 


    obj = Object( coord = Coordinate(2,2,2), name = 'Gregory', dimension = [5,5,5] )     

    if obj._name != 'Gregory' or obj._dimension != [5,5,5] or obj.getPosition() != (2,2,2):
        print('Object.__Initit__ Failed!! ', obj._name, obj._id, obj._dimension, obj.getPosition())    
        result = False 

    try:
        obj = Object( coord = Coordinate(2,2,2), name = 'Antony', dimension = [5,5,5], emissivity = {"radio": 0, "thermal": 0, "optical": 0, "nuclear": 0, "electric": 0, "minchiatic": 0, "chemist": 0} )     
    except Exception:
        pass
    else:
        print('Object.__Initit__ Failed!! ', obj._name, obj._id, obj._dimension, obj.getPosition())    
        result = False 


    obj.setName('Ollio')

    if obj._name != 'Ollio':
        print('Object.setName() Failed!! ', obj._name)
        result = False 


    if not obj.setName(12):
        print('Object.setName() Failed!! ', obj._name)
        result = False 

    obj.setId(999)

    if obj._id != '999':
        print('Object.setId() Failed!! ', obj._id)
        result = False 

    obj.setDimension([1,1,1])

    if obj.getDimension() != [1,1,1]:
        print('Object.setDimension() Failed!! ', obj._dimension)
        result = False 

    obj.setCoord( Coordinate(2,2,2) )

    if obj.getPosition() != (2, 2, 2):
        print('Object.setCoord() Failed!! ', obj.getPosition())
        result = False 

    if obj.getDistance( Coordinate(3,3,3) ) != 3**0.5:
        print('Object.getDistance() Failed!! ', obj.getDistance( Coordinate(5,5,5) ) )
        result = False 

    # isCollision(volume) test
    # NOTA: volume = [ [xl, yl, zl],  [xh, yh, zh] ] dove xl, yl, zl <= xh, yh, zh

    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [0, 0, 0 ], [5, 5, 5] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if not obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 


    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [4,4,4], [15, 15, 15] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 


    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [3,3,3], [15, 15, 15] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if not obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 


    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [-3,-3,-3], [0, 0, 0] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if not obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 


    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [-3,-3,-3], [-1, -1, -1] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 


    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [-3, 0, 1], [-1, 2, 5] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 



    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    volume = [ [3, -1, 0], [3, -2, 5] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 


    coord = Coordinate(0,0,0)
    dimension = [3,3,3]
    # NOTA: volume = [ [xl, yl, zl],  [xh, yh, zh] ] dove xl, yl, zl <= xh, yh, zh
    volume = [ [3, -2, 0], [3, 0, 5] ]

    obj.setCoord( coord )
    obj.setDimension( dimension )

    if not obj.isCollision( volume ):
        print('isCollision(volume) Failed!! ', obj.getPosition(), obj.getDimension(), volume)
        result = False 

    if not Object.checkObjectClass(obj, obj):
        print('Object.checkObjectClass(sensor) Failed!! ', obj._state, obj._state._health)
        result = False 
    
    objects = [Object(), Object(), Object(), Object()]

    if not Object.checkObjectList(obj, objects):
        print('Object.checkObjectList(sensors) Failed!! ', objects[0]._id, objects[0]._state, objects[0]._state._health)
        result = False 

    objects = [Object(), Object(), list(), Object()]

    if Object.checkObjectList(obj, objects):
        print('Object.checkObjectList(sensors) Failed!! ', objects[0]._id, objects[0]._state, objects[0]._state._health)
        result = False 

    x = 24
    y = 27
    z = 19
    dimension = [2,2,2]
    obj = Object( coord = Coordinate(x,y,z), name = 'Marcantony', dimension = dimension ) 
    volume_position = obj.getVolumePosition() 

    if not ( volume_position[ (x,y,z) ] and volume_position[ (x+dimension[0]-1,y+dimension[1]-1,z+dimension[2]-1) ] and volume_position[ (x,y+dimension[1]-1,z) ] and volume_position[ (x+dimension[0]-1,y,z+dimension[2]-1) ] ):
        print('Object.getVolumePosition() Failed!! ', volume_position[ (x,y,z) ] , volume_position[ (x+dimension[0]-1,y+dimension[1]-1,z+dimension[2]-1) ] , volume_position[ (x,y+dimension[1]-1,z) ] , volume_position[ (x+dimension[0]-1,y,z+dimension[2]-1) ])
        result = False 

    try:
        not ( volume_position[ (x-1,y,z) ] and volume_position[ (x,y,z+dimension[2]) ] and volume_position[ (x,y+dimension[1],z) ] and volume_position[ (x+dimension[0],y,z+dimension[2]) ] )

    except Exception:
        pass

    else:
        print('Object.getVolumePosition() Failed!! ', volume_position[ (x-1,y,z) ], volume_position[ (x,y,z+dimension[2]) ], volume_position[ (x,y+dimension[1],z) ], volume_position[ (x+dimension[0],y,z+dimension[2])] )
        result = False 


    state = obj._state    
    obj.destroy()

    if not state.isDestroyed() or not obj._state.isDestroyed():
        message = message +'\n' + 'Object.destroy() Failed!!! '
        print( message , state, obj )
        return False


    print( message )
    return result




print("Object class test result:", testClassObject())

