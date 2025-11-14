

'''

import time
from datetime import datetime
from db_conexion import conectar_sql#, crear_tabla
from db_table import crear_tabla
from config_json_loader import cargar_config
from ad_utils import obtener_equipos_ad, insertar_o_actualizar  

# ======================
# CONFIGURACIÓN
# ======================
config = cargar_config()  # ✅ Se carga desde config_loader
PING_INTERVAL = config["PING_INTERVAL"]

# ======================
# BUCLE PRINCIPAL
# ======================
def main():
    conn = conectar_sql()
    if not conn:
        return

    # Si deseas crear la tabla manualmente alguna vez:
    crear_tabla(conn)

    while True:
        try:
            equipos = obtener_equipos_ad()
            if not equipos:
                print("[WARN] No se encontraron equipos en AD.")
                time.sleep(PING_INTERVAL)
                continue

            equipos_ad_actuales = [eq["nombre"] for eq in equipos]
            insertar_o_actualizar(conn, equipos, equipos_ad_actuales)
            print(f"[INFO] Actualización completada. Esperando {PING_INTERVAL} segundos...\n")
            time.sleep(PING_INTERVAL)

        except KeyboardInterrupt:
            print("\n[INFO] Script detenido manualmente.")
            break
        except Exception as e:
            print("[ERROR] Ocurrió un error inesperado en el bucle principal:", e)
            time.sleep(PING_INTERVAL)

if __name__ == "__main__":
    main()
'''
####################################################################################
import time
from db_conexion import conectar_sql
from db_table import crear_tabla
from ad_utils import obtener_equipos_ad, insertar_o_actualizar
import gui_config

# ---------------------
# BUCLE PRINCIPAL
# ---------------------
def main(config):
    PING_INTERVAL = int(config["PING_INTERVAL"])
    conn = conectar_sql()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos.")
        return

    crear_tabla(conn)

    try:
        while True:
            equipos = obtener_equipos_ad()
            if not equipos:
                print("[WARN] No se encontraron equipos en AD.")
                time.sleep(PING_INTERVAL)
                continue

            equipos_ad_actuales = [eq["nombre"] for eq in equipos]
            insertar_o_actualizar(conn, equipos, equipos_ad_actuales)
            print(f"[INFO] Actualización completada. Esperando {PING_INTERVAL} segundos...\n")
            time.sleep(PING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[INFO] Script detenido manualmente.")

    except Exception as e:
        print("[ERROR] Ocurrió un error inesperado:", e)

# ---------------------
# INICIO DEL PROGRAMA
# ---------------------
if __name__ == "__main__":
    config = gui_config.abrir_gui_pro()

    if not config:
        print("[INFO] Configuración inválida o cancelada. Saliendo.")
    else:
        print("[INFO] Configuración cargada correctamente. Iniciando scanner...")
        main(config)
