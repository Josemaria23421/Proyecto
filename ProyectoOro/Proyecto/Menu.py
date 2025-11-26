from Proyecto.Gestion.Gestor import Gestor
from Proyecto.DB.Factory.faktoria import FactoriaDatos
class Menu:
    def __init__(self):
        self.gestor = Gestor()

    def mostrar(self):
        while True:
            print("\n--- MENÚ PRINCIPAL ---")
            print("1 - Insertar un nuevo cliente")
            print("2 - Gráfico: Cantidad de oro vendida por cliente")
            print("3 - Gráfico: Total de ventas por mes")
            print("4 - Mostrar ventas realizadas en un mes")
            print("5 - Mostrar ventas realizadas por un cliente")
            print("6 - Mostrar tasaciones no aceptadas")
            print("7 - Mostrar cliente con más ventas")
            print("8 - Mostrar clientes con 3 meses sin ventas")
            print("9 - Generar Una Nueva Venta")
            print("0 - Salir")

            try:
                opc = int(input("Selecciona una opción: "))
            except ValueError:
                print("Opción inválida. Introduce un número.")
                continue

            # 1) Insertar un nuevo cliente
            if opc == 1:
                self.gestor.insertar_Cliente()

            # 2) Gráfico: ventas por cliente
            elif opc == 2:
                self.gestor.graficoCantidadOroVendidaPorCliente()

            # 3) Gráfico: ventas por mes
            elif opc == 3:
                self.gestor.totalVentasPorMes()

            # 4) Ventas en un mes específico
            elif opc == 4:
                try:
                    mes = int(input("Introduce el número del mes (1-12): "))
                    if 1 <= mes <= 12:
                        self.gestor.ventas_realizadas_en_un_mes(mes)
                    else:
                        print("El mes debe estar entre 1 y 12.")
                except ValueError:
                    print("Debes introducir un número de mes válido.")

            # 5) Ventas realizadas por un cliente según DNI
            elif opc == 5:
                dni = input("Introduce el DNI del cliente: ")
                self.gestor.ventas_realizadas_por_un_cliente(dni)

            # 6) Tasaciones no aceptadas
            elif opc == 6:
                self.gestor.tasaciones_no_aceptas()

            # 7) Cliente con más ventas
            elif opc == 7:
                self.gestor.cliente_con_mas_venta()

            # 8) Clientes con 3 meses sin ventas
            elif opc == 8:
                self.gestor.clientes_con_3_meses_sin_ventas()
            # 9) Generar Una Venta (Tasar una cantidad de oro y luego añadirla o no a Ventas)
            elif opc == 9:
                self.gestor.crear_venta_por_tasacion()

            # 0) Salir del programa
            elif opc == 0:
                print("Fin de la sesión.")
                break

            else:
                print("Opción no válida. Inténtalo de nuevo.")

def main():
    print("Iniciando sistema...")

    # Ejecutar carga inicial
    FactoriaDatos().ejecutar()

    # Crear instancia del menú y mostrarlo
    menu = Menu()
    menu.mostrar()

if __name__ == '__main__':
    main()
