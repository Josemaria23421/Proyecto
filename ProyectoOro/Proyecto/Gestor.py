import datetime
from multiprocessing.connection import Client

from faker import Faker
from sqlalchemy import func, desc, text

from Proyecto.Model import clientes, ventas, tasaciones
from Proyecto.config import session
from config import Session


class Gestor:


    fake = Faker("es_ES")


def __init__(self):
    self.session = Session()


# 1️⃣ Introducir un cliente Nuevo
def insertar_Cliente(self):
    dni_cliente = input("Dime el DNI del cliente: ")
    nombre_cliente = input("Dime el nombre del cliente: ")
    apellidos_cliente = input("Dime los apellidos del cliente: ")
    fecha_nacimiento_Cliente = input("Dime la fecha de nacimiento (YYYY-MM-DD): ")
    email_cliente = input("Dime el email del cliente: ")
    nacionalidad_cliente = input("Dime la nacionalidad del cliente: ")
    telefono_cliente = input("Dime el teléfono del cliente: ")
    direccion_cliente = input("Dime la dirección del cliente: ")

    # Convertimos la fecha a DATE
    try:
        fecha_nac = datetime.strptime(fecha_nacimiento_Cliente, "%Y-%m-%d").date()
    except ValueError:
        print("Formato de fecha inválido. Debe ser YYYY-MM-DD.")
        return
    cliente = clientes(
        dni=dni_cliente,
        nombre=nombre_cliente,
        apellidos=apellidos_cliente,
        fecha_nacimiento=fecha_nac,
        email=email_cliente,
        nacionalidad=nacionalidad_cliente,
        telefono=telefono_cliente,
        direccion=direccion_cliente)
    self.session.add(cliente)
    self.session.commit()
    print("✅ Se ha guardado el cliente correctamente.")


def ventas_realizadas_en_un_mes(self, mes):
    meses = ["ENERO", "FEBRERO", 'MARZO',
             "ABRIL", "MAYO", 'JUNIO',
             "JULIO", "AGOSTO", 'SEPTIEMBRE',
             "OCTUBRE", "NOVIEMBRE", 'DICIEMBRE']
    todas_las_ventas = (self.session.query(ventas).filter
                        (func.extract('month', ventas.fecha_venta) == meses[mes - 1])).all()
    for venta in todas_las_ventas:
        print(venta)


def ventas_realizadas_por_un_cliente(self, cliente_Dni):
    ventas_de_un_cliente = self.session.query(ventas).join(
        tasaciones.id == ventas.tasacion_id).join(
        clientes.dni == tasaciones.cliente_id).filter_by(
        clientes.dni == cliente_Dni)
    for venta in ventas_de_un_cliente:
        print(venta)


def tasaciones_no_aceptas(self):
    tasaciones_negativas = self.session.query(tasaciones).filter(tasaciones.estado != 'ACEPTADA')
    for tasacion in tasaciones_negativas:
        print(tasacion)


def cliente_con_mas_venta(self):
    cliente_MAX = self.session.query(clientes.nombre,
                                     func.count(ventas.id).label("total_ventas")).join(
        clientes.dni == tasaciones.cliente_id).join(
        tasaciones.id == ventas.tasacion_id).group_by(clientes.nombre).order_by(desc("total_ventas")).first()
    print(cliente_MAX)


def clientes_con_3_meses_sin_ventas(self):
    mes = func.current_date() - text("INTERVAL '3 months'")
    clientes_sin_ventas = self.session.query(clientes.nombre).join(
        clientes.dni == tasaciones.cliente_id).join(
        tasaciones.id == ventas.tasacion_id).filter_by(ventas.fecha_venta <= mes)
    for cliente in clientes_sin_ventas:
        print(cliente)
