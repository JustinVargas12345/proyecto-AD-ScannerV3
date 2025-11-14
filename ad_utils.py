


import socket
import subprocess
import platform
import time
from datetime import datetime
from ldap3 import Server, Connection, ALL
from db_conexion import conectar_sql
from logs_utils import escribir_log
from concurrent.futures import ThreadPoolExecutor, as_completed

estado_ping = {}

# ------------------------
# Validar credenciales AD
# ------------------------
def validar_ad(config):
    """
    Valida credenciales de AD usando los valores actuales del config.
    """
    try:
        server = Server(config["AD_SERVER"], get_info=ALL)
        conn = Connection(server, user=config["AD_USER"], password=config["AD_PASSWORD"], auto_bind=True)
        conn.unbind()
        return True
    except Exception as e:
        escribir_log(f"Excepción al validar AD: {e}", tipo="ERROR")
        return False

# ------------------------
# Obtener equipos desde AD
# ------------------------
def obtener_equipos_ad(config):
    """
    Obtiene los equipos de AD usando las credenciales actuales.
    """
    equipos = []
    try:
        server = Server(config["AD_SERVER"], get_info=ALL)
        conn = Connection(server, user=config["AD_USER"], password=config["AD_PASSWORD"], auto_bind=True)
        conn.search(
            config["AD_SEARCH_BASE"],
            "(objectClass=computer)",
            attributes=[
                "name", "dNSHostName", "operatingSystem", "operatingSystemVersion",
                "description", "whenCreated", "lastLogonTimestamp", "managedBy",
                "location", "userAccountControl"
            ]
        )
        for entry in conn.entries:
            nombre = str(entry.name)
            so = str(entry.operatingSystem) if hasattr(entry, 'operatingSystem') else "N/A"
            desc = str(entry.description) if hasattr(entry, 'description') else "N/A"
            nombre_dns = str(entry.dNSHostName) if hasattr(entry, 'dNSHostName') else "N/A"
            version_so = str(entry.operatingSystemVersion) if hasattr(entry, 'operatingSystemVersion') else "N/A"
            creado_el = str(entry.whenCreated) if hasattr(entry, 'whenCreated') else "N/A"
            ultimo_logon = str(entry.lastLogonTimestamp) if hasattr(entry, 'lastLogonTimestamp') else "N/A"
            responsable = str(entry.managedBy) if hasattr(entry, 'managedBy') else "N/A"
            ubicacion = str(entry.location) if hasattr(entry, 'location') else "N/A"
            estado_cuenta = str(entry.userAccountControl) if hasattr(entry, 'userAccountControl') else "N/A"

            try:
                ip = socket.gethostbyname(nombre)
            except socket.gaierror:
                ip = "No resuelve"

            equipos.append({
                "nombre": nombre,
                "so": so,
                "descripcion": desc,
                "ip": ip,
                "nombredns": nombre_dns,
                "versionso": version_so,
                "creadoel": creado_el,
                "ultimologon": ultimo_logon,
                "responsable": responsable,
                "ubicacion": ubicacion,
                "estadocuenta": estado_cuenta
            })

        escribir_log(f"Equipos obtenidos desde AD: {len(equipos)}", tipo="INFO")

    except Exception as e:
        escribir_log(f"Excepción al leer AD: {e}", tipo="ERROR")

    return equipos

# ------------------------
# Función de ping
# ------------------------
def hacer_ping(host):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        result = subprocess.run(["ping", param, "1", host], capture_output=True, timeout=6)
        estado = "Activo" if result.returncode == 0 else "Inactivo"

        if estado != "Activo":
            escribir_log(f"Ping fallido: {host} → {estado}", tipo="WARNING")
        return estado

    except subprocess.TimeoutExpired:
        escribir_log(f"Ping timeout: {host}", tipo="ERROR")
        return "Timeout"
    except Exception as e:
        escribir_log(f"Error en ping {host}: {e}", tipo="ERROR")
        return "Error"

# ------------------------
# Ejecutar SQL con reintento
# ------------------------
def ejecutar_sql_reintento(conn, query, params=(), reintentos=3, espera=5):
    for intento in range(1, reintentos + 1):
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            escribir_log(f"SQL intento {intento} fallido: {e}", tipo="ERROR")
            if intento < reintentos:
                time.sleep(espera)
                conn = conectar_sql()
            else:
                return False

# ------------------------
# Insertar o actualizar equipos con multithreading para ping
# ------------------------
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lock global para acceso a SQL
sql_lock = Lock()

