from nicegui import ui, app, APIRouter, events
from modules import db_connection
from services.notifications import notify


@ui.page('/mostrar_companhias')
async def content() -> None:

    ui.add_head_html('<style>.ag-row { cursor: pointer; }</style>')

    # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Companhias Aéreas').classes('page-title').style('color: #003A83 !important;')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Atualizar', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')

    column_defs = [
        {'field': 'id_companhia',   'headerName': 'ID',         'sortable': True, 'editable': False, 'hide': True},
        {'field': 'nome_companhia', 'headerName': 'Nome',       'sortable': True, 'editable': True},
        {'field': 'nome_pais',      'headerName': 'País',       'sortable': True, 'editable': False},
        {'field': 'pais',           'headerName': 'País (ID)',  'sortable': True, 'editable': False, 'hide': True},
    ]

    grid_ref = {}

    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Buscar…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')

    with ui.column().classes('w-full flex-grow').style('height: calc(100vh - 400px); overflow-y: auto;'):

        grid = ui.aggrid({
            'columnDefs': column_defs,
            'rowData': db_connection.get_companhias(),
            'rowSelection': 'single',
            'defaultColDef': {
                'sortable': True,
                'cellStyle': {'display': 'flex', 'align-items': 'center', 'white-space': 'pre-wrap'},
            },
            'autoSizeStrategy': {'type': 'fitGridWidth'},
            ':onGridSizeChanged': '(params) => params.api.sizeColumnsToFit()',
            'pagination': True,
            'paginationPageSize': 20,
            'paginationPageSizeSelector': [10, 20, 50, 100],
        }, html_columns=[], theme='balham').classes('w-full flex-grow')

        grid_ref['grid'] = grid

        search.on('update:model-value', lambda e: grid.run_grid_method(
            'setGridOption', 'quickFilterText', e.args or ''))

        selected_row = {'data': None}
        edit_inputs = {}

        async def on_row_selected(e):
            selected_rows = await grid.get_selected_rows()
            if selected_rows:
                selected_row['data'] = selected_rows[0]
                row = selected_row['data']

                nome = row.get('nome_companhia', '')
                pais_id = row.get('pais', '')
                pais_nome = {row.get('pais', ''): row.get('nome_pais', '')}

                await render_edit_dialog()

                # Clear first
                edit_inputs['nome_companhia'].value = ''
                edit_inputs['pais'].value = None
                edit_inputs['pais'].options = pais_nome
                edit_inputs['pais'].update()

                ui.timer(0.05, lambda n=nome, p=pais_id: (
                    edit_inputs['nome_companhia'].set_value(n),
                    edit_inputs['pais'].set_value(p),
                ), once=True)

        grid.on('cellClicked', on_row_selected)

    # ── FAB ─────────────────────────────────────────────────────
    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', on_click=lambda: render_dialog(), color='primary').props('fab')

    # ── Add dialog ──────────────────────────────────────────────
    async def render_dialog():

        async def on_filter_pais(e):
            search_term = e.args[0]
            filtered_options = db_connection.search_database_paises(search_term)
            pais.options = filtered_options
            pais.update()

        with ui.dialog() as dialog, ui.card().classes('w-150').style('padding: 20px'):
            ui.label('Adicionar Companhia Aérea').classes('text-lg font-bold mb-4')
            with ui.row().classes('w-full'):
                with ui.card().classes('flex-grow'):
                    with ui.column().classes('w-full'):

                        ui.label('Nome da companhia').classes('text-sm font-medium mb-1')
                        nome_companhia = ui.input(
                            label='Nome da companhia',
                            placeholder='Digite o nome da companhia'
                        ).props('outlined rounded dense').classes('w-full')

                        ui.label('País').classes('text-sm font-medium mb-1')
                        pais = ui.select(
                            [], label='País', with_input=True
                        ).classes('w-full').on('filter', lambda e: on_filter_pais(e))

                    with ui.row().classes('justify-end gap-2 q-mt-lg'):
                        ui.button(
                            'Cadastrar',
                            on_click=lambda: add_companhia(grid_ref, nome_companhia.value, pais.value, dialog)
                        ).classes('button button-primary').style('margin-right: 8px;')
                        ui.button('Cancelar', on_click=lambda: dialog.close()).classes('button button-secondary')
                        ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao adicionar companhia'))

        return dialog.open()

    # ── Edit dialog ─────────────────────────────────────────────
    async def render_edit_dialog():

        async def on_filter_pais(e):
            search_term = e.args[0]
            filtered_options = db_connection.search_database_paises(search_term)
            edit_inputs['pais'].options = filtered_options
            edit_inputs['pais'].update()

        with ui.dialog() as edit_dialog, ui.card().classes('w-150').style('padding: 20px'):
            ui.label('Editar Companhia Aérea').classes('text-lg font-bold mb-4')
            with ui.row().classes('w-full'):
                with ui.card().classes('flex-grow'):
                    with ui.column().classes('w-full'):

                        ui.label('Nome da companhia').classes('text-sm font-medium mb-1')
                        edit_inputs['nome_companhia'] = ui.input(
                            label='Nome da companhia',
                            placeholder='Digite o nome da companhia'
                        ).props('outlined rounded dense').classes('w-full')

                        ui.label('País').classes('text-sm font-medium mb-1')
                        edit_inputs['pais'] = ui.select(
                            {}, label='País', with_input=True
                        ).classes('w-full').on('filter', lambda e: on_filter_pais(e))

                    with ui.row().classes('justify-end gap-2 q-mt-lg w-full'):
                        ui.button(
                            'Confirmar',
                            on_click=lambda: edit_companhia(
                                grid_ref, selected_row,
                                edit_inputs['nome_companhia'].value,
                                edit_inputs['pais'].value,
                                edit_dialog
                            )
                        ).classes('button button-primary').style('margin-right: 8px;')
                        ui.button('Cancelar', on_click=lambda: edit_dialog.close()).classes('button button-secondary')
                        ui.button(
                            'Excluir',
                            on_click=lambda: delete_selected(grid_ref, selected_row, edit_dialog),
                            color='red'
                        ).classes('button button-danger ml-auto').style('margin-right: 8px;')
                        ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao editar companhia'))

        return edit_dialog.open()


