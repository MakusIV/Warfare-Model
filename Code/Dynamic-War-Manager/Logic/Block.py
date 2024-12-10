import random
import Utility
from State import State
from LoggerClass import Logger
from Event import Event
from Context import STATE

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Block')

# ASSET o BLOCK
class Block:    

    def __init__(self, name = None ):

            # propriety
            self._name = name 
            self._id = Utility.setId("Block_" + name + "_")
            self._description = None
            self._category = None
            self._function = None
            self._value = None
            self._position = None
            self._acs = None # assigned 
            self._rcs = None # requested
            self._payload = None
        
            
            

            if not self.checkParam( dimension, mass, resilience, state, coord ):
                raise Exception("Invalid parameters! Object not istantiate.")


            if not name:
                self._name = Utility.setName('Block_')
                self._id = Utility.setId('Block_ID_', None)

            else:
                self._name = "Block_" + name
                self._id = Utility.setId('Block_' + name + '_ID', None)
           
            # Association      
            self._state = State(self._name)


 
    def setState(self, state):

        if not state or not isinstance(state, State):
            self._state = State( run = True )

        else:
            self._state = state

        return True

    def getState(self):
        return self._state


    def setId(self, id):

        if not id:
            return False

        elif isinstance(id, str):
            self._id = id       
        
        else:
            self._id = str( id )       
            
        return True


    def setName(self, name):

        if not name:
            return False
        else:
            self._name = name

        return True
            

    
    def setDimension(self, dimension):

        if not dimension or not isinstance(dimension, tuple) and not len(dimension) == 3 or not isinstance( dimension[0], int) or not  isinstance( dimension[1], int) or not  isinstance( dimension[2], int):
            return False
        else:
            self._dimension = dimension

     
        #if not General.checkDimension(dimension): # not dimension or not isinstance(dimension, list) and not len(dimension) == 3 or not isinstance( dimension[0], int) or not  isinstance( dimension[1], int) or not  isinstance( dimension[2], int) :
         #   return False
        #else:
         #   self._dimension = dimension

        return True


    def isCollision(self, volume):
        """Return True if object's volume collide with volume"""
        # xd = dimension[0], yd = dimension[1], zd =dimension[2]
        # xvol_low = volume[0][0], yvol_low = volume[0][1], zvol_low = volume[0][2]
        # xvol_high = volume[1][0], yvol_high = volume[1][1], zvol_high = volume[1][2]
        # not intersection in x axes: x > xvol_high and x + xd < xvol_low
        # not intersection in y axes: y > yvol_high and y + yd < yvol_low
        # not intersection in z axes: z > zvol_high and z + zd < zvol_low
        # not interection -> one or more axis not intersection

        ## NOTA: volume = [ [xl, yl, zl],  [xh, yh, zh] ] dove xl, yl, zl <= xh, yh, zh

        if not General.checkVolume(volume): #not volume or not isinstance( volume, list ):
            raise Exception('Invalid parameters')

        pos = self._coord.getPosition()

        x_not_intersection =  pos[0] > volume[1][0] or pos[0] + self._dimension[0] < volume[0][0] 
        y_not_intersection =  pos[1] > volume[1][1] or pos[1] + self._dimension[1] < volume[0][1] 
        z_not_intersection =  pos[2] > volume[1][2] or pos[2] + self._dimension[2] < volume[0][2] 

        # not interection -> one or more axis not intersection
        if x_not_intersection or y_not_intersection or z_not_intersection:
            return False

        return True


    def getDistance(self, coord):
        """Return distance (d, xd, yd, zd) from object.coordinate to pos:[x, y, z]""" 

        if not coord or not isinstance(coord, Coordinate):
            return False       

        return self._coord.distance(coord)
        

    def getHealth( self ):
        return self._state.getHealth()

    def getId(self):
        return self._id

    def getName(self):
        return self._name

    def getPosition(self):
        return self._coord.getPosition()

    def setPosition(self, position):
        self._coord.setPosition( position )

    def getDimension(self):
        return self._dimension

    def to_string(self):
        return 'Name: {0}  -  Id: {1}'.format(self.getName(), str(self._id))
    
    def checkBlockClass(self, object):
        """Return True if objects is a Object object otherwise False"""
        if not object or not isinstance(object, Block):
            return False
        
        return True

    def checkBlockList(self, objects):
        """Return True if objectsobject is a list of Object object otherwise False"""

        if objects and isinstance(objects, list) and all( isinstance(object, Block) for object in objects ):
            return True

        return False


     # vedi il libro
    def checkParam(self, dimension, mass, resilience, state, coord ):
        """Return True if conformity of the parameters is verified"""   
    
        if state != None and not isinstance( state, State ) or coord != None and not isinstance( coord, Coordinate ) or resilience != None and ( not isinstance( resilience, int )  or not( resilience <= 100 and resilience >= 0 ) ) or not( mass >= 0 ) or not General.checkDimension( dimension ):
            return False
                
        return True


    def getVolumePosition( self ):
        """Return the position of the object's volume"""
        
        position = self.getPosition()
        dimension = self.getDimension()
        volume_position = dict()

        for z in range( position[ 2 ], position[ 2 ] + dimension[ 2 ] ):           
           for y in range( position[ 1 ], position[ 1 ] + dimension[ 1 ] ):              
              for x in range( position[ 0 ], position[ 0 ] + dimension[ 0 ] ):
                  volume_position[ ( x, y, z ) ] = True

        return volume_position


    def getVolume( self, position = None, dimension = None ):
        """Return [ [ position ], [ position + dimensione ] ] """
        
        if position == None:
            position = self.getPosition() 
        
        if dimension == None:
            dimension = self.getDimension()

        return [ position, [ position[ 0 ] + dimension[ 0 ], position[ 1 ] + dimension[ 1 ], position[ 2 ] + dimension[ 2 ] ] ] 


    def destroy( self ):
        """Destroy this object"""

        for ev in self._eventsQueue:
            ev.destroy()

        self._state.destroy()
        self._coord = None
        self._eventsQueue = None        
        logger.logger.debug("Object: {0} destroyed".format( self._name ) )
        return True

    def getValueVolume( self ):
        """Return Object volume dimension"""
        return self._dimension[0] * self._dimension[1] * self._dimension[2]

    def differenceWithValueVolume( self, valueVolume ):        
        """Return difference of automa volume dimensione and valueVolume:"""
        return self.getValueVolume() - valueVolume

    def getFootPrint( self ):
        """Return hash code for Object"""        
    
        objectFootPrint = hash( General.calcVectorModule( self._dimension ) + self._mass )
        return objectFootPrint, False
