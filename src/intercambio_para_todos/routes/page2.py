from nicegui import ui,app,APIRouter

@ui.page('/page2')
def page2():
    ui.label('Página 2')
    ui.button('Voltar para a página inicial', on_click=lambda: ui.navigate.to('/'))