# ── Grid helpers ─────────────────────────────────────────────────────────────

def add_companhia(grid_ref, nome_companhia, pais, dialog):
    db_connection.add_companhia(nome_companhia, pais)
    dialog.close()

    novos_valores = db_connection.get_companhias()
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()


def edit_companhia(grid_ref, selected_row, nome_companhia, pais, dialog):
    row_data = selected_row['data']
    if not row_data:
        ui.notify('Nenhuma companhia selecionada', type='warning')
        return

    id_companhia = row_data.get('id_companhia')
    db_connection.update_companhia(nome_companhia, pais, id_companhia)
    dialog.close()

    novos_valores = db_connection.get_companhias()
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()


async def delete_selected(grid_ref, selected_row, edit_dialog):
    row_data = selected_row['data']
    grid = grid_ref.get('grid')
    id_companhia = row_data.get('id_companhia')

    with ui.dialog() as dialog, ui.card().classes('p-7'):
        ui.label('Deseja excluir a companhia selecionada?')
        with ui.row(align_items='center').classes('w-full justify-center'):
            ui.button('Confirmar', on_click=lambda: dialog.submit(True))
            ui.button('Cancelar',  on_click=lambda: dialog.submit(False))

    result = await dialog

    if result:
        db_connection.delete_companhia(id_companhia)
        data = db_connection.get_companhias()
        grid.options['rowData'] = data
        grid.update()
        ui.notify('Companhia excluída com sucesso', type='info')
    else:
        ui.notify('Operação cancelada', type='info')

    edit_dialog.close()