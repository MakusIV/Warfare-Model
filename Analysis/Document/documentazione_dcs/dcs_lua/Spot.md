#### Spot

Represents a spot from laser or IR-pointer. Final class.

**Types**

_Spot.Category_ enum that stores spot categories.

```
 Spot.Category = {
   INFRA_RED,
   LASER
 }

```

**Static functions**

```
 Spot function Spot.createInfraRed(Object source, Vec3 localPoint = nil, Vec3 point)

```

creates laser ray from the object to the given point.

_source_

-   The object as the IR beam source.

_localPoint_

-   The point in the object reference frame where the IR beam is radiated from. May be nil.

_point_

-   The spot point - end point of the IR beam.

```
 Spot function Spot.createInfraRed(Object source, Vec3 localPoint = nil, Vec3 point, number laserCode)

```

creates laser ray from the object to the given point.

_source_

-   The object as the laser beam source.

_localPoint_

-   The point in the object reference frame where the laser beam is radiated from. May be nil.

_point_

-   The spot point - end point of the laser beam.

_laserCode_

-   The code that is used by laser designator.

**Member functions**

```
 function Spot.destroy(Spot self)

```

Destroys the spot.

```
 Spot.Category function Spot.getCategory(Spot self)

```

Returns category of the spot.

```
 Vec3 function Spot.getPoint(Spot self)

```

Returns position of the spot, end of the beam.

```
 number function Spot.getCode(Spot self)

```

Returns laser code.

```
 function Spot.setPoint(Spot self, Vec3 point)

```

Sets position of the spot.

_point_

-   Position of the spot.

```
 function Spot.setCode(Spot self, number code)

```

Sets position of the spot.

_code_

-   Laser code.