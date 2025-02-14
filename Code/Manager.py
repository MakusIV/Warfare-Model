"""
 MODULE Manager
 
Sequence of processes for evaluating DCS data (missions and status), recording statistics, planning missions and writing DCS data to LUA tables

"""



# scenario property
blocks = {

    "blue": {},
    "red": {},
    "neutral": {}

    }


regions = {

    "blue": {},
    "red": {},
    "neutral": {}

    }

missions = {

    "blue": {},
    "red": {},
    "neutral": {}

    }

state = {

    "morale": {"blue": {}, "red": {}, "neutral": {}},
    "global_efficiency": {"blue": {}, "red": {}, "neutral": {}},
    "production": { "goods": {"blue": {}, "red": {}, "neutral": {}},
                    "food": {"blue": {}, "red": {}, "neutral": {}}, 
                    "energy": {"blue": {}, "red": {}, "neutral": {}}, 
                    "human resource": {"HC": {"blue": {}, "red": {}, "neutral": {}}, "HS": {"blue": {}, "red": {}, "neutral": {}}, "HB": {"blue": {}, "red": {}, "neutral": {}}, "HR": {"blue": {}, "red": {}, "neutral": {}}}
                    },
    "transport": {"blue": {}, "red": {}, "neutral": {}},
    "military": {"blue": {}, "red": {}, "neutral": {}},
    "urban": {"blue": {}, "red": {}, "neutral": {}},

    }



# reading and loading DCS data: reading from lua table and loading to python object
pass

# evaluate mission result: from python object evaluate mission results
pass

# execute simulation for virtual mission result: execution of the simulation in relation to the mission results
pass

# save mission result: saving the mission results for statistical use and analysis 
pass

# execute tactical blocks evaluation and planning: loop of report request to all blocks
pass

# execute strategical and tactical evaluation and planning: analysis of block reports and global situation (general status and intelligence) and block mission planning
pass

# writing DCS data to lua table: writing from python object to lua table
pass