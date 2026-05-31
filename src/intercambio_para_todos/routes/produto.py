from nicegui import ui,app,APIRouter,events
from modules import db_connection
from services.notifications import notify
import re


@ui.page('/mostrar_produtos')

async def content() -> None:

    ui.add_head_html('<style>.ag-row { cursor: pointer; }</style>')

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Produtos').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Atualizar', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')
    

    column_defs = [
        {'field': 'id_produto', 'headerName': 'ID', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'nome_produto', 'headerName': 'Nome', 'sortable': True, 'editable': True},
        {'field': 'tipo', 'headerName': 'Tipo', 'sortable': True, 'editable': True},
        {'field': 'valor_minimo', 'headerName': 'Valor Mínimo', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'nome_pais', 'headerName': 'País', 'sortable': True, 'editable': True},
        {'field': 'nome_cidade', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
    ]

    grid_ref = {}
    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Buscar…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')

    with ui.column().classes('w-full flex-grow').style('height: calc(100vh - 400px); overflow-y: auto;'):

        grid = ui.aggrid({
            'columnDefs': column_defs,
            'rowData': db_connection.get_produtos(),
            'rowSelection': {'mode': 'multiRow'},
            'defaultColDef': {'sortable': True},
            'autoSizeStrategy': {'type': 'fitGridWidth'},
            ':onGridSizeChanged': '(params) => params.api.sizeColumnsToFit()',
            'rowSelection': 'single',
            'defaultColDef': {'cellStyle': {'display': 'flex', 'align-items': 'center', 'white-space': 'pre-wrap' }},
            'pagination': True,
            'paginationPageSize': 20,    # Rows per page
            'paginationPageSizeSelector': [10, 20, 50, 100], # User can pick page size
        }, html_columns=[],theme='balham').classes('w-full flex-grow')
        grid_ref['grid'] = grid

        search.on('update:model-value', lambda e: grid.run_grid_method(
            'setGridOption', 'quickFilterText', e.args or ''))  #verificar diferentes condições de filtro
        
        # Store selected row data in a closure variable
        selected_row = {'data': None}
        
        # Store references to edit dialog inputs
        edit_inputs = {}
        
        async def on_row_selected(e):
            # Use get_selected_rows() instead of event data for reliable row selection
            selected_rows = await grid.get_selected_rows()
            if selected_rows:
                selected_row['data'] = selected_rows[0]
                notify(f"Selected: {selected_row['data']['nome_produto']}", type='info')
                
                # Capture values at selection time (not by reference)
                row = selected_row['data']
                nome = row.get('nome_produto', '')
                valor = row.get('valor_minimo')
                tipo_val = row.get('tipo', '')
                pais_val = row.get('pais', '')
                cidade_val = row.get('cidade', '')
                
                # Clear inputs first to prevent stale values
                edit_inputs['nome_produto'].value = ''
                edit_inputs['valor_minimo'].value = None
                edit_inputs['tipo'].value = None
                edit_inputs['pais'].value = None
                edit_inputs['cidade'].value = ''
                
                edit_dialog.open()
                # Use timer to ensure dialog renders before setting values
                ui.timer(0.05, lambda n=nome, v=valor, t=tipo_val, p=pais_val, c=cidade_val: (
                    edit_inputs['nome_produto'].set_value(n),
                    edit_inputs['valor_minimo'].set_value(v),
                    edit_inputs['tipo'].set_value(t),
                    edit_inputs['pais'].set_value(p),
                    edit_inputs['cidade'].set_value(c)
                ), once=True)
        
        grid.on('cellClicked', on_row_selected)
        

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', on_click=lambda: render_dialog(), color='primary').props('fab')

                
    # paises = db_connection.get_paises()
    # cidades = db_connection.get_cidades()
    async def render_dialog():

        async def on_filter_pais(e):
            notify(e.args, type='info')
            search_term = e.args[0]
            # Fetch filtered data
            filtered_options = db_connection.search_database_paises(search_term)
            
            # Update the UI options dynamically
            pais.options = filtered_options
            pais.update()
            cidade.value = None
            cidade.options = []
        
        async def on_filter_cidade(e):
            notify(e.args, type='info')
            search_term = e.args[0]
            # Fetch filtered data
            filtered_options = db_connection.search_database_cidades(search_term, pais.value)
            
            # Update the UI options dynamically
            cidade.options = filtered_options
            cidade.update()
    
        with ui.dialog() as dialog, ui.card().classes('w-150').style('padding: 20px'):
            ui.label('Adicionar Produto').classes('text-lg font-bold mb-4')
            with ui.row().classes("w-full"):
                with ui.card().classes("flex-grow"):
                    with ui.column().classes("w-full"):

                        # paises = await update_paises()

                        ui.label('Nome do produto').classes('text-sm font-medium mb-1')
                        nome_produto = ui.input(label='Nome do produto', placeholder='Digite o nome do produto').props('outlined rounded dense').classes('w-full')

                        ui.label('Tipo').classes('text-sm font-medium mb-1')
                        tipo = ui.select(['Intercâmbio','Pacote de viagem'],label='Tipo').classes('w-full')

                        ui.label('País').classes('text-sm font-medium mb-1')
                        pais = ui.select({}, label='País',with_input=True, on_change=lambda e: notify(e.value, type='info')).classes('w-full').on('filter', lambda e: on_filter_pais(e))

                        ui.label('Cidade').classes('text-sm font-medium mb-1')
                        cidade = ui.select({}, label='Cidade',with_input=True).classes('w-full').on('filter', lambda e: on_filter_cidade(e))

                        ui.label('Valor Mínimo do pacote').classes('text-sm font-medium mb-1')
                        valor_minimo = ui.number(label='Valor Mínimo', placeholder='0.00',min=0, format='%.2f').props('prefix=R$').classes('w-full')


                    with ui.row().classes("justify-end gap-2 q-mt-lg"):
                        ui.button('Cadastrar', on_click=lambda: update_grid(grid_ref, nome_produto.value,tipo.value, valor_minimo.value, pais.value, cidade.value,dialog)).classes('button button-primary').style('margin-right: 8px;')
                        ui.button('Cancelar', on_click=lambda: dialog.close()).classes('button button-secondary')
                        ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao adicionar produto'))

        return dialog.open()
    

    with ui.dialog() as edit_dialog, ui.card().classes('w-150').style('padding: 20px'):
        ui.label('Editar Produto').classes('text-lg font-bold mb-4')
        with ui.row().classes("w-full"):
            with ui.card().classes("flex-grow"):
                with ui.column().classes("w-full"):
                    
                    ui.label('Nome do produto').classes('text-sm font-medium mb-1')
                    edit_inputs['nome_produto'] = ui.input(label='Nome do produto', placeholder='Digite o nome do produto').props('outlined rounded dense').classes('w-full')

                    ui.label('Tipo').classes('text-sm font-medium mb-1')
                    edit_inputs['tipo'] = ui.select(['Intercâmbio','Pacote de viagem'],label='Tipo').classes('w-full')

                    ui.label('País').classes('text-sm font-medium mb-1')
                    edit_inputs['pais'] = ui.select(['Brasil', 'Estados Unidos', 'Reino Unido', 'Canadá', 'Austrália'], label='País',with_input=True,new_value_mode='add').classes('w-full')

                    ui.label('Cidade').classes('text-sm font-medium mb-1')
                    edit_inputs['cidade'] = ui.input(label='Cidade').classes('w-full')

                    ui.label('Valor Mínimo do pacote').classes('text-sm font-medium mb-1')
                    edit_inputs['valor_minimo'] = ui.number(label='Valor Mínimo', placeholder='0.00',min=0, format='%.2f').props('prefix=R$').classes('w-full')

                with ui.row().classes("justify-end gap-2 q-mt-lg w-full"):
                    ui.button('Confirmar', on_click=lambda: edit_produto(grid_ref, selected_row, edit_inputs['nome_produto'].value, edit_inputs['tipo'].value, edit_inputs['valor_minimo'].value, edit_inputs['pais'].value, edit_inputs['cidade'].value, edit_dialog)).classes('button button-primary').style('margin-right: 8px;')
                    ui.button('Cancelar', on_click=lambda: edit_dialog.close()).classes('button button-secondary')
                    ui.button('Excluir', on_click=lambda: delete_selected(grid_ref, selected_row, edit_dialog),color='red').classes('button button-danger ml-auto').style('margin-right: 8px;')
                    ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao editar produto'))

            
def on_cell_change(e):

    updated_row = e.args["data"]
    db_connection.update_produto(updated_row)
    db_connection.get_produtos()
    
    
def update_grid(grid_ref, nome_produto, tipo, valor_minimo, pais, cidade,dialog):
    db_connection.add_produto(nome_produto, tipo, valor_minimo, pais, cidade)
    dialog.close()
    
    novos_valores = db_connection.get_produtos()
    
    # 3. Update AG Grid Data
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

def edit_produto(grid_ref, selected_row, nome_produto, tipo, valor_minimo, pais, cidade, dialog):
    row_data = selected_row['data']
    if not row_data:
        ui.notify('Nenhum produto selecionado', type='warning')
        return
    
    id_produto = row_data.get('id_produto')
    db_connection.update_produto(nome_produto, tipo, valor_minimo, pais, cidade, id_produto)
    dialog.close()
    
    novos_valores = db_connection.get_produtos()
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

async def delete_selected(grid_ref,selected_row,edit_dialog):
    row_data = selected_row['data']
    grid = grid_ref.get('grid')
    id_produto = row_data.get('id_produto')

    with ui.dialog() as dialog, ui.card().classes('p-7'):
        
        ui.label('Deseja excluir o(s) item(s) selecionado(s)?')
        with ui.row(align_items='center').classes('w-full justify-center'):
            ui.button('Confirmar', on_click=lambda: dialog.submit(True))
            ui.button('Cancelar', on_click=lambda: dialog.submit(False))

    result = await dialog

    if result == True:

        db_connection.delete_produto(id_produto)
        data = db_connection.get_produtos()
        grid.options['rowData'] = data
        grid.update()
        ui.notify('Item(s) excluído(s) com sucesso', type='info')
    
    else :
        ui.notify('Operação cancelada', type='info')

    edit_dialog.close()

async def update_paises():
    try:
        paises = await db_connection.get_paises()
        notify(paises[0]['pais'])
        return paises
    except Exception as e:
        notify(f"Erro ao carregar países: {str(e)}", type='error')
        return []
    





