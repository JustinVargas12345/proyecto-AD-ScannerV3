'''
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

CONFIG_FILE = "config.json"

def abrir_gui_config(callback_start):
    window = tk.Tk()
    window.title("Configuración del AD Scanner")
    window.geometry("420x500")
    window.resizable(False, False)

    # ----------- CAMPOS -------------
    labels = [
        ("Servidor AD", "AD_SERVER"),
        ("Usuario AD", "AD_USER"),
        ("Contraseña AD", "AD_PASSWORD"),
        ("Search Base", "AD_SEARCH_BASE"),
        ("Driver SQL", "DB_DRIVER"),
        ("Servidor SQL", "DB_SERVER"),
        ("Nombre DB", "DB_NAME"),
        ("Ping Interval (segundos)", "PING_INTERVAL"),
    ]

    entries = {}

    for idx, (label, key) in enumerate(labels):
        tk.Label(window, text=label, font=("Arial", 10)).place(x=20, y=20 + idx*40)
        entry = tk.Entry(window, width=35, font=("Arial", 10), show="*" if "PASS" in key else "")
        entry.place(x=180, y=20 + idx*40)
        entries[key] = entry

    # Trusted Connection checkbox
    trusted_var = tk.BooleanVar(value=True)
    tk.Checkbutton(window, text="Trusted Connection", variable=trusted_var).place(x=20, y=20 + len(labels)*40)

    # ------------ BOTÓN GUARDAR ----------
    def guardar_y_iniciar():
        try:
            # Convertir todo a diccionario
            data = {
                "PING_INTERVAL": int(entries["PING_INTERVAL"].get()),
                "AD_SERVER": entries["AD_SERVER"].get(),
                "AD_USER": entries["AD_USER"].get(),
                "AD_PASSWORD": entries["AD_PASSWORD"].get(),
                "AD_SEARCH_BASE": entries["AD_SEARCH_BASE"].get(),
                "DB_DRIVER": entries["DB_DRIVER"].get(),
                "DB_SERVER": entries["DB_SERVER"].get(),
                "DB_NAME": entries["DB_NAME"].get(),
                "DB_TRUSTED": "yes" if trusted_var.get() else "no",
                "DB_USER": None if trusted_var.get() else "",
                "DB_PASSWORD": None if trusted_var.get() else ""
            }

            # Guardar en config.json
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            messagebox.showinfo("OK", "Configuración guardada correctamente.")
            window.destroy()

            # Ejecutar el programa principal
            callback_start()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(window, text="Guardar y Ejecutar", command=guardar_y_iniciar).place(x=150, y=440)

    window.mainloop()
'''
'''
import json
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox

CONFIG_FILE = "Config_json"

DRIVERS = [
    "{ODBC Driver 17 for SQL Server}",
    "{ODBC Driver 18 for SQL Server}",
    "{SQL Server}",
    "{SQL Server Native Client 11.0}"
]

# -----------------------
# Cargar configuración
# -----------------------
def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# -----------------------
# Guardar configuración
# -----------------------
def guardar_config(values):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(values, f, indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{e}")
        return

    messagebox.showinfo("Guardado", "Configuración guardada correctamente.")
    root.destroy()   # <<— NO iniciar main.py aquí (lo hará iniciar_gui_config)


# ==========================
# GUI MODERNA FINAL
# ==========================

root = ttk.Window(themename="darkly")
root.title("Configuración del AD Scanner")
root.geometry("520x700")
root.resizable(False, False)
root.configure(bg="#000000")

config = cargar_config()


# --------------------
# Helpers de estilo
# --------------------
def formatear_label(texto):
    texto = texto.replace("_", " ").lower()
    return texto.capitalize() + ":"


def agregar_campo(label, ejemplo, valor, fila):
    label_format = formatear_label(label)

    ttk.Label(
        root,
        text=label_format,
        font=("Segoe UI", 11, "bold"),
        background="#000000",
        foreground="white"
    ).grid(row=fila, column=0, sticky="w", padx=20, pady=(10, 3))

    var = ttk.StringVar(value=valor)
    entry = ttk.Entry(
        root,
        textvariable=var,
        width=42,
        bootstyle="secondary"  # gris limpio
    )
    entry.grid(row=fila, column=1, padx=10)

    ttk.Label(
        root,
        text=f"Ej: {ejemplo}",
        font=("Segoe UI", 7),
        background="#000000",
        foreground="#bbbbbb"
    ).grid(row=fila + 1, column=1, sticky="w", padx=12)

    return var


# --------------------
# Campos
# --------------------
PING_INTERVAL = agregar_campo("PING_INTERVAL", "25", config.get("PING_INTERVAL", ""), 0)
AD_SERVER = agregar_campo("AD_SERVER", "DC.lab.local", config.get("AD_SERVER", ""), 2)
AD_USER = agregar_campo("AD_USER", "admin@lab.local", config.get("AD_USER", ""), 4)
AD_PASSWORD = agregar_campo("AD_PASSWORD", "TuClave", config.get("AD_PASSWORD", ""), 6)
AD_SEARCH_BASE = agregar_campo("AD_SEARCH_BASE", "DC=lab,DC=local", config.get("AD_SEARCH_BASE", ""), 8)

# --------------------
# Driver SQL
# --------------------
ttk.Label(
    root,
    text="Db driver:",
    font=("Segoe UI", 11, "bold"),
    background="#000000",
    foreground="white"
).grid(row=10, column=0, sticky="w", padx=20, pady=(10, 3))

DB_DRIVER = ttk.Combobox(
    root,
    values=DRIVERS,
    width=40,
    bootstyle="secondary"
)
DB_DRIVER.set(config.get("DB_DRIVER", DRIVERS[0]))
DB_DRIVER.grid(row=10, column=1, padx=10)

ttk.Label(
    root,
    text="Ej: {ODBC Driver 17 for SQL Server}",
    font=("Segoe UI", 7),
    background="#000000",
    foreground="#bbbbbb"
).grid(row=11, column=1, sticky="w", padx=12)

DB_SERVER = agregar_campo("DB_SERVER", ".\\SQLEXPRESS", config.get("DB_SERVER", ""), 12)
DB_NAME = agregar_campo("DB_NAME", "DbAlgoritmo", config.get("DB_NAME", ""), 14)
DB_TRUSTED = agregar_campo("DB_TRUSTED", "yes/no", config.get("DB_TRUSTED", ""), 16)
DB_USER = agregar_campo("DB_USER", "sa", config.get("DB_USER", ""), 18)
DB_PASSWORD = agregar_campo("DB_PASSWORD", "Clave123", config.get("DB_PASSWORD", ""), 20)


# --------------------
# Botón Guardar
# --------------------
def click_guardar():
    values = {
        "PING_INTERVAL": int(PING_INTERVAL.get()) if PING_INTERVAL.get().isdigit() else 25,
        "AD_SERVER": AD_SERVER.get(),
        "AD_USER": AD_USER.get(),
        "AD_PASSWORD": AD_PASSWORD.get(),
        "AD_SEARCH_BASE": AD_SEARCH_BASE.get(),
        "DB_DRIVER": DB_DRIVER.get(),
        "DB_SERVER": DB_SERVER.get(),
        "DB_NAME": DB_NAME.get(),
        "DB_TRUSTED": DB_TRUSTED.get(),
        "DB_USER": DB_USER.get() if DB_TRUSTED.get().lower() != "yes" else None,
        "DB_PASSWORD": DB_PASSWORD.get() if DB_TRUSTED.get().lower() != "yes" else None
    }

    guardar_config(values)


ttk.Button(
    root,
    text="Guardar y ejecutar",
    bootstyle="secondary",
    width=28,
    command=click_guardar
).grid(row=22, column=1, pady=40)

root.mainloop()
'''