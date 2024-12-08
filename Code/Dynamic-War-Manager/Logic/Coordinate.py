from math import sqrt
from LoggerClass import Logger
import General

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Coordinate')


class Coordinate:
    
    """ Rappresents a coordinate in an x, y, z  system """
    
    
    def __init__(self, x = None, y = None, z = None):

        if  x != None and not y and not z and General.checkPosition( x ):
            self.x = x[ 0 ]
            self.y = x[ 1 ]
            self.z = x[ 2 ]
        
        elif x != None and isinstance(x, int) and y != None and isinstance(y, int) and z != None and isinstance(z, int):
            self.x = x
            self.y = y
            self.z = z
        
        elif not x and not y and not z:
            self.x = 0
            self.y = 0
            self.z = 0

        else:
            raise Exception( "Invalid properties! Coordinate not istantiate." )
    

    def eval_direction(self, pos, des):
        """Evalutate direction from parameters"""

        dir_ = ""

        if pos[ 1 ] > des[ 1 ]:
            dir_ = "backward"
        
        elif pos[ 1 ] < des[ 1 ]:
            dir_ = "foward"
        

        if pos[ 2 ] > des[ 2 ]:
            dir_ = dir_ + "_down"
        
        elif pos[ 2 ] < des[ 2 ]:
            dir_ = dir_ + "_up"

        
        if pos[ 0 ] > des[ 0 ]:
            dir_ = dir_ + "_left"
        
        elif pos[ 0 ] < des[ 0 ]:
            dir_ = dir_ + "_right"
                
        

        return dir_

        
        

    def move(self, direct):
        """ update x, y, z regards direction string:
        foward, foward_left. foward_right, foward_up_left, foward_up_right, foward_down_left, foward_down_right, foward_up, foward_down
        backward, backward_left. backward_right, backward_up_left, backward_up_right, backward_down_left, backward_down_right, bacward_up, backward_down       
        _left, _up_left, _down_left
        _right, _up_right, _down_right
        _up, _down
        Not recognized direction raise a ValueError exception
        """
        if direct == 'foward':
            self.foward()
        
        elif direct == 'foward_left':
            self.foward()
            self.left()
            
        elif direct == 'foward_right':
            self.foward()
            self.right()            
            
        elif direct == 'foward_up':            
            self.foward()
            self.up()
            
        elif direct == 'foward_up_left':
            self.foward()
            self.up()
            self.left()
            
        elif direct == 'foward_up_right':
            self.foward()
            self.up()
            self.right()
            
        elif direct == 'foward_down':            
            self.foward()
            self.down()
        
        elif direct == 'foward_down_left':
            self.foward()
            self.down()
            self.left()
            
        elif direct == 'foward_down_right':
            self.foward()
            self.down()
            self.right()                
            
        elif direct == 'backward':
            self.back()
            
        elif direct == 'backward_left':
            self.back()
            self.left()
            
        elif direct == 'backward_right':
            self.back()
            self.right()            
            
        elif direct == 'backward_up':            
            self.back()
            self.up()
            
        elif direct == 'backward_up_left':
            self.back()
            self.up()
            self.left()
            
        elif direct == 'backward_up_right':
            self.back()
            self.up()
            self.right()
            
        elif direct == 'backward_down':            
            self.back()
            self.down()        
        
        elif direct == 'backward_down_left':
            self.back()
            self.down()
            self.left()
            
        elif direct == 'backward_down_right':
            self.back()
            self.down()
            self.right()
                            
        elif direct == '_left':                    
            self.left()
            
        elif direct == '_up_left':
            self.left()
            self.up()
                    
        elif direct == '_down_left':
            self.left()
            self.down()
                
        elif direct == '_right':
            self.right()
            
        elif direct == '_up_right':
            self.right()
            self.up()                                    

        elif direct == '_down_right':
            self.right()
            self.down()      

        elif direct == '_up':
            self.up()                                    

        elif direct == '_down':            
            self.down()                                       
                    
        else:
            return False
        
        return True
    
    
    def foward(self):
        """decrease y of 1"""
        self.y = self.y + 1

    def back(self):
        """increase y of 1"""
        self.y = self.y - 1

    def left(self):
        """decrease x of 1"""
        self.x = self.x - 1

    def right(self):
        """increase x of 1"""
        self.x = self.x + 1
 
    def up(self):
        """increase z of 1"""
        self.z = self.z + 1

    def down(self):
        """decrease y , of 1"""
        self.z = self.z - 1

    def duplicate(self):
        """ return a clone """
        return Coordinate(self.x, self.y, self.z)
    
    def distance(self, coord):

        if not coord or not isinstance(coord, Coordinate):
            return False

        """return absolute distance from coords =sqrt( (x - x)^2 + (t - y)^2 + (z-z)^2))"""        
        return ( (self.x - coord.x) ** 2 + (self.y - coord.y) ** 2 + (self.z - coord.z) ** 2 ) ** 0.5

    
    def distance_x(self, coord):
        """ return relative distance from x"""        

        if not coord or not isinstance(coord, Coordinate):
            return False

        return self.x - coord.x
    
    def distance_y(self, coord):
        """ return relative distance from y"""

        if not coord or not isinstance(coord, Coordinate):
            return False

        return self.y - coord.y
    
    def distance_z(self, coord):
        """ return relative distance from z"""

        if not coord or not isinstance(coord, Coordinate):
            return False

        return self.z - coord.z
    
    def is_same(self, coord):
        """return true if coord is self"""

        if not coord or not isinstance(coord, Coordinate):
            return False

        if coord == self:
            return True
        else:
            return False
    
    def is_egual(self, coord):
        """return true if coord have same x,y,z of self"""
        
        if not coord or not isinstance(coord, Coordinate):
            return False

        if coord.x == self.x and coord.z == self.z and coord.z == self.z:
            return True
        else:
            return False
            
    
    
    def is_in_range(self, coord, dist):
        """return true if coord distance from self is eugual or less of dist"""
        
        if not coord or not isinstance(coord, Coordinate) or not dist or not ( isinstance(dist, int) or isinstance(dist, float) ):
            return False 

        if coord.distance(self) <= abs(dist):
            return True
        else:
            return False

    
    
    def in_limits(self, limits):
        """return 2D-Array with state of corrispective coordinate:
        limits = [ [x-min, y_min, z_min], [x-max, y_max, z_max] ]

        """
        if not limits or not isinstance(limits, list) or not isinstance( limits[0][0], int) or not isinstance( limits[0][1], int) or not isinstance( limits[0][2], int) or not isinstance( limits[1][0], int) or not isinstance( limits[1][1], int) or not isinstance( limits[1][2], int):
            return False

        out_limit = [ [False, False, False], [False, False, False] ]
        result = True

        if self.x > limits[1][0]:
            out_limit[1][0] = True
            result = False
        
        if self.y > limits[1][1]:
            out_limit[1][1] = True
            result = False
        
        if self.z > limits[1][2]:
            out_limit[1][2] = True
            result = False

        if self.x < limits[0][0]:
            out_limit[0][0] = True
            result = False
        
        if self.y < limits[0][1]:
            out_limit[0][1] = True
            result = False
        
        if self.z < limits[0][2]:
            out_limit[0][2] = True
            result = False
                
        return result, out_limit
    
    
    def to_string(self):
    
        return str(self.x) + ','+ str(self.y) + ',' + str(self.z)


    def getId(self):
        """Return (x, y, z) tuple"""
        return tuple(self.getPosition())
    
    def getPosition(self):
        """Return (x, y, z) list"""
        return (self.x, self.y, self.z)

    def setPosition(self, pos):
        """Set x,y,z"""

        if not pos or not isinstance(pos, tuple ) or len(pos) != 3 or not isinstance(pos[0], int) or not isinstance(pos[1], int) or not isinstance(pos[2], int):
            return False
        
        self.x = pos[0]
        self.y = pos[1]
        self.z = pos[2]

        return False

    def getDirection( old_pos, new_pos ):
        """Return a vector from self.position to position"""        
        vect = General.calcVectorDiff( old_pos, new_pos )        
        mod = General.calcVectorModule( vect )
        return vect, mod 

    def getVector( self, position ):
        """Return a vector from self.position to position"""
        self_pos = self.getPosition()        
        vect = General.calcVectorDiff( self_pos, position )        
        mod = General.calcVectorModule( vect )
        return vect, mod 

    def getVectorAspect( self, vect, position ):
        """Return vector aspect, scalar product and vectorial product of vect and vector = origin-position """
        # se perpendicolari: prod_scal = 0, se alfa>0, <=90 prod scal > 0, se alfa>90, <=180 prod scal < 0
        aspect = None
        prod_scal = General.calcScalProd( vect, position )
        # ha il modulo proporzionale all'area del parallelogramma formato dai due vettori. Quindi se sono allineati(paralleli) il prod_vect = 0
        # (y1*z2 - z1*y2), (z1*x2 - x1*z2), (x1*y2 - y1*x2)
        prod_vect = General.calcVectProd( vect, position )
        
        if prod_scal > 0:
            aspect = "approach"
        
        elif prod_scal == 0:
            aspect = "tangent"
        
        else:
            aspect = "away"
        return aspect, prod_scal, prod_vect

    