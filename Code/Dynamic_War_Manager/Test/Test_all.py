

import Position_manager_test as pmt
import Object_test as obj
import Coordinate_test as coord
import State_test as st
import Actuator_test as act
import Sensor_test as sen
import Sensibility_test as sensi
import Automa_test as au

test = []

test.append( ["TestClassPosition_manager", pmt.TestClassPosition_manager() ] )
test.append( ["testClassObject", obj.testClassObject() ]  )
test.append( ["testClassCoordinate", coord.testClassCoordinate() ] )
test.append( ["testClassState", st.testClassState() ] )
test.append( ["testClassSensor", sen.testClassSensor() ] )
test.append( ["testClassActuator", act.testClassActuator() ] )
test.append( ["testClassSensibility", sensi.testClassSensibility() ] )
test.append( ["testClassAutoma", au.testClassAutoma() ] )

result = True

for t in test:

    if not t[1]:
        result = False
    print(t[ 0 ], t[ 1 ])

print("----------------------------------------------------->  All test result: ", result)