from faker import Faker as fk
from Proyecto.config import session

from datetime import date, timedelta
import random
from decimal import Decimal
from sqlalchemy.orm import joinedload
from sqlalchemy import func

# Importar tus clases
from Model import clientes, precios_del_oro, tasaciones, ventas, estado

# Inicializar Faker
fake = fk('es_ES')


# --- Funcones de Ayuda para Comprobación de Estado ---

def is_table_empty(model):
    """Verifica si la tabla asociada al modelo está vacía."""
    # Usamos el alias de la tabla en el esquema 'proyecto'
    # La comprobación se hace sobre el número total de registros.
    return session.query(model).count() == 0


def get_latest_gold_price_date():
    """Obtiene la fecha más reciente registrada en la tabla precios_del_oro."""
    latest_date = session.query(func.max(precios_del_oro.fecha)).scalar()
    return latest_date if latest_date else date(2025, 1, 1)  # Retorna fecha de inicio si está vacía


# ==================================
#  ✅ Lógica de Verificación y Creación
# ==================================

# 1️⃣ Generar Clientes (Solo si la tabla está vacía)
# ----------------------------------------------------
print("1. Verificando y Generando Clientes...")
if is_table_empty(clientes):
    clientes_list = []
    for _ in range(20):
        # Asegurarse de que el DNI es una cadena única
        try:
            dni_val = str(fake.unique.random_int(min=10000000, max=99999999))
        except Exception:
            # En caso de que se acaben los únicos (aunque poco probable con 20)
            dni_val = str(fake.random_int(min=10000000, max=99999999))

        c = clientes(
            dni=dni_val,
            nombre=fake.first_name(),
            apellidos=fake.last_name(),
            fecha_nacimiento=fake.date_of_birth(minimum_age=18, maximum_age=80),
            email=fake.email(),
            nacionalidad=fake.country(),
            telefono=fake.random_number(digits=9, fix_len=True),
            direccion=fake.address()
        )
        clientes_list.append(c)
        session.add(c)

    session.commit()
    print(f"   -> {len(clientes_list)} clientes creados.")
else:
    # Cargar los clientes existentes para usarlos en tasaciones
    clientes_list = session.query(clientes).all()
    print(f"   -> Tabla 'clientes' ya poblada. {len(clientes_list)} clientes cargados.")

# 2️⃣ Generar precios diarios del oro (Histórico o solo Hoy)
# -----------------------------------------------------------
print("2. Verificando y Generando Precios del Oro...")
fecha_hoy = date.today()
latest_date = get_latest_gold_price_date()
precios_oro_list = []
precios_nuevos_count = 0

if is_table_empty(precios_del_oro):
    print("   -> Tabla 'precios_oro' vacía. Generando histórico completo...")
    fecha_inicio = latest_date
    precio_actual = Decimal("50.00")
else:
    print(f"   -> Último precio registrado: {latest_date}. Generando precios desde esa fecha.")
    fecha_inicio = latest_date + timedelta(days=1)

    # Intentar obtener el último precio si no está vacío para simular continuidad
    last_price_record = session.query(precios_del_oro).order_by(precios_del_oro.fecha.desc()).first()
    precio_actual = last_price_record.precio_kg / 1000 if last_price_record else Decimal("50.00")

# Si la fecha de inicio es anterior o igual a hoy, generamos datos
if fecha_inicio <= fecha_hoy:
    dias = (fecha_hoy - fecha_inicio).days + 1

    for i in range(dias):
        fecha = fecha_inicio + timedelta(days=i)

        # Simular ligera variación diaria
        variacion = Decimal(random.uniform(-0.5, 0.5))
        precio_actual = max(Decimal("45.00"), precio_actual + variacion)

        precio = precios_del_oro(
            fecha=fecha,
            # Guardamos el precio en kg (50 * 1000)
            precio_kg=precio_actual * 1000
        )
        precios_oro_list.append(precio)
        session.add(precio)
        precios_nuevos_count += 1

    session.commit()
    print(f"   -> {precios_nuevos_count} precios diarios creados (hasta hoy).")
