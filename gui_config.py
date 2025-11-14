import json
import os
import customtkinter as ctk
from tkinter import messagebox

CONFIG_FILE = "Config.json"

# --------------------------
# Cargar configuración
# --------------------------
def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# --------------------------
# Guardar configuración
# --------------------------
def guardar_config(values):
    # Validación mínima
    try:
        int(values.get("PING_INTERVAL", ""))
    except ValueError:
        messagebox.showerror("Error", "PING_INTERVAL debe ser un número entero.")
        return False

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(values, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{e}")
        return False

    return True

# --------------------------
# Abrir GUI
# --------------------------
def abrir_gui_pro():
    config = cargar_config()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Configuración AD Scanner – Pro")
    root.geometry("520x700")
    root.resizable(False, False)

    # ------------------------
    # Función para crear campos
    # ------------------------
    def campo(label, default, row):
        ctk.CTkLabel(root, text=label, font=("Segoe UI", 14)).grid(
            row=row, column=0, padx=20, pady=10, sticky="w"
        )
        entry = ctk.CTkEntry(root, width=300)
        entry.grid(row=row, column=1, pady=10)
        valor = config.get(label, default)
        entry.insert(0, "" if valor is None else valor)
        return entry

    # Campos
    ping = campo("PING_INTERVAL", "25", 0)
    ad_server = campo("AD_SERVER", "DC.lab.local", 1)
    ad_user = campo("AD_USER", "admin@lab.local", 2)
    ad_pass = campo("AD_PASSWORD", "TuClave", 3)
    ad_base = campo("AD_SEARCH_BASE", "DC=lab,DC=local", 4)
    db_driver = campo("DB_DRIVER", "{ODBC Driver 17 for SQL Server}", 5)
    db_server = campo("DB_SERVER", ".\\SQLEXPRESS", 6)
    db_name = campo("DB_NAME", "DbAlgoritmo", 7)
    db_trusted = campo("DB_TRUSTED", "yes/no", 8)
    db_user = campo("DB_USER", "sa", 9)
    db_pass = campo("DB_PASSWORD", "Clave123", 10)

    config_result = {}

    # ------------------------
    # Botón guardar
    # ------------------------
    def click_guardar():
        nonlocal config_result
        values = {
            "PING_INTERVAL": ping.get(),
            "AD_SERVER": ad_server.get(),
            "AD_USER": ad_user.get(),
            "AD_PASSWORD": ad_pass.get(),
            "AD_SEARCH_BASE": ad_base.get(),
            "DB_DRIVER": db_driver.get(),
            "DB_SERVER": db_server.get(),
            "DB_NAME": db_name.get(),
            "DB_TRUSTED": db_trusted.get(),
            "DB_USER": None if db_trusted.get().lower() == "yes" else db_user.get(),
            "DB_PASSWORD": None if db_trusted.get().lower() == "yes" else db_pass.get(),
        }

        # Guardar solo si es válido
        if guardar_config(values):
            config_result = values
            root.destroy()
        else:
            config_result = {}

    btn = ctk.CTkButton(
        root,
        text="Guardar",
        width=250,
        height=40,
        corner_radius=10,
        command=click_guardar
    )
    btn.grid(row=20, column=1, pady=40)

    root.mainloop()
    return config_result
