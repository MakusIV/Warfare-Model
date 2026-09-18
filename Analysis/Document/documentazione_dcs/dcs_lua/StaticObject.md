## StaticObject

-   [StaticObject](https://www.digitalcombatsimulator.com/it/support/faq/1814/#3333827)

#### StaticObject

Represents static object added in the Mission Editor. Extends _CoalitionObject_. Final class.

**Types**

```
 StaticObject.ID

```

Identifier of a static object. It is assigned to a static object by the Mission Editor automatically.

**Structures**

```
 StaticObject.Desc = Unit.Desc

```

Descriptor of _StaticObject_ and _Unit_ are equal. _StaticObject_ is just a passive variant of _Unit_.

**Static functions:**

```
 StaticObject function StaticObject.getByName(string name)

```

returns static object by its name. If no static object found nil will be returned.

**Member functions:**

```
 StaticObject.ID function StaticObject.getID(StaticObject self)

```

returns identifier of the static object.

```
 StaticObject.Desc StaticObject.getDesc(StaticObject self)

```

return descriptor of the static object.

_name_

-   Name of static object to find.