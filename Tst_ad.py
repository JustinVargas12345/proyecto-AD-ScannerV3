from config_json_loader import cargar_config
from ldap3 import Server, Connection, ALL

config = cargar_config()

server = Server(config["AD_SERVER"], get_info=ALL)
conn = Connection(server, user=config["AD_USER"], password=config["AD_PASSWORD"], auto_bind=True)

print("[OK] Conectado correctamente al Active Directory")

conn.search(
    search_base=config["AD_SEARCH_BASE"],
    search_filter="(objectClass=computer)",
    attributes=["name", "operatingSystem"]
)

for entry in conn.entries:
    print(entry)
