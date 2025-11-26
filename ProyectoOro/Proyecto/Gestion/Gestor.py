import datetime
from decimal import Decimal

import pandas as pd
from faker import Faker
from sqlalchemy import func, desc, text
from matplotlib import pyplot as plt

from Proyecto.DB.Models.Model import clientes, ventas, tasaciones, estado, precios_del_oro
from Proyecto.DB.config import Session, session
import logging

# Configuración del LOG
logging.basicConfig(
    filename='C:\\Users\\jose-\\PycharmProjects\\ProyectoOro\\Proyecto\\Log\\actividad.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def registrar_actividad(func):
    def wrapper(self, *args, **kwargs):
        dni = None
        # Si el usuario pasa un DNI lo registramos
        if args:
            for arg in args:
                if isinstance(arg, str) and len(arg) >= 8:
                    dni = arg

        resultado = func(self, *args, **kwargs)

        mensaje = f"Funcion ejecutada: {func.__name__}"
        if dni:
            mensaje += f" | DNI: {dni}"

        logging.info(mensaje)
        return resultado

    return wrapper


class Gestor:
    fake = Faker("es_ES")

    def __init__(self):
        self.session = Session()

    @registrar_actividad
    # -------------------------------------------------------------
    # 1️⃣ INTRODUCIR UN CLIENTE NUEVO
    #    Solicita los datos por consola, valida la fecha y guarda
    #    el cliente en la base de datos.
    # -------------------------------------------------------------
    @registrar_actividad
    def insertar_Cliente(self):
        # ---- DNI (no duplicado) ----
        while True:
            dni_cliente = input("Dime el DNI del cliente: ").strip()

            if not dni_cliente:
                print("❌ El DNI no puede estar vacío.")
                continue

            # Comprobar si ya existe en la BBDD
            existe = (
                self.session.query(clientes)
                .filter(clientes.dni == dni_cliente)
                .first()
            )
            if existe:
                print(f"❌ Ya existe un cliente con el DNI {dni_cliente}.")
                # Puedes elegir aquí: o return, o volver a pedir DNI
                volver = input("¿Quieres introducir otro DNI? (s/n): ").strip().lower()
                if volver == "s":
                    continue
                else:
                    return
            break

        # ---- Nombre ----
        while True:
            nombre_cliente = input("Dime el nombre del cliente: ").strip()
            if not nombre_cliente:
                print("❌ El nombre no puede estar vacío.")
            else:
                break

        # ---- Apellidos ----
        while True:
            apellidos_cliente = input("Dime los apellidos del cliente: ").strip()
            if not apellidos_cliente:
                print("❌ Los apellidos no pueden estar vacíos.")
            else:
                break

        # ---- Fecha de nacimiento (validación inmediata) ----
        while True:
            fecha_nacimiento_Cliente = input("Dime la fecha de nacimiento (YYYY-MM-DD): ").strip()
            try:
                fecha_nac = datetime.datetime.strptime(fecha_nacimiento_Cliente, "%Y-%m-%d").date()
                break
            except ValueError:
                print("❌ Formato de fecha inválido. Debe ser YYYY-MM-DD (ejemplo: 1990-05-21).")

        # ---- Email ----
        while True:
            email_cliente = input("Dime el email del cliente: ").strip()
            if "@" not in email_cliente or "." not in email_cliente:
                print("❌ Email no válido.")
            else:
                break

        # ---- Nacionalidad ----
        nacionalidad_cliente = input("Dime la nacionalidad del cliente: ").strip()

        # ---- Teléfono ----
        while True:
            telefono_cliente = input("Dime el teléfono del cliente (solo números): ").strip()
            if not telefono_cliente.isdigit():
                print("❌ El teléfono debe contener solo números.")
            elif len(telefono_cliente) < 9:
                print("❌ El teléfono debe tener al menos 9 dígitos.")
            else:
                break

        # ---- Dirección ----
        direccion_cliente = input("Dime la dirección del cliente: ").strip()

        # Crear objeto cliente
        cliente = clientes(
            dni=dni_cliente,
            nombre=nombre_cliente,
            apellidos=apellidos_cliente,
            fecha_nacimiento=fecha_nac,
            email=email_cliente,
            nacionalidad=nacionalidad_cliente,
            telefono=telefono_cliente,
            direccion=direccion_cliente
        )

        self.session.add(cliente)
        self.session.commit()
        print("✅ Se ha guardado el cliente correctamente.")

    # -------------------------------------------------------------
    # 2️⃣ VENTAS REALIZADAS EN UN MES
    #    Recibe un número de mes y devuelve todas las ventas cuya
    #    fecha_venta coincide con ese mes.
    # -------------------------------------------------------------
    @registrar_actividad
    def ventas_realizadas_en_un_mes(self, mes):
        meses = ["ENERO", "FEBRERO", "MARZO",
                 "ABRIL", "MAYO", "JUNIO",
                 "JULIO", "AGOSTO", "SEPTIEMBRE",
                 "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]

        todas_las_ventas = (
            self.session.query(ventas)
            .filter(func.extract('month', ventas.fecha_venta) == mes)
            .all()
        )

        for venta in todas_las_ventas:
            print(venta)

    # -------------------------------------------------------------
    # 3️⃣ VENTAS REALIZADAS POR UN CLIENTE
    #    Devuelve todas las ventas cuyo DNI coincide con el dado.
    # -------------------------------------------------------------
    @registrar_actividad
    def ventas_realizadas_por_un_cliente(self, cliente_Dni):
        ventas_de_un_cliente = (
            self.session.query(ventas)
            .join(tasaciones, tasaciones.id == ventas.tasacion_id)
            .join(clientes, clientes.dni == tasaciones.cliente_id)
            .filter(clientes.dni == cliente_Dni)
            .all()
        )

        for venta in ventas_de_un_cliente:
            print(venta)

    # -------------------------------------------------------------
    # 4️⃣ TASACIONES NO ACEPTADAS
    #    Muestra todas las tasaciones cuyo estado NO sea 'ACEPTADA'.
    # -------------------------------------------------------------
    @registrar_actividad
    def tasaciones_no_aceptas(self):
        tasaciones_negativas = (
            self.session.query(tasaciones)
            .join(estado, tasaciones.estado == estado.id_estado)
            .filter(estado.estado != 'ACEPTADA')
            .all()
        )

        for tasacion in tasaciones_negativas:
            print(tasacion)

    # -------------------------------------------------------------
    # 5️⃣ CLIENTE CON MÁS VENTAS
    #    Calcula el cliente que más ventas tiene mediante un COUNT.
    # -------------------------------------------------------------
    @registrar_actividad
    def cliente_con_mas_venta(self):
        cliente_MAX = (
            self.session.query(
                clientes.nombre,
                func.count(ventas.id_venta_realizada).label("total_ventas")
            )
            .join(tasaciones, clientes.dni == tasaciones.cliente_id)
            .join(ventas, tasaciones.id == ventas.tasacion_id)
            .group_by(clientes.nombre)
            .order_by(desc("total_ventas"))
            .first()
        )
        print(cliente_MAX)

    # -------------------------------------------------------------
    # 6️⃣ CLIENTES CON 3 MESES SIN VENTAS
    #    → Calcula la fecha de hace 3 meses
    #    → Busca clientes cuyas ventas son anteriores a esa fecha
    # -------------------------------------------------------------
    @registrar_actividad
    def clientes_con_3_meses_sin_ventas(self):
        fecha_limite = func.current_date() - text("INTERVAL '3 months'")

        clientes_sin_ventas = (
            self.session.query(clientes.nombre)
            .join(tasaciones, clientes.dni == tasaciones.cliente_id)
            .join(ventas, tasaciones.id == ventas.tasacion_id)
            .filter(ventas.fecha_venta <= fecha_limite)
            .all()
        )

        for cliente in clientes_sin_ventas:
            print(cliente)

    # -------------------------------------------------------------
    # 7️⃣ GRÁFICO: CANTIDAD DE ORO VENDIDA POR CLIENTE
    #    Muestra un gráfico de barras con cuántas ventas hizo cada
    #    cliente. Muestra etiquetas encima de cada barra.
    # -------------------------------------------------------------
    @registrar_actividad
    def graficoCantidadOroVendidaPorCliente(self):

        consulta = self.session.query(
            clientes.nombre.label("Nombre"),
            func.count(ventas.id_venta_realizada).label("Numero_Ventas")
        ).join(
            tasaciones, tasaciones.cliente_id == clientes.dni
        ).join(
            ventas, ventas.tasacion_id == tasaciones.id  # <-- así
        ).group_by(clientes.dni)

        resultados = consulta.all()

        if not resultados:
            print("No se han encontrado ventas asociadas a ninguna tasación")
            return

        df = pd.DataFrame(resultados, columns=["nombre", "Numero_Ventas"])

        plt.figure(figsize=(10, 6))
        barras = plt.bar(df["nombre"], df["Numero_Ventas"], color="#3498db")

        for barra in barras:
            y = barra.get_height()
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                y + 0.1,
                int(y),
                ha='center',
                va='bottom',
                fontsize=10
            )

        plt.title("Número De Ventas", fontsize=14, fontweight='bold')
        plt.xlabel("Nombre del Cliente")
        plt.ylabel("Cantidad de Ventas")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    # -------------------------------------------------------------
    # 8️⃣ TOTAL DE VENTAS POR MES (INCLUYENDO MESES SIN VENTAS)
    #    → Obtiene ventas por mes real
    #    → Crea un dataframe con los 12 meses
    #    → Une ambos y pone 0 en meses sin ventas
    #    → Grafica el resultado
    # -------------------------------------------------------------
    @registrar_actividad
    def totalVentasPorMes(self):

        consultaMeses = self.session.query(
            func.extract("month", ventas.fecha_venta).label("mes"),
            func.count(ventas.id_venta_realizada).label("numero_ventas")
        ).group_by(func.extract("month", ventas.fecha_venta))

        resultados = consultaMeses.all()

        df = pd.DataFrame(resultados, columns=["mes", "numero_ventas"])

        meses_completos = pd.DataFrame({
            "mes": range(1, 13),
            "nombre_mes": [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]
        })

        df_completo = meses_completos.merge(df, on="mes", how="left")
        df_completo["numero_ventas"] = df_completo["numero_ventas"].fillna(0).astype(int)

        print(df_completo)

        plt.figure(figsize=(12, 6))
        barras = plt.bar(df_completo["nombre_mes"], df_completo["numero_ventas"], color="#3498db")

        for barra in barras:
            y = barra.get_height()
            plt.text(
                barra.get_x() + barra.get_width() / 2,
                y + 0.2,
                int(y),
                ha='center',
                va='bottom',
                fontsize=10
            )

        plt.title("Número de Ventas por Mes")
        plt.xlabel("Mes")
        plt.ylabel("Cantidad de Ventas")
        plt.xticks(rotation=45)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    # -------------------------------------------------------------
    #  9️⃣ Generar Una venta En base a un cliente especifico
    #    → Generar una Tasacion
    #    → Indicar el estado de esa tasacion
    #    → Si es aceptada pasarla a la tabla ventas
    #    → Indicando el cliente y reciviendo si no existe indicarlo
    # -------------------------------------------------------------
    def crear_venta_por_tasacion(self):
        tasacione = tasaciones()
        # 1. Mostrar todos los clientes de la base de datos
        print("\nLista de clientes registrados:\n")
        todos_clientes = session.query(clientes).all()

        if not todos_clientes:
            print("No hay clientes registrados en la base de datos.")
        else:
            for c in todos_clientes:
                print(f"DNI: {c.dni} | Nombre: {c.nombre} {c.apellidos}")

        print("\n---------------------------------------------")

        # 2. Pedir DNI
        dni = input("Introduce el DNI del cliente para la venta/tasación: ").strip()
        cliente = session.query(clientes).filter_by(dni=dni).first()

        # 3. Si NO existe el cliente
        if not cliente:
            print(f"No existe un cliente con DNI {dni}.")
            print("¿Qué deseas hacer?")
            print("  1. Registrar nuevo cliente y continuar")
            print("  2. Salir")

            opcion = input("Selecciona 1 o 2: ").strip()

            if opcion == "1":
                print("Registrando nuevo cliente...")
                self.insertar_Cliente()  # tu método ya existente

                # buscarlo de nuevo tras registrarlo
                cliente = session.query(clientes).filter_by(dni=dni).first()

                if not cliente:
                    print("El cliente no fue registrado correctamente.")
                    return

                print(f"Cliente registrado correctamente. Continuando el proceso para DNI {dni}...\n")

            else:
                print("Operación cancelada. Volviendo al menú.")
                return

        # si llega aquí, cliente existe y sigues tu flujo actual

        # Obtener ID del estado "ACEPTADA" y "PENDIENTE"
        id_aceptada = session.query(estado.id_estado).filter_by(estado="ACEPTADA").scalar()
        id_pendiente = session.query(estado.id_estado).filter_by(estado="PENDIENTE").scalar()
        id_rechazado = session.query(estado.id_estado).filter_by(estado="RECHAZADO").scalar()
        fecha_actual = datetime.date.today()
        # Tasaciones disponibles para ese cliente (incluyendo PENDIENTES y ACEPTADAS/Intentos)
        # Filtramos por cliente_id y aquellas que AUN NO tienen una venta asociada.
        precios_disponibles = (
            session.query(precios_del_oro)
            .filter(precios_del_oro.fecha == fecha_actual)
            .all()
        )

        if not precios_disponibles:
            print("❌ No hay tasaciones/intentos de venta disponibles para este cliente.")
            return
        # -------------------------------------------------------------------
        # 🎯 LÓGICA: Obtener el precio del oro EXACTO de la fecha de hoy (tabla precio_oro)
        # -------------------------------------------------------------------
        precio_kg_tasacion = (
            session.query(precios_del_oro.precio_kg)
            .filter(precios_del_oro.fecha == fecha_actual)
            .scalar()
        )

        if precio_kg_tasacion:
            print(f"\nPrecio del oro usado (Fecha: {fecha_actual}): {precio_kg_tasacion} €/kg")
        else:
            print(f"\n No tengo tasaciones para Para el dia de hoy ")
        # Pedir peso
        while True:
            try:
                peso = Decimal(input(f"Introduce el peso en gramos"))
                if 0 < peso:
                    break
                else:
                    print("❌ Peso inválido.")
            except:
                print("❌ Debes introducir un número válido.")

        # Calcular importe total
        importe_total = (peso * precio_kg_tasacion / 1000).quantize(Decimal("0.01"))

        print(f"\nImporte total calculado: {importe_total} €")
        respuesta = input("¿Desea **ACEPTAR** y registrar esta venta final (S/N)? ").strip().upper()
        # 1. Actualizar el estado de la tasación a ACEPTADA
        tasacione.precio_oro_id = (
            session.query(precios_del_oro.id_oro)
            .filter(precios_del_oro.fecha == fecha_actual)
            .scalar()
        )

        tasacione.fecha_tasacion = fecha_actual
        tasacione.peso_oro_gramos = peso
        tasacione.cliente_id = dni
        tasacione.estado = id_aceptada

        if respuesta == 'S':
            # 1. Actualizar el estado de la tasación a ACEPTADA
            tasacione.estado = id_aceptada

            session.add(tasacione)
            session.commit()

            # 2. Crear venta final aceptada
            nueva_venta = ventas(
                tasacion_id=tasacione.id,
                fecha_venta=fecha_actual,
                importe_total=importe_total
            )
            session.add(nueva_venta)
            session.commit()

            print(f"✅ Venta registrada y aceptada con éxito. Importe total: {importe_total} €")

        else:
            print("\nLa venta NO ha sido aceptada.")
            print("¿Qué deseas hacer con la tasación?")
            print("  R = Rechazar la tasación")
            print("  P = Mantenerla como PENDIENTE")
            print("  (No se generará ninguna venta)")

            decision = input("Selecciona R o P: ").strip().upper()

            if decision == "R":
                tasacione.estado = id_rechazado
                session.add(tasacione)

                session.commit()
                print(f"❌ Tasación marcada como RECHAZADA (ID: {tasacione.id}).")

            elif decision == "P":
                tasacione.estado = id_pendiente
                session.add(tasacione)

                session.commit()
                print(f"⏳ Tasación marcada como PENDIENTE (ID: {tasacione.id}).")

            else:
                print("⚠ Opción no válida. No se realizaron cambios.")
