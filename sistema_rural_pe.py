import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from functools import reduce
import hashlib
import re
import unittest
import json
import os

class ErrorValidacion(Exception):
    pass

class Persona:
    def __init__(self, nombres, apellidos):
        self.nombres = nombres
        self.apellidos = apellidos

    @property
    def nombres(self):
        return self.__nombres

    @nombres.setter
    def nombres(self, valor):
        valor = valor.strip()
        if not valor:
            raise ErrorValidacion("Los nombres son obligatorios.")
        self.__nombres = valor

    @property
    def apellidos(self):
        return self.__apellidos

    @apellidos.setter
    def apellidos(self, valor):
        valor = valor.strip()
        if not valor:
            raise ErrorValidacion("Los apellidos son obligatorios.")
        self.__apellidos = valor

    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

class Paciente(Persona):
    def __init__(self, nombres, apellidos, DNI, fecha_nacimiento, telefono):
        super().__init__(nombres, apellidos)
        DNI = DNI.strip()
        fecha_nacimiento = fecha_nacimiento.strip()
        telefono = telefono.strip()

        if not re.fullmatch(r"\d{8}", DNI):
            raise ErrorValidacion("El DNI debe tener 8 dígitos.")

        try:
            fecha = datetime.strptime(fecha_nacimiento, "%d/%m/%Y")
        except ValueError:
            raise ErrorValidacion(
                "La fecha de nacimiento no tiene un formato válido (DD/MM/AAAA)."
            )
        if fecha > datetime.now():
            raise ErrorValidacion("La fecha de nacimiento no puede ser futura.")

        self.__fecha_nacimiento = fecha
        self.__DNI_hash = hashlib.sha256(DNI.encode("utf-8")).hexdigest()
        self.__DNI_referencia = "***" + DNI[-2:]
        self.telefono = telefono

    @property
    def DNI(self):
        return self.__DNI_referencia

    @property
    def fecha_nacimiento(self):
        return self.__fecha_nacimiento.strftime("%d/%m/%Y")

    @property
    def edad(self):
        hoy = datetime.now()
        nac = self.__fecha_nacimiento
        return hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = valor.strip()
        if valor and not re.fullmatch(r"\d{6,15}", valor):
            raise ErrorValidacion("El teléfono debe tener entre 6 y 15 dígitos.")
        self.__telefono = valor

    def coincide_DNI(self, DNI):
        consulta = hashlib.sha256(DNI.strip().encode("utf-8")).hexdigest()
        return self.__DNI_hash == consulta
    @property
    def DNI_hash(self):
        return self.__DNI_hash

    def a_diccionario(self):
        return {
            "nombres": self.nombres,
            "apellidos": self.apellidos,
            "DNI_hash": self.__DNI_hash,
            "fecha_nacimiento": self.fecha_nacimiento,
            "telefono": self.telefono
        }

    @classmethod
    def desde_diccionario(cls, d):
        p = cls.__new__(cls)
        p.nombres = d["nombres"]
        p.apellidos = d["apellidos"]
        p.__DNI_hash = d["DNI_hash"]
        p.__DNI_referencia = d ["DNI_referencia"]
        p.__fecha_nacimiento = datetime.striptime(d["fecha_nacimiento"], "%d/%m/%Y")
        p.telefono = d["telefono"]
        return p

class Cita:
    def __init__(self, paciente, fecha, hora, especialidad):
        if not isinstance(paciente, Paciente):
            raise ErrorValidacion("Debe seleccionar un paciente válido.")

        hora_normalizada = hora.strip().replace("-", " ").upper()
        hora_normalizada = re.sub(r"\s+", " ", hora_normalizada)
        try:
            fecha_hora = datetime.strptime(
                fecha.strip() + " " + hora_normalizada, "%d/%m/%Y %I:%M %p"
            )
        except ValueError:
            raise ErrorValidacion(
                "Use fecha DD/MM/AAAA y hora HH:MM-AM o HH:MM-PM."
            )
        if fecha_hora < datetime.now():
            raise ErrorValidacion("La cita no puede programarse en el pasado.")
        if not especialidad.strip():
            raise ErrorValidacion("La especialidad es obligatoria.")

        self.__paciente = paciente
        self.__fecha_hora = fecha_hora
        self.__especialidad = especialidad.strip()
        self.__estado = "Programada"

    @property
    def paciente(self):
        return self.__paciente

    @property
    def fecha_hora(self):
        return self.__fecha_hora

    @property
    def especialidad(self):
        return self.__especialidad

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, valor):
        if valor not in ("Programada", "Atendida", "Cancelada"):
            raise ErrorValidacion("Estado de cita no válido.")
        self.__estado = valor

    def a_diccionario(self):
        return{
            "DNI_hash": self.__paciente.DNI_hash,
            "fecha_hora": self.__fecha_hora.striftime("%d/%m/%Y %H:%M"),
            "especialidad": self.__especialidad,
            "estado": self.__estado,
        }

    @classmethod
    def desde_diccionario(cls, d, paciente):
        c = cls.__new__(cls)
        c.__paciente = paciente
        c.__fecha_hora = datetime.strptime(d["fecha_hora"], "%d/%m/%Y %H:%M")
        c.__especialidad = d["especialidad"]
        c.__estado = d["estado"]
        return c

