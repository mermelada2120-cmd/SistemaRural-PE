"""
Interfaz gráfica (Tkinter) — SistemaRural-PE — Posta de Salud "San Gabriel"

IMPORTANTE: este archivo debe estar en la MISMA carpeta que sistema_rural_pe.py
(el archivo con las clases Persona, Paciente, Cita, GestorCitas y los reportes).

Para ejecutar:   python interfaz_sistema_rural.py

Cada pestaña es la parte de un integrante:
  - Pestaña "Pacientes" -> Joshua
  - Pestaña "Citas"     -> Sebas
  - Pestaña "Reportes"  -> Juan
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Usamos las clases y funciones que ya construimos entre los tres
from sistema_rural_pe import (
    Paciente, PersonalSalud, Cita, GestorCitas,
    contar_citas_por_paciente, pacientes_con_mas_citas, atenciones_por_semana,
)

# ---------------------------------------------------------------
# Colores (tema azul y blanco)
# ---------------------------------------------------------------
AZUL = "#1d4ed8"
AZUL_CLARO = "#dbeafe"
BLANCO = "#ffffff"
TEXTO = "#0f172a"

# ---------------------------------------------------------------
# Datos del sistema (viven mientras el programa esté abierto)
# ---------------------------------------------------------------
gestor = GestorCitas()          # Singleton (parte de Sebas)
pacientes = []                  # lista de objetos Paciente
medicos = [
    PersonalSalud("Carlos López", 45, "11223344", "Medicina General"),
    PersonalSalud("Ana Torres", 39, "55667788", "Enfermería"),
]
contador_citas = 0

# ---------------------------------------------------------------
# Ventana principal y estilo
# ---------------------------------------------------------------
ventana = tk.Tk()
ventana.title("SistemaRural-PE — Posta San Gabriel")
ventana.geometry("820x560")
ventana.configure(bg=BLANCO)

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TNotebook", background=BLANCO, borderwidth=0)
estilo.configure("TNotebook.Tab", padding=(18, 8), font=("Segoe UI", 11, "bold"),
                 background=AZUL_CLARO, foreground=AZUL)
estilo.map("TNotebook.Tab", background=[("selected", AZUL)], foreground=[("selected", BLANCO)])
estilo.configure("TFrame", background=BLANCO)
estilo.configure("TLabel", background=BLANCO, foreground=TEXTO, font=("Segoe UI", 11))
estilo.configure("Azul.TButton", background=AZUL, foreground=BLANCO,
                 font=("Segoe UI", 11, "bold"), padding=8)
estilo.map("Azul.TButton", background=[("active", "#1e40af")])
estilo.configure("Treeview.Heading", background=AZUL, foreground=BLANCO, font=("Segoe UI", 10, "bold"))
estilo.configure("Treeview", rowheight=26, font=("Segoe UI", 10))

# Franja azul de título
encabezado = tk.Frame(ventana, bg=AZUL, height=64)
encabezado.pack(fill="x")
tk.Label(encabezado, text="SistemaRural-PE", bg=AZUL, fg=BLANCO,
         font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=12)
tk.Label(encabezado, text="Posta de Salud San Gabriel", bg=AZUL, fg=AZUL_CLARO,
         font=("Segoe UI", 11)).pack(side="left")

pestanas = ttk.Notebook(ventana)
pestanas.pack(fill="both", expand=True, padx=14, pady=14)


# ===============================================================
# PESTAÑA 1 — PACIENTES  (parte de JOSHUA)
# ===============================================================
tab_pacientes = ttk.Frame(pestanas)
pestanas.add(tab_pacientes, text="Pacientes")

ttk.Label(tab_pacientes, text="Nombre").grid(row=0, column=0, padx=8, pady=8, sticky="e")
entrada_nombre = ttk.Entry(tab_pacientes, width=26)
entrada_nombre.grid(row=0, column=1, pady=8)

ttk.Label(tab_pacientes, text="Edad").grid(row=0, column=2, padx=8, sticky="e")
entrada_edad = ttk.Entry(tab_pacientes, width=8)
entrada_edad.grid(row=0, column=3)

ttk.Label(tab_pacientes, text="DNI").grid(row=1, column=0, padx=8, pady=8, sticky="e")
entrada_dni = ttk.Entry(tab_pacientes, width=26)
entrada_dni.grid(row=1, column=1, pady=8)

tabla_pacientes = ttk.Treeview(tab_pacientes, columns=("nombre", "edad", "dni"),
                               show="headings", height=10)
tabla_pacientes.heading("nombre", text="Nombre")
tabla_pacientes.heading("edad", text="Edad")
tabla_pacientes.heading("dni", text="DNI (protegido)")
tabla_pacientes.grid(row=3, column=0, columnspan=5, padx=8, pady=10, sticky="nsew")


def registrar_paciente():
    """Handler del botón: crea un Paciente. Si el dato es inválido, muestra un aviso."""
    try:
        edad = int(entrada_edad.get())
        nuevo = Paciente(entrada_nombre.get(), edad, entrada_dni.get())  # valida edad y DNI
    except ValueError as error:
        messagebox.showwarning("Dato inválido", f"No se pudo registrar: {error}")
        return
    pacientes.append(nuevo)
    tabla_pacientes.insert("", "end", values=(nuevo.nombre, nuevo.edad, nuevo.dni))  # dni sale enmascarado
    combo_paciente["values"] = [p.nombre for p in pacientes]
    for campo in (entrada_nombre, entrada_edad, entrada_dni):
        campo.delete(0, "end")


ttk.Button(tab_pacientes, text="Registrar paciente", style="Azul.TButton",
           command=registrar_paciente).grid(row=1, column=3, columnspan=2, padx=8)
tab_pacientes.rowconfigure(3, weight=1)
tab_pacientes.columnconfigure(1, weight=1)


# ===============================================================
# PESTAÑA 2 — CITAS  (parte de SEBAS)
# ===============================================================
tab_citas = ttk.Frame(pestanas)
pestanas.add(tab_citas, text="Citas")

ttk.Label(tab_citas, text="Paciente").grid(row=0, column=0, padx=8, pady=8, sticky="e")
combo_paciente = ttk.Combobox(tab_citas, state="readonly", width=24)
combo_paciente.grid(row=0, column=1)

ttk.Label(tab_citas, text="Médico").grid(row=0, column=2, padx=8, sticky="e")
combo_medico = ttk.Combobox(tab_citas, state="readonly", width=20,
                            values=[m.nombre for m in medicos])
combo_medico.grid(row=0, column=3)

ttk.Label(tab_citas, text="Fecha (dd/mm/aaaa)").grid(row=1, column=0, padx=8, pady=8, sticky="e")
entrada_fecha = ttk.Entry(tab_citas, width=26)
entrada_fecha.grid(row=1, column=1)

ttk.Label(tab_citas, text="Estado").grid(row=1, column=2, padx=8, sticky="e")
combo_estado = ttk.Combobox(tab_citas, state="readonly", width=20,
                            values=["pendiente", "confirmada", "atendida", "cancelada"])
combo_estado.set("pendiente")
combo_estado.grid(row=1, column=3)

ttk.Label(tab_citas, text="Ver:").grid(row=3, column=0, padx=8, sticky="e")
combo_filtro = ttk.Combobox(tab_citas, state="readonly", width=24,
                            values=["todas", "pendiente", "confirmada", "atendida", "cancelada"])
combo_filtro.set("todas")
combo_filtro.grid(row=3, column=1, pady=6)

tabla_citas = ttk.Treeview(tab_citas, columns=("id", "paciente", "medico", "fecha", "estado"),
                           show="headings", height=9)
for columna, titulo in [("id", "N°"), ("paciente", "Paciente"), ("medico", "Médico"),
                        ("fecha", "Fecha"), ("estado", "Estado")]:
    tabla_citas.heading(columna, text=titulo)
    tabla_citas.column(columna, width=110 if columna != "id" else 40)
tabla_citas.grid(row=4, column=0, columnspan=5, padx=8, pady=8, sticky="nsew")


def mostrar_citas(evento=None):
    """Redibuja la tabla usando el filtro elegido (usa filter del GestorCitas)."""
    tabla_citas.delete(*tabla_citas.get_children())
    if combo_filtro.get() == "todas":
        lista = gestor.obtener_citas()
    else:
        lista = gestor.filtrar_citas_por_estado(combo_filtro.get())
    for c in lista:
        tabla_citas.insert("", "end", values=(c.id_cita, c.paciente.nombre, c.medico.nombre,
                                              c.fecha.strftime("%d/%m/%Y"), c.estado))


def agendar_cita():
    """Handler del botón: crea una Cita y la agrega al GestorCitas (Singleton)."""
    global contador_citas
    if not combo_paciente.get() or not combo_medico.get():
        messagebox.showwarning("Faltan datos", "Elige un paciente y un médico.")
        return
    try:
        fecha = datetime.strptime(entrada_fecha.get(), "%d/%m/%Y").date()
    except ValueError:
        messagebox.showwarning("Fecha inválida", "Escribe la fecha así: 25/09/2026")
        return
    paciente = pacientes[combo_paciente.current()]
    medico = medicos[combo_medico.current()]
    contador_citas += 1
    gestor.agregar_cita(Cita(contador_citas, paciente, medico, fecha, combo_estado.get()))
    entrada_fecha.delete(0, "end")
    mostrar_citas()


ttk.Button(tab_citas, text="Agendar cita", style="Azul.TButton",
           command=agendar_cita).grid(row=2, column=3, pady=8)
combo_filtro.bind("<<ComboboxSelected>>", mostrar_citas)   # listener: cambia el filtro -> redibuja
tab_citas.rowconfigure(4, weight=1)


# ===============================================================
# PESTAÑA 3 — REPORTES  (parte de JUAN)
# ===============================================================
tab_reportes = ttk.Frame(pestanas)
pestanas.add(tab_reportes, text="Reportes")

caja_reporte = tk.Text(tab_reportes, height=14, font=("Consolas", 11), bg=AZUL_CLARO,
                       fg=TEXTO, relief="flat", padx=12, pady=12)
caja_reporte.grid(row=1, column=0, columnspan=3, padx=8, pady=10, sticky="nsew")


def escribir_reporte(titulo, lineas):
    caja_reporte.delete("1.0", "end")
    caja_reporte.insert("end", titulo + "\n" + "-" * 40 + "\n")
    caja_reporte.insert("end", "\n".join(lineas) if lineas else "Todavía no hay citas registradas.")


def reporte_por_paciente():
    conteo = contar_citas_por_paciente(gestor.obtener_citas())
    escribir_reporte("Citas por paciente", [f"{n}: {c} cita(s)" for n, c in conteo.items()])


def reporte_mas_citas():
    orden = pacientes_con_mas_citas(gestor.obtener_citas())
    escribir_reporte("Pacientes con más citas", [f"{n}: {c}" for n, c in orden])


def reporte_semanal():
    semanas = atenciones_por_semana(gestor.obtener_citas())
    escribir_reporte("Atenciones por semana", [f"Año {a}, semana {s}: {c}" for (a, s), c in semanas.items()])


ttk.Button(tab_reportes, text="Citas por paciente", style="Azul.TButton",
           command=reporte_por_paciente).grid(row=0, column=0, padx=8, pady=8)
ttk.Button(tab_reportes, text="Pacientes con más citas", style="Azul.TButton",
           command=reporte_mas_citas).grid(row=0, column=1, padx=8)
ttk.Button(tab_reportes, text="Atenciones por semana", style="Azul.TButton",
           command=reporte_semanal).grid(row=0, column=2, padx=8)
tab_reportes.rowconfigure(1, weight=1)
tab_reportes.columnconfigure((0, 1, 2), weight=1)

# ---------------------------------------------------------------
# Arranca la aplicación (queda esperando clics del usuario)
# ---------------------------------------------------------------
ventana.mainloop()
