"""
 MODULE Code/I-O-Persistence/Source/Conversion_Lua_Python.py
 
 Functions for file/data structure conversion between LUA and Python


 TEST: OK with Jupiter Notebook

"""

from typing import Literal
import lupa
from lupa import LuaRuntime
import unicodedata, logging, os


# LOGGING --
# non èpossibile usare la classe Logger per evitare le circular dependencies: Logger importa General e Geneal imprta Logger

logging.basicConfig( level = logging.DEBUG )
# Create a custom logger
logger = logging.getLogger( __name__ )

log_dir = os.path.join(os.path.normpath(os.getcwd()), 'logs')
log_fname = os.path.join(log_dir, 'Conversion_Lua_Python.log')


# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler( log_fname )
c_handler.setLevel( logging.DEBUG )
f_handler.setLevel( logging.ERROR )

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(funcName)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)



MAX_WORLD_DISTANCE = 1.2e+90
STATE: Literal["Active", "Inactive", "Standby", "Destroyed"]
SHAPE3D: Literal["Cylinder", "Cube", "Sphere", "SemiSphere", "Cone", "Trunc_Cone", "Prism", "Solid"]
SHAPE2D: Literal["Circle", "Square", "Hexagon"]
VALUE: Literal["Critical", "Very_High", "High", "Medium", "Low", "Very_Low"]
CATEGORY: Literal["Goods", "Energy", "Goods & Energy"]
MIL_CATEGORY: Literal["Airbase", "Port", "Stronghold", "Farp", "Regiment", "Battallion", "Brigade", "Company", "EWR"]

def convert_lua_to_python_module_with_code_formatting(lua_file_path, output_module_path, table_name):
    
    """
    Converts a Lua table from a given Lua file into a formatted Python module.

    This function reads a Lua script from the specified file path, executes it to 
    retrieve a table, and converts this table into a Python dictionary-like format. 
    The resulting string is written to a new Python file with proper formatting and 
    normalized text for compatibility.

    Args:
        lua_file_path (str): Path to the Lua file containing the table definition.
        output_module_path (str): Path where the generated Python module will be saved.
        table_name (str): The name of the Lua table to be converted.

    Raises:
        Exception: If the specified Lua table is not found or if there are issues 
        reading the Lua file.

    Note:
        Non-printable characters in the Lua file are identified and printed for debug purposes.
    """

    lua = LuaRuntime(unpack_returned_tuples=True)

    with open(lua_file_path, 'r', encoding='utf-8') as f:
        lua_content = f.read()

    # Debug per caratteri non stampabili
    for i, char in enumerate(lua_content):
        if not char.isprintable() and char not in '\n\t\r':
            print(f"Carattere non stampabile trovato alla posizione {i}: {repr(char)}")

    # Esegui il codice Lua
    lua_globals = lua.execute(lua_content + "\nreturn " + table_name)

    if lua_globals is None:
        print("Errore: La variabile 'mission' non è stata trovata.")
        return

    def lua_to_dict_with_formatting(lua_obj, indent=0):
        """Converte un oggetto Lua in una stringa con chiavi Python standard e formattazione corretta."""
        if lupa.lua_type(lua_obj) in ('table', 'userdata'):
            result = []
            indent_str = "    " * indent
            for k, v in lua_obj.items():
                # Usa stringhe standard per le chiavi
                formatted_key = f'"{k}"' if isinstance(k, str) else f"{k}"
                formatted_value = lua_to_dict_with_formatting(v, indent + 1)
                result.append(f"{indent_str}{formatted_key}: {formatted_value}")
            return "{\n" + ",\n".join(result) + f"\n{'    ' * (indent - 1)}}}"
        
        elif isinstance(lua_obj, str):
            # Rappresenta la stringa esattamente come in Lua, con gli escape corretti
            return repr(lua_obj)
        
        else:
            return str(lua_obj)

    # Converti l'oggetto Lua in un formato stringa leggibile
    formatted_dict = lua_to_dict_with_formatting(lua_globals)

    def normalize_text(text):
        return unicodedata.normalize('NFKC', text)

    # Normalizza il dizionario formattato prima di scrivere
    formatted_dict = normalize_text(formatted_dict)

    with open(output_module_path, 'w', encoding='utf-8') as f:
        f.write("# Modulo Python generato dal file Lua\n")
        f.write("mission = ")
        f.write(formatted_dict)


def convert_lua_to_python_module(lua_file_path, output_module_path, table_name):
    lua = LuaRuntime(unpack_returned_tuples=True)

    with open(lua_file_path, 'r', encoding='utf-8') as f:
        lua_content = f.read()

    lua_globals = lua.execute(lua_content + "\nreturn " + table_name)

    if lua_globals is None:
        print("Errore: La variabile 'mission' non è stata trovata.")
        return

    def lua_to_dict(lua_obj):
        if lupa.lua_type(lua_obj) in ('table', 'userdata'):
            return {k: lua_to_dict(v) for k, v in lua_obj.items()}
        return lua_obj

    python_dict = lua_to_dict(lua_globals)

    with open(output_module_path, 'w', encoding='utf-8') as f:
        f.write("# Modulo Python generato dal file Lua\n")
        f.write("mission = ")
        f.write(repr(python_dict))