class Menu:
    def __init__(self):
        self.gestor = Gestor()

    def mostrar(self):
        while True:
            print("\n--- MENÚ PRINCIPAL ---")
            print("0 - Salir")

            try:
                opc = int(input("Dime qué quieres hacer: "))
            except ValueError:
                print("Opción no válida, introduce un número.")
                continue

            if opc == 1:
                self.gestor.insertar_rol()
            elif opc == 0:
                    print("👋 Fin de sesión.")
                    break
            else:
                print("⚠️ Opción no válida, inténtalo de nuevo.")


if __name__ == '__main__':
    menu = Menu()
    menu.mostrar()