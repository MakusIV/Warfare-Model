#### Unit

Represents units: airplanes, helicopters, vehicles, ships and armed ground structures. Extends _CoalitionObject_. Final class. _Units_ exist in groups.

**Types**

```
 Unit.ID

```

Identifier of an unit. It assigned to an unit by the Mission Editor automatically.

```
 Unit.Category

```

enum that stores unit categories

```
 Unit.Category = {
   AIRPLANE,
   HELICOPTER,
   GROUND_UNIT,
   SHIP,
   STRUCTURE
 }

```

```
 Unit.RefuelingSystem

```

enum that stores aircraft refueling system types.

```
 Unit.RefuelingSystem = {
   BOOM_AND_RECEPTACLE,
   PROBE_AND_DROGUE
 }

```

```
 Unit.SensorType

```

enum that stores sensor types.

```
 Unit.SensorType = {
   OPTIC,
   RADAR,
   IRST,
   RWR
 }

```

```
 Unit.OpticType

```

enum that stores types of optic sensors.

```
 Unit.OpticType = {
   TV, --TV-sensor
   LLTV, --Low-level TV-sensor
   IR --Infra-Red optic sensor
 }

```

```
 Unit.RadarType

```

enum that stores radar types.

```
 Unit.RadarType = {
   AS, --air search radar
   SS --surface/land search radar
 }

```

**Structures**

```
 Unit.Desc extends Object.Desc = {
   category = enum Unit.Category,
   massEmpty = Mass, --mass of empty unit
   speedMax = Distance / Time, --maximal velocity
 }

```

an unit descriptor. This is common part of unit descriptor. Its format depends on unit category.

```
 Unit.DescAircraft extends Unit.Desc = {
   fuelMassMax = Mass, --maximal inner fuel mass
   range = Distance, --operational range
   Hmax = Distance, --ceiling
   VyMax = Distance / Time, --maximal climb rate
   NyMin = number, --minimal safe acceleration
   NyMax = number, --maximal safe acceleration
   tankerType = enum Unit.RefuelingSystem, --refueling system type
 }

```

an aircraft descriptor.

```
 Unit.DescAirplane extends Unit.DescAircraft = {
   speedMax0 = Distance / Time, --maximal TAS at ground level
   speedMax10K = Distance / Time --maximal TAS at altitude of 10 km
 }

```

an airplane descriptor.

```
 Unit.DescHelicopter extends Unit.DescAircraft = {
   HmaxStat = Distance, --static ceiling
 }

```

a helicopter descriptor.

```
 Unit.DescVehicle extends Unit.Desc = {
   maxSlopeAngle = Angle, --maximal slope angle
   riverCrossing = boolean, --can the vehicle cross a rivers
 }

```

a vehicle descriptor.

```
 Unit.DescShip extends Unit.Desc = {
 }

```

a ship descriptor.

```
 Unit.AmmoItem = {
   desc = Weapon.Desc, --ammunition descriptor
   count = number --ammunition count
 }

```

ammunition item: "type-count" pair.

```
 Unit.Ammo = array of Unit.AmmoItem

```

an unit ammunition.

```
 Unit.Sensor = {
   typeName = TypeName,
   type = enum Unit.SensorType
 }

```

an unit sensor.

```
 Unit.Optic extends Unit.Sensor = {
   opticType = enum Unit.OpticType
 }

```

an optic sensor.

```
 Unit.Radar extends Unit.Sensor = {
   detectionDistanceRBM = Distance or nil, --detection distance for RCS=1m^2 in real-beam mapping mode, nil if radar doesn't support surface/land search
   detectionDistanceHRM = Distance or nil, --detection distance for RCS=1m^2 in high-resolution mapping mode, nil if radar has no HRM
   detectionDistanceAir = { --detection distance for RCS=1m^2 airborne target, nil if radar doesn't support air search
     upperHemisphere = {
       headOn = Distance,
       tailOn = Distance
     },
     lowerHemisphere = {
       headOn = Distance,
       tailOn = Distance
     }
   }
 }

```

