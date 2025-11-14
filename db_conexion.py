'''
import pyodbc
import time
from config_json_loader import cargar_config   # ← Nuevo loader basado en JSON


def conectar_sql():
    """
    Intenta conectarse a SQL Server indefinidamente hasta que tenga éxito.
    Devuelve la conexión activa.
    """
    while True:
        try:
            config = cargar_config()

            DB_DRIVER = config["DB_DRIVER"]
            DB_SERVER = config["DB_SERVER"]
            DB_NAME = config["DB_NAME"]
            DB_TRUSTED = config["DB_TRUSTED"]
            DB_USER = config["DB_USER"]
            DB_PASSWORD = config["DB_PASSWORD"]

            if DB_TRUSTED.lower() == "yes":
                conn_str = (
                    f"DRIVER={DB_DRIVER};"
                    f"SERVER={DB_SERVER};"
                    f"DATABASE={DB_NAME};"
                    "Trusted_Connection=yes;"
                )
            else:
                conn_str = (
                    f"DRIVER={DB_DRIVER};"
                    f"SERVER={DB_SERVER};"
                    f"DATABASE={DB_NAME};"
                    f"UID={DB_USER};"
                    f"PWD={DB_PASSWORD};"
                )

            conn = pyodbc.connect(conn_str, timeout=5)
            print("[OK] Conectado a SQL Server correctamente.")
            return conn

        except pyodbc.Error as e:
            print(f"[ERROR] No se pudo conectar a SQL Server: {e}")
            print("  Reintentando en 5 segundos...")
            time.sleep(5)


def ejecutar_sql(conn, query, params=(), reintentos=3, espera=5):
    """
    Ejecuta un query SQL con reconexión automática en caso de fallo.
    """
    for intento in range(1, reintentos + 1):
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True

        except pyodbc.OperationalError as e:
            print(f"[ERROR] Fallo de conexión: {e}")
            print(f"  Reconectando y reintentando ({intento}/{reintentos})...")
            conn = conectar_sql()
            time.sleep(espera)

        except pyodbc.Error as e:
            print(f"[ERROR] SQL Error: {e}")
            return False

    print("[FATAL] No se pudo ejecutar la consulta tras varios intentos.")
    return False
'''
import pyodbc
import time

# ------------------------
# Conexión a SQL Server con reconexión
# ------------------------
def conectar_sql(config):
    """
    Intenta conectarse a SQL Server indefinidamente hasta que tenga éxito.
    Recibe un diccionario 'config' con los datos de conexión.
    Devuelve la conexión activa.
    """
    while True:
        try:
            DB_DRIVER = config["DB_DRIVER"]
            DB_SERVER = config["DB_SERVER"]
            DB_NAME = config["DB_NAME"]
            DB_TRUSTED = config.get("DB_TRUSTED", "yes")
            DB_USER = config.get("DB_USER")
            DB_PASSWORD = config.get("DB_PASSWORD")

            if DB_TRUSTED.lower() == "yes":
                conn_str = (
                    f"DRIVER={DB_DRIVER};"
                    f"SERVER={DB_SERVER};"
                    f"DATABASE={DB_NAME};"
                    "Trusted_Connection=yes;"
                )
            else:
                conn_str = (
                    f"DRIVER={DB_DRIVER};"
                    f"SERVER={DB_SERVER};"
                    f"DATABASE={DB_NAME};"
                    f"UID={DB_USER};"
                    f"PWD={DB_PASSWORD};"
                )

            conn = pyodbc.connect(conn_str, timeout=5)
            print("[OK] Conectado a SQL Server correctamente.")
            return conn

        except pyodbc.Error as e:
            print(f"[ERROR] No se pudo conectar a SQL Server: {e}")
            print("  Reintentando en 5 segundos...")
            time.sleep(5)


# ------------------------
# Ejecutar query SQL con reintentos
# ------------------------
def ejecutar_sql(conn, query, params=(), reintentos=3, espera=5, config=None):
    """
    Ejecuta un query SQL con reconexión automática en caso de fallo.
    Si falla, reconecta usando 'config' y reintenta.
    """
    for intento in range(1, reintentos + 1):
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True

        except pyodbc.OperationalError as e:
            print(f"[ERROR] Fallo de conexión: {e}")
            if config:
                print(f"  Reconectando y reintentando ({intento}/{reintentos})...")
                conn = conectar_sql(config)
            time.sleep(espera)

        except pyodbc.Error as e:
            print(f"[ERROR] SQL Error: {e}")
            return False

    print("[FATAL] No se pudo ejecutar la consulta tras varios intentos.")
    return False
