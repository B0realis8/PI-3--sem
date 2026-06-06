from nicegui import ui,app,APIRouter,events
from modules import db_connection
from services.notifications import notify
import re


@ui.page('/mostrar_clientes')

async def content() -> None:

    ui.add_head_html('<style>.ag-row { cursor: pointer; }</style>')

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Clientes').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Atualizar', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')
    

    column_defs = [
        {'field': 'id_cliente', 'headerName': 'ID', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'nome', 'headerName': 'Nome', 'sortable': True, 'editable': True},
        {'field': 'sexo', 'headerName': 'Sexo', 'sortable': True, 'editable': True},
        {'field': 'data_nascimento', 'headerName': 'Data de Nascimento', 'sortable': True, 'editable': True,'filter': 'agDateColumnFilter', 'valueFormatter': 'value ? value.split("-").reverse().join("/") : "N/A"'},
        {'field': 'cpf', 'headerName': 'CPF', 'sortable': True, 'editable': True, 'valueFormatter': 'value ? value.replace(/(\\d{3})(\\d{3})(\\d{3})(\\d{2})/, "$1.$2.$3-$4") : "N/A"'},
        {'field': 'telefone', 'headerName': 'Telefone', 'sortable': True, 'editable': True},
        {'field': 'nome_cidade', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
        {'field': 'estado', 'headerName': 'Estado', 'sortable': True, 'editable': True},
        {'field': 'cidade', 'headerName': 'Cidade', 'sortable': True, 'editable': True, 'hide': True},
        ]

    grid_ref = {}
    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Buscar…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')

    with ui.column().classes('w-full flex-grow').style('height: calc(100vh - 400px); overflow-y: auto;'):

        grid = ui.aggrid({
            'columnDefs': column_defs,
            'rowData': db_connection.get_clientes(),
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
                notify(f"Selected: {selected_row['data']['nome']}", type='info')

                # Capture values at selection time (not by reference)
                row = selected_row['data']
                nome = row.get('nome', '')
                data_nascimento = row.get('data_nascimento', '')
                sexo = row.get('sexo', '')
                cpf = row.get('cpf', '')
                telefone = row.get('telefone', '')
                cidade_val = {row.get('cidade', ''): row.get('nome_cidade', '')}
                cidade_id = row.get('cidade', '')
                estado = row.get('estado', '')

                await render_edit_dialog()
                
                # Clear inputs first to prevent stale values
                edit_inputs['nome'].value = ''
                edit_inputs['data_nascimento'].value = None
                edit_inputs['sexo'].value = None
                edit_inputs['cpf'].value = None
                edit_inputs['telefone'].value = None
                
                edit_inputs['estado'].value = ''

                edit_inputs['cidade'].value = ''
                edit_inputs['cidade'].options = cidade_val
                edit_inputs['cidade'].update()
                
                
                
                # Use timer to ensure dialog renders before setting values
                ui.timer(0.05, lambda n=nome, d=data_nascimento, s=sexo, c=cpf, t=telefone, e=estado, ci=cidade_id: (
                    edit_inputs['nome'].set_value(n),
                    edit_inputs['data_nascimento'].set_value(d),
                    edit_inputs['sexo'].set_value(s),
                    edit_inputs['cpf'].set_value(c),
                    edit_inputs['telefone'].set_value(t),
                    edit_inputs['estado'].set_value(e),
                    edit_inputs['cidade'].set_value(ci)

                ), once=True)
        
        grid.on('cellClicked', on_row_selected)
        

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', on_click=lambda: render_dialog(), color='primary').props('fab')

                
    # paises = db_connection.get_paises()
    # cidades = db_connection.get_cidades()
    async def render_dialog():

        estados_brasil = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
            "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
            "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]

        
        async def on_filter_cidade(e):
            # notify(e.args, type='info')
            search_term = e.args[0]
            # Fetch filtered data
            filtered_options = db_connection.search_database_cidades(search_term, 31)
            
            # Update the UI options dynamically
            cidade.options = filtered_options
            cidade.update()
    
        with ui.dialog() as dialog, ui.card().classes('w-150').style('padding: 20px'):
            ui.label('Adicionar Cliente').classes('text-lg font-bold mb-4')
            with ui.row().classes("w-full"):
                with ui.card().classes("flex-grow"):
                    with ui.column().classes("w-full"):

                        # paises = await update_paises()

                        ui.label('Nome do cliente').classes('text-sm font-medium mb-1')
                        nome = ui.input(label='Nome do cliente', placeholder='Digite o nome do cliente').props('outlined rounded dense').classes('w-full')

                        ui.label('Data de Nascimento').classes('text-sm font-medium mb-1')
                        data_nascimento = ui.date_input(label='Data de Nascimento', placeholder='Data de Nascimento').classes('w-full rounded-md').props('outlined')
                        
                        ui.label('CPF').classes('text-sm font-medium mb-1')
                        cpf = ui.input(label='CPF', placeholder='Digite o CPF').props('outlined rounded dense').classes('w-full')

                        ui.label('Telefone').classes('text-sm font-medium mb-1')
                        telefone = ui.input(label='Telefone', placeholder='Digite o telefone').props('outlined rounded dense').classes('w-full')

                        ui.label('Sexo').classes('text-sm font-medium mb-1')
                        sexo = ui.select(['M', 'F'], label='Sexo',with_input=True).classes('w-full')

                        ui.label('Estado').classes('text-sm font-medium mb-1')
                        estado = ui.select(estados_brasil, label='Estado',with_input=True).classes('w-full')

                        ui.label('Cidade').classes('text-sm font-medium mb-1')
                        cidade = ui.select([], label='Cidade',with_input=True).classes('w-full').on('filter', lambda e: on_filter_cidade(e))


                    with ui.row().classes("justify-end gap-2 q-mt-lg"):
                        ui.button('Cadastrar', on_click=lambda: update_grid(grid_ref, nome.value, cpf.value, telefone.value, sexo.value, data_nascimento.value, estado.value, cidade.value, dialog)).classes('button button-primary').style('margin-right: 8px;')
                        ui.button('Cancelar', on_click=lambda: dialog.close()).classes('button button-secondary')
                        ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao adicionar cliente'))

        return dialog.open()
    
    async def render_edit_dialog():
        
        async def on_filter_cidade(e):
            # notify(e.args, type='info')
            search_term = e.args[0]
            # Fetch filtered data
            filtered_options = db_connection.search_database_cidades(search_term, 31)
            
            # Update the UI options dynamically
            edit_inputs['cidade'].options = filtered_options
            edit_inputs['cidade'].update()

        estados_brasil = [
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
            "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
            "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ]
        
        with ui.dialog() as edit_dialog, ui.card().classes('w-150').style('padding: 20px'):
            ui.label('Editar Cliente').classes('text-lg font-bold mb-4')
            with ui.row().classes("w-full"):
                with ui.card().classes("flex-grow"):
                    with ui.column().classes("w-full"):
                        
                        ui.label('Nome do cliente').classes('text-sm font-medium mb-1')
                        edit_inputs['nome'] = ui.input(label='Nome do cliente', placeholder='Digite o nome do cliente').props('outlined rounded dense').classes('w-full')

                        ui.label('CPF').classes('text-sm font-medium mb-1')
                        edit_inputs['cpf'] = ui.input(label='CPF', placeholder='Digite o CPF').props('outlined rounded dense').classes('w-full')

                        ui.label('Telefone').classes('text-sm font-medium mb-1')
                        edit_inputs['telefone'] = ui.input(label='Telefone', placeholder='Digite o telefone').props('outlined rounded dense').classes('w-full')

                        ui.label('Data de Nascimento').classes('text-sm font-medium mb-1')
                        edit_inputs['data_nascimento'] = ui.date_input(label='Data de Nascimento', placeholder='Data de Nascimento').classes('w-full rounded-md').props('outlined')

                        ui.label('Sexo').classes('text-sm font-medium mb-1')
                        edit_inputs['sexo'] = ui.select(['M', 'F'], label='Sexo',with_input=True).classes('w-full')

                        ui.label('Estado').classes('text-sm font-medium mb-1')
                        edit_inputs['estado'] = ui.select(estados_brasil, label='Estado',with_input=True).classes('w-full')

                        ui.label('Cidade').classes('text-sm font-medium mb-1')
                        edit_inputs['cidade'] = ui.select({}, label='Cidade',with_input=True).classes('w-full').on('filter', lambda e: on_filter_cidade(e))


                    with ui.row().classes("justify-end gap-2 q-mt-lg w-full"):
                        ui.button('Confirmar', on_click=lambda: edit_cliente(grid_ref, selected_row, edit_inputs['nome'].value, edit_inputs['sexo'].value, edit_inputs['data_nascimento'].value, edit_inputs['cpf'].value, edit_inputs['telefone'].value, edit_inputs['estado'].value, edit_inputs['cidade'].value, edit_dialog)).classes('button button-primary').style('margin-right: 8px;')
                        ui.button('Cancelar', on_click=lambda: edit_dialog.close()).classes('button button-secondary')
                        ui.button('Excluir', on_click=lambda: delete_selected(grid_ref, selected_row, edit_dialog),color='red').classes('button button-danger ml-auto').style('margin-right: 8px;')
                        ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao editar cliente'))

        return edit_dialog.open()

            
def on_cell_change(e):

    updated_row = e.args["data"]
    db_connection.update_produto(updated_row)
    db_connection.get_produtos()
    
    
def update_grid(grid_ref, nome, sexo, data_nascimento, cpf, telefone, estado, cidade, dialog):
    db_connection.add_cliente(nome, sexo, data_nascimento, cpf, telefone, cidade, estado, dialog)

    novos_valores = db_connection.get_clientes()
    
    # 3. Update AG Grid Data
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

def edit_cliente(grid_ref, selected_row, nome, sexo, data_nascimento, cpf, telefone, estado, cidade, dialog):
    row_data = selected_row['data']
    if not row_data:
        ui.notify('Nenhum cliente selecionado', type='warning')
        return
    
    id_cliente = row_data.get('id_cliente')
    db_connection.update_cliente(nome, sexo, data_nascimento, cpf, telefone, cidade, estado, id_cliente)
    dialog.close()
    
    novos_valores = db_connection.get_clientes()
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

async def delete_selected(grid_ref,selected_row,edit_dialog):
    row_data = selected_row['data']
    grid = grid_ref.get('grid')
    id_cliente = row_data.get('id_cliente')

    with ui.dialog() as dialog, ui.card().classes('p-7'):
        
        ui.label('Deseja excluir o(s) item(s) selecionado(s)?')
        with ui.row(align_items='center').classes('w-full justify-center'):
            ui.button('Confirmar', on_click=lambda: dialog.submit(True))
            ui.button('Cancelar', on_click=lambda: dialog.submit(False))

    result = await dialog

    if result == True:

        db_connection.delete_cliente(id_cliente)
        data = db_connection.get_clientes()
        grid.options['rowData'] = data
        grid.update()
        ui.notify('Item(s) excluído(s) com sucesso', type='info')
    
    else :
        ui.notify('Operação cancelada', type='info')

    edit_dialog.close()






