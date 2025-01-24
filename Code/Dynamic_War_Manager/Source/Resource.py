
from LoggerClass import Logger


# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Resource')


class Resource():

    def __init__( self, obj, type = 'FOOD', name = None ):            

        
        if not( type and obj ):
                raise Exception("Invalid parameters! Resource not istantiate.")
        
        self._name = None
        self._id = None

        if not name:
            self._name = General.setName('Threat')
        else:
            self._name = name

        if not id:
            self._id = General.setId('Threat')
        else:
            self._id = id

        self._type = type #FOOD, WATER, ENERGY, ....
        self.obj = obj
        
                        
            


    def setId(self, id = None):

        if not id:
            return False
        else:
            self._id = id        
            
        return True


    def setName(self, name):

        if not name:
            return False
        else:
            self._name = name

        return True
                            
           
    