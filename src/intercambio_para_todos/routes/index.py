from nicegui import ui,app,APIRouter

@ui.page('/')
def main_page():
    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.left_drawer().classes('bg-blue-100') as left_drawer:
        ui.image('src/intercambio_para_todos/assets/css/images/logo.png').classes('w-32 h-32 mx-auto my-4')
        ui.button('Clique aqui', on_click=lambda: redirect_page2())
        ui.button('Mostrar Produtos', on_click=lambda: ui.navigate.to('/mostrar_produtos'))
        ui.button('Mostrar Instagram', on_click=lambda: ui.navigate.to('/mostrar_instagram'))

    
    

def redirect_page2():
    ui.notify('Redirecionando...')
    ui.navigate.to('/page2')