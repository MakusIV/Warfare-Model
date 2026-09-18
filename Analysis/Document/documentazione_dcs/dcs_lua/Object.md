#### Object

Represents an object with body, unique name, category and type. Non-final class.

**Types**

_Object.Category_ enum that stores object categories.

```
 Object.Category = {
   UNIT,
   WEAPON,
   STATIC,
   SCENERY,
   BASE
 }

```

**Structures**

```
 Object.Desc = extends Desc {
   life = number, --initial life level
   box = Box3 --bounding box of collision geometry
 }

```

object descriptor. Each object belongs to a type and each such type has its own descriptor. Descriptor format depends on object category, but always extends _Object.Desc_.

**Member functions**

```
 boolean function Object.isExist(Object self)

```

return if the object exist.

```
 function Object.destroy(Object self)

```

destroys the object without making damage to it and generation any event. The object just disappear. For now it is impossible to destroy remote objects.

```
 enum Object.Category Object.getCategory(Object self)

```

returns category of the object.

```
 TypeName Object.getTypeName(Object self)

```

returns type name of the object.

```
 Object.Desc Object.getDesc(Object self)

```

returns object descriptor.

```
 boolean function Object.hasAttribute(Unit self, AttributeName attributeName) 
 

```

_attributeName_

-   Attribute name to check.

returns true if the object belongs to the _category_.

```
 string Object.getName(Object self)

```

returns name of the object. This is the name that is assigned to the object in the Mission Editor.

```
 Vec3 function Object.getPoint(Object self) 

```

returns object coordinates for current time.

```
 Position3 function Object.getPosition(Object self) 

```

returns object position for current time.

```
 Vec3 function Object.getVelocity(Object self) 

```

returns the unit's velocity vector.

```
 boolean function Object.inAir(Object self) 

```

returns true if the unit is in air.