a radar.

```
 Unit.IRST extends Unit.Sensor = {
   detectionDistanceIdle = Distance, -- detection of tail-on target with heat signature = 1 in upper hemisphere, engines are in idle
   detectionDistanceMaximal = Distance, -- ..., engines are in maximal mode
   detectionDistanceAfterburner = Distance, -- ..., engines are in afterburner mode
 }

```

an IRST.

```
 Unit.RWR extends Unit.Sensor = {
 }

```

an RWR.

```
 Sensors = {
   [Unit.SensorType.OPTIC] = array of Unit.OpticSensor or nil,
   [Unit.SensorType.RADAR] = array of Unit.Radar or nil,
   [Unit.SensorType.IRST] = array of Unit.IRST or nil,
   [Unit.SensorType.RWR] = array of Unit.RWR or nil,
 }

```

table that stores all unit sensors.

**Static functions**

```
 Unit function Unit.getByName(string name) 

```

returns unit object by the name assigned to the unit in Mission Editor. If there is unit with such name or the unit is destroyed the function will return nil. The function provides access to non-activated units too.

**Member functions**

```
 boolean function Unit.isActive(Unit self) 

```

returns if the unit is activated.

```
 string function Unit.getPlayerName(Unit self)

```

returns name of the player that control the unit or nil if the unit is controlled by A.I.

```
 Unit.ID function Unit.getID(Unit self)

```

returns the unit's unique identifier.

```
 number function Unit.getNumber(Unit self) 

```

returns the unit's number in the group. The number is the same number the unit has in ME. It may not be changed during the mission. If any unit in the group is destroyed, the numbers of another units will not be changed.

```
 Controller function Unit.getController(Unit self) 

```

returns controller of the unit if it exist and nil otherwise

```
 Group function Unit.getGroup(Unit self) 

```

returns the unit's group if it exist and nil otherwise

```
 string function Unit.getCallsign(Unit self) 

```

returns the unit's callsign - the localized string.

```
 number function Unit.getLife(Unit self) 

```

returns the unit's health. Dead units has health <= 1.0

```
 number function Unit.getLife0(Unit self) 

```

returns the unit's initial health.

```
 number function Unit.getFuel(Unit self) 

```

returns relative amount of fuel (from 0.0 to 1.0) the unit has in its internal tanks. If there are additional fuel tanks the value may be greater than 1.0.

```
 Unit.Ammo function Unit.getAmmo(Unit self)

```

returns the unit ammunition.

```
 Unit.Sensors function Unit.getSensors(Unit self)

```

returns the unit sensors.

```
 boolean function Unit.hasSensors(Unit self, enum Unit.SensorType sensorType = nil, ...)

```

returns true if the unit has specified types of sensors. This function is more preferable than _Unit.getSensors()_ if you don't want to get information about all the unit's sensors, and just want to check if the unit has specified types of sensors.

-   sensorType

Sensor type.

-   ...

Additional parameters.

If _sensorType_ is _Unit.SensorType.OPTIC_, additional parameters are optic sensor types. Following example checks if the unit has LLTV or IR optics:

```
 unit:hasSensors(Unit.SensorType.OPTIC, Unit.OpticType.LLTV, Unit.OpticType.IR)

```

If _sensorType_ is _Unit.SensorType.RADAR_, additional parameters are radar types. Following example checks if the unit has air search radars:

```
 unit:hasSensors(Unit.SensorType.RADAR, Unit.RadarType.AS)

```

If no additional parameters are specified the function returns true if the unit has at least one sensor of specified type.

If sensor type is not specified the function returns true if the unit has at least one sensor of any type.

```
 boolean, Object function Unit.getRadar(Unit self)

```

returns two values:

-   first value indicates if at least one of the unit's radar(s) is on
-   second value is the object of the radar's interest. Not nil only if at least one radar of the unit is tracking a target.

```
 Unit.Desc function Unit.getDesc(Unit self)

```

returns unit descriptor. Descriptor type depends on unit category.