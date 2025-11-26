from faker import Faker
from datetime import date, timedelta
from decimal import Decimal
import random
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from Proyecto.DB.config import session
from Proyecto.DB.Models.Model import clientes, precios_del_oro, tasaciones, ventas, estado


class FactoriaDatos:
    # -------------------------------------------------------------
    # TASACIONES INICIALES (solo si la tabla está vacía)
    # -------------------------------------------------------------
    def generar_tasaciones_iniciales(self, clientes_list):
        print("\n3. Generando tasaciones iniciales (450 registros)...")

        id_aceptada = session.query(estado.id_estado).filter_by(estado="ACEPTADA").scalar()
        id_rechazada = session.query(estado.id_estado).filter_by(estado="RECHAZADO").scalar()
        id_pendiente = session.query(estado.id_estado).filter_by(estado="PENDIENTE").scalar()

        precios_list = session.query(precios_del_oro).all()

        # 400 aceptadas
        for _ in range(400):
            p = random.choice(precios_list)
            session.add(tasaciones(
                cliente_id=random.choice(clientes_list).dni,
                precio_oro_id=p.id_oro,
                peso_oro_gramos=Decimal(random.uniform(5, 200)).quantize(Decimal("0.01")),
                fecha_tasacion=p.fecha,
                estado=id_aceptada
            ))

        # 30 rechazadas
        for _ in range(30):
            p = random.choice(precios_list)
            session.add(tasaciones(
                cliente_id=random.choice(clientes_list).dni,
                precio_oro_id=p.id_oro,
                peso_oro_gramos=Decimal(random.uniform(5, 200)).quantize(Decimal("0.01")),
                fecha_tasacion=p.fecha,
                estado=id_rechazada
            ))

        # 20 pendientes
        for _ in range(20):
            p = random.choice(precios_list)
            session.add(tasaciones(
                cliente_id=random.choice(clientes_list).dni,
                precio_oro_id=p.id_oro,
                peso_oro_gramos=Decimal(random.uniform(5, 200)).quantize(Decimal("0.01")),
                fecha_tasacion=p.fecha,
                estado=id_pendiente
            ))

        session.commit()
        print("   -> 450 tasaciones iniciales generadas.")

    # -------------------------------------------------------------
    # TASACIONES INCREMENTALES (solo si YA existen tasaciones)
    # -------------------------------------------------------------
    def generar_tasaciones_incrementales(self):
        print("\n3. Generando tasaciones nuevas (incremental)...")

        id_aceptada = session.query(estado.id_estado).filter_by(estado="ACEPTADA").scalar()
        id_rechazada = session.query(estado.id_estado).filter_by(estado="RECHAZADO").scalar()
        id_pendiente = session.query(estado.id_estado).filter_by(estado="PENDIENTE").scalar()

        last_tas_date = session.query(func.max(tasaciones.fecha_tasacion)).scalar()
        today = date.today()

        if not last_tas_date:
            print("   -> ERROR: No existen tasaciones para continuar.")
            return

        print(f"   -> Continuando desde {last_tas_date}")

        dias = (today - last_tas_date).days
        if dias <= 0:
            print("   -> Tabla ya actualizada. No hay tasaciones nuevas.")
            return

        precios_list = session.query(precios_del_oro).all()
        clientes_list = session.query(clientes).all()

        total_generadas = 0

        # Generamos 10 tasaciones por día
        for i in range(dias):
            fecha_actual = last_tas_date + timedelta(days=i + 1)

            for _ in range(10):
                p = random.choice(precios_list)
                estado_escogido = random.choice([id_aceptada, id_rechazada, id_pendiente])

                session.add(tasaciones(
                    cliente_id=random.choice(clientes_list).dni,
                    precio_oro_id=p.id_oro,
                    peso_oro_gramos=Decimal(random.uniform(5, 200)).quantize(Decimal("0.01")),
                    fecha_tasacion=fecha_actual,
                    estado=estado_escogido
                ))
                total_generadas += 1

        session.commit()
        print(f"   -> {total_generadas} tasaciones nuevas generadas.")

    def __init__(self):
        self.fake = Faker("es_ES")

    # -------------------------------------------------------------
    # FUNCIONES DE AYUDA
    # -------------------------------------------------------------
    def is_table_empty(self, model):
        return session.query(model).count() == 0

    def get_last_gold_price(self):
        return session.query(func.max(precios_del_oro.fecha)).scalar()

    # -------------------------------------------------------------
    # MÉTODO PRINCIPAL
    # -------------------------------------------------------------
    def ejecutar(self):
        print("\n========== INICIANDO CARGA INICIAL ==========\n")

        # ---------------------------------------------------------
        # 1) CLIENTES
        # ---------------------------------------------------------
        print("1. Generando clientes...")

        letras_dni = "TRWAGMYFPDXBNJZSQVHLCKE"

        if self.is_table_empty(clientes):
            clientes_list = []
            for _ in range(20):
                # Generar DNI numérico
                numero_dni = random.randint(10000000, 99999999)
                letra_dni = letras_dni[numero_dni % 23]
                dni = str(numero_dni)  # Guardamos solo el número en la base de datos

                c = clientes(
                    dni=dni,
                    nombre=self.fake.first_name(),
                    apellidos=self.fake.last_name(),
                    fecha_nacimiento=self.fake.date_of_birth(minimum_age=18, maximum_age=80),
                    email=self.fake.email(),
                    nacionalidad=self.fake.country(),
                    telefono=self.fake.random_number(digits=9, fix_len=True),
                    direccion=self.fake.address()
                )
                session.add(c)
                clientes_list.append(c)

                # Mostrar DNI completo con letra
                print(f"Cliente generado: {c.nombre} {c.apellidos} | DNI: {dni}{letra_dni}")

            session.commit()
            print("   -> 20 clientes creados.")
        else:
            clientes_list = session.query(clientes).all()
            print(f"   -> Tabla ya poblada: {len(clientes_list)} clientes cargados.")

            # Mostrar clientes existentes con letra calculada
            for c in clientes_list:
                numero_dni = int(c.dni)
                letra_dni = letras_dni[numero_dni % 23]
                print(f"DNI completo: {c.dni}{letra_dni} | Nombre: {c.nombre} {c.apellidos}")

        # ---------------------------------------------------------
        # 2) PRECIOS DEL ORO
        # ---------------------------------------------------------
        print("\n2. Generando precios del oro...")

        fecha_inicio = date(2025, 1, 1)
        fecha_hoy = date.today()

        last_date = self.get_last_gold_price()

        if last_date:
            fecha_inicio = last_date + timedelta(days=1)
            print(f"   -> Continuando desde {last_date}")
        else:
            print("   -> Generando histórico completo desde 1 enero 2025")

        precio_actual = Decimal("113002.00")


        dias = (fecha_hoy - fecha_inicio).days + 1
        contador = 0

        for i in range(dias):
            fecha = fecha_inicio + timedelta(days=i)

            cambio = random.uniform(0.01, 0.03)  # 1% a 3%

            # aleatorio si sube o baja
            if random.choice([True, False]):
                variacion_pct = Decimal(cambio)
            else:
                variacion_pct = Decimal(-cambio)
            precio_actual = max(Decimal("40.00"), precio_actual * (1 + variacion_pct))

            registro = precios_del_oro(
                fecha=fecha,
                precio_kg=precio_actual.quantize(Decimal("0.01"))
            )
            session.add(registro)
            contador += 1

        session.commit()
        print(f"   -> {contador} precios generados.")
        if self.is_table_empty(tasaciones):
            self.generar_tasaciones_iniciales(clientes_list)
        else:
            self.generar_tasaciones_incrementales()
            if self.is_table_empty(tasaciones):
                self.generar_tasaciones_iniciales(clientes_list)
            else:
                self.generar_tasaciones_incrementales()

            # ---------------------------------------------------------
            # 4) VENTAS
            # ---------------------------------------------------------
            print("\n4. Generando ventas...")

            id_aceptada = session.query(estado.id_estado).filter_by(estado="ACEPTADA").scalar()

            tasaciones_aceptadas = session.query(tasaciones) \
                .options(joinedload(tasaciones.precio_oro)) \
                .filter(tasaciones.estado == id_aceptada) \
                .filter(~tasaciones.venta.has()) \
                .all()

            ventas_count = 0

            for t in tasaciones_aceptadas:
                importe_total = (t.peso_oro_gramos * t.precio_oro.precio_kg / 1000).quantize(Decimal("0.01"))
                session.add(ventas(
                    tasacion_id=t.id,
                    fecha_venta=t.fecha_tasacion,
                    importe_total=importe_total
                ))
                ventas_count += 1

            session.commit()
            print(f"   -> {ventas_count} ventas creadas.")

        print("\n========== CARGA INICIAL COMPLETADA ==========\n")
