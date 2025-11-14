'''
import json
import os
import customtkinter as ctk
from tkinter import messagebox
from ad_utils import validar_ad

CONFIG_FILE = "Config.json"

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_config(values):
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

def abrir_gui_pro():
    config = cargar_config()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Configuración AD Scanner – Pro")
    root.geometry("650x780")
    root.resizable(False, False)

    error_labels = {}

    # Función para crear campos
    def campo(label, default, row, show=None):
        ctk.CTkLabel(root, text=label, font=("Segoe UI", 14)).grid(
            row=row, column=0, padx=20, pady=5, sticky="e"
        )
        entry = ctk.CTkEntry(root, width=400, show=show)
        entry.grid(row=row, column=1, pady=5, sticky="w")
        valor = config.get(label, default)
        entry.insert(0, "" if valor is None else valor)

        # Label de error debajo del campo
        error = ctk.CTkLabel(root, text="", text_color="red", font=("Segoe UI", 12))
        error.grid(row=row+1, column=1, sticky="w")
        error_labels[label] = error

        return entry

    # Campos AD
    ping = campo("PING_INTERVAL", "25", 0)
    ad_server = campo("AD_SERVER", "DC.lab.local", 2)
    ad_user = campo("AD_USER", "admin@lab.local", 4)
    ad_pass = campo("AD_PASSWORD", "TuClave", 6, show="*")
    ad_base = campo("AD_SEARCH_BASE", "DC=lab,DC=local", 8)

    # Botón mostrar/ocultar password AD
    def toggle_pass():
        if ad_pass.cget("show") == "*":
            ad_pass.configure(show="")
            btn_toggle.configure(text="O")
        else:
            ad_pass.configure(show="*")
            btn_toggle.configure(text="M")
    btn_toggle = ctk.CTkButton(root, text="M", width=30, command=toggle_pass)
    btn_toggle.grid(row=6, column=2, padx=5, sticky="w")

    # Campos DB
    driver_options = ["ODBC Driver 17 for SQL Server",
                      "ODBC Driver 18 for SQL Server",
                      "ODBC Driver 13 for SQL Server"]
    ctk.CTkLabel(root, text="DB_DRIVER", font=("Segoe UI", 14)).grid(row=10, column=0, padx=20, pady=5, sticky="e")
    db_driver = ctk.CTkOptionMenu(root, values=driver_options, width=400)
    db_driver.grid(row=10, column=1, sticky="w")
    db_driver.set(config.get("DB_DRIVER", driver_options[0]))

    db_server = campo("DB_SERVER", ".\\SQLEXPRESS", 12)
    db_name = campo("DB_NAME", "DbAlgoritmo", 14)
    db_trusted = campo("DB_TRUSTED", "yes", 16)
    db_user = campo("DB_USER", "sa", 18)
    db_pass = campo("DB_PASSWORD", "Clave123", 20, show="*")

    # Botón mostrar/ocultar password DB
    def toggle_db_pass():
        if db_pass.cget("show") == "*":
            db_pass.configure(show="")
            btn_toggle_db.configure(text="O")
        else:
            db_pass.configure(show="*")
            btn_toggle_db.configure(text="M")
    btn_toggle_db = ctk.CTkButton(root, text="M", width=30, command=toggle_db_pass)
    btn_toggle_db.grid(row=20, column=2, padx=5, sticky="w")

    config_result = {}

    # Guardar configuración con validación
    def click_guardar():
        nonlocal config_result

        # Limpiar errores anteriores
        for lbl in error_labels.values():
            lbl.configure(text="")

        errores = False
        # Validar PING_INTERVAL
        try:
            int(ping.get())
        except ValueError:
            error_labels["PING_INTERVAL"].configure(text="Debe ser un número entero")
            errores = True

        # Validar AD
        credenciales_ad = {
            "AD_SERVER": ad_server.get(),
            "AD_USER": ad_user.get(),
            "AD_PASSWORD": ad_pass.get(),
            "AD_SEARCH_BASE": ad_base.get()
        }
        if not errores:
            if not validar_ad(credenciales_ad):
                error_labels["AD_PASSWORD"].configure(text="Credenciales AD inválidas")
                errores = True

        if errores:
            return  # NO cerrar la ventana si hay errores

        # Guardar configuración si todo está correcto
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
            "DB_USER": db_user.get() if db_trusted.get().lower() != "yes" else "",
            "DB_PASSWORD": db_pass.get() if db_trusted.get().lower() != "yes" else "",
        }

        if guardar_config(values):
            config_result = values
            root.destroy()

    btn = ctk.CTkButton(root, text="Guardar", width=300, height=40, corner_radius=10, command=click_guardar)
    btn.grid(row=22, column=0, columnspan=3, pady=40)

    root.mainloop()
    return config_result
'''


import json
import os
import customtkinter as ctk
from tkinter import messagebox
from ad_utils import validar_ad
from logs_utils import eliminar_logs  # Importamos la función que estará en otro archivo

CONFIG_FILE = "Config.json"

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_config(values):
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

