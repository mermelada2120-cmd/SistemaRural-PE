"""
SistemaRural-PE — Posta de Salud "San Gabriel"
Lenguajes de Programación (UAIN1288P) — UPN

Integrantes:
  - Joshua (herencia y datos base de personas)
  - Sebas  (citas y gestor de citas, patrón Singleton, funciones funcionales)
  - Juan   (reportes y pruebas automatizadas)
"""

from datetime import date


# ======================================================================
# PARTE DE JOSHUA — Herencia, encapsulamiento y manejo de errores
# ======================================================================

class Persona:
    def __init__(self, nombre, edad, dni):
        if edad < 0:
            raise ValueError("La edad no puede ser negativa")
        if not dni:
            raise ValueError("El DNI no puede estar vacío")
        self.nombre = nombre
        self.edad = edad
        self.__dni = dni

    @property
    def dni(self):
        return "**** **** " + self.__dni[-4:]


class Paciente(Persona):
    def __init__(self, nombre, edad, dni, historial_medico=None):
        super().__init__(nombre, edad, dni)
        self.historial_medico = historial_medico if historial_medico is not None else []


class PersonalSalud(Persona):
    def __init__(self, nombre, edad, dni, cargo):
        super().__init__(nombre, edad, dni)
        self.cargo = cargo


# ======================================================================
# PARTE DE SEBAS — Citas, GestorCitas (Singleton), filter/map/reduce
#
# NOTA DE INTEGRACIÓN (corregido respecto a la primera versión):
#   - La fecha se guarda como objeto `date`, no como texto ("26/09/2026"),
#     porque el reporte de Juan usa fecha.isocalendar(), que solo existe
#     en objetos date.
#   - El estado se guarda siempre en minúscula ("atendida", "pendiente",
#     "confirmada"), porque el reporte de Juan compara con
#     cita.estado == "atendida" en minúscula exacta.
# ======================================================================

class Cita:
    def __init__(self, id_cita, paciente, medico, fecha, estado):
        self.id_cita = id_cita
        self.paciente = paciente
        self.medico = medico
        self.fecha = fecha          # objeto date
        self.estado = estado.lower()  # siempre en minúscula

    def __str__(self):
        return (
            f"Cita #{self.id_cita} | Paciente: {self.paciente.nombre} | "
            f"Médico: {self.medico.nombre} | Fecha: {self.fecha.strftime('%d/%m/%Y')} | "
            f"Estado: {self.estado}"
        )


class GestorCitas:
    """Patrón Singleton: solo puede existir UNA instancia de GestorCitas
    en todo el programa, para que todas las partes del sistema trabajen
    sobre la misma lista de citas."""

    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia.citas = []
        return cls._instancia

    def agregar_cita(self, cita):
        self.citas.append(cita)

    def obtener_citas(self):
        return self.citas

    # ---- FILTER ----
    def filtrar_citas_por_estado(self, estado):
        estado = estado.lower()
        return list(filter(lambda c: c.estado == estado, self.citas))

    # ---- MAP ----
    def obtener_resumen_citas(self):
        return list(map(
            lambda c: f"Cita #{c.id_cita}: {c.paciente.nombre} con {c.medico.nombre} ({c.estado})",
            self.citas
        ))

    # ---- REDUCE ----
    def contar_citas_por_medico(self, nombre_medico):
        from functools import reduce
        return reduce(
            lambda total, c: total + 1 if c.medico.nombre == nombre_medico else total,
            self.citas,
            0
        )


# ======================================================================
# PARTE DE JUAN — Reportes y funciones de orden superior sobre citas
# ======================================================================

def contar_citas_por_paciente(citas):
    conteo = {}
    for cita in citas:
        nombre = cita.paciente.nombre
        conteo[nombre] = conteo.get(nombre, 0) + 1
    return conteo


def pacientes_con_mas_citas(citas):
    conteo = contar_citas_por_paciente(citas)
    return sorted(conteo.items(), key=lambda par: par[1], reverse=True)


def atenciones_por_semana(citas):
    conteo = {}
    for cita in citas:
        if cita.estado == "atendida":
            iso = cita.fecha.isocalendar()
            clave = (iso[0], iso[1])  # (año, número de semana)
            conteo[clave] = conteo.get(clave, 0) + 1
    return conteo


# ======================================================================
# DEMO INTEGRADA — todas las partes trabajando juntas
# ======================================================================

if __name__ == "__main__":
    # --- Personas (Joshua) ---
    paciente1 = Paciente("Ana Quispe", 34, "45678912")
    paciente2 = Paciente("Luis Mamani", 50, "78912345")
    paciente3 = Paciente("Rosa Huamán", 28, "12345678")

    medico1 = PersonalSalud("Carlos López", 45, "11223344", "Medicina General")
    medico2 = PersonalSalud("Ana Torres", 39, "55667788", "Enfermería")

    # --- Citas (Sebas) ---
    cita1 = Cita(1, paciente1, medico2, date(2026, 9, 25), "confirmada")
    cita2 = Cita(2, paciente2, medico2, date(2026, 9, 26), "confirmada")
    cita3 = Cita(3, paciente3, medico1, date(2026, 9, 27), "pendiente")
    cita4 = Cita(4, paciente1, medico1, date(2026, 9, 28), "atendida")

    gestor = GestorCitas()
    for c in (cita1, cita2, cita3, cita4):
        gestor.agregar_cita(c)

    print("=" * 60)
    print("TODAS LAS CITAS")
    print("=" * 60)
    for cita in gestor.obtener_citas():
        print(cita)

    print("\n" + "=" * 60)
    print("CITAS PENDIENTES - FILTER")
    print("=" * 60)
    for cita in gestor.filtrar_citas_por_estado("pendiente"):
        print(cita)

    print("\n" + "=" * 60)
    print("RESUMEN DE CITAS - MAP")
    print("=" * 60)
    for elemento in gestor.obtener_resumen_citas():
        print(elemento)

    print("\n" + "=" * 60)
    print("CITAS POR MÉDICO - REDUCE")
    print("=" * 60)
    print(f"Dr. Carlos López tiene {gestor.contar_citas_por_medico('Carlos López')} citas.")
    print(f"Dra. Ana Torres tiene {gestor.contar_citas_por_medico('Ana Torres')} citas.")

    print("\n" + "=" * 60)
    print("PRUEBA DEL SINGLETON")
    print("=" * 60)
    gestor2 = GestorCitas()
    if gestor is gestor2:
        print("GestorCitas utiliza correctamente el patrón Singleton.")
    else:
        print("Se crearon dos instancias diferentes.")

    # --- Reportes (Juan) ---
    print("\n" + "=" * 60)
    print("REPORTES")
    print("=" * 60)
    print("Citas por paciente:", contar_citas_por_paciente(gestor.obtener_citas()))
    print("Pacientes con más citas:", pacientes_con_mas_citas(gestor.obtener_citas()))
    print("Atenciones por semana:", atenciones_por_semana(gestor.obtener_citas()))
