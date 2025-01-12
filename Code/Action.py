from Coordinate import Coordinate
import Code.General as General
from State import State
from Code.LoggerClass import Logger

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Action')


class Action:
    
    def __init__( self, typ, time2go = 1, duration = 1, position = None, obj = None, param = None  ):

        if not self.checkParam(typ,  time2go, duration ):
            raise Exception("Invalid parameters! Action not istantiate.")        

        self._type = typ # type: ACTION_TYPE = ( "move", "run", "take", "catch", "eat", "attack", "escape", "nothing", "shot", "hit" )
        self._id = General.setId(self._type, None) # l'id viene generato automaticamente nel runtime per ogni istanza creata
        self._time2go = time2go
        self._duration = duration
        self._position = position
        self._object = obj
        self._param = param
   

    def decrTime2Go( self ):
        self._time2go = self._time2go -1
        return self._time2go

    def decrDuration( self ):
        self._duration = self._duration - 1
        return self._duration

    def isActivable( self ):
        return self._time2go == 0 and self._duration > 0

    def isAwaiting( self ):
        return self._time2go > 0


    def isActionType( self, typ ):
        return self._type == typ

    def getActionParam( self ):
        
        if self._position != None and self._object == None:
            return [ self._type, self._position, self._param ]
        
        elif self._position == None and self._object != None:
            return [ self._type, self._object, self._param ]

        else:
            raise Exception("position or object should to be None")


    def checkParam( self, typ, time2go, duration ):

        if not typ or time2go < 0 or duration < 0 or not General.checkActionType( typ ):
            return False
        return True

    def setDuration(self, duration):
        """Set duration and return True"""

        if not isinstance( duration, int ):
            return False
        self._duration = duration
        return True

    def getId( self ):
        return self._id

    def destroy( self ):
        self._typ = None
        self._id = "destroyed"
        self._obj = None