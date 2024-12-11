"""
 MODULE Context
 
 Elenco delle variabili di contesto

"""
from enum import Enum

class STATE(Enum):
    Active = 1
    Inactive = 2
    Standby = 3
    Destroyed = 4
    
class SHAPE3D(Enum):
    Cylinder = 1
    Cube = 2
    Sphere = 3
    SemiSphere = 4
    Pyramid = 5
    Cone = 6
    Trunc_Cone = 7

class SHAPE2D(Enum):
    Circonference = 1
    Square = 2
    Hexagon = 3
    