def insertar_o_actualizar(conn, equipos, equipos_ad_actuales, ping_interval, max_threads=10):
    """
    Inserta o actualiza los registros de AD en la base de datos.
    Los pings se hacen en paralelo, pero las consultas SQL se serializan usando un lock.
    """
    def procesar_equipo(eq):
        ping = hacer_ping(eq["nombre"])
        estado_ad = "Dentro de AD" if eq["nombre"] in equipos_ad_actuales else "Removido de AD"

        # Actualizar estado_ping
        if eq["nombre"] in estado_ping:
            anterior = estado_ping[eq["nombre"]]["estado"]
            if anterior != ping:
                escribir_log(f"Estado de {eq['nombre']} cambió de {anterior} a {ping}")
                estado_ping[eq["nombre"]]["estado"] = ping
                estado_ping[eq["nombre"]]["contador"] = 1
            else:
                estado_ping[eq["nombre"]]["contador"] += 1
        else:
            estado_ping[eq["nombre"]] = {"estado": ping, "contador": 1}

        inactivo_desde = estado_ping[eq["nombre"]].get("inactivo_desde")
        if ping in ("Inactivo", "Timeout", "Error"):
            if not inactivo_desde:
                estado_ping[eq["nombre"]]["inactivo_desde"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        else:
            estado_ping[eq["nombre"]]["inactivo_desde"] = None

        tiempo_total_segundos = estado_ping[eq["nombre"]]["contador"] * ping_interval
        horas = tiempo_total_segundos // 3600
        minutos = (tiempo_total_segundos % 3600) // 60
        segundos = tiempo_total_segundos % 60
        tiempo_formateado = f"{horas:02}:{minutos:02}:{segundos:02}"

        query = """
            MERGE EquiposAD AS target
            USING (SELECT ? AS Nombre, ? AS SO, ? AS Descripcion, ? AS IP, ? AS NombreDNS,
                          ? AS VersionSO, ? AS CreadoEl, ? AS UltimoLogon, ? AS Responsable,
                          ? AS Ubicacion, ? AS EstadoCuenta, ? AS PingStatus, ? AS TiempoPing,
                          ? AS InactivoDesde, ? AS EstadoAD) AS src
            ON target.Nombre = src.Nombre
            WHEN MATCHED THEN
                UPDATE SET target.SO = src.SO,
                           target.Descripcion = src.Descripcion,
                           target.IP = src.IP,
                           target.NombreDNS = src.NombreDNS,
                           target.VersionSO = src.VersionSO,
                           target.CreadoEl = src.CreadoEl,
                           target.UltimoLogon = src.UltimoLogon,
                           target.Responsable = src.Responsable,
                           target.Ubicacion = src.Ubicacion,
                           target.EstadoCuenta = src.EstadoCuenta,
                           target.PingStatus = src.PingStatus,
                           target.TiempoPing = src.TiempoPing,
                           target.InactivoDesde = src.InactivoDesde,
                           target.EstadoAD = src.EstadoAD,
                           target.UltimaActualizacion = GETDATE()
            WHEN NOT MATCHED THEN
                INSERT (Nombre, SO, Descripcion, IP, NombreDNS, VersionSO, CreadoEl,
                        UltimoLogon, Responsable, Ubicacion, EstadoCuenta, PingStatus,
                        TiempoPing, InactivoDesde, EstadoAD)
                VALUES (src.Nombre, src.SO, src.Descripcion, src.IP, src.NombreDNS,
                        src.VersionSO, src.CreadoEl, src.UltimoLogon, src.Responsable,
                        src.Ubicacion, src.EstadoCuenta, src.PingStatus, src.TiempoPing,
                        src.InactivoDesde, src.EstadoAD);
        """

        # Serializamos la ejecución SQL usando el lock
        with sql_lock:
            ejecutar_sql_reintento(conn, query, (
                eq["nombre"], eq["so"], eq["descripcion"], eq["ip"], eq["nombredns"],
                eq["versionso"], eq["creadoel"], eq["ultimologon"], eq["responsable"],
                eq["ubicacion"], eq["estadocuenta"], ping, tiempo_formateado,
                estado_ping[eq["nombre"]]["inactivo_desde"], estado_ad
            ))

        texto_fecha = f" | Inactivo desde: {estado_ping[eq['nombre']].get('inactivo_desde')}" if estado_ping[eq["nombre"]].get('inactivo_desde') else ""
        print(f"[PING] {eq['nombre']} ({eq['ip']}) → {ping} | {estado_ad} ({tiempo_formateado}){texto_fecha}")

    # Ejecutar pings en paralelo
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(procesar_equipo, eq) for eq in equipos]
        for _ in as_completed(futures):
            pass
