local mod_name = "Dynamic Campaign Engine"

local mod_config = {
	installed 	 = true,
	dirName	  	 = current_mod_path,
	fileMenuName = _("DCE"),
	version		 = "11.01.2020",
	state		 = "installed", 
	developerName= "MBot",
	info		 = _("Dynamic Campaign Engine"),

	Skins	= 
	{
		{
			name	= _("DCE"),
			dir		= "Theme"
		},
	},
	
	Missions =
	{
		{
			name		= _("DCE"),
			dir			= "Missions",	
		},
	},	
}

declare_plugin(mod_name, mod_config)
plugin_done()