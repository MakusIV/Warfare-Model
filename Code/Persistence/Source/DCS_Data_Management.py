"""
 MODULE Code/I-O-Persistence/Source/Conversion_Lua_Python.py
 
 Functions for file/data structure conversion between LUA and Python


 TEST: OK with Jupiter Notebook

"""
from Code.Dynamic_War_Manager.Source.Utility.LoggerClass import Logger
from typing import Literal
import lupa
from lupa import LuaRuntime
import unicodedata, logging, os
import shutil



# LOGGING --
# non è possibile usare la classe Logger per evitare le circular dependencies: Logger importa Utility e Utility imprta Logger
# tuttavia, considerando che Logger importa utility solo per utilizzare il metodo setName(), elimina la questo utilizzo ed implementa qui logger

logging.basicConfig( level = logging.DEBUG )
# Create a custom logger
logger = logging.getLogger( __name__ )

log_dir = os.path.join(os.path.normpath(os.getcwd()), 'logs')
log_fname = os.path.join(log_dir, 'log_Utility.log')


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


def convert_lua_to_python_module_with_code_formatting(lua_file_path, output_module_path, table_name):
    
    """
    Converts a Lua table from a given Lua file into a formatted Python module using dictionary structure. Returns dictionary

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
    write_on_file = False

    lua = LuaRuntime(unpack_returned_tuples = True)

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

    # questo salva il dizionario come file python, tuttavia probabilmente non serve: le informazioni utili per le valutazioni strategiche devono essere estratte dal dizionario e 
    # eventualmente registrate su un dizionario appostiamente creato
    if write_on_file:

        with open(output_module_path, 'w', encoding='utf-8') as f:
            f.write("# Modulo Python generato dal file Lua\n")
            f.write("mission = ")
            f.write(formatted_dict)
            print("python dictionary write on file")

    return formatted_dict

def convert_lua_to_python_module(lua_file_path, output_module_path, table_name):

    write_on_file = False

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
    
    # questo salva il dizionario come file python, tuttavia probabilmente non serve: le informazioni utili per le valutazioni strategiche devono essere estratte dal dizionario e 
    # eventualmente registrate su un dizionario appostiamente creato    
    if write_on_file:

        with open(output_module_path, 'w', encoding='utf-8') as f:
            f.write("# Modulo Python generato dal file Lua\n")
            f.write("mission = ")
            f.write(repr(python_dict))
            print("python dictionary write on file")

    return python_dict

def duplicate_file(file_path, destination_file_path):
    """
    Duplica un file specificato nell'argomento file_path nella directory specificata dall'argomento destination_file_path.
    """
    # Controlla che i due argomenti siano presenti, che il file esista e che la directory di destinazione esista
    check_File_Path(file_path = file_path, destination_file_path = destination_file_path)

    # Crea il percorso completo del file di destinazione
    destination_dir = os.path.dirname(destination_file_path)
    destination_filename = os.path.basename(file_path)
    destination_path = os.path.join(destination_dir, destination_filename)

    # Copia il file nella directory di destinazione
    shutil.copy(file_path, destination_path)   

def override_file(file_path, destination_file_path):
    """
    Sovrascrive un file presente nella directory specificata dall'argomento destination_file_path
    utilizzando il file specificato nell'argomento file_path.
    """
    # Controlla che i due argomenti siano presenti, che il file esista e che la directory di destinazione esista
    check_File_Path(file_path = file_path, destination_file_path = destination_file_path)
    
    # Controlla che il file di destinazione esista
    if not os.path.exists(destination_file_path):
        raise ValueError("Error: destination file does not exist")

    # Sovrascrive il file nella directory di destinazione
    try:
        shutil.copy2(file_path, destination_file_path)
    except Exception as e:
        raise ValueError(f"Error: unable to override file - {str(e)}")
    
def check_File_Path(file_path, destination_file_path):
     # Controlla che i due argomenti siano presenti e che il file esista
    if not (file_path and destination_file_path and os.path.exists(file_path)):
        raise ValueError("Error: missing or invalid arguments")

    # Controlla che la directory di destinazione esista
    if not os.path.exists(os.path.dirname(destination_file_path)):
        raise ValueError("Error: destination directory does not exist")    
    
    return

"""

Ad ogni missione:

La tabella LUA viene salvata dal contesto Lua di DCS, il contesto Python crea il dizionario DCS contenente tutte le informazioni della tabella Lua e 
lo utilizza per creare tutte le classi necessarie per il Dynamic_War_Manager (DWM): Task, Route, RoutePoint, Group, Country. QUeste classi  sono utilizzate per
il salvataggio delle informazioni di Log e di stato incluse quelle necessarie le analisi strategiche e tattiche.
Durante l'esecuzione delle attività di competenza, il DWM aggiorna le classi suddette. Concluse le attività, il DWM aggiorna i dati del dizionario DCS, la corrispettiva tabella LUA e
tutte gli altri file Lua necessari a DCS per lo svolgimento della missione successiva.  


"""