else:
    print("   -> La tabla de precios ya está actualizada hasta hoy.")

# 3️⃣ Generar Tasaciones (Independientemente si la tabla ya tiene datos)
# ---------------------------------------------------------------------
# Es mejor cargar los precios y estados existentes para evitar errores.
print("3. Generando Tasaciones...")

# Cargar IDs de precios y clientes (necesarios para las FK)
precios_oro_ids = session.query(precios_del_oro.id_oro).all()
precios_oro_ids = [id_[0] for id_ in precios_oro_ids]

# Cargar la lista completa de objetos precios_del_oro para obtener las fechas
all_precios_oro = session.query(precios_del_oro).all()

# Crear un diccionario para mapear id_oro a su objeto para fácil acceso
precio_oro_map = {p.id_oro: p for p in all_precios_oro}

# Obtener IDs de estado
estado_aceptado_id = session.query(estado.id_estado).filter(estado.estado == "ACEPTADA").scalar()
estado_rechazado_id = session.query(estado.id_estado).filter(estado.estado == "RECHAZADA").scalar()
estado_pendiente_id = session.query(estado.id_estado).filter(estado.estado == "PENDIENTE").scalar()

if not all_precios_oro or not clientes_list or not estado_aceptado_id:
    print("   -> ERROR: No hay suficientes datos base (clientes, precios_oro, o estados) para generar tasaciones.")
    # SALIR O CONTINUAR, dependiendo de la tolerancia a errores
else:
    tasaciones_list = []
    num_tasaciones_a_crear = 350  # Ejemplo de total a crear

    for i in range(num_tasaciones_a_crear):
        cliente = random.choice(clientes_list)
        # Seleccionar un ID de precio de oro y luego obtener el objeto
        precio_oro_id = random.choice(precios_oro_ids)
        precio_oro = precio_oro_map[precio_oro_id]

        peso_oro = Decimal(random.uniform(5, 200)).quantize(Decimal('0.01'))

        # Asignar estados de forma ponderada
        if i < 300:  # 300 ACEPTADAS
            estado_id = estado_aceptado_id
        elif i < 330:  # 30 RECHAZADAS
            estado_id = estado_rechazado_id
        else:  # 20 PENDIENTES
            estado_id = estado_pendiente_id

        tasacion = tasaciones(
            cliente_id=cliente.dni,
            precio_oro_id=precio_oro_id,
            peso_oro_gramos=peso_oro,
            fecha_tasacion=precio_oro.fecha,  # La fecha de tasación es la fecha del precio del oro
            estado=estado_id
        )
        tasaciones_list.append(tasacion)
        session.add(tasacion)

    session.commit()
    print(f"   -> {len(tasaciones_list)} tasaciones creadas.")

# 4️⃣ Generar Ventas solo para tasaciones ACEPTADAS
# ----------------------------------------------------
# Nota: Si se corre este script varias veces, puede duplicar ventas para tasaciones viejas.
# Para un escenario robusto, se debe verificar si ya existe una venta para esa tasación.
print("4. Generando Ventas (solo ACEPTADAS)...")
ventas_count = 0

# Cargar las tasaciones ACEPTADAS que **no tienen una venta asociada aún**
tasaciones_aceptadas_sin_venta = session.query(tasaciones) \
    .options(joinedload(tasaciones.precio_oro)) \
    .filter(tasaciones.estado == estado_aceptado_id) \
    .filter(~tasaciones.venta.has()) \
    .all()

for t in tasaciones_aceptadas_sin_venta:
    # Cálculo del importe total
    # (Peso en gramos * Precio por KG) / 1000 gramos/kg
    importe_total = round(t.peso_oro_gramos * t.precio_oro.precio_kg / 1000, 2)

    venta = ventas(
        tasacion_id=t.id,
        fecha_venta=t.fecha_tasacion,  # Se usa la fecha de tasación como fecha de venta
        importe_total=importe_total
    )
    session.add(venta)
    ventas_count += 1

session.commit()
print(f"   -> {ventas_count} ventas creadas.")

print("\nCarga inicial completada (según estado de las tablas).")