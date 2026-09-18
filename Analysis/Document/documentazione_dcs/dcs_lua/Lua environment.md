#### Lua environment

The scripting engine uses the [Lua](http://www.lua.org/) language. Mission scripts run in a special, isolated Lua environment - the Mission Scripting Environment. There are two ways to run a Lua script:

**AI Tasking System**

1\. "Script" command of A.I. Tasking System (available in a group's advanced waypoint actions and in triggered actions). If "Script" command is a waypoint action, then the command will run when the group reaches the waypoint the command is associated with. If "Script" command is a triggered action, then the command will run when the triggered action is called via the "AI TASK" trigger action.

2\. "Script File" command of A.I. Tasking System (available in a group's advanced waypoint actions and in triggered actions). If "Script File" command is a waypoint action, then the command file will run when the group reaches the waypoint the script is associated with. If "Script File" command is a triggered action, then the command file will run when the triggered action is called via the "AI TASK" trigger action.

3\. "CONDITION (LUA EXPRESSION)" for condition / stop condition for any type of action of the A.I. Tasking System. Such code should return boolean value or nil.

**Triggers**

1\. "DO SCRIPT" trigger action.

2\. "DO SCRIPT FILE" trigger action.

3\. "EXPRESSTION" trigger condition. Such code must return boolean value of nil.

**Other**

1\. Initialization script.

or

2\. Initialization script file.

This script runs before spawn of first unit and before run of first trigger action. Script of script file can be selected, no both ways at the same time.