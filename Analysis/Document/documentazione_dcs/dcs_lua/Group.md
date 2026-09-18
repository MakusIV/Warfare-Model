#### Group

Represents group of _Units_.

**Types**

```
 Group.Category = {
   AIRPLANE,
   HELICOPTER,
   GROUND,
   SHIP
 }

```

enum contains identifiers of group types.

```
 Group.ID

```

Identifier of a group. It is assigned to a group by Mission Editor automatically.

**Static functions**

```
 Group function Group.getByName(string name) 

```

returns group by the name assigned to the group in Mission Editor.

**Member functions**

```
 boolean function Group.isExist(Group self)

```

returns true if the group exist or false otherwise.

```
 function Group.destroy(Group self)

```

destroys the group and all of its units.

```
 enum Group.Category function Group.getCategory(Group self)

```

returns category of the group.

```
 enum coalition.side function Group.getCoalition(Group self)

```

returns coalition of the group.

```
 string function Group.getName(Group self)

```

returns the group's name. This is the same name assigned to the group in Mission Editor.

```
 Group.ID function Group.getID(Group self)

```

returns the group identifier.

```
 Unit function Group.getUnit(number unitNumber)

```

returns the unit with number _unitNumber_. If the unit is not exists the function will return _nil_.

```
 number function Group.getSize(Group self)

```

returns initial size of the group. If some of the units will be destroyed, initial size of the group will not be changed. Initial size limits the _unitNumber_ parameter for _Group.getUnit()_ function.

```
 array of Unit function Group.getUnits(Group self)

```

returns array of the units present in the group now. Destroyed units will not be enlisted at all.

```
 Controller function Group.getController(Group self)

```

returns controller of the group.