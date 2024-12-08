from LoggerClass import Logger
import General
import math

# LOGGING --
 
logger = Logger(module_name = __name__, class_name = 'Sensibility')

class Sensibility:
    
    def __init__(self, max_range, accuracy = 5, type_space = 'TETRAHEDRIC'):

        if not self.checkParam( max_range, type_space ):
            raise Exception("Invalid parameters! Sensibility not istantiate.")

        self._type_space = type_space
        self._max_range = max_range
        self._accuracy = accuracy
        
        
        
    
    def checkParam( self, max_range, type_space ):
        if not max_range or not General.checkDimension(max_range) or type_space != 'TETRAHEDRIC':
            return False
        return True



    # tets: ok
    def get_probability_of_perception(self, start_percept_position):

        
        if self._type_space == 'TETRAHEDRIC':            
            return self.get_tetrahedric_probability( start_percept_position, self._accuracy )

        #if self._type_space == 'SPHERICAL':
        #    return self.spherical_sensibility(target_position)

        #if self._type_space == 'CONE':
        #    return self.cone_sensibility(target_position)

        #if self._type_space == 'PYRAMIDAL':
        #    return self.pyramidal_sensibility(target_position)

        
    # test: ok
    def get_tetrahedric_probability(self, position, num_volumes):
        """Return [subvolume, probability] where subvolume is a volume subset (volume/num_volumes)"""
        #position = start position of scanning
        #num_volumes = sections number of volume scanning (sub volumes)
        #Nota se maax_range contiene valori negativi la definizione dei subvolume è in direzione negativa. QUesto ha comportanto la necessità di eliminare il controllo in General.checkVolume() della coerenza dei limiti superiori e inferiori
        
        if not General.checkDimension(position):
            return False

        step_prob_volumes = 1 /num_volumes    
        dim_volumes = ( math.floor( self._max_range[0] / num_volumes ), math.floor( self._max_range[1] / num_volumes ), math.floor( self._max_range[2] / num_volumes ) )
        scanning_volumes = list() #None # scanning_volume = (volume, probability)
        logger.logger.debug("step_prob_volumes:{0} dim_volumes:{1}".format( step_prob_volumes, dim_volumes))

        for i in range(num_volumes):

            xi = int( position[0] + i * dim_volumes[0] )
            yi = int( position[1] + i * dim_volumes[1] )
            zi = int( position[2] + i * dim_volumes[2] )
            xf = int( position[0] + ( i + 1 ) * dim_volumes[0] - 1 )
            yf = int( position[1] + ( i + 1 ) * dim_volumes[1] - 1 )
            zf = int( position[2] + ( i + 1 ) * dim_volumes[2] - 1 )            
            volume = [ [ xi, yi, zi ] , [ xf, yf, zf ] ]
            probability = 1 - i * step_prob_volumes
            scanning_volumes.insert( i, [ volume, probability ] )
            logger.logger.debug("volume:{0}, volume points:{1}, probability:{2}".format( i, volume, probability))


        return scanning_volumes # scanning_volume = (volume, probability)


    def toString(self):
        return "type_space: " + self._type_space + " ,max_range: " + self._max_range



    