#### Airbase

Represents airbases: airdromes, helipads and ships with flying decks or landing pads.

Extends _CoalitionObject_.

Final class.

**Types**

```
 Airbase.ID

```

Identifier of an airbase. It assigned to an airbase by the Mission Editor automatically.

This identifier is used in AI tasks to refer an airbase that exists (spawned and not dead) or not.

```
 Airbase.Category = {
   AIRDROME,
   HELIPAD,
   SHIP
 }

```

enum contains identifiers of airbase categories.

**Structures**

```
 Airbase.Desc = extends Desc {
   category = Airbase.Category
 }

```

airbase descriptor. Airdromes are unique and their types are unique, but helipads and ships are not always unique and may have the same type.

_category_

-   Category of the airbase type.

**Static function**

```
 Airbase Airbase.getByName(string name)

```

returns airbase by its name. If no airbase found the function will return nil.

```
 Airbase.Desc Airbase.getDescByName(TypeName typeName)

```

returns airbase descriptor by type name. If no descriptor is found the function will return nil.

_typeName_

-   Airbase type name.

**Member functions**

```
 Unit Airbase.getUnit(Airbase self)

```

returns _Unit_ that is corresponded to the airbase. Works only for ships.

```
 Airbase.ID Airbase.getID(Airbase self)

```

returns identifier of the airbase.

```
 string function Airbase.getCallsign(Airbase self) 

```

returns the airbase's callsign - the localized string.

```
 Airbase.Desc getDesc(Airbase self)

```

returns descriptor of the airbase.