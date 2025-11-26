from sqlalchemy import (
    Column, Integer, BigInteger, String, Numeric, Text, Date,
    ForeignKey, UniqueConstraint, Boolean, false
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ============  ==============
#   TABLA CLIENTES
# ==========================
class clientes(Base):
    __tablename__ = "clientes"
    __table_args__ = {"schema": "proyecto"}

    dni = Column(String(20), primary_key=True, nullable=False, unique=True)
    nombre = Column(String(20), nullable=False)
    apellidos = Column(String(20), nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    email = Column(String(20), nullable=False)
    nacionalidad = Column(String(20), nullable=False)
    telefono = Column(String(9), nullable=False)
    direccion = Column(String(20), nullable=False)

    tasaciones = relationship("tasaciones", back_populates="cliente")

    def __repr__(self):
        return f"<Cliente DNI={self.dni} nombre={self.nombre!r}>"


# ==========================
#   TABLA PRECIOS ORO
# ==========================
class precios_del_oro(Base):
    __tablename__ = "precios_oro"
    __table_args__ = {"schema": "proyecto"}

    id_oro = Column(BigInteger, primary_key=True, autoincrement=True)
    fecha = Column(Date, nullable=False)
    precio_kg = Column(Numeric(12, 2), nullable=False)

    tasaciones = relationship("tasaciones", back_populates="precio_oro")

    def __repr__(self):
        return (f"<precios_oro Id={self.id_oro} fecha={self.fecha}, "
                f"precio_kg={self.precio_kg}>")


# ==========================
#   TABLA TASACIONES
# ==========================
class tasaciones(Base):
    __tablename__ = "tasaciones"
    __table_args__ = {"schema": "proyecto"}

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Clave foránea → precios_oro.id_oro
    precio_oro_id = Column(
        BigInteger,
        ForeignKey("proyecto.precios_oro.id_oro"),
        nullable=False
    )
    peso_oro_gramos = Column(Numeric(10, 2), nullable=False)

    # Columna requerida por NOT NULL
    fecha_tasacion = Column(Date, nullable=False)

    # Clave foránea → clientes.dni
    cliente_id = Column(
        String(20),  # Tipo corregido
        ForeignKey("proyecto.clientes.dni"),
        nullable=False
    )

    estado = Column(Integer,
    ForeignKey("proyecto.estado.id_estado", onupdate="RESTRICT", ondelete="RESTRICT"))

    precio_oro = relationship("precios_del_oro", back_populates="tasaciones")
    cliente = relationship("clientes", back_populates="tasaciones")
    venta = relationship("ventas", back_populates="tasacion", uselist=False)

    def __repr__(self):
        return f"<Tasación id={self.id} cliente={self.cliente_id}>"


# ==========================
#   TABLA VENTAS
# ==========================
class ventas(Base):
    __tablename__ = "ventas"
    __table_args__ = {"schema": "proyecto"}

    id_venta_realizada = Column(BigInteger, primary_key=True, autoincrement=True)

    # Clave foránea → tasaciones.id
    tasacion_id = Column(
        BigInteger,
        ForeignKey("proyecto.tasaciones.id"),
        nullable=False
    )

    fecha_venta = Column(Date, nullable=False)
    importe_total = Column(Numeric(10, 2), nullable=False)

    tasacion = relationship("tasaciones", back_populates="venta")

    def __repr__(self):
        return f"<Venta id={self.id_venta_realizada} tasacion={self.tasacion_id}, importe total: {self.importe_total}>"
# ==========================
#   TABLA ESTADOS
# ==========================
class estado(Base):
    __tablename__ = "estado"
    __table_args__ = {"schema": "proyecto"}

    id_estado = Column(BigInteger, primary_key=True, autoincrement=True)

    # Clave foránea → tasaciones.id
    estado = Column(String, nullable=False)