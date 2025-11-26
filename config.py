import pyodbc
import json

def get_connection():
    with open('Seguridad.json') as f:
        data = json.load(f)

    name_server = data['server']
    database = data['database']
    username = data['username']
    password = data['password']
    controlador_odbc = data['driver']

    connection_string = f'DRIVER={controlador_odbc};SERVER={name_server};DATABASE={database};UID={username};PWD={password}'
    return pyodbc.connect(connection_string)