import json
import os

def cargar_config(config_file="config.json"):
    """
    Carga el archivo config.json y devuelve los valores en forma de diccionario.
    Si el archivo no existe o tiene errores, lanza una excepción.
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"[ERROR] No se encontró el archivo de configuración: {config_file}")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Normalización de tipos (por si el JSON trae strings numéricos)
        config["PING_INTERVAL"] = int(config.get("PING_INTERVAL", 30))

        return config

    except json.JSONDecodeError as e:
        raise ValueError(f"[ERROR] El archivo JSON está mal formado: {e}")
    except Exception as e:
        raise ValueError(f"[ERROR] No se pudieron leer los valores del archivo JSON: {e}")
