from nicegui import ui,app,APIRouter
from modules import db_connection

@ui.page('/mostrar_produtos')
def mostrar_produtos():
    produtos = db_connection.get_produtos()
    for produto in produtos:
        ui.label(f"ID: {produto[0]}, Nome: {produto[1]}, Tipo: {produto[2]}")