class Repositorio:
    _instancia = None
    ARCHIVO = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "datos_sistemarural.json"
    )

    def __new__(cls):
        if cls._instancia is None:
            cls._intancia = super().__new__(cls)
            cls.instancia.pacientes =[]
            cls.instancia.citas = []
        return cls._instancia

    def guardar(self):
        datos ={
            "pacientes": [p.a_diccionario() for p in self.pacientes],
            "citas": [c.a_diccionario( )for c in self.citas],
        }
        with open(self.ARCHIVO, "W", enconding="utf-8")as f:
                  json.dump(datos, f, ensure_ascii=False, indent=2)

    def cargar(self):
        if not os.path.exists(self.ARCHIVO):
            return
        with open(self.AECHIVO, "r", enconding="utf-8") as f:
            datos = json.load(f)
        self.pacientes.clear()
        self.citas.clear()
        for d in datos.get("pacientes", []):
            self.pacientes.append(Paciente.desde_diccionario(d))
        por_hash= {p.DNI_hash: p for p in self.pacientes}
        for d in datos.get("citas", []):
            paciente = por_hash.get(d["DNI_hash"])
            if paciente:
                self.citas.append(Cita.desde_diccionario(d, paciente))

class ServicioSalud:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def registrar_paciente(self, nombres, apellidos, DNI, fecha_nacimiento, telefono):
        if any(p.coincide_DNI(DNI) for p in self.repositorio.pacientes):
            raise ErrorValidacion("El paciente ya está registrado.")
        paciente = Paciente(nombres, apellidos, DNI, fecha_nacimiento, telefono)
        self.repositorio.pacientes.append(paciente)
        return paciente

    def registrar_cita(self, DNI, fecha, hora, especialidad):
        paciente = next(
            (p for p in self.repositorio.pacientes if p.coincide_DNI(DNI)), None
        )
        if paciente is None:
            raise ErrorValidacion("No se encontró al paciente.")
        cita = Cita(paciente, fecha, hora, especialidad)
        self.repositorio.citas.append(cita)
        return cita

    def buscar_pacientes(self, texto):
        texto = texto.lower().strip()
        return list(filter(
            lambda p: texto in p.nombre_completo().lower(),
            self.repositorio.pacientes
        ))

    def resumen_pacientes(self):
        return list(map(
            lambda p: (p.nombre_completo(), p.DNI, p.edad, p.telefono or "No registrado"),
            self.repositorio.pacientes
        ))

    def total_citas(self):
        return reduce(lambda total, cita: total + 1,
                      self.repositorio.citas, 0)

    def citas_programadas(self):
        return list(filter(
            lambda c: c.estado == "Programada",
            self.repositorio.citas
        ))

