import json
from dataclasses import dataclass
from typing import List
from os.path import exists
from collections import Counter
from functools import reduce


@dataclass
class Ingrediente:
    nombre: str
    cantidad: float
    unidad: str


@dataclass
class Receta:
    dia: str
    receta: str
    ingredientes: List[Ingrediente]


def cargar_menu_desde_json(json_str):
    data = json.loads(json_str)
    return list(
        map(
            lambda item: Receta(
                dia=item["dia"],
                receta=item["receta"],
                ingredientes=list(
                    map(
                        lambda i: Ingrediente(i["nombre"], i["cantidad"], i["unidad"]),
                        item["ingredientes"],
                    )
                ),
            ),
            data,
        )
    )


def cargar_inventario_desde_json(json_str):
    data = json.loads(json_str)
    return list(
        map(lambda i: Ingrediente(i["nombre"], i["cantidad"], i["unidad"]), data)
    )


def mostrar_menu_json(menu):
    return json.dumps(
        list(
            map(
                lambda receta: {
                    "dia": receta.dia,
                    "receta": receta.receta,
                    "ingredientes": list(
                        map(
                            lambda ing: {
                                "nombre": ing.nombre,
                                "cantidad": ing.cantidad,
                                "unidad": ing.unidad,
                            },
                            receta.ingredientes,
                        )
                    ),
                },
                menu,
            )
        ),
        indent=2,
        ensure_ascii=False,
    )


def mostrar_inventario_json(inventario):
    return json.dumps(
        list(
            map(
                lambda ing: {
                    "nombre": ing.nombre,
                    "cantidad": ing.cantidad,
                    "unidad": ing.unidad,
                },
                inventario,
            )
        ),
        indent=2,
        ensure_ascii=False,
    )


def generar_lista_compras(menu, inventario):
    todos_ingredientes = reduce(lambda acc, receta: acc + receta.ingredientes, menu, [])

    necesarios = Counter()
    unidades = {}
    for ing in todos_ingredientes:
        necesarios[ing.nombre] += ing.cantidad
        unidades[ing.nombre] = ing.unidad

    disponibles = Counter({ing.nombre: ing.cantidad for ing in inventario})

    faltantes = filter(
        lambda nombre: necesarios[nombre] > disponibles[nombre], necesarios
    )

    return list(
        map(
            lambda nombre: Ingrediente(
                nombre, necesarios[nombre] - disponibles[nombre], unidades[nombre]
            ),
            faltantes,
        )
    )


def mostrar_lista_compras_json(lista):
    return json.dumps(
        list(
            map(
                lambda ing: {
                    "nombre": ing.nombre,
                    "cantidad": ing.cantidad,
                    "unidad": ing.unidad,
                },
                lista,
            )
        ),
        indent=2,
        ensure_ascii=False,
    )


def agregar_receta_desde_terminal():
    print("\nIngrese los datos de la nueva receta")
    dia = input("Día: ").strip()
    nombre_receta = input("Nombre de la receta: ").strip()
    ingredientes = []
    while True:
        nombre = input(
            "Nombre del ingrediente (o presione ENTER para terminar): "
        ).strip()
        if nombre == "":
            break
        try:
            cantidad = float(input("Cantidad: "))
            unidad = input("Unidad: ").strip()
            ingredientes.append(Ingrediente(nombre, cantidad, unidad))
        except ValueError:
            print("Cantidad inválida. Intente nuevamente.")
    return Receta(dia, nombre_receta, ingredientes)


def agregar_ingrediente_inventario_desde_terminal():
    print("\nIngrese los datos del nuevo ingrediente para el inventario")
    nombre = input("Nombre del ingrediente: ").strip()
    try:
        cantidad = float(input("Cantidad: "))
        unidad = input("Unidad: ").strip()
        nuevo = Ingrediente(nombre, cantidad, unidad)
        inventario.append(nuevo)
        guardar_json_en_archivo("inventario.json", mostrar_inventario_json(inventario))
        print("Ingrediente agregado y guardado correctamente en el inventario.")
    except ValueError:
        print("Cantidad inválida. No se agregó el ingrediente.")


def guardar_json_en_archivo(nombre_archivo, json_str):
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(json_str)


def menu_principal():
    global menu, inventario
    while True:
        print("\n ✰ Planificador de Compras Semanales ✰ ")
        print("1. Mostrar menú semanal (JSON)")
        print("2. Mostrar inventario disponible (JSON)")
        print("3. Generar lista de compras (JSON)")
        print("4. Agregar nueva receta al menú")
        print("5. Agregar nuevo ingrediente al inventario")
        print("6. Guardar menú e inventario en archivos")
        print("7. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            print(mostrar_menu_json(menu))
        elif opcion == "2":
            print(mostrar_inventario_json(inventario))
        elif opcion == "3":
            compras = generar_lista_compras(menu, inventario)
            print(mostrar_lista_compras_json(compras))
        elif opcion == "4":
            nueva_receta = agregar_receta_desde_terminal()
            menu.append(nueva_receta)
            guardar_json_en_archivo("menu.json", mostrar_menu_json(menu))
        elif opcion == "5":
            agregar_ingrediente_inventario_desde_terminal()
        elif opcion == "6":
            guardar_json_en_archivo("menu.json", mostrar_menu_json(menu))
            guardar_json_en_archivo(
                "inventario.json", mostrar_inventario_json(inventario)
            )
            print("Menú e inventario guardados correctamente.")
        elif opcion == "7":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intente de nuevo.")


# Intenta cargar desde archivos si existen
if exists("menu.json"):
    with open("menu.json", "r", encoding="utf-8") as f:
        menu = cargar_menu_desde_json(f.read())
else:
    menu_json = """
    [
      {
        "dia": "lunes",
        "receta": "ensalada",
        "ingredientes": [
          { "nombre": "lechuga", "cantidad": 1, "unidad": "pieza" },
          { "nombre": "tomate", "cantidad": 2, "unidad": "pieza" }
        ]
      },
      {
        "dia": "martes",
        "receta": "pasta",
        "ingredientes": [
          { "nombre": "pasta", "cantidad": 200, "unidad": "gramos" },
          { "nombre": "tomate", "cantidad": 1, "unidad": "pieza" }
        ]
      }
    ]"""
    menu = cargar_menu_desde_json(menu_json)

if exists("inventario.json"):
    with open("inventario.json", "r", encoding="utf-8") as f:
        inventario = cargar_inventario_desde_json(f.read())
else:
    inventario_json = """
    [
      { "nombre": "tomate", "cantidad": 1, "unidad": "pieza" },
      { "nombre": "pasta", "cantidad": 100, "unidad": "gramos" }
    ]"""
    inventario = cargar_inventario_desde_json(inventario_json)

# Iniciar menú
if __name__ == "__main__":
    menu_principal()
