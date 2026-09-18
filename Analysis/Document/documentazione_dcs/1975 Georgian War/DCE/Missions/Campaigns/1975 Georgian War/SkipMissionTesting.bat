REM do not modify this file
REM The paths are to be modified only in the file Init/path.bat

call Init/path.bat

start "Skip Mission" cmd /k start cmd /k "..\..\..\..\..\..\..\DCS_Lua\luae.exe" ..\..\..\ScriptsMod.%versionPackageICM%\BAT_SkipMission.lua"