class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("SistemaRural-PE | Centro de Salud Santa Rosa")
        self.ventana.geometry("850x600")
        self.servicio = ServicioSalud(Repositorio())
        self._construir_interfaz()
        self.servicio.repositorio.cargar()
        self.actualizar_pacientes()
        self.actualizar_citas()
        self.actualizar_reporte()

    def _construir_interfaz(self):
        ttk.Label(
            self.ventana, text="SISTEMARURAL-PE",
            font=("Arial", 18, "bold")
        ).pack(pady=8)
        ttk.Label(
            self.ventana,
            text="Centro de Salud Rural Santa Rosa – Chugur, Cajamarca"
        ).pack()

        tabs = ttk.Notebook(self.ventana)
        tabs.pack(fill="both", expand=True, padx=12, pady=12)
        self.tab_pacientes = ttk.Frame(tabs, padding=10)
        self.tab_citas = ttk.Frame(tabs, padding=10)
        self.tab_reportes = ttk.Frame(tabs, padding=10)
        tabs.add(self.tab_pacientes, text="Pacientes")
        tabs.add(self.tab_citas, text="Citas")
        tabs.add(self.tab_reportes, text="Reportes")

        self._crear_pacientes()
        self._crear_citas()
        self._crear_reportes()

    def _crear_pacientes(self):
        marco = ttk.LabelFrame(
            self.tab_pacientes, text="Registrar paciente", padding=10
        )
        marco.pack(fill="x")
        self.nombres = tk.StringVar()
        self.apellidos = tk.StringVar()
        self.DNI = tk.StringVar()
        self.Fecha_de_nacimiento = tk.StringVar()
        self.telefono = tk.StringVar()

        for fila, (texto, variable) in enumerate([
            ("Nombres", self.nombres),
            ("Apellidos", self.apellidos),
            ("DNI", self.DNI),
            ("Fecha de Nacimiento", self.Fecha_de_nacimiento),
            ("Teléfono", self.telefono)
        ]):
            ttk.Label(marco, text=texto).grid(
                row=fila, column=0, sticky="w", padx=5, pady=4
            )
            ttk.Entry(marco, textvariable=variable).grid(
                row=fila, column=1, sticky="ew", padx=5, pady=4
            )
        marco.columnconfigure(1, weight=1)
        ttk.Button(
            marco, text="Registrar paciente",
            command=self.evento_registrar_paciente
        ).grid(row=5, column=0, columnspan=2, pady=8)

        busqueda = ttk.Frame(self.tab_pacientes)
        busqueda.pack(fill="x", pady=8)
        ttk.Label(busqueda, text="Buscar:").pack(side="left")
        self.busqueda = tk.StringVar()
        entrada = ttk.Entry(busqueda, textvariable=self.busqueda)
        entrada.pack(side="left", padx=6)
        entrada.bind("<KeyRelease>", self.evento_buscar)

        self.tabla_pacientes = ttk.Treeview(
            self.tab_pacientes,
            columns=("nombre", "DNI", "Fecha_nac", "edad", "telefono"),
            show="headings"
        )
        for col, titulo in [
            ("nombre", "Paciente"), ("DNI", "DNI"),
            ("Fecha_nac", "Fecha de Nacimiento"), ("edad", "Edad"),
            ("telefono", "Teléfono")
        ]:
            self.tabla_pacientes.heading(col, text=titulo)
        self.tabla_pacientes.column("edad", width=60, anchor="center")
        self.tabla_pacientes.pack(fill="both", expand=True)

    def _crear_citas(self):
        marco = ttk.LabelFrame(
            self.tab_citas, text="Programar cita médica", padding=10
        )
        marco.pack(fill="x")
        self.DNI_cita = tk.StringVar()
        self.fecha = tk.StringVar()
        self.hora = tk.StringVar(value="")
        self.especialidad = tk.StringVar()

        for fila, (texto, variable) in enumerate([
            ("DNI del paciente", self.DNI_cita),
            ("Fecha", self.fecha),
            ("Hora", self.hora),
            ("Especialidad", self.especialidad)
        ]):
            ttk.Label(marco, text=texto).grid(
                row=fila, column=0, sticky="w", padx=5, pady=4
            )
            ttk.Entry(marco, textvariable=variable).grid(
                row=fila, column=1, sticky="ew", padx=5, pady=4
            )
        marco.columnconfigure(1, weight=1)
        ttk.Button(
            marco, text="Registrar cita",
            command=self.evento_registrar_cita
        ).grid(row=4, column=0, columnspan=2, pady=8)

        self.tabla_citas = ttk.Treeview(
            self.tab_citas,
            columns=("fecha", "paciente", "edad", "especialidad", "estado"),
            show="headings"
        )
        for col, titulo in [
            ("fecha", "Fecha y hora"), ("paciente", "Paciente"),
            ("edad", "Edad"), ("especialidad", "Especialidad"), ("estado", "Estado")
        ]:
            self.tabla_citas.heading(col, text=titulo)
        self.tabla_citas.column("edad", width=60, anchor="center")
        self.tabla_citas.pack(fill="both", expand=True, pady=10)

    def _crear_reportes(self):
        ttk.Label(
            self.tab_reportes, text="Resumen de atención",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", pady=8)
        self.reporte = ttk.Label(self.tab_reportes, text="", justify="left")
        self.reporte.pack(anchor="w", pady=8)
        ttk.Button(
            self.tab_reportes, text="Actualizar reporte",
            command=self.actualizar_reporte
        ).pack(anchor="w")
        self.actualizar_reporte()

    def evento_registrar_paciente(self):
        try:
            self.servicio.registrar_paciente(
                self.nombres.get(),
                self.apellidos.get(),
                self.DNI.get(),
                self.Fecha_de_nacimiento.get(),
                self.telefono.get(),
                self.servicio.repositorio.guardar()
            )
            messagebox.showinfo("Correcto", "Paciente registrado.")
            for variable in (
                self.nombres, self.apellidos, self.DNI,
                self.Fecha_de_nacimiento, self.telefono
            ):
                variable.set("")
            self.busqueda.set("")
            self.actualizar_pacientes()
            self.actualizar_reporte()
        except ErrorValidacion as error:
            messagebox.showwarning("Validación", str(error))
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def evento_registrar_cita(self):
        try:
            self.servicio.registrar_cita(
                self.DNI_cita.get(), self.fecha.get(),
                self.hora.get(), self.especialidad.get(),
                self.servicio.repositorio.guardar()
            )
            messagebox.showinfo("Correcto", "Cita registrada.")
            for variable in (
                self.DNI_cita, self.fecha, self.hora, self.especialidad
            ):
                variable.set("")
            self.actualizar_citas()
            self.actualizar_reporte()
        except ErrorValidacion as error:
            messagebox.showwarning("Validación", str(error))
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def evento_buscar(self, evento=None):
        pacientes = self.servicio.buscar_pacientes(self.busqueda.get())
        self.actualizar_pacientes(pacientes)

    def actualizar_pacientes(self, pacientes=None):
        for item in self.tabla_pacientes.get_children():
            self.tabla_pacientes.delete(item)
        if pacientes is None:
            pacientes = self.servicio.repositorio.pacientes
        for p in pacientes:
            self.tabla_pacientes.insert(
                "", "end",
                values=(p.nombre_completo(),
                        p.DNI,
                        p.fecha_nacimiento,
                        f"{p.edad} años",
                        p.telefono or "No registrado")
            )

    def actualizar_citas(self):
        for item in self.tabla_citas.get_children():
            self.tabla_citas.delete(item)
        for c in self.servicio.repositorio.citas:
            self.tabla_citas.insert(
                "", "end",
                values=(c.fecha_hora.strftime("%d/%m/%Y %I:%M %p"),
                        c.paciente.nombre_completo(),
                        f"{c.paciente.edad} años",
                        c.especialidad, c.estado)
            )

    def actualizar_reporte(self):
        citas = self.servicio.repositorio.citas
        atendidas = sum(1 for c in citas if c.estado == "Atendida")
        self.reporte.config(text=(
            f"Pacientes registrados: {len(self.servicio.repositorio.pacientes)}\n"
            f"Total de citas: {self.servicio.total_citas()}\n"
            f"Citas programadas: {len(self.servicio.citas_programadas())}\n"
            f"Citas atendidas: {atendidas}\n\n"
            "AGENDA DE CITAS MEDICAS"
        ))
class PruebasSistemaRural(unittest.TestCase):
    def setUp(self):
        self.repo = Repositorio()
        self.repo.pacientes.clear()
        self.repo.citas.clear()
        self.servicio = ServicioSalud(self.repo)

    def registrar(self, nombre="Ana", DNI="12345678", fecha="01/01/1990"):
        return self.servicio.registrar_paciente(
            nombre, "Pérez", DNI, fecha, "987654321"
        )

    def test_registro_paciente(self):
        p = self.registrar()
        self.assertEqual(p.nombre_completo(), "Ana Pérez")
        self.assertTrue(p.coincide_DNI("12345678"))
        self.assertEqual(p.fecha_nacimiento, "01/01/1990")

    def test_DNI_no_expuesto(self):
        p = self.registrar(DNI="87654321")
        self.assertNotEqual(p.DNI, "87654321")
        self.assertTrue(p.coincide_DNI("87654321"))

    def test_busqueda_filter(self):
        self.registrar(nombre="María")
        self.assertEqual(len(self.servicio.buscar_pacientes("maría")), 1)

    def test_datos_invalidos(self):
        for DNI, fecha in [("123", "07/07/1980"), ("12345678", "45/13/2020")]:
            with self.assertRaises(ErrorValidacion):
                self.registrar(DNI=DNI, fecha=fecha)

    def test_paciente_duplicado(self):
        self.registrar()
        with self.assertRaises(ErrorValidacion):
            self.registrar()

    def test_cita_valida_y_pasada(self):
        self.registrar()
        cita = self.servicio.registrar_cita(
            "12345678", "01/01/2099", "09:30-AM", "Medicina General"
        )
        self.assertEqual(cita.estado, "Programada")
        self.assertEqual(self.servicio.total_citas(), 1)
        with self.assertRaises(ErrorValidacion):
            self.servicio.registrar_cita(
                "12345678", "01/01/2000", "09:30-AM", "Medicina General"
            )

    def test_edad(self):
        hoy = datetime.now()
        esperado = hoy.year - 1990 - ((hoy.month, hoy.day) < (1, 1))
        self.assertEqual(self.registrar().edad, esperado)
if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    else:
        root = tk.Tk()
        app = Aplicacion(root)
        root.mainloop()