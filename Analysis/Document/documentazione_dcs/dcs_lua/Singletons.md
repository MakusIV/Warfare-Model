-   [Singletons](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333808)
-   [env](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333809)
-   [timer](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333810)
-   [land](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333811)
-   [atmosphere](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333812)
-   [world](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333813)
-   [coalition](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333814)
-   [country](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333815)
-   [trigger](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333816)
-   [coord](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333817)
-   [radio](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333818)
-   [missionCommands](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333819)
-   [AI](https://www.digitalcombatsimulator.com/it/support/faq/1807/#3333820)

#### Singletons

Singletons represent the types of object those have only single instance. Here are the usual Lua tables.

#### env

```
 function env.info(string message, bool showMessageBox = false)
 function env.warning(string message, bool showMessageBox = false)
 function env.error(string message, bool showMessageBox = false)

```

add message to simulator log with caption "INFO", "WARNING" or "ERROR". Message box is optional.

_message_

-   message string to add to log.

_showMessageBox_

-   If the parameter is true Message Box will appear. Optional.

```
 function env.setErrorMessageBoxEnabled(boolean on)

```

enables/disables appearance of message box each time lua error occurs.

_on_

-   if true message box appearance is enabled

#### timer

```
 Time function timer.getTime() 

```

returns model time in seconds.

```
 Time function timer.getAbsTime() 

```

returns mission time in seconds.

```
 Time function timer.getTime0() 

```

returns mission start time

```
 Time function FunctionToCall(any argument, Time time)
   ...
   return ...
 end

```

must return model time of next call or nil.

```
 FunctionId = number
 

```

is a numeric identifier of scheduled _FunctionToCall_.

```
 FunctionId function timer.scheduleFunction(FunctionToCall functionToCall, any functionArgument, Time time) 

```

schedules function to call at desired model time.

_functionToCall_

-   Lua-function to call. Must have prototype of _FunctionToCall_.

_functionArgument_

-   Function argument of any type to pass to _functionToCall_.

_time_

-   Model time of the function call.

```
 function timer.setFunctionTime(FunctionId functionId, Time time)

```

re-schedules function to call at another model time.

_functionToCall_

-   Lua-function to call. Must have prototype of _FunctionToCall_.

_time_

-   Model time of the function call.

```
 function timer.removeFunction(FunctionId functionId)
 

```

removes the function from schedule.

_functionId_

-   Function identifier to remove from schedule

#### land

```
 land.SurfaceType = {
   LAND,
   SHALLOW_WATER,
   WATER,
   ROAD,
   RUNWAY
 }

```

enum contains identifiers of surface types.

```
 boolean function land.isVisible(Vec3 from, Vec3 to) 

```

returns true if there is LOS between point _from_ and point _to_. Function verifies only obstruction due the terrain and don't takes in account objects (units, static and terrain objects).

```
 Distance function land.getHeight(Vec2 point) 

```

returns altitude MSL of the _point_.

_point_

-   point on the ground.

```
 Vec3 function land.getIP(Vec3 from, Vec3 direction, Distance maxDistance) 

```

returns point where the ray intersects the terrain. If no intersection found the function will return nil.

_from_

-   Ray vertex.

_direction_

-   Ray normalized direction.

_maxDistance_

-   Maximal search distance from ray vertex.

```
 array of Vec3 function land.profile(Vec3 from, Vec3 to) 

```

returns table of vectors those are form profile of the terrain between point _from_ and point _to_.

Only x and z components of both vectors matters. The first _Vec3_ in the result table is equal to vector _from_, the last vector in the result table is equal to vector _to_.

```
 enum land.SurfaceType function land.getSurfaceType(Vec2 point) 

```

returns surface type at the given point.

_point_

-   Point on the land.

#### atmosphere

```
 Vec3 atmosphere.getWind(Vec3 point)

```

returns wind velocity at the given point. No turbulence.

_point_

-   Point in the air.

```
 Vec3 atmosphere.getWindWithTurbulence(Vec3 point)

```

returns wind velocity at the given point. With turbulence.

_point_

-   Point in the air.

#### world

```
 world.event = {
   S_EVENT_SHOT,
   S_EVENT_HIT,
   S_EVENT_TAKEOFF,
   S_EVENT_LAND,
   S_EVENT_CRASH,
   S_EVENT_EJECTION,
   S_EVENT_REFUELING,
   S_EVENT_DEAD,
   S_EVENT_PILOT_DEAD,
   S_EVENT_BASE_CAPTURED,
   S_EVENT_MISSION_START, -- currently can not be caught in script due to happens before script load
   S_EVENT_MISSION_END,
   S_EVENT_TOOK_CONTROL,
   S_EVENT_REFUELING_STOP,
   S_EVENT_BIRTH,
   S_EVENT_HUMAN_FAILURE,
   S_EVENT_ENGINE_STARTUP,
   S_EVENT_ENGINE_SHUTDOWN,
   S_EVENT_PLAYER_ENTER_UNIT,
   S_EVENT_PLAYER_LEAVE_UNIT,
   S_EVENT_PLAYER_COMMENT,
   S_EVENT_SHOOTING_START,
   S_EVENT_SHOOTING_END,
   S_EVENT_MARK_ADDED,
   S_EVENT_MARK_CHANGE,
   S_EVENT_MARK_REMOVED,
   S_EVENT_KILL,
   S_EVENT_SCORE,
   S_EVENT_UNIT_LOST,
   S_EVENT_LANDING_AFTER_EJECTION,
   S_EVENT_PARATROOPER_LENDING,
   S_EVENT_DISCARD_CHAIR_AFTER_EJECTION,
   S_EVENT_WEAPON_ADD,
   S_EVENT_TRIGGER_ZONE,
   S_EVENT_LANDING_QUALITY_MARK,
   S_EVENT_BDA,
   S_EVENT_AI_ABORT_MISSION,
   S_EVENT_DAYNIGHT,
   S_EVENT_FLIGHT_TIME,
   S_EVENT_PLAYER_SELF_KILL_PILOT,
   S_EVENT_PLAYER_CAPTURE_AIRFIELD,
   S_EVENT_EMERGENCY_LANDING,  -- useful event to handle when a bot ditches, and "group dead" condition can't be met 
 }

```

enum contains identifiers of simulator events.

```
 world.BirthPlace = {
   wsBirthPlace_Air,
   wsBirthPlace_RunWay,
   wsBirthPlace_Park,
   wsBirthPlace_Heliport_Hot,
   wsBirthPlace_Heliport_Cold,
 }

```

enum contains identifiers of birth place.

```
 Event = {
   id = enum world.event,
   time = Time,
   initiator = Unit,
   target = Unit,
   place = Unit,
   subPlace = enum world.BirthPlace,
   weapon = Weapon
 }

```

table represents a simulator event. Not all the parameters are valid for any event.

```
 function EventHandler(Event event)
   ...
 end

```

is a handler of simulator event.

```
 function world.addEventHandler(EventHandler handler)

```

adds event handler.

_handler_

-   event handler. Must have prototype of _EventHandler_.

```
 function world.removeEventHandler(EventHandler handler)

```

removes event handler.

**Note:** event handling will be moved from ./Scripts/World/EventHandlers.lua to the code. Function _world.addEventHandler_ will support argument passing.

_handler_

-   event handler. Must have form of _EventHandler_.

```
 Unit function Unit world.getPlayer()

```

returns _Unit_ player's aircraft.

```
 function array of Airbase world.getAirbases()

```

returns list of airbases

```
 world.VolumeType = {
   SEGMENT,
   BOX,
   SPHERE,
   PYRAMID
 }

```

enum contains types of volume to search.

```
 Volume = {
   id = enum world.VolumeType,
   params = {
     ...    
   }
 }

```

Table that contains information about the given volume.

_id_

-   Identifies volume type.

_params_

-   Table that contains parameters of the volume. Content is depended on volume type.

```
 VolumeSegment = {
   id = world.VolumeType.SEGMENT,
   params = {
     from = Vec3,
     to = Vec3
   }
 }

```

Represents 3D-segment.

_from_

-   Point where is the segment started.

_to_

-   Point where is the segment finished.

```
 VolumeBox = {
   id = world.VolumeType.BOX,
   params = {
     min = Vec3,
     max = Vec3
   }
 }

```

Represents 3D-box.

_min_

-   Coordinates of western-southern-lower vertex of the box.

_max_

-   Coordinates of eastern-northern-upper vertex of the box.

```
 VolumeSphere = {
   id = world.VolumeType.SPHERE,
   params = {
     point = Vec3,
     radius = Distance
   }
 }

```

Represents sphere.

_point_

-   Coordinates of the sphere center.

_radius_

-   Radius of the sphere.

```
 VolumePyramid = {
   id = world.VolumeType.PYRAMID,
   params = {
     pos = Position3,
     length = Distance,
     halfAngleHor = Angle,
     halfAngleVer = Angle
   }
 }

```

Represents camera FOV or oriented pyramid.

_pos_

-   Position of the pyramid.

_length_

-   Maximal distance from the pyramid vertex to an object.

_halfAngleHor_

-   Horizontal half angle.

_halfAngleVer_

-   Vertical half angle.

```
 ObjectSearchHandler = function(Object object, any data)
   ...
   return boolean
 end

```

Function to be called for each found object. Returns true to continue search and false to stop it.

```
 function array of Airbase world.searchObjects([array of enum Object.Category] or [Object.Category] objectCategory, Volume volume, ObjectSearchHandler handler, any data)

```

searches objects of the given categories in the given volume and calls _handler_ function for each found object with _data_ as 2nd argument.

_objectCategory_

-   Category or categories of objects to search.

_volume_

-   Volume to search.

_handler_

-   Function to call.

_data_

-   Data to pass to _handler_ as 2nd argument.

#### coalition

```
 coalition.side = {
   NEUTRAL,
   RED,
   BLUE
 }

```

enum contains side identifiers.

```
 coalition.service = {
   ATC,
   AWACS,
   TANKER,
   FAC
 }

```

enum stores identifiers of coalition services.

```
 enum coalition.side function coalition.getCountryCoalition(enum country.id country)

```

returns coalition of the given country.

_country_

-   country identifier.

```
 Vec3 function coalition.getMainRefPoint(enum coalition.side coalition)

```

returns main reference point (bullseye).

_coalition_

-   coalition identifier.

```
 RefPoint = {
   callsign = number,
   type = number,
   point = Vec3
 }

```

table is a reference point (used by JTAC AI for example).

```
 array of RefPoint function coalition.getRefPoints(enum coalition.side coalition)

```

returns coalition reference points.

_coalition_

-   coalition identifier

```
 function coalition.addRefPoint(enum coalition.side coalition, RefPoint refPoint)

```

adds reference point to the coalition's list.

_coalition_

-   coalition identifier.

_refPoint_

-   reference point to add.

```
 array of Unit function coalition.getServiceProviders(enum coalition.side coalition, enum country.service serviceId)

```

returns list of units which are the coalition service providers

_coalition_

-   coalition identifier

```
 array of Unit function coalition.getPlayers(enum coalition.side coalition)

```

_coalition_

-   coalition identifier

returns list of units controlled by players (local and remote)

_serviceId_

-   coalition service identifier

```
 array of Airbase function coalition.getAirbases(enum coalition.side coalition)

```

returns list of airbases owned by the coalition

_coalition_

-   coalition identifier

```
 array of Unit function coalition.getGroups(enum coalition.side coalition, enum Group.Category groupCategory or nil)

```

returns list of groups belong to the coalition. It returns all groups or groups of specified type.

_coalition_

-   coalition identifier

_groupCategory_

-   group category. If nil the function will return list of groups of all categories.

```
 array of StaticObject function coalition.getStaticObjects(enum coalition.side coalition)

```

returns list of static objects belong to the coalition.

_coalition_

-   coalition identifier

```
 Group function coalition.addGroup(enum country.id country, enum Group.Category groupCategory, table groupData)

```

_country_

-   country identifier

_groupCategory_

-   group category.

_groupData_

-   table with group data. The table has the same format groups have in a mission file.

**Note:**

-   **Coalition of a group is determined by its country**

-   **If another group has the same name new group has, that group will be destroyed and new group will take its mission ID.**

-   **If another units has the same name an unit of new group has, that unit will be destroyed and the unit of new group will take its mission ID.**

-   **If new group contains player's aircraft current unit that is under player's control will be destroyed.**

-   **Groups with client aircraft are not allowed.**

-   **If group mission ID are not specified or busy, simulator will assign mission ID automatically.**
-   **If unit mission ID are not specified or busy, simulator will assign mission ID = unit name.**

```
 Group function coalition.addStaticObject(enum country.id country, table staticObjectData)

```

_country_

-   country identifier

_staticObjectData_

-   table with static object data. The table has the same format static objects have in a mission file.

**Note:**

-   **Coalition of a static object is determined by its country**

-   **If another static object has the same name new static object has, that static object will be destroyed and new static object will take its mission ID.**

-   **If static object mission ID is not specified or busy, simulator will assign new mission ID automatically.**

#### country

```
 country.id = {
   RUSSIA,
   UKRAINE,
   USA,
   TURKEY,
   UK,
   FRANCE,
   GERMANY,
   CANADA,
   SPAIN,
   THE_NETHERLANDS,
   BELGIUM,
   NORWAY,
   DENMARK,
   ISRAEL,
   GEORGIA,
   INSURGENTS,
   ABKHAZIA,
   SOUTH_OSETIA,
   ITALY
 }

```

enum contains country identifiers.

#### trigger

```
 trigger.smokeColor = {
   Green,
   Red,
   White,
   Orange,
   Blue
 }

```

enum contains identifiers of smoke color.

```
 trigger.flareColor = {
   Green,
   Red,
   White,
   Yellow
 }

```

enum contains identifiers of signal flare color.

```
 number function trigger.misc.getUserFlag(string userFlagName)

```

returns value of the user flag.

_userFlagName_

-   User flag name.

```
 TriggerZone = {
   point = Vec3,
   radius = Distance
 }

```

is a trigger zone.

```
 TriggerZone function trigger.misc.getZone(string triggerZoneName) 

```

returns trigger zone.

_triggerZoneName_

-   Trigger zone name.

```
 function trigger.action.setUserFlag(string userFlagName, boolean or number userFlagValue)

```

sets new value of the user flag

_userFlagName_

-   User flag name.

_userFlagValue_

-   New value of the user flag. Numeric or boolean (0 or 1).

```
 function trigger.action.outSound(string soundFile)

```

plays sound file to all players.

_soundFile_

-   name of sound file stored in the mission archive (miz).

```
 function trigger.action.outSoundForCoalition(enum coalition.side coalition, string soundFile)

```

plays sound file to all players on a specific coalition.

_coalition_

-   coalition identifier.

_soundFile_

-   name of sound file stored in the mission archive (miz).

```
 function trigger.action.outSoundForCountry(enum country.id country, string soundFile)

```

plays sound file to all players on a specific country.

_country_

-   country identifier.

_soundFile_

-   name of sound file stored in the mission archive (miz).

```
 function trigger.action.outSoundForGroup(GroupId groupId, string soundFile)

```

plays sound file to players in a specific group.

_groupId_

-   group identifier.

_soundFile_

-   name of sound file stored in the mission archive (miz).

```
 function trigger.action.outText(string text, Time delay)

```

output text to screen to all players.

_text_

-   text to show.

_delay_

-   text delay.

```
 function trigger.action.outTextForCoalition(enum coalition.side coalition, string text, Time delay)

```

output text to screen to all players on a specific coalition.

_coalition_

-   coalition identifier.

_text_

-   text to show.

_delay_

-   text delay.

```
 function trigger.action.outTextForCountry(enum country.id country, string text, Time delay)

```

output text to screen to all players on a specific country.

_country_

-   country identifier.

_text_

-   text to show.

_delay_

-   text delay.

```
 function trigger.action.outTextForGroup(GroupId groupId, string text, Time delay)

```

output text to screen to all players in a specific unit group.

_groupId_

-   group identifier.

_text_

-   text to show.

_delay_

-   text delay.

```
 function trigger.action.explosion(Vec3 point, number power)

```

creates an explosion.

_point_

-   point in 3D space.

_power_

-   explosion power.

```
 function trigger.action.smoke(Vec3 point, enum trigger.smokeColor color)

```

creates a smoke marker.

_point_

-   point in 3D space.

_color_

-   color of the smoke.

```
 function trigger.action.illuminationBomb(Vec3 point)

```

creates illumination bomb at the point.

_point_

-   point where the illumination bomb will appear.

```
 trigger.action.signalFlare(Vec3 point, enum trigger.flareColor color, Azimuth azimuth)

```

launches signal flare from the point.

_point_

-   point the signal flare will be launched from.

_color_

-   signal flare color.

_azimuth_

-   signal flare flight direction.

```
 function trigger.action.addOtherCommand(string name, string userFlagName, number userFlagValue = 1) 

```

adds command to "F10. Other" menu of the Radio Command Panel. The command will set the flag _userFlagName_ to _userFlagValue_.

Calls _missionCommands.addCommand()_.

_name_

-   menu command name.

_userFlagName_

-   user flag name.

_userFlagValue_

-   user flag value. By default equals to 1.

```
 function trigger.action.removeOtherCommand(string name)

```

removes menu item.

Calls _missionCommands.removeItem()_.

```
 function trigger.action.addOtherCommandForCoalition(enum coalition.id coalition, string name, string userFlagName, number userFlagValue = 1) 

```

adds command to "F10. Other" menu of the Radio Command Panel for the coalition. The command will set the flag _userFlagName_ to _userFlagValue_.

Calls _missionCommands.addCommandForCoalition()_.

_coalition_

-   coalition the command to add for

_name_

-   menu command name.

_userFlagName_

-   user flag name.

_userFlagValue_

-   user flag value. By default equals to 1.

```
 function trigger.action.removeOtherCommandForCoalition(enum coalition.id coalition, string name)

```

removes the item for the coalition.

Calls _missionCommands.removeItemForCoalition()_.

_coalition_

-   coalition the command to remove for

_name_

-   name of the menu item to remove

```
 function trigger.action.addOtherCommandForGroup(GroupId groupId, string name, string userFlagName, number userFlagValue = 1) 

```

adds command to "F10. Other" menu of the Radio Command Panel for the group. The command will set the flag _userFlagName_ to _userFlagValue_.

Calls _missionCommands.addCommandForGroup()_

_groupId_

-   id of the group to add the command for

_name_

-   menu command name.

_userFlagName_

-   user flag name.

_userFlagValue_

-   user flag value. By default equals to 1.

```
 function trigger.action.removeOtherCommandForGroup(GroupId groupId, string name)

```

removes the item for the group.

Calls _missionCommands.removeItemForGroup()_

_groupId_

-   id of the group to remove the command for

_name_

-   name of the menu item to remove

```
 function trigger.action.radioTransmission(string fileName, Vec3 point, enum radio.modulation modulation, boolean loop, number frequency, number power) 

```

transmits audio file to broadcast.

_fileName_

-   name of audio file. The file must be packed into the mission archive (miz).

_point_

-   position of the transmitter

_modulation_

-   modulation of the transmission

_loop_

-   indicates if the transmission is looped or not

_frequency_

-   transmitter frequency in Hz

_power_

-   transmitter power in Watts

```
 function trigger.action.setAITask(Group group, number taskIndex)

```

sets triggered task for the group.

_group_

-   the group to set the task for.

_taskIndex_

-   index of triggered task.

```
 function trigger.action.pushAITask(Group group, number taskIndex)

```

pushes triggered task for the group.

_group_

-   the group to push the task for.

_taskIndex_

-   index of triggered task.

```
 function trigger.action.activateGroup(Group group)

```

activates the group. Calls _group:activate()_.

_group_

-   group to activate.

```
 function trigger.action.deactivateGroup(Group group)

```

deactivates the group. Calls _group:destroy()_.

_group_

-   group to deactivate.

```
 function trigger.action.setGroupAIOn(Group group)

```

sets the controller of the group on. Calls _group:getController():setOnOff(true)_.

_group_

-   group to set the controller on.

```
 function trigger.action.setGroupAIOff(Group group)

```

sets the controller of the group off. Calls _group:getController():setOnOff(false)_.

_group_

-   group to set the controller off.

```
 function trigger.action.groupStopMoving(Group group)

```

orders the group to stop moving. Sets _StopRoute_ command with _value = true_ to the group controller.

_group_

-   group order to stop moving.

```
 function trigger.action.groupContinueMoving(Group group)

```

orders the group to continue moving. Sets _StopRoute_ command with _value = false_ to the group controller.

_group_

-   group order to continue moving.

#### coord

```
 Vec3 coord.LLtoLO(GeoCoord latitude, GeoCoord longitude, Distance altitude = 0)

```

returns point converted from latitude/longitude to _Vec3_.

_latitude, longitude_

-   latitude and longitude.

_altitude_

-   point altitude. _Vec3.y = altitude_. Optional parameter, equals to 0 by default.

```
 GeoCoord, GeoCoord, Distance function coord.LOtoLL(Vec3 point)

```

returns point converted to latitude/longitude/altitude from Vec3. Altitude is equals to _point.y_.

_point_

-   point to convert. Only x and z matters.

```
 MGRS function coord.LLtoMGRS(GeoCoord latitude, GeoCoord longitude)

```

converts latitude/longitude to MGRS.

_latitude, longitude_

-   latitude and longitude.

```
 GeoCoord, GeoCoord function coord.MGRStoLL(MGRS mgrs)

```

converts point from MGRS to latitude/longitude

_mgrs_

-   MGRS-coordinates of the point.

#### radio

```
 radio.modulation = {
   AM,
   FM
 }

```

enum contains identifiers of modulation types.

#### missionCommands

Provides access to the mission commands available for players in "F10. Other" menu in the communication menu.

```
 Path

```

contains menu item path.

**Note: Path is the inner type. Do not construct variables of this type, use values returned from _addCommand_... and _addSubMenu_ instead**!

```
 Time function CommandFunction(any argument)
   ...
 end

```

-   function to be called by selecting the menu item

**All**

```
 Path missionCommands.addCommand(string name, Path or nil path, CommandFunction сommandFunction, any argument)

```

adds the command for all

_name_

-   command caption

_path_

-   path to the submenu the command must be inserted to. If nil the command will be inserted into root menu.

_commandFunction_

-   function to call

_argument_

-   argument to pass to the function

```
 Path missionCommands.addSubMenu(string name, Path or nil path)

```

adds the submenu for all

_name_

-   command caption

_path_

-   path to the submenu the command must be inserted to. If nil the command will be inserted into root menu.

```
 Path missionCommands.removeItem(Path or nil path)

```

removes the item for all

_path_

-   path to the item (command or submenu) to remove. If nil all items will be removed from the root menu.

**Coalition**

```
 Path missionCommands.addCommandForCoalition(enum coalition.side coalition, string name, Path or nil path, CommandFunction сommandFunction, any argument)

```

adds the command for the coalition

_coalition_

-   the coalition to add the command for

_name_

-   command caption

_path_

-   path to the submenu the command must be inserted to. If nil the command will be inserted into root menu.

_commandFunction_

-   function to call

_argument_

-   argument to pass to the function

```
 Path missionCommands.addSubMenuForCoalition(enum coalition.side coalition, string name, Path or nil path)

```

adds the submenu the coalition

_coalition_

-   the coalition to add the submenu for

_name_

-   command caption

_path_

-   path to the submenu the command must be inserted to. If nil the command will be inserted into root menu.

```
 Path missionCommands.removeItemForCoalition(enum coalition.side coalition, Path or nil path)

```

removes the item for the coalition

_coalition_

-   the coalition to remove the item for

_path_

-   path to the item (command or submenu) to remove. If nil all items will be removed from the root menu.

**Group**

```
 Path missionCommands.addCommandForGroup(GroupId groupId, string name, Path or nil path, CommandFunction сommandFunction, any argument)

```

adds the command for the group. Any type of groups available: airborne, ground, naval.

_groupId_

-   id of the group to add the command for

_name_

-   command caption

_path_

-   path to the submenu the command must be inserted to. If nil the command will be inserted into root menu.

_commandFunction_

-   function to call

_argument_

-   argument to pass to the function

```
 Path missionCommands.addSubMenuForGroup(GroupId groupId, string name, Path or nil path)

```

adds submenu to menu for the coalition

_groupId_

-   id of the group to add the submenu for

_name_

-   command caption

_path_

-   path to the submenu the command must be inserted to. If nil the command will be inserted into root menu.

```
 Path missionCommands.removeItemForGroup(GroupId groupId, Path or nil path)

```

removes the item for the coalition

_groupId_

-   id of the group to remove the item for

_coalition_

-   the coalition to remove the item for

_path_

-   path to the item (command or submenu) to remove. If nil all items will be removed from the root menu.

#### AI

Contains constants used in _Controller_ functions.

```
 AI.Skill = {
   AVERAGE,
   GOOD,
   HIGH,
   EXCELLENT,
   PLAYER,
   CLIENT
 }

```

enum contains unit skill values.

```
 AI = {
   Task = {
     ...
   },
   Option = {
     ...
   }
 }

```

_Task_ subtable contains constants used in tasks, _Option_ subtable contains behavior option constants and their values.

```
 AI.Task.WeaponExpend = {
   ONE,
   TWO,
   FOUR,
   QUARTER,
   HALF,
   ALL
 }

```

enum contains identifiers of weapon expend modes.

```
 AI.Task.OrbitPattern = {
   CIRCLE,
   RACE_TRACK
 }

```

enum contains identifiers of orbit patterns.

```
 AI.Task.Designation = {
   NO,
   AUTO,
   WP,
   IR_POINTER,
   LASER
 }

```

enum contains identifiers of target designation modes.

```
 AI.Task.WaypointType = {
   TAKEOFF,
   TAKEOFF_PARKING,
   TURNING_POINT,
   LAND,
 }

```

enum contains identifiers of waypoint types.

```
 AI.Task.TurnMethod = {
   FLY_OVER_POINT,
   FIN_POINT
 }

```

enum contains identifiers of turn methods

```
 AI.Task.AltitudeType = {
   BARO,
   RADIO
 }

```

enum contains identifiers of altitude types

```
 AI.Task.VehicleFormation = {
   OFF_ROAD,
   ON_ROAD,
   RANK,
   CONE,
   DIAMOND,
   VEE,
   ECHELON_LEFT,
   ECHELON_RIGHT
 }

```

enum contains identifiers of vehicle formations

```
  AI.Option = {
     Air = {
        id = enum ???,
        val = map ???, enum ???
     },
     Ground = {
        id = enum ???,
        val = map ???, enum ???
     },
     Naval = {
        id = enum ???,
        val = map ???, enum ???
     }
  }

```

table contains identifiers of behavior options (_id_) and their values (_val_) as enums for airborne, ground and naval units / groups.

_id_

-   enum that contains options identifiers.

_val_

-   map that contains identifiers of option values for each option. Keys match names of option identifiers.