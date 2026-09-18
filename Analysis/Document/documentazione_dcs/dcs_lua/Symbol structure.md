#### Symbol structure

Simulator exports some functions and constants to the Mission Scripting Environment. All symbols are grouped in tables.  

#### Class emulation

Simulator has many entities which behave like an objects and classes in terms of object-oriented languages. To make manipulation with such objects easer "class-object" relations were emulated in the Lua environement with metatables. This framework is located in _./Scripts/Common/LuaClass.Lua._

Lua-"class" is a table that has following structure:

```
 Class = { 
   static = { 
     staticFunc1 = function(...) 
     ... 
     end, 
   ... 
     staticFuncN = function(...) 
     ... 
     end 
   }, 
   member = { 
     memberFunc1 = function(objectID, ...) 
     ... 
     end, 
   ... 
     memberFuncM = function(objectID, ...) 
     ... 
     end 
   },
   className_ = "ClassName", 
   parentClass_ = Class 
 }
 

```

_static_

-   Table with "static" functions. These functions have no object id as a parameter.

_member_

-   Table with "member" functions. These functions always have object id as a first parameter.

_className\__

-   String class name.

_parentClass\__

-   Reference to parent class table.

Lua-"object" is a table that has following structure:

```
 ObjectName = { 
   id_ = ... 
 }

```

_id\__

-   Object identifier. Its type depends on class. Member functions of Lua-"classes" has this identifier as a first argument.

Objects of the same class have set the same metatable - the class table.

The framework allows single inheritance, but doesn't allow multiple inheritance. Table of base class must be value of _parentClass\__ field table of derivative class.

_LuaClass_ table must be assigned as a metatable to all Lua-"classes". _LuaClass_ does all the job when user uses Lua-"classes" and Lua-"objects". _LuaClass.\_\_index_ metamethod is a function that looks for function that user want to call in Lua-"class" that the Lua-"object" belongs to or in base "classes" and calls the function.

_LuaClass_ has also useful several functions those may be called any Lua-"class".

```
 function LuaClass.createFor(class, id_) 

```

creates and returns Lua-"object" that belongs to class Lua-"class" and has identifier _id\__. No new entity created. The function just creates and initializies Lua-"object" table for existing entity.

```
 function LuaClass.create(class, ...) 

```

uses _class.static.create_ function to create new entity and then uses _LuaClass.createFor_ to create Lua-"object" class for just created entity.

```
 function LuaClass.cast(class, object) 

```

casts object to object of another class. Downcast must be unsafe if user will cast the object to class that object not realy belongs to.

```
 function class(tbl, parent) 

```

declares table _tbl_ as a Lua-"class" and as a derrivative class of a _parent_ if _parent_ is not nil

#### How does it works

Simulator exported some tables with functions and constants to the Mission Scripting Environment and then runs _./Scripts/MissionScripting.lua_ script do declare these tables a Lua-"classes".

However you may declare your own classes. To do it you must:

-   Create table and complete the table same way it shown here.
-   Declare the table as a class (and if you want as a derivative class). To do this call _class_ function.