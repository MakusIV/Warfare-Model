-   [Controller](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333830)
-   [Tasks](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333831)
-   [Main Tasks](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333832)
-   [Enroute tasks](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333833)
-   [Special Tasks](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333834)
-   [Commands](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333835)
-   [Behavior options](https://www.digitalcombatsimulator.com/it/support/faq/1817/#3333836)

#### Controller

Controller is an object that performs A.I.-routines. Other words controller is an instance of A.I.. Controller stores current main task, active enroute tasks and behavior options. Controller performs commands.

Please, read **DCS A-10C GUI Manual EN.pdf chapter "Task Planning for Unit Groups", page 91** to understand A.I. system of DCS:A-10C.

```
 function Controller.setOnOff(Controller self, boolean value) 

```

enables and disables the controller.

**Note: Now it works only for ground / naval groups!**

_value_

-   Enable / disable.

#### Tasks

```
 function Controller.setTask(Controller self, Task task) 

```

resets current task and then sets the task to the controller. Task is a table that contains task identifier and task parameters.

```
 function Controller.resetTask(Controller self) 

```

resets current task of the controller

Common task format is:

```
Task = {
  id = string, 
  params = { 
  } 
} 

```

-   _id_

String task identifier.

```
 function Controller.pushTask(Controller self, Task task) 

```

pushes the task to the front of the queue and makes the task active. Further call of _function Controller.setTask()_ function will stop current task, clear the queue and set the new task active. If the task queue is empty the function will work like _function Controller.setTask()_ function.

```
 function Controller.popTask(Controller self) 

```

pops current (front) task from the queue and makes active next task in the queue (if exists). If no more tasks in the queue the function works like _function Controller.resetTask()_ function. Does nothing if the queue is empty.

```
 boolean function Controller.hasTask(Controller self) 

```

returns true if the controller has a task.

#### Main Tasks

#### Tasks for airborne units/groups

**1\. NoTask**

An empty task. It finished just being started.

```
 NoTask = { 
   id = 'NoTask', 
   params = { 
   } 
 } 

```

**2\. AttackGroup**

Attacking the target group (airborne, ground or naval).

```
 AttackGroup = { 
   id = 'AttackGroup', 
   params = { 
     groupId = Group.ID,
     weaponType = number,
     expend = enum AI.Task.WeaponExpend,
     attackQty = number,
     directionEnabled = boolean,
     direction = Azimuth,
     altitudeEnabled = boolean,
     altitude = Distance,
     attackQtyLimit = boolean,
   } 
 }

```

_groupId_

-   Inner unique identifier of the group to attack.

_weaponType_ (optional)

-   Bitmask of weapon types those allowed to use. If parameter is not defined that means no limits on weapon usage.

Weapon flags are enlisted in _Weapon.flag_ table.

-   expend (optional)

Determines how much weapon will be released at each attack. If parameter is not defined the unit / group will choose expend on its own discretion.

-   _attackQty_ (optional)

This parameter limits maximal quantity of attack. The aicraft/group will not make more attack than allowed even if the target group not destroyed and the aicraft/group still have ammo. If not defined the aircraft/group will attack target until it will be destroyed or until the aircraft/group will run out of ammo.

-   _attackQtyLimit_ (optional)

The flag determines how to interpret _attackQty_ parameter. If the flag is true then _attackQty_ is a limit on maximal attack quantity for "AttackGroup" and "AttackUnit" tasks. If the flag is false then _attackQty_ is a desired attack quantity for "Bombing" and "BombingRunway" tasks.

**Note:** this looks like not a good solution. It would be better to have two number parameters: required parameter _attackQty_ for "Bombing" and "BombingRunway" tasks and _attackQtyLimit_ for "AttackGroup" and "AttackUnit" tasks.

-   _directionEnabled_

Indicates ingress direction is defined.

-   _direction_ (optional)

Desired ingress direction from the target to the attacking aircraft. Group/aircraft will make its attacks from the direction. Of course if there is no way to attack from the direction due the terrain group/aircraft will choose another direction.

-   _altitudeEnabled_

Indicates attack start altitude is defined.

-   _direction_ (optional)

Desired attack start altitude. Group/aircraft will make its attacks from the altitude. If the altitude is too low or too high to use weapon aircraft/group will choose closest altitude to the desired attack start altitude. If the desired altitude is defined group/aircraft will not attack from safe altitude.

**3\. AttackUnit**

Attacking the target (airborne, ground or naval).

```
AttackUnit = { 
  id = 'AttackUnit', 
  params = { 
    unitId = Unit.ID, 
    weaponType = number, 
    expend = enum AI.Task.WeaponExpend
    attackQty = number, 
    direction = Azimuth, 
    attackQtyLimit = boolean, 
    groupAttack = boolean, 
  } 
} 

```

The task has the same parameters of _AttackGroup_, but has _unitId_ parameter instead of _groupId_ and additional parameter _groupAttack_.

-   _unitId_

Inner unique identifier of the unit to attack.

-   _groupAttack_ (optional)

Flag indicates that the target must be engaged by all aircrafts of the group. Has effect only if the task is assigned to a group, not to a single aircraft.

**4\. Bombing**

Delivering weapon at the point on the ground.

```
Bombing = { 
  id = 'Bombing', 
  params = { 
    point = Vec2,
    weaponType = number, 
    expend = enum AI.Task.WeaponExpend,
    attackQty = number, 
    direction = Azimuth, 
    groupAttack = boolean, 
  } 
} 

```

The task has the same parameters of _AttackUnit_ task, but has parameters _point_ instead of _unitId_, plus _attackQty_ and minus _attackQtyLimit_ parameters.

_point_

-   2D-coordinates of the point to deliver weapon at.

_attackQty_

-   Desired quantity of passes. The parameter is not the same in _AttackGroup_ and _AttackUnit_ tasks.

**5\. AttackMapObject**

Attacking the map object (building, structure, e.t.c).

```
AttackMapObject = { 
  id = 'AttackMapObject', 
  params = { 
    point = Vec2,
    weaponType = number, 
    expend = enum AI.Task.WeaponExpend,
    attackQty = number, 
    direction = Azimuth, 
    groupAttack = boolean, 
  } 
} 

```

The task has the same parameters _AttackUnit_ task has, but has parameters _point_ instead of _unitId_.

_point_

-   2D-coordinates of the point the map object is closest to. The distance between the point and the map object must not be greater than 2000 meters.

Object id is not used here because Mission Editor doesn't support map object identificators.

**6\. BombingRunway**

Delivering weapon on the runway.

```
 BombingRunway = { 
   id = 'BombingRunway', 
   params = { 
     runwayId = AirdromeId, 
     weaponType = number, 
     expend = enum AI.Task.WeaponExpend,
     attackQty = number, 
     direction = Azimuth, 
     groupAttack = boolean, 
   } 
 }

```

The task has the same parameters _Bombing_ task has, but has parameter _runwayId_ instead of _point_.

_runwayId_

-   Numeric identifier of the airdrome.

_attackQty_

-   Desired quantity of attack of the point. The parameter is not the same in _AttackGroup_ and _AttackUnit_ tasks.

**7\. Orbit**

Flying orbit.

```
Orbit = { 
  id = 'Orbit', 
  params = { 
    pattern = enum AI.Task.OribtPattern,
    point = Vec2,
    point2 = Vec2,
    speed = Distance,
    altitude = Distance
  } 
}


```

_pattern_

-   String identifier of orbit pattern. Pattern constants: "Circle", "Race-Track".

_point_ (optional)

-   2D-coordinates of the orbit point. If not defined position of the current waypoint will be used.

_speed_ (optional)

-   Desired aircraft(s) speed. If not defined 1.5 \* stall velocity will be used.

_altitude_ (optional)

-   Desired orbit altitude. If not defined altitude of the current waypoint will be used.

_point2_ (optional)

-   Second point for Race-Rrack orbit pattern. If not defined the next waypoint position will be used.

Orbit Patterns.

-   Circle. Aircraft will stay in left turn. The center of circle-shaped trajectory is anchored to _point_.

-   Race-Track. The trajectory consists of two parallel legs and 180-degrees left turns on each side of the legs. Race-track trajectory is defined by a two 2D-points those form the right leg. The first point is _point_, the second point is _point2_.

_speed_ and _altitude_ are an optional parameters. If not defined aircraft will fly orbit at altitude of first waypoint and with speed equal 1.5 of stall airspeed.

**8\. Refueling**

Refueling from the nearest tanker. No parameters.

```
 Refueling = { 
   id = 'Refueling', 
   params = {} 
 }

```

**9\. Land**

Landing at the ground. For helicopters only.

```
 Land = {
   id= 'Land',
   params = {
     point = Vec2,
     durationFlag = boolean,
     duration = Time
   }
 }

```

_point_

-   The point to land at.

_durationFlag_

-   The flag specifies is time on land is limited or not.

_duration_

-   Time on land. Has effect only if _durationFlag_ is true.

**10\. Follow**

Following another airborne group. The unit / group will follow lead unit of another group, wingmens of both groups will continue following their leaders. If another group is on land the unit / group will orbit around.

```
 Follow = {
   id = 'Follow',
   params = {
     groupId = Group.ID,
     pos = Vec3,
     lastWptIndexFlag = boolean,
     lastWptIndex = number
   }    
 }

```

_groupId_

-   Itendificator of the group to follow to.

_pos_

-   Position of the unit / lead unit of the group relative lead unit of another group in frame reference oriented by course of lead unit of another group. If another group is on land the unit / group will orbit around.

_lastWptIndexFlag_

-   The flag indicates the unit / group will follow another group until another group reach specified waypoint.

_lastWptIndex_

-   Detach waypoint of another group. Once reached the unit / group _Follow_ task is finished.

**11\. Escort**

Escort another airborne group. The unit / group will follow lead unit of another group, wingmens of both groups will continue following their leaders. The unit / group will also protect that group from threats of specified types.

```
 Escort = {
   id = 'Escort',
   params = {
     groupId = Group.ID,
     pos = Vec3,
     lastWptIndexFlag = boolean,
     lastWptIndex = number,
     engagementDistMax = Distance,
     targetTypes = array of AttributeName
   }
 }

```

The parameters are the same _Follow_ task has, but plus 2 additional:

_engagementDistMax_

-   Maximal distance from escorted group to threat. If the threat is already engaged by escort escort will disengage if the distance becomes greater than 1.5 \* _engagementDistMax_.

_targetTypes_

-   Array of _AttributeName_ that is contains threat categories allowed to engage.

**12\. Mission**

Mission is a complex task. Performing the Mission means flying the route and performing tasks at each waypoint of the route.

```
 Mission = { 
   id = 'Mission', 
   params = { 
     route = { 
       points = { 
         [1] = { 
           type = enum AI.Task.WaypointType, 
           airdromeId = Airbase.ID, 
           helipadId = Airbase.ID, 
           action = enum AI.Task.TurnMethod, 
           x = Distance, 
           y = Distance, 
           alt = Distance, 
           alt_type = enum AI.Task.AltitudeType, 
           speed = Distance, 
           speed_locked = boolean, 
           ETA = Time, 
           ETA_locked = boolean, 
           name = string, 
           task = Task 
         }, 
         [2] = { 
           ... 
         }, 
         ... 
         [N]= { 
           ... 
         } 
       } 
     }, 
   } 
 } 

```

_route_

-   Table that stores route data such as waypoints, destination airdrome. To understand route structure please, read **DCS A-10C GUI Manual EN.pdf chapter "Group Route Planning", page 94**.

_points_

-   Waypoints of the route.

_type_

-   Waypoint type.

_airdromeId_

-   identifier of the airdrome to land. Has effect only if waypoint type is "Land".

_helipadId_

-   Inner unique identifier of helipad or ship to land. Has effect only if waypoint type is "Land".

_action_

-   Turn method.

_x, y_

-   2D-coordinates of the waypoint.

_alt_

-   Altitude assigned to the waypoint. The aircraft(s) will climb/descent to reach the waypoint at asigned altitude.

_alt\_type_

-   Type of altitude assigned to the waypoint.

_speed_

-   True airspeed assigned to the waypoint. Has effect only if _speed\_locked_ is true.

_speed\_locked_

-   Flag that means the true airspeed is assigned to the waypoint and the aircraft(s) will keep it on its way to the waypoint.

_ETA_

-   Time-On-Target of the waypoint. Has effect only if _ETA\_locked_ is true.

_ETA\_locked_

-   Flag that means that the Time-On-Target is assigned to the waypoint and the aircraft(s) will adjust its airspeed to reach the waypoint at assigned time.

_name_

-   Helper in Mission Editor. Has no effect in simulator.

_task_

-   Task that must be performed when aircraft/air group will passed over the waypoint.

#### Tasks for ground units

**1\. FireAtPoint**

Firing at point until there is ammo.

```
 FireAtPoint = { 
   id = 'FireAtPoint', 
   params = { 
     point = Vec2,
     radius = Distance, 
   } 
 }


```

_point_

-   2-D coordinates of the point to fire at.

_radius_ (optional)

-   Radius of the zone to fire at. If the radius is defined the vehicle group will fire at random places within the radius and fire at point otherwise.

**2\. Hold**

Not moving. No parameters.

```
 Hold = { 
   id = 'Hold', 
   params = { 
   } 
 }


```

**3\. Mission**

Mission is a complex task. Performing the Mission means following the route and performing tasks at each waypoint of the route.

```
 Mission = { 
   id = 'Mission', 
   params = { 
     route = { 
       points = { 
         [1] = {
           action = enum AI.Task.VehicleFormation,
           x = Distance, 
           y = Distance, 
           speed = Distance,
           ETA = Time,
           ETA_locked = boolean,
           name = string, 
           task = Task 
         }, 
         [2] = { 
           ... 
         }, 
         ... 
         [N]= { 
           ... 
         } 
       } 
     }, 
   } 
 }


```

_route_

-   Table that stores route data such as waypoints, destination airdrome. To understand route structure please read **DCS A-10C GUI Manual EN.pdf chapter "Group Route Planning", page 94**.

_points_

-   Waypoints of the route.

Waypoint

_action_

-   Vehicle formation:

_x, y_

-   2D-coordinates of the waypoint.

_speed_

-   Speed assigned to the waypoint. Has effect only if _speed\_locked_ is true.

_ETA_

-   Required/estimated time of arrival. If _ETA\_locked_ is true _ETA_ is required time of arrival and group will adjust its speed to arrive at the waypoint at the given time. Estimated time of arrival has sense only for Mission Editor.

_ETA\_locked_

-   Indicates is _ETA_ required or estimated time of arrival.

_name_

-   Helper in Mission Editor. Has no effect in simulator.

_task_

-   Task that must be performed when unit/group will passed the waypoint.

#### Tasks for airborne and group units/groups

**1\. FAC\_AttackGroup**

The task makes the group/unit a FAC and orders the FAC to control the target (enemy ground group) destruction. The killer is player-controlled allied CAS-aircraft that is in contact with the FAC.

If the task is assigned to the group lead unit will be a FAC.

```
 FAC_AttackGroup = { 
   id = 'FAC_AttackGroup', 
   params = { 
     groupId = Group.ID,
     weaponType = number,
     designation = enum AI.Task.Designation,
     datalink = boolean
   } 
 }

```

-   _groupId_
-   Target group identifier.

_weaponType_ (optional)

-   Bitmask of weapon types those allowed to use. If parameter is not defined that means no limits on weapon usage.

Weapon flags are enlisted in _Weapon.flag_ table.

_designation_ (optional)

-   Designation type.

_datalink_ (optional)

-   Allows to use datalink to send the target information to attack aircraft. Enabled by default.

#### Enroute tasks

#### En-route tasks for airborne units/groups

**1\. EngageTargets**

All enroute tasks have the priority parameter. This is a number (less value - higher priority) that determines actions related to what task will be performed first.

Engaging a targets of defined types.

```
 EngageTargets ={ 
   id = 'EngageTargets', 
   params = { 
     maxDist = Distance, 
     targetTypes = array of AttributeName, 
     priority = number 
   } 
 }

```

_maxDist_

-   Maximal distance from the target to a route leg. If the target is on a greater distance it will be ignored.

_targetTypes_

-   Array of target categories allowed to engage.

**2\. EngageTargetsInZone**

Engaging a targets of defined types at circle-shaped zone.

```
 EngageTargetsInZone = { 
   id = 'EngageTargetsInZone', 
   params = { 
     point = Vec2, 
     zoneRadius = Distance, 
     targetTypes = array of AttributeName,  
     priority = number 
   }
 }

```

_point_

-   2D-coordinates of the zone.

_zoneRadius_

-   Radius of the zone.

_targetTypes_

-   Array of target categories allowed to engage.

**3\. Engage Group**

Engaging a group. The task does not assign the target group to the unit/group to attack now; it just allows the unit/group to engage the target group as well as other assigned targets.

```
 EngageGroup = { 
   id = 'EngageGroup', 
   params = { 
     groupId = Group.ID, 
     weaponType = number, 
     expend = enum AI.Task.WeaponExpend, 
     attackQty = number, 
     direction = Azimuth, 
     attackQtyLimit = boolean, 
     priority = number 
   } 
 } 

```

The task has same parameters of AttackGroup task, plus priority.

**4\. EngageUnit**

Engaging an unit. By this task you do not assign the target to the unit/group to attack now, you just allow the unit/group to engage the target as well as other assigned targets.

```
 EngageUnit = { 
   id = 'EngageUnit', 
   params = { 
     unitId = UnitId, 
     weaponType = number, 
     expend = enum AI.Task.WeaponExpend, 
     attackQty = number, 
     direction = Azimuth, 
     attackQtyLimit = boolean, 
     groupAttack = boolean, 
     priority = number 
   } 
 }

```

The task has same parameters of AttackUnit task, plus priority.

**5\. AWACS**

Aircraft will act as an AWACS for friendly units (will provide them with information about contacts). No parameters.

```
 AWACS = { 
   id = 'AWACS', 
   params = { 
   } 
 }


```

**6\. Tanker**

Aircraft will act as a tanker for friendly units. No parameters.

```
 Tanker = { 
   id = 'Tanker', 
   params = { 
   } 
 }

```

#### En-route tasks for ground units/groups

**1\. EWR**

Ground unit (EW-radar) will act as an EWR for friendly units (will provide them with information about contacts). No parameters.

```
 EWR = { 
   id = 'EWR', 
   params = { 
   } 
 }

```

#### En-route tasks for airborne and ground units/groups

**1\. FAC\_EngageGroup**

The task makes the group/unit a FAC and lets the FAC to choose the target (enemy ground group) as well as other assigned targets. The killer is player-controlled allied CAS-aircraft that is in contact with the FAC.

If the task is assigned to the group lead unit will be a FAC.

```
 FAC_EngageGroup = { 
   id = 'FAC_AttackGroup', 
   params = { 
     groupId = Group.ID,
     weaponType = number,
     designation = enum AI.Task.Designation,
     datalink = boolean,
     priority = number
   } 
 }

```

The parameters are the same _FAC\_AttackGroup_ task has plus _priority_.

**2\. FAC**

The task makes the group/unit a FAC andlets the FAC to choose a targets (enemy ground group) around as well as other assigned targets. The killer is player-controlled allied CAS-aircraft that is in contact with the FAC.

If the task is assigned to the group lead unit will be a FAC.

```
 FAC = { 
   id = 'FAC', 
   params = { 
     radius = Distance,
     priority = number
   } 
 }

```

_radius_

-   The maximal distance from the FAC to a target.

#### Special Tasks

**1\. Controlled Task**

This is a wrapper for a task that makes possible to assign special conditions to stop a task.

```
 ControlledTask = { 
   id = 'ControlledTask', 
   params = { 
     task = Task, 
     stopCondition = StopCondition, 
   } 
 }

```

_StopCondition_ consists of several sub-conditions. Each sub-condition is optional. If at least one of the conditions has met, the task will be stopped. All the sub-conditions will being checked periodically.

```
 StopCondition = { 
   time = Time, 
   userFlag = string, 
   userFlagValue = boolean, 
   condition = string, 
   duration = Time, 
   lastWaypoint = number, 
 }

```

_time_ (optional)

-   Time of the task finish. If the _time_ is defined, the condition will be met if the current time is greater than the _time_.

or

User Flag (optional).

_userFlag_

-   Name of the user flag.

_userFlagValue_

-   Value of the user flag

The condition will be met only is the _userFlag_ has value that equals to _userFlagValue_.

or

_condition_ (optional)

-   Lua code that will be wrapped into the function that returns boolean type.

```
 function [generated name]() 
   return [Lua code] 
 end

```

The condition will be met when the function will return true.

or

_duration_ (optional)

-   Limit on task duration. The condition will be met when the task duration will become greater than _duration_.

or

_lastWaypoint_ (optional)

-   Last waypoint where the task will still active. Used for enroute tasks only. The condition will be met if the group/unit switched to the next waypoint after _lastWaypoint_.

**2\. Combo Task**

Combo Task is a list of actions to run them in the order they are enlisted.

```
 ComboTask = { 
   id = 'ComboTask', 
   params = { 
     tasks = { 
       [1] = Task, 
       [2] = Task, 
       ... 
       [N] = Task 
     } 
   } 
 } 

```

The task may be useful if it is necessary to assign list of actions to the group/unit. For example, actions list created for the waypoint in Mission Editor is a Combo Task. It is only possible to fill Combo Task with tasks. To fill the Combo Task with Commands and Behavior Options you should use Wrapped Action task.

**3\. Wrapped Action**

A command wrapped into task. This construction may be useful in _ComboTask_.

```
 WrappedAction = { 
   id = 'WrappedAction', 
   params = { 
     action = Command 
   }
 }


```

#### Commands

Commands are instant actions those required zero time to perform. Commands may be used both for control unit/group behavior and control game mechanics.

```
 function Controller.setCommand(Controller self, Command command) 

```

sets the command to perform by controller.

_Command_

```
 Table that contains command identifier and command parameters. 

```

Commands have following format

```
 Command = { 
   id = string, 
   params = { 
   } 
 }

```

_id_ is a string identifier of the command

**1\. No Action**

Empty action. No parameters.

```
 NoAction = { 
   id = 'NoAction', 
   params = { 
   } 
 }

```

**2\. Script**

Runs Lua-script.

```
 Script = { 
   id = 'Script', 
   params = { 
     command = string  
   } 
 }

```

_command_

-   String that contains Lua code

**3\. Set callsign**

Sets callsign to the group. It is only valid for western groups those have hierarchic callsigns: \[group callname\]\[flight number\]\[aircraft number\]. You can change \[group callname\]\[flight number\] part of callsign for all aircraft in the group of for single aircraft.

```
 SetCallsign = { 
   id = 'SetCallsign', 
   params = { 
     callname = number, 
     number = number, 
   } 
 }

```

_callname_

-   Numeric group callname identifier. Note that the different group callnames can have same identifier, but there are no conflicts because these callnames cannot be used by unit of same type. Callnames are enlisted in _./Scripts/Database/db\_callnames.Lua_.

Aircrafts

<table><tbody><tr><td>Callname</td><td>Identifier</td></tr><tr><td>Enfield</td><td>1</td></tr><tr><td>Springfield</td><td>2</td></tr><tr><td>Uzi</td><td>3</td></tr><tr><td>Colt</td><td>4</td></tr><tr><td>Dodge</td><td>5</td></tr><tr><td>Ford</td><td>6</td></tr><tr><td>Chevy</td><td>7</td></tr><tr><td>Pontiac</td><td>8</td></tr><tr><td>Hawg</td><td>9</td></tr><tr><td>Boar</td><td>10</td></tr><tr><td>Pig</td><td>11</td></tr><tr><td>Tusk</td><td>12</td></tr></tbody></table>

AWACS

<table><tbody><tr><td>Callname</td><td>Identifier</td></tr><tr><td>Overlord</td><td>1</td></tr><tr><td>Magic</td><td>2</td></tr><tr><td>Wizard</td><td>3</td></tr><tr><td>Focus</td><td>4</td></tr><tr><td>Darkstar</td><td>5</td></tr></tbody></table>

Tanker

<table><tbody><tr><td>Callname</td><td>Identifier</td></tr><tr><td>Texaco</td><td>1</td></tr><tr><td>Arco</td><td>2</td></tr><tr><td>Shell</td><td>3</td></tr></tbody></table>

Ground JTAC

<table><tbody><tr><td>Callname</td><td>Identifier</td></tr><tr><td>Axeman</td><td>1</td></tr><tr><td>Darknight</td><td>2</td></tr><tr><td>Warrior</td><td>3</td></tr><tr><td>Pointer</td><td>4</td></tr><tr><td>Eyeball</td><td>5</td></tr><tr><td>Moonbeam</td><td>6</td></tr><tr><td>Whiplash</td><td>7</td></tr><tr><td>Finger</td><td>8</td></tr><tr><td>Pinpoint</td><td>9</td></tr><tr><td>Ferret</td><td>10</td></tr><tr><td>Shaba</td><td>11</td></tr><tr><td>Playboy</td><td>12</td></tr><tr><td>Hammer</td><td>13</td></tr><tr><td>Jaguar</td><td>14</td></tr><tr><td>Deathstar</td><td>15</td></tr><tr><td>Anvil</td><td>16</td></tr><tr><td>Firefly</td><td>17</td></tr><tr><td>Mantis</td><td>18</td></tr><tr><td>Badger</td><td>19</td></tr></tbody></table>

_number_

-   Flight number.

**4\. Set frequency**

Sets frequency and modulation to the unit's radio or to the radio of each unit in the group.

```
 SetFrequency = { 
   id = 'SetFrequency', 
   params = { 
     frequency = number, 
     modulation = enum radio.modulation, 
   } 
 }


```

_modulation_

-   Modulation of the radio.

_frequency_

-   Frequency of the radio in Hz.

**5\. Switch waypoint**

Switches current leg of the route. Has effect only if the "Mission" task is active.

```
 SwitchWaypoint = { 
   id = 'SwitchWaypoint', 
   params = { 
     fromWaypointIndex = number,  
     goToWaypointIndex = number, 
   } 
 } 

```

New leg is defined by a two parameters:

_fromWaypointIndex_

-   Index of the waypoint "from" of the new route leg.

_goToWaypointIndex_

-   Index of the waypoint "to" of the new route leg.

  
**6\. Stop route**

Stops / resumes following the route. Has effect only if the "Mission" task is active.

```
 StopRoute = { 
   id = 'StopRoute', 
   params = { 
     value = boolean, 
   } 
 }

```

_value_

-   Stops (true) or resumes (false) following the route.

**7\. Switch action**

Switches to an another action of the actions list of the waypoint. Has effect only if the "Mission" task is active.

```
 SwitchAction = { 
   id = 'SwitchAction', 
   params = { 
     actionIndex = number, 
   }   
 }

```

_actionIndex_

-   Index of the action to switch to. Actions are enumerated from 1 to N.

**8\. Invisible**

Makes the unit/group invisible for enemy A.I.

```
 SetInvisible = { 
   id = 'SetInvisible', 
   params = { 
     value = boolean 
   } 
 }


```

_value_

-   Invisible status.

**9\. Immortal**

Makes the unit/group immortal.

```
 SetImmortal = { 
   id = 'SetImmortal', 
   params = { 
     value = boolean 
   } 
 }

```

_value_

-   Immortal status

**10\. Activate beacon**

Activates the beacon onboard the aircraft or onboard first aircraft of the group. Note that the only one beacon can be activate at the same time. If you activated new beacon having another beacon active that old beacon will be deactivated.

```
 ActivateBeacon = { 
   id = 'ActivateBeacon', 
   params = { 
     type = number, 
     system = number, 
     name = string, 
     callsign = string, 
     frequency = number, 
   } 
 }

```

_type_

-   Beacon type. The constants are enlisted in _./Scripts/World/Radio/BeaconTypes.Lua_

```
 BEACON_TYPE_NULL = 0 
 BEACON_TYPE_VOR = 1 
 BEACON_TYPE_DME = 2 
 BEACON_TYPE_VOR_DME = 3 
 BEACON_TYPE_TACAN = 4 
 BEACON_TYPE_VORTAC = 5 
 BEACON_TYPE_RSBN = 32 
 BEACON_TYPE_BROADCAST_STATION = 1024 
 BEACON_TYPE_HOMER = 8 
 BEACON_TYPE_AIRPORT_HOMER = 4104 
 BEACON_TYPE_AIRPORT_HOMER_WITH_MARKER = 4136 
 BEACON_TYPE_ILS_FAR_HOMER = 16408 
 BEACON_TYPE_ILS_NEAR_HOMER = 16456 
 BEACON_TYPE_ILS_LOCALIZER = 16640 
 BEACON_TYPE_ILS_GLIDESLOPE = 16896 
 BEACON_TYPE_NAUTICAL_HOMER = 32776

```

_system_

-   Determines what device(s) will be used. System constants are enlisted in _./Scripts/World/Radio/BeaconSites.Lua_ in table _SystemName_.

```
 SystemName = { 
   PAR_10 = 1, 
   RSBN_5 = 2, 
   TACAN = 3, 
   TACAN_TANKER = 4, 
   ILS_LOCALIZER = 5, 
   ILS_GLIDESLOPE = 6, 
   BROADCAST_STATION = 7 
 }

```

_name_

-   Helper in Mission Editor. Has no effect in simulator.

_callsign_

-   Beacon identifier that will being broadcasting in Morse code.

_frequency_

-   Frequency of the beacon's transmitter(s) in Hz.

**11\. Deactivate beacon**

Deactivates beacon onboard the unit. If it is a group the beacon will be activated onboard a first unit of the group. No parameters.

```
 { 
   id = 'DeactivateBeacon', 
   params = { 
   } 
 }

```

**12\. EPLRS**

Sets parameters of EPLRS datalink of the unit/group. If EPLRS command called for the airborne group then all aircrafts of the group will be affected. If EPLRS command called for vehicle group then only the first unit of the group will be affected. You can switch EPLRS on/off and change track number of the first unit of the vehicle group.

```
 { 
   id = 'EPLRS', 
   params = { 
     value = boolean, 
     groupId = number, 
   } 
 }

```

_value_

-   EPLRS status.

_groupId_

-   Track number of the first unit of the vehicle group. Used only for vehicle group.

#### Behavior options

Option is a pair of identifier and value. Behavior options are global parameters those affect controller behavior in all tasks it performs.

Option identifiers and values are stored in table _AI.Option_ in subtables _Air_, _Ground_ and _Naval_.

```
 OptionId = AI.Option.Air.id or AI.Option.Ground.id or AI.Option.Naval.id

```

```
 OptionValue = AI.Option.Air.val[optionName] or AI.Option.Ground.val[optionName] or AI.Option.Naval.val[optionName]

```

```
 function Controller.setOption(Controller self, OptionId optionId, OptionValue optionValue) 

```

sets the option to the controller.

_optionId_

-   Option identifier.

_optionValue_

-   Value of the option

**Airborne units**

<table><tbody><tr><td>Option</td><td>Values</td></tr><tr><td>AI.Option.Air.id.NO_OPTION</td><td><br></td></tr><tr><td>AI.Option.Air.id.ROE</td><td>AI.Option.Air.val.ROE.WEAPON_FREE<p>AI.Option.Air.val.ROE.OPEN_FIRE_WEAPON_FREE</p><p>AI.Option.Air.val.ROE.OPEN_FIRE</p><p>AI.Option.Air.val.ROE.RETURN_FIRE</p><p>AI.Option.Air.val.ROE.WEAPON_HOLD</p></td></tr><tr><td>AI.Option.Air.id.REACTION_ON_THREAT</td><td>AI.Option.Air.val.REACTION_ON_THREAT.NO_REACTION<p>AI.Option.Air.val.REACTION_ON_THREAT.PASSIVE_DEFENCE</p><p>AI.Option.Air.val.REACTION_ON_THREAT.EVADE_FIRE</p><p>AI.Option.Air.val.REACTION_ON_THREAT.BYPASS_AND_ESCAPE</p><p>AI.Option.Air.val.REACTION_ON_THREAT.ALLOW_ABORT_MISSION</p></td></tr><tr><td>AI.Option.Air.id.RADAR_USING</td><td>AI.Option.Air.val.RADAR_USING.NEVER<p>AI.Option.Air.val.RADAR_USING.FOR_ATTACK_ONLY</p><p>AI.Option.Air.val.RADAR_USING.FOR_SEARCH_IF_REQUIRED</p><p>AI.Option.Air.val.RADAR_USING.FOR_CONTINUOUS_SEARCH</p></td></tr><tr><td>AI.Option.Air.id.FLARE_USING</td><td>AI.Option.Air.val.FLARE_USING.NEVER<p>AI.Option.Air.val.FLARE_USING.AGAINST_FIRED_MISSILE</p><p>AI.Option.Air.val.FLARE_USING.WHEN_FLYING_IN_SAM_WEZ</p><p>AI.Option.Air.val.FLARE_USING.WHEN_FLYING_NEAR_ENEMIES</p></td></tr><tr><td>AI.Option.Air.id.FORMATION</td><td>complex option. See the description below.</td></tr><tr><td>AI.Option.Air.id.RTB_ON_BINGO</td><td>true<p>false</p></td></tr><tr><td>AI.Option.Air.id.SILENCE</td><td>true<p>false</p></td></tr></tbody></table>

**Ground units**

<table><tbody><tr><td>Option</td><td>Values</td></tr><tr><td>AI.Option.Ground.id.NO_OPTION</td><td><br></td></tr><tr><td>AI.Option.Ground.id.ROE</td><td>AI.Option.Ground.val.ROE.OPEN_FIRE<p>AI.Option.Ground.val.ROE.RETURN_FIRE</p><p>AI.Option.Ground.val.ROE.WEAPON_HOLD</p></td></tr><tr><td>AI.Option.Ground.id.DISPERSE_ON_ATTACK</td><td>true<p>false</p></td></tr><tr><td>AI.Option.Ground.id.ALARM_STATE</td><td>AI.Option.Ground.val.ALARM_STATE.AUTO,<p>AI.Option.Ground.val.ALARM_STATE.GREEN</p><p>AI.Option.Ground.val.ALARM_STATE.RED</p></td></tr></tbody></table>

**Naval units**

<table><tbody><tr><td>Option</td><td>Values</td></tr><tr><td>AI.Option.Naval.id.NO_OPTION</td><td><br></td></tr><tr><td>AI.Option.Naval.id.ROE</td><td>AI.Option.Naval.val.ROE.OPEN_FIRE<p>AI.Option.Naval.val.ROE.RETURN_FIRE</p><p>AI.Option.Naval.val.ROE.WEAPON_HOLD</p></td></tr></tbody></table>

#### Formation

Formation is a complex parameter that consists of 3 sub-parameters: formation type, formation variant and formation orientation (left/right). Each sub-parameter is represented by a number. These three numbers are packed into a single number - the formation code.

**Note:** it is not an elegant solution, but we have a limitation here - option value may be a number or boolean. May be it will be reworked later.

\[4 bytes formation code\] = \[2 bytes - formation type\]\[1 byte - formation orientation\]\[1 byte - formation variant\]

Formations are enlisted in _./Scripts/Database/db\_formations.Lua_.

Formation type identifiers

```
 local id = { 
   NO_FORMATION    = 0, 
   --airplanes 
   LINE_ABREAST    = 1, 
   TRAIL           = 2, 
   WEDGE           = 3, 
   ECHELON_RIGHT   = 4, 
   ECHELON_LEFT    = 5, 
   FINGER_FOUR     = 6, 
   SPREAD_FOUR     = 7, 
   --helicopters 
   HEL_WEDGE       = 8, 
   HEL_ECHELON     = 9, 
   HEL_FRONT       = 10, 
   HEL_COLUMN      = 11, 
   -- 
   MAX             = 12 
 }

```

Formation orientation

Default orientation of each formation type determines by a formation geometry given in the script. All existed formation types have right orientation. To inverse orientation (to the left) the value of formation orientation sub-parameter must be 1.

Formation variant

Some formation types have several variants usually different by a density. Variants are enumerated from 1 to N. If the variant is 0 then default variant will be used.

Airplane formations "Trail", "Wedge", "Echelon Right", "Echelon Left", "Finger Four", "Spred Four" have two variants: "Open" and "Close" (default) and have no variable orientation. Helicopter formation "Echelon" has three variants "50x70", "50x300" (default), "50x600" and has variable orientation. Helicopter formation "Front" has three variants: "interval 300" (default), "interval 600" and has variable orientation. All other formations have no variants and no variable orientation.