def abrir_gui_pro():
    config = cargar_config()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Configuración AD Scanner – Pro")
    root.geometry("650x820")
    root.resizable(False, False)

    error_labels = {}

    # Función para crear campos
    def campo(label, default, row, show=None):
        ctk.CTkLabel(root, text=label, font=("Segoe UI", 14)).grid(
            row=row, column=0, padx=20, pady=5, sticky="e"
        )
        entry = ctk.CTkEntry(root, width=400, show=show)
        entry.grid(row=row, column=1, pady=5, sticky="w")
        valor = config.get(label, default)
        entry.insert(0, "" if valor is None else valor)

        # Label de error debajo del campo
        error = ctk.CTkLabel(root, text="", text_color="red", font=("Segoe UI", 12))
        error.grid(row=row+1, column=1, sticky="w")
        error_labels[label] = error

        return entry

    # Campos AD
    ping = campo("PING_INTERVAL", "25", 0)
    ad_server = campo("AD_SERVER", "DC.lab.local", 2)
    ad_user = campo("AD_USER", "admin@lab.local", 4)
    ad_pass = campo("AD_PASSWORD", "TuClave", 6, show="*")
    ad_base = campo("AD_SEARCH_BASE", "DC=lab,DC=local", 8)

    # Botón mostrar/ocultar password AD
    def toggle_pass():
        if ad_pass.cget("show") == "*":
            ad_pass.configure(show="")
            btn_toggle.configure(text="O")
        else:
            ad_pass.configure(show="*")
            btn_toggle.configure(text="M")
    btn_toggle = ctk.CTkButton(root, text="M", width=30, command=toggle_pass)
    btn_toggle.grid(row=6, column=2, padx=5, sticky="w")

    # Campos DB
    driver_options = ["ODBC Driver 17 for SQL Server",
                      "ODBC Driver 18 for SQL Server",
                      "ODBC Driver 13 for SQL Server"]
    ctk.CTkLabel(root, text="DB_DRIVER", font=("Segoe UI", 14)).grid(row=10, column=0, padx=20, pady=5, sticky="e")
    db_driver = ctk.CTkOptionMenu(root, values=driver_options, width=400)
    db_driver.grid(row=10, column=1, sticky="w")
    db_driver.set(config.get("DB_DRIVER", driver_options[0]))

    db_server = campo("DB_SERVER", ".\\SQLEXPRESS", 12)
    db_name = campo("DB_NAME", "DbAlgoritmo", 14)
    db_trusted = campo("DB_TRUSTED", "yes", 16)
    db_user = campo("DB_USER", "sa", 18)
    db_pass = campo("DB_PASSWORD", "Clave123", 20, show="*")

    # Botón mostrar/ocultar password DB
    def toggle_db_pass():
        if db_pass.cget("show") == "*":
            db_pass.configure(show="")
            btn_toggle_db.configure(text="O")
        else:
            db_pass.configure(show="*")
            btn_toggle_db.configure(text="M")
    btn_toggle_db = ctk.CTkButton(root, text="M", width=30, command=toggle_db_pass)
    btn_toggle_db.grid(row=20, column=2, padx=5, sticky="w")

    # -------------------
    # Opción de limpieza de logs
    # -------------------
    ctk.CTkLabel(root, text="Modo Limpieza Logs", font=("Segoe UI", 14)).grid(row=22, column=0, padx=20, pady=5, sticky="e")
    log_options = ["Manual", "Automático"]
    log_option_menu = ctk.CTkOptionMenu(root, values=log_options, width=400)
    log_option_menu.grid(row=22, column=1, sticky="w")
    log_option_menu.set(config.get("LOG_MODE", "Manual"))

    config_result = {}

    # Guardar configuración con validación
    def click_guardar():
        nonlocal config_result

        # Limpiar errores anteriores
        for lbl in error_labels.values():
            lbl.configure(text="")

        errores = False
        # Validar PING_INTERVAL
        try:
            int(ping.get())
        except ValueError:
            error_labels["PING_INTERVAL"].configure(text="Debe ser un número entero")
            errores = True

        # Validar AD
        credenciales_ad = {
            "AD_SERVER": ad_server.get(),
            "AD_USER": ad_user.get(),
            "AD_PASSWORD": ad_pass.get(),
            "AD_SEARCH_BASE": ad_base.get()
        }
        if not errores:
            if not validar_ad(credenciales_ad):
                error_labels["AD_PASSWORD"].configure(text="Credenciales AD inválidas")
                errores = True

        if errores:
            return  # NO cerrar la ventana si hay errores

        # Guardar configuración si todo está correcto
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
            "DB_USER": db_user.get() if db_trusted.get().lower() != "yes" else "",
            "DB_PASSWORD": db_pass.get() if db_trusted.get().lower() != "yes" else "",
            "LOG_MODE": log_option_menu.get()  # Guardamos el modo de logs
        }

        if guardar_config(values):
            # Si es automático, llamamos a eliminar_logs inmediatamente
            if values["LOG_MODE"] == "Automático":
                eliminar_logs()
            config_result = values
            root.destroy()

    btn = ctk.CTkButton(root, text="Guardar", width=300, height=40, corner_radius=10, command=click_guardar)
    btn.grid(row=24, column=0, columnspan=3, pady=40)

    root.mainloop()
    return config_result
