from nicegui import ui,app,APIRouter,events
from modules import db_connection
from services.notifications import notify
import re


@ui.page('/mostrar_orcamentos')

def content() -> None:


        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Orçamentos').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Refresh', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')

    column_defs = [
        {'field': 'id_orcamento', 'headerName': 'ID', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'id_produto', 'headerName': 'ID Produto', 'sortable': True, 'editable': True},
        {'field': 'id_voo', 'headerName': 'ID Voo', 'sortable': True, 'editable': True},
        {'field': 'id_cliente', 'headerName': 'ID Cliente', 'sortable': True, 'editable': True},
        {'field': 'valor_total', 'headerName': 'Valor Total', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
    ]

    grid_ref = {}
    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Buscar…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')

    with ui.column().classes('w-full flex-grow').style('height: calc(100vh - 400px); overflow-y: auto;'):

        grid = ui.aggrid({
            'columnDefs': column_defs,
            'rowData': db_connection.get_orcamentos(),
            'rowSelection': {'mode': 'multiRow'},
            'defaultColDef': {'sortable': True},
            'autoSizeStrategy': {'type': 'fitGridWidth'},
            ':onGridSizeChanged': '(params) => params.api.sizeColumnsToFit()',
        }, html_columns=[4]).classes('w-full flex-grow').on("cellValueChanged", on_cell_change)
        grid_ref['grid'] = grid

        search.on('update:model-value', lambda e: grid.run_grid_method(
            'setGridOption', 'quickFilterText', e.args or ''))           #verificar diferentes condições de filtro

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', on_click=lambda: dialog.open(), color='primary').props('fab')
            ui.button(icon='delete', on_click=lambda: delete_selected(grid_ref), color='red').props('fab')
    
    with ui.dialog() as dialog, ui.card().classes('w-150').style('padding: 20px'):
        ui.label('Adicionar Orçamento').classes('text-lg font-bold mb-4')
        with ui.row().classes("w-full"):
            with ui.card().classes("flex-grow"):
                with ui.column().classes("w-full"):
                    
                    ui.label('Produto').classes('text-sm font-medium mb-1')
                    id_produto = ui.number(label='ID Produto', placeholder='Digite o ID do produto', min=0, step=1).props('outlined rounded dense').classes('w-full')

                    ui.label('Voo').classes('text-sm font-medium mb-1')
                    id_voo = ui.number(label='ID Voo', placeholder='Digite o ID do voo', min=0, step=1).props('outlined rounded dense').classes('w-full')

                    ui.label('Cliente').classes('text-sm font-medium mb-1')
                    id_cliente = ui.number(label='ID Cliente', placeholder='Digite o ID do cliente', min=0, step=1).props('outlined rounded dense').classes('w-full')

                    ui.label('Valor Total').classes('text-sm font-medium mb-1')
                    valor_total = ui.number(label='Valor Total', placeholder='0.00', min=0, format='%.2f').props('prefix=R$').classes('w-full')

                with ui.row().classes("justify-end gap-2 q-mt-lg"):
                    ui.button('Cadastrar', on_click=lambda: update_grid(grid_ref, id_produto.value, id_voo.value, id_cliente.value, valor_total.value, dialog)).classes('button button-primary').style('margin-right: 8px;')
                    ui.button('Cancelar', on_click=lambda: dialog.close()).classes('button button-secondary')
                    ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao adicionar orçamento'))
    

            
def on_cell_change(e):

    updated_row = e.args["data"]
    db_connection.update_orcamento(updated_row)
    db_connection.get_orcamentos()
    
    
    
def update_grid(grid_ref, id_produto, id_voo, id_cliente, valor_total, dialog):
    db_connection.add_orcamento(id_produto, id_voo, id_cliente, valor_total)
    dialog.close()
    
    novos_valores = db_connection.get_orcamentos()
    
    # 3. Update AG Grid Data
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

async def delete_selected(grid_ref):
    grid = grid_ref.get('grid')
    selected_rows = await grid.get_selected_rows()
    if not selected_rows:
        ui.notify('Nenhum item selecionado para exclusão', type='warning')
        return

    with ui.dialog() as dialog, ui.card().classes('p-7'):
        
        ui.label('Deseja excluir o(s) item(s) selecionado(s)?')
        with ui.row(align_items='center').classes('w-full justify-center'):
            ui.button('Confirmar', on_click=lambda: dialog.submit(True))
            ui.button('Cancelar', on_click=lambda: dialog.submit(False))

    result = await dialog

    if result == True:

        for row in selected_rows:
            db_connection.delete_orcamento(row['id_orcamento'])
        data = db_connection.get_orcamentos()
        grid.options['rowData'] = data
        grid.update()
        ui.notify('Item(s) excluído(s) com sucesso', type='info')
    
    else :
        ui.notify('Operação cancelada', type='info')