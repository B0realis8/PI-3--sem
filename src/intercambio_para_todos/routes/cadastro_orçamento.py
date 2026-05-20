from nicegui import ui,app,APIRouter,events
from modules import db_connection
from services.notifications import notify
import re
import json
from datetime import datetime


def format_dt(dt_str):
    if not dt_str:
        return ''
    try:
        # Adjust input format if needed (this assumes ISO-like string)
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%d/%m/%Y - %H:%M')
    except Exception:
        return dt_str  # fallback if parsing fails

def format_orcamentos_for_grid(orcamentos):
    
    for orc in orcamentos:
        if 'voo_lista_ida' in orc and orc['voo_lista_ida']:
            if isinstance(orc['voo_lista_ida'], list):
                formatted_voos = []
                for v in orc['voo_lista_ida']:
                    if v:
                        dt_saida = format_dt(v.get('dt_hr_saida'))
                        dt_chegada = format_dt(v.get('dt_hr_chegada'))

                        formatted = (
                            f"Saída: {v.get('cidade_saida', '')} ({v.get('pais_saida', '')}), {v.get('aeroporto_saida', '')}\n"
                            f"{dt_saida}\n\n"
                            f"Chegada: {v.get('cidade_destino', '')} ({v.get('pais_destino', '')}), {v.get('aeroporto_destino', '')}\n"
                            f"{dt_chegada}"
                        )
                        formatted_voos.append(formatted)
                orc['voo_lista_ida'] = '\n\n'.join(formatted_voos)

        if 'voo_lista_volta' in orc and orc['voo_lista_volta']:
            if isinstance(orc['voo_lista_volta'], list):
                formatted_voos = []
                for v in orc['voo_lista_volta']:
                    if v:
                        dt_saida = format_dt(v.get('dt_hr_saida'))
                        dt_chegada = format_dt(v.get('dt_hr_chegada'))

                        formatted = (
                            f"Saída: {v.get('cidade_saida', '')} ({v.get('pais_saida', '')}), {v.get('aeroporto_saida', '')}\n"
                            f"{dt_saida}\n\n"
                            f"Chegada: {v.get('cidade_destino', '')} ({v.get('pais_destino', '')}), {v.get('aeroporto_destino', '')}\n"
                            f"{dt_chegada}"
                        )
                        formatted_voos.append(formatted)
                orc['voo_lista_volta'] = '\n\n'.join(formatted_voos)
    return orcamentos


@ui.page('/mostrar_orcamento')

def content() -> None:

    ui.add_head_html('<style>.ag-row { cursor: pointer; }</style>')

    ui.add_body_html("""
                        <style>
                            body {
                                --ag-row-hover-color: rgb(227, 227, 227);
                                --ag-line-height: 25px;
                            }
                        </style>
                        """)
    ui.add_head_html('<style>.tight-textarea .q-field__control { padding: 8px 8px 0 8px !important; }</style>')

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Orçamentos').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Atualizar', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')
    
    join_dict_js = "x => Array.isArray(x) ? x.map(v => v.cidade_destino).join(', ') : x" 
    column_defs = [

        {'field': 'id_orcamento', 'headerName': 'Orçamento #', 'sortable': True, 'editable': False},
        {'field': 'id_produto', 'headerName': 'ID Produto', 'sortable': True, 'editable': True, 'hide': True},
        {'field': 'id_voo', 'headerName': 'ID Voo', 'sortable': True, 'editable': True, 'hide': True},
        {'field': 'id_cliente', 'headerName': 'ID Cliente', 'sortable': True, 'editable': True, 'hide': True},
        {'field': 'id_hospedagem', 'headerName': 'ID Hospedagem', 'sortable': True, 'editable': True, 'hide': True},
        {'field': 'id_servico', 'headerName': 'ID Serviço', 'sortable': True, 'editable': True, 'hide': True},

        {'field': 'nome', 'headerName': 'Cliente', 'sortable': True, 'editable': True},
        {'field': 'nome_produto', 'headerName': 'Produto', 'sortable': True, 'editable': True},
        {'field': 'tipo', 'headerName': 'Tipo', 'sortable': True, 'editable': True},
        {'field': 'valor_minimo', 'headerName': 'Valor Base', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'pais', 'headerName': 'País', 'sortable': True, 'editable': True},
        {'field': 'cidade', 'headerName': 'Cidade', 'sortable': True, 'editable': True},

        {'field': 'voo_lista_ida', 'headerName': 'Voo (Ida)', 'sortable': True, 'editable': True, 'wrapText': True, 'autoHeight': True, 'width': 600},
        {'field': 'nome_companhia_ida', 'headerName': 'Companhia Aérea (Ida)', 'sortable': True, 'editable': True, 'width': 200},
        {'field': 'valor_passagem_ida', 'headerName': 'Valor Passagem (Ida)', 'sortable': True, 'editable': True, 'width': 200, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'qtd_passagens_ida', 'headerName': 'Qtd. Passagens (Ida)', 'sortable': True, 'editable': True, 'width': 100},


        {'field': 'voo_lista_volta', 'headerName': 'Voo (Volta)', 'sortable': True, 'editable': True, 'wrapText': True, 'autoHeight': True, 'width': 600},
        {'field': 'nome_companhia_volta', 'headerName': 'Companhia Aérea (Volta)', 'sortable': True, 'editable': True, 'width': 200},
        {'field': 'valor_passagem_volta', 'headerName': 'Valor Passagem (Volta)', 'sortable': True, 'editable': True, 'width': 200, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'qtd_passagens_volta', 'headerName': 'Qtd. Passagens (Volta)', 'sortable': True, 'editable': True, 'width': 100},

        
        {'field': 'data_saida_ida', 'headerName': 'Data da Saida', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'hora_saida_ida', 'headerName': 'Hora da Saida', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'data_chegada_volta', 'headerName': 'Data da Chegada', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'hora_chegada_volta', 'headerName': 'Hora da Chegada', 'sortable': True, 'editable': False, 'hide': True},

        {'field': 'endereco', 'headerName': 'Endereço da Hospedagem', 'sortable': True, 'editable': True, 'wrapText': True},
        {'field': 'diaria', 'headerName': 'Diária', 'sortable': True, 'editable': True, 'width': 120, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'dias', 'headerName': 'Dias', 'sortable': True, 'editable': True, 'width': 100},
        {'field': 'obs', 'headerName': 'Observações sobre a Hospedagem', 'sortable': True, 'editable': True}, #mudar para obs_hospedagem

        {'field': 'descricao', 'headerName': 'Descrição do Serviço', 'sortable': True, 'editable': True},
        {'field': 'valor_total_servicos', 'headerName': 'Valor Total dos Serviços', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'obs_servicos', 'headerName': 'Observações do Serviço', 'sortable': True, 'editable': True},

        {'field': 'valor_total', 'headerName': 'Valor Total', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},



    ]

    grid_ref = {}
    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Buscar…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')

    with ui.column().classes('w-full flex-grow').style('height: calc(100vh - 400px); overflow-y: auto;'):

        grid = ui.aggrid({
            'columnDefs': column_defs,
            'rowData': format_orcamentos_for_grid(db_connection.teste_get_orcamentos()),
            'defaultColDef': {'sortable': True},
            'autoSizeStrategy': {'type': 'fitCellContents'},
            'suppressSizeToFit': True,
            #':onGridSizeChanged': '(params) => params.api.sizeColumnsToFit()',
            'onGridReady': '(params) => { params.api.sizeColumnsToFit(); }',
            'rowSelection': 'single',
            'defaultColDef': {'cellStyle': {'display': 'flex', 'align-items': 'center', 'white-space': 'pre-wrap' }},
            'pagination': True,
            'paginationPageSize': 10,    # Rows per page
            'paginationPageSizeSelector': [10, 20, 50, 100], # User can pick page size
        }, html_columns=[10],theme='balham').classes('w-full flex-grow')
        grid_ref['grid'] = grid

        search.on('update:model-value', lambda e: grid.run_grid_method(
            'setGridOption', 'quickFilterText', e.args or ''))  #verificar diferentes condições de filtro
            
            

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', color='primary', on_click=lambda: dialog.open()).props('fab')

    def on_selection_change_produto(event):
        selected_id = event.value
        # Fetch new data
        data = db_connection.get_produtos()
        notify(str(data), type='info')
        for row in data:
            if row['id_produto'] == selected_id:
                data = row
                break
        if data:
            # Update inputs

            nome_produto.set_value(data['nome_produto'])
            tipo_produto.set_value(data['tipo'])
            pais_produto.set_value(data['pais'])
            cidade_produto.set_value(data['cidade'])
            preco_minimo_input.set_value(data['valor_minimo'])

    def on_selection_change_cliente(event):
        selected_id = event.value
        # Fetch new data
        data = db_connection.get_clientes()
        for row in data:
            if row['id_cliente'] == selected_id:
                data = row
                break
        if data:
            # Update inputs

            nome_cliente.set_value(data['nome_cliente'])
            email_cliente.set_value(data['email_cliente'])
            telefone_cliente.set_value(data['telefone_cliente'])
            
    def on_value_change(e):

        valor_total_input.value = float(valor_passagem.value or 0) * int(qtd_passagens.value or 0) + float(valor_passagem_volta.value or 0) * int(qtd_passagens_volta.value or 0) + float(valor_total_servicos_input.value or 0) + (float(diaria_input.value or 0) * int(dias_input.value or 0))

    def on_value_change_edit(e):

        edit_inputs['valor_total_input'].value = float(edit_inputs['valor_passagem_ida'].value or 0) * int(edit_inputs['qtd_passagens_ida'].value or 0) + float(edit_inputs['valor_passagem_volta'].value or 0) * int(edit_inputs['qtd_passagens_volta'].value or 0) + float(edit_inputs['valor_total_servicos_input'].value or 0) + (float(edit_inputs['diaria_input'].value or 0) * int(edit_inputs['dias_input'].value or 0))
    
    with ui.dialog() as dialog, ui.card().classes('w-320').style('padding: 20px'):
        ui.label('Adicionar Orçamento').classes('text-lg font-bold mb-4')

        with ui.row().classes("w-full no-wrap"):
            with ui.column().classes("w-1/2 no-wrap"):
                with ui.card().classes("w-full"):

        #              ────────Produto─────────────────────

                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Produto').classes('text-lg font-medium mb-1')
                        id_produto_input = ui.select([], label='Selecione o produto', with_input=True,on_change=on_selection_change_produto).classes('w-full rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left" popup-content-style="text-align: left;" menu-class="left-align-menu"')
                        nome_produto = ui.input(label='Nome do produto', placeholder='Produto').classes('hidden').props('readonly')
                    with ui.row().classes("w-full no-wrap"):
                        with ui.column().classes('w-1/2'):
                            ui.label('Tipo do produto').classes('text-sm font-medium mb-1')
                            tipo_produto = ui.input(label='Tipo do produto', placeholder='Tipo').classes('w-full').props('readonly')
                        with ui.column().classes('w-1/2'):
                            ui.label('País').classes('text-sm font-medium mb-1')
                            pais_produto = ui.input(label='País', placeholder='País').classes('w-full').props('readonly')
                    with ui.row().classes("w-full no-wrap"):
                        with ui.column().classes('w-1/2'):
                            ui.label('Cidade').classes('text-sm font-medium mb-1')
                            cidade_produto = ui.input(label='Cidade', placeholder='Cidade').classes('w-full').props('readonly')
                        with ui.column().classes('w-1/2'):
                            ui.label('Preço mínimo').classes('text-sm font-medium mb-1')
                            preco_minimo_input = ui.number(label='Preço mínimo', placeholder='0.00', min=0, format='%.2f').props('readonly prefix=R$').classes('w-full')

        #              ─────────Voo─────────────────────────

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Voo').classes('text-lg font-medium mb-1')
                        ui.icon('flight', color="#DFDFDF", size="md").classes('ml-auto justify-self-end h-full')

                    #--------------------------------------Ida

                    with ui.expansion('Ida', icon='flight').classes('w-full no-wrap'):
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Saída').classes('text-medium font-medium mb-1')
                        ui.separator()        
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_saida = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined')
                            cidade_saida = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined')
                            aeroporto_saida = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_saida = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-1/4 rounded-md').props('outlined')
                            hora_saida = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-1/4 rounded-md').props('outlined')
                            dt_hr_saida = f'{data_saida.value}T{hora_saida.value}:00' if data_saida.value and hora_saida.value else None
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_destino = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined')
                            cidade_destino = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined')
                            aeroporto_destino = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_chegada = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-1/4 rounded-md').props('outlined') 
                            hora_chegada = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-1/4 rounded-md').props('format24h outlined')
                            dt_hr_chegada = f'{data_chegada.value}T{hora_chegada.value}:00' if data_chegada.value and hora_chegada.value else None
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            id_companhia_input = ui.select([], label='Selecione a companhia aérea', with_input=True).props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left"').classes('w-2/3 rounded-md')
                            valor_passagem = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f',on_change=on_value_change).props('prefix=R$ outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            qtd_passagens = ui.number(label='Qtd. de passagens', placeholder='0', min=0,on_change=on_value_change).props('outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            observacoes_input = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none"')

                    #--------------------------------------Volta

                    with ui.expansion('Volta', icon='flight').classes('w-full no-wrap'):
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Saída').classes('text-medium font-medium mb-1')
                        ui.separator()        
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_saida_volta = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined')
                            cidade_saida_volta = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined')
                            aeroporto_saida_volta = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_saida_volta = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-2/4 rounded-md').props('outlined')
                            hora_saida_volta = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-2/4 rounded-md').props('outlined')
                            dt_hr_saida = f'{data_saida_volta.value}T{hora_saida_volta.value}:00' if data_saida_volta.value and hora_saida_volta.value else None
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_destino_volta = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined')
                            cidade_destino_volta = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined')
                            aeroporto_destino_volta = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_chegada_volta = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-2/4 rounded-md').props('outlined') 
                            hora_chegada_volta = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-2/4 rounded-md').props('format24h outlined')
                            dt_hr_chegada_volta = f'{data_chegada.value}T{hora_chegada.value}:00' if data_chegada.value and hora_chegada.value else None
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            id_companhia_input_volta = ui.select([], label='Selecione a companhia aérea', with_input=True).props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left"').classes('w-2/3 rounded-md')
                            valor_passagem_volta = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f', on_change=on_value_change).props('prefix=R$ outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            qtd_passagens_volta = ui.number(label='Qtd. de passagens', placeholder='0', min=0, on_change=on_value_change).props('outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            observacoes_input_volta = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none"')    
                            
        #              ────────Cliente─────────────────────
            with ui.column().classes("w-1/2 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Cliente').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        id_cliente_input = ui.select([], label='Selecione o cliente', with_input=True).classes('w-2/3 rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left"')
                        ui.button('Novo cliente', on_click=lambda: adicionar_cliente.open()).classes('button button-secodary rounded-md h-full')
            
        #              ────────Hospedagem─────────────────────   
                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Hospedagem').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Endereço').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        endereco_hospedagem_input = ui.input(label='Selecione o cliente').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Diária').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        ui.label('Dias').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        diaria_input = ui.number(label='Diária', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined').classes('w-2/3 rounded-md')
                        dias_input = ui.number(label='Dias', placeholder='0', min=0, on_change=on_value_change).props('outlined').classes('w-1/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_hospedagem_input = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none"')
        #              ────────Serviços───────────────────── 

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Serviços').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Descrição').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        descricao_servico_input = ui.input(label='Descrição do serviço').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor total dos serviços').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        valor_total_servicos_input = ui.number(label='Valor total dos serviços', placeholder='0.00', min=0, format='%.2f', on_change=on_value_change).props('prefix=R$ outlined').classes('w-2/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_servico_input = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none"')

        #              ─────────Total─────────────────────────

                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        with ui.column().classes("w-full"):
                            ui.label('Valor Total').classes('text-sm font-medium mb-1')
                            valor_total_input = ui.number(label='Valor Total', placeholder='0.00',min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-full rounded-md')

        with ui.row().classes("justify-end gap-2 q-mt-lg w-full"):
            ui.button('Cadastrar', on_click=lambda: update_grid(grid_ref,
                                                                id_produto_input.value,
                                                                id_cliente_input.value,
                                                                pais_saida.value,
                                                                cidade_saida.value,
                                                                aeroporto_saida.value,
                                                                data_saida.value,
                                                                hora_saida.value,
                                                                pais_destino.value,
                                                                cidade_destino.value,
                                                                aeroporto_destino.value,
                                                                data_chegada.value,
                                                                hora_chegada.value,
                                                                valor_passagem.value,
                                                                qtd_passagens.value,
                                                                id_companhia_input.value, 
                                                                observacoes_input.value,
                                                                pais_saida_volta.value,
                                                                cidade_saida_volta.value,
                                                                aeroporto_saida_volta.value,
                                                                data_saida_volta.value,
                                                                hora_saida_volta.value,
                                                                pais_destino_volta.value,
                                                                cidade_destino_volta.value,
                                                                aeroporto_destino_volta.value,
                                                                data_chegada_volta.value,
                                                                hora_chegada_volta.value,
                                                                valor_passagem_volta.value,
                                                                qtd_passagens_volta.value,
                                                                id_companhia_input_volta.value, 
                                                                observacoes_input_volta.value,
                                                                endereco_hospedagem_input.value,
                                                                diaria_input.value,
                                                                dias_input.value,
                                                                observacoes_hospedagem_input.value,
                                                                descricao_servico_input.value,
                                                                valor_total_servicos_input.value,
                                                                observacoes_servico_input.value,
                                                                valor_total_input.value,

                                                                dialog)).classes('button button-primary').style('margin-right: 8px;')
            
            ui.button('Cancelar', on_click=lambda: dialog.close()).classes('button button-secondary')
            ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao adicionar orçamento'))
                
    
        # Load options for selects
        produtos = db_connection.get_produtos()
        id_produto_input.options = {p['id_produto']: p['nome_produto'] for p in produtos} if produtos else {}
        id_produto_input.update()
        
        companhias = db_connection.get_companhias()
        id_companhia_input.options = {c['id_companhia']: f"{c.get('nome_companhia', '')}" for c in companhias} if companhias else {}
        id_companhia_input.update()
        
        clientes = db_connection.get_clientes()
        id_cliente_input.options = {c['id_cliente']: c['nome'] for c in clientes} if clientes else {}
        id_cliente_input.update()

        # Store selected row data in a closure variable
        selected_row = {'data': None}
        
        # Store references to edit dialog inputs
        edit_inputs = {}
        
        async def on_row_selected(e):
            # Use get_selected_rows() instead of event data for reliable row selection
            selected_rows = await grid.get_selected_rows()
            
            if selected_rows:
                selected_row['data'] = selected_rows[0]
                #notify(f"Selected: Orçamento #{selected_row['data']['id_orcamento']}", type='info')
                
                # Capture values at selection time (not by reference)
                row = selected_row['data']
                id_produto = row.get('id_produto')
                nome_produto = row.get('nome_produto')
                tipo = row.get('tipo')
                pais = row.get('pais')
                cidade = row.get('cidade')
                valor_minimo = row.get('valor_minimo')
                id_cliente = row.get('id_cliente')
                valor_total = row.get('valor_total')

                endereco_hospedagem = row.get('endereco')
                diaria = row.get('diaria')
                dias = row.get('dias')
                observacoes_hospedagem = row.get('obs')

                descricao_servico = row.get('descricao')
                valor_total_servicos = row.get('valor_total_servicos')
                observacoes_servico = row.get('obs_servicos')

                
                # Clear inputs first to prevent stale values
                edit_inputs['id_produto'].value = None
                edit_inputs['nome_produto'].value = None
                edit_inputs['tipo'].value = None
                edit_inputs['pais'].value = None
                edit_inputs['cidade'].value = None
                edit_inputs['valor_minimo'].value = None
                edit_inputs['id_cliente'].value = None

                edit_inputs['pais_saida_ida'].value = None
                edit_inputs['cidade_saida_ida'].value = None
                edit_inputs['aeroporto_saida_ida'].value = None
                edit_inputs['data_saida_ida'].value = None
                edit_inputs['hora_saida_ida'].value = None
                edit_inputs['pais_destino_ida'].value = None
                edit_inputs['cidade_destino_ida'].value = None
                edit_inputs['aeroporto_destino_ida'].value = None
                edit_inputs['data_chegada_ida'].value = None
                edit_inputs['hora_chegada_ida'].value = None
                edit_inputs['valor_passagem_ida'].value = None
                edit_inputs['id_companhia_ida'].value = None
                edit_inputs['obs_ida'].value = None
                edit_inputs['qtd_passagens_ida'].value = None

                edit_inputs['pais_saida_volta'].value = None
                edit_inputs['cidade_saida_volta'].value = None
                edit_inputs['aeroporto_saida_volta'].value = None
                edit_inputs['data_saida_volta'].value = None
                edit_inputs['hora_saida_volta'].value = None
                edit_inputs['pais_destino_volta'].value = None
                edit_inputs['cidade_destino_volta'].value = None
                edit_inputs['aeroporto_destino_volta'].value = None
                edit_inputs['data_chegada_volta'].value = None
                edit_inputs['hora_chegada_volta'].value = None
                edit_inputs['valor_passagem_volta'].value = None
                edit_inputs['id_companhia_volta'].value = None
                edit_inputs['obs_volta'].value = None
                edit_inputs['qtd_passagens_volta'].value = None

                edit_inputs['endereco_hospedagem_input'].value = None
                edit_inputs['diaria_input'].value = None
                edit_inputs['dias_input'].value = None
                edit_inputs['observacoes_hospedagem_input'].value = None

                edit_inputs['descricao_servico_input'].value = None
                edit_inputs['valor_total_servicos_input'].value = None
                edit_inputs['observacoes_servico_input'].value = None

                edit_dialog.open()

                produtos = db_connection.get_produtos()
                clientes = db_connection.get_clientes()
                companhias = db_connection.get_companhias()

                voos = db_connection.get_voos_w_id(selected_rows[0]['id_orcamento'])
                data = None
                for row in voos:
                    if row['ida_volta'] == 'Ida':
                        data = row
                        break

                pais_saida_ida = data['pais_saida']
                cidade_saida_ida = data['cidade_saida']
                aeroporto_saida_ida = data['aeroporto_saida']
                pais_destino_ida = data['pais_destino']
                cidade_destino_ida = data['cidade_destino']
                aeroporto_destino_ida = data['aeroporto_destino']
                valor_passagem_ida = data['valor_passagem']
                qtd_passagens_ida = data['qtd_passagens']
                observacoes_ida = data['obs']
                id_companhia_ida = data['id_companhia']

                data = None
                for row in voos:
                    if row['ida_volta'] == 'Volta':
                        data = row
                        break

                pais_saida_volta = data['pais_saida']
                cidade_saida_volta = data['cidade_saida']            
                aeroporto_saida_volta = data['aeroporto_saida']
                pais_destino_volta = data['pais_destino']
                cidade_destino_volta = data['cidade_destino']
                aeroporto_destino_volta = data['aeroporto_destino']
                valor_passagem_volta = data['valor_passagem']
                qtd_passagens_volta = data['qtd_passagens']
                observacoes_volta = data['obs']
                id_companhia_volta = data['id_companhia']

                edit_inputs['nome_produto'].options = {p['id_produto']: p['nome_produto'] for p in produtos} if produtos else {}               
                edit_inputs['id_cliente'].options = {c['id_cliente']: f"{c['nome']}" for c in clientes} if clientes else {}
                edit_inputs['id_companhia_ida'].options = {c['id_companhia']: f"{c['nome_companhia']}" for c in companhias} if companhias else {}
                edit_inputs['id_companhia_volta'].options = {c['id_companhia']: f"{c['nome_companhia']}" for c in companhias} if companhias else {}

                # Set options before setting values
                
                # Use timer to ensure dialog renders before setting values
                ui.timer(0.05, lambda p=id_produto,
                        n=nome_produto,
                        t=tipo,
                        pa=pais,
                        ci=cidade,
                        vm=valor_minimo,
                        c=id_cliente,
                        vt=valor_total,

                        p_s_ida=pais_saida_ida,
                        c_s_ida=cidade_saida_ida,
                        a_s_ida=aeroporto_saida_ida,
                        p_dest_ida=pais_destino_ida,
                        c_dest_ida=cidade_destino_ida,
                        a_dest_ida=aeroporto_destino_ida,
                        vp_ida=valor_passagem_ida,
                        qtd_ida=qtd_passagens_ida,
                        i_comp_ida=id_companhia_ida,
                        obs_ida=observacoes_ida,

                        p_s_volta=pais_saida_volta,
                        c_s_volta=cidade_saida_volta,
                        a_s_volta=aeroporto_saida_volta,
                        p_dest_volta=pais_destino_volta,
                        c_dest_volta=cidade_destino_volta,
                        a_dest_volta=aeroporto_destino_volta,
                        vp_volta=valor_passagem_volta,
                        qtd_volta=qtd_passagens_volta,
                        i_comp_volta=id_companhia_volta,
                        obs_volta=observacoes_volta,

                        endereco_hospedagem=endereco_hospedagem,
                        diaria=diaria,
                        qtd_dias=dias,
                        obs_hospedagem=observacoes_hospedagem,

                        descricao_servico=descricao_servico,
                        valor_total_servicos=valor_total_servicos,
                        obs_servicos=observacoes_servico,

                        :
                        (
                    edit_inputs['id_produto'].set_value(p),
                    edit_inputs['nome_produto'].set_value(p),
                    edit_inputs['tipo'].set_value(t),
                    edit_inputs['pais'].set_value(pa),
                    edit_inputs['cidade'].set_value(ci),
                    edit_inputs['valor_minimo'].set_value(vm),
                    edit_inputs['id_cliente'].set_value(c),

                    edit_inputs['pais_saida_ida'].set_value(p_s_ida),
                    edit_inputs['cidade_saida_ida'].set_value(c_s_ida),
                    edit_inputs['aeroporto_saida_ida'].set_value(a_s_ida),
                    edit_inputs['pais_destino_ida'].set_value(p_dest_ida),
                    edit_inputs['cidade_destino_ida'].set_value(c_dest_ida),
                    edit_inputs['aeroporto_destino_ida'].set_value(a_dest_ida),
                    edit_inputs['valor_passagem_ida'].set_value(vp_ida),
                    edit_inputs['id_companhia_ida'].set_value(i_comp_ida),
                    edit_inputs['obs_ida'].set_value(obs_ida),
                    edit_inputs['qtd_passagens_ida'].set_value(qtd_ida),

                    edit_inputs['pais_saida_volta'].set_value(p_s_volta),
                    edit_inputs['cidade_saida_volta'].set_value(c_s_volta),
                    edit_inputs['aeroporto_saida_volta'].set_value(a_s_volta),
                    edit_inputs['pais_destino_volta'].set_value(p_dest_volta),
                    edit_inputs['cidade_destino_volta'].set_value(c_dest_volta),
                    edit_inputs['aeroporto_destino_volta'].set_value(a_dest_volta),
                    edit_inputs['valor_passagem_volta'].set_value(vp_volta),
                    edit_inputs['id_companhia_volta'].set_value(i_comp_volta),
                    edit_inputs['obs_volta'].set_value(obs_volta),
                    edit_inputs['qtd_passagens_volta'].set_value(qtd_volta),

                    edit_inputs['endereco_hospedagem_input'].set_value(endereco_hospedagem),
                    edit_inputs['diaria_input'].set_value(diaria),
                    edit_inputs['dias_input'].set_value(dias),
                    edit_inputs['observacoes_hospedagem_input'].set_value(observacoes_hospedagem),

                    edit_inputs['descricao_servico_input'].set_value(descricao_servico),
                    edit_inputs['valor_total_servicos_input'].set_value(valor_total_servicos),
                    edit_inputs['observacoes_servico_input'].set_value(observacoes_servico),

                    edit_inputs['valor_total_input'].set_value(vt)

                ), once=True)
        
        grid.on('cellClicked', on_row_selected)
    
        def on_selection_change_edit(event):
            selected_id = event.value
            if selected_id is None:
                return
    
            data = None
            orcamentos = db_connection.get_produtos()
            
            for row in orcamentos:
                if row['id_produto'] == selected_id:
                    data = row
                    break
            
            if data is None:
                return  # No match found
            notify(data['id_produto'], type='info')
            notify(f"ID do Produto selecionado: {data['id_produto']}", type='success')
            edit_inputs['id_produto'].set_value(data['id_produto'])
            edit_inputs['pais'].set_value(data['pais'])
            edit_inputs['cidade'].set_value(data['cidade'])
            edit_inputs['tipo'].set_value(data['tipo'])
            edit_inputs['valor_minimo'].set_value(data['valor_minimo'])
            

    with ui.dialog() as edit_dialog, ui.card().classes('w-320').style('padding: 20px'):
        ui.label('Editar Orçamento').classes('text-lg font-bold mb-4')
        with ui.row().classes("w-full no-wrap"):
            with ui.column().classes("w-1/2 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                            ui.label('Produto').classes('text-lg font-medium mb-1')
                            edit_inputs['nome_produto'] = ui.select([], label='Selecione o produto', with_input=True,on_change=on_selection_change_edit).classes('w-full rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left" popup-content-style="text-align: left;" menu-class="left-align-menu"')
                            edit_inputs['id_produto'] = ui.input(label='ID do produto', placeholder='ID').classes('hidden').props('readonly')
                    with ui.row().classes("w-full no-wrap"):
                        with ui.column().classes('w-1/2'):
                            ui.label('Tipo do produto').classes('text-sm font-medium mb-1')
                            edit_inputs['tipo'] = ui.input(label='Tipo do produto', placeholder='Tipo').classes('w-full').props('readonly')
                        with ui.column().classes('w-1/2'):
                            ui.label('País').classes('text-sm font-medium mb-1')
                            edit_inputs['pais'] = ui.input(label='País', placeholder='País').classes('w-full').props('readonly')
                    with ui.row().classes("w-full no-wrap"):
                        with ui.column().classes('w-1/2'):
                            ui.label('Cidade').classes('text-sm font-medium mb-1')
                            edit_inputs['cidade'] = ui.input(label='Cidade', placeholder='Cidade').classes('w-full').props('readonly')
                        with ui.column().classes('w-1/2'):
                            ui.label('Preço mínimo').classes('text-sm font-medium mb-1')
                            edit_inputs['valor_minimo'] = ui.number(label='Preço mínimo', placeholder='0.00', min=0, format='%.2f').props('readonly prefix=R$').classes('w-full')
                            

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Voo').classes('text-lg font-medium mb-1')
                        ui.icon('flight', color="#DFDFDF", size="md").classes('ml-auto justify-self-end h-full')
                        edit_inputs['id_voo'] = ui.input(label='ID do voo', placeholder='ID').classes('hidden').props('readonly')

                #---------------------------------------Ida---------------------------------------#
                        
                    with ui.expansion('Ida', icon='flight').classes('w-full no-wrap'):
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Saída').classes('text-medium font-medium mb-1')
                        ui.separator()        
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['pais_saida_ida'] = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined')
                            edit_inputs['cidade_saida_ida'] = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined')
                            edit_inputs['aeroporto_saida_ida'] = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['data_saida_ida'] = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-1/4 rounded-md').props('outlined')
                            edit_inputs['hora_saida_ida'] = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-1/4 rounded-md').props('outlined')
                            dt_hr_saida = f'{edit_inputs['data_saida_ida'].value}T{edit_inputs["hora_saida_ida"].value}:00' if edit_inputs['data_saida_ida'].value and edit_inputs["hora_saida_ida"].value else None
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['pais_destino_ida'] = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined')
                            edit_inputs['cidade_destino_ida'] = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined')
                            edit_inputs['aeroporto_destino_ida'] = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['data_chegada_ida'] = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-1/4 rounded-md').props('outlined') 
                            edit_inputs['hora_chegada_ida'] = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-1/4 rounded-md').props('format24h outlined')
                        
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['id_companhia_ida'] = ui.select([], label='Selecione a companhia aérea', with_input=True).props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left"').classes('w-2/3 rounded-md')
                            edit_inputs['valor_passagem_ida'] = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f',on_change=on_value_change_edit).props('prefix=R$ outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['qtd_passagens_ida'] = ui.number(label='Qtd. de passagens', placeholder='0', min=0, on_change=on_value_change_edit).props('outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            edit_inputs['obs_ida'] = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none"')

            #--------------------------------------Volta---------------------------------------#

                    with ui.expansion('Volta', icon='flight').classes('w-full no-wrap'):
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Saída').classes('text-medium font-medium mb-1')
                        ui.separator()        
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['pais_saida_volta'] = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined')
                            edit_inputs['cidade_saida_volta'] = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined')
                            edit_inputs['aeroporto_saida_volta'] = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['data_saida_volta'] = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-2/4 rounded-md').props('outlined')
                            edit_inputs['hora_saida_volta'] = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-2/4 rounded-md').props('outlined')
                            edit_inputs['dt_hr_saida'] = f'{edit_inputs["data_saida_volta"].value}T{edit_inputs["hora_saida_volta"].value}:00' if edit_inputs["data_saida_volta"].value and edit_inputs["hora_saida_volta"].value else None
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['pais_destino_volta'] = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined')
                            edit_inputs['cidade_destino_volta'] = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined')
                            edit_inputs['aeroporto_destino_volta'] = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['data_chegada_volta'] = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-2/4 rounded-md').props('outlined') 
                            edit_inputs['hora_chegada_volta'] = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-2/4 rounded-md').props('format24h outlined')
                            edit_inputs['dt_hr_chegada_volta'] = f'{edit_inputs["data_chegada_volta"].value}T{edit_inputs["hora_chegada_volta"].value}:00' if edit_inputs["data_chegada_volta"].value and edit_inputs["hora_chegada_volta"].value else None
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['id_companhia_volta'] = ui.select([], label='Selecione a companhia aérea', with_input=True).props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left"').classes('w-2/3 rounded-md')
                            edit_inputs['valor_passagem_volta'] = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f',on_change=on_value_change_edit).props('prefix=R$ outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            edit_inputs['qtd_passagens_volta'] = ui.number(label='Qtd. de passagens', placeholder='0', min=0, on_change=on_value_change_edit).props('outlined').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            edit_inputs['obs_volta'] = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none"')
                    
                
#              ────────Cliente─────────────────────

            with ui.column().classes("w-1/2 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Cliente').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        edit_inputs['id_cliente'] = ui.select([], label='Selecione o cliente', with_input=True).classes('w-2/3 rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left"')
                        ui.button('Novo cliente', on_click=lambda: adicionar_cliente.open()).classes('button button-secodary rounded-md h-full')

#              ────────Hospedagem─────────────────────  
             
                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Hospedagem').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Endereço').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        edit_inputs['endereco_hospedagem_input'] = ui.input(label='Endereço', placeholder='Endereço').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Diária').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        ui.label('Dias').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        edit_inputs['diaria_input'] = ui.number(label='Diária', placeholder='0.00', min=0, format='%.2f', on_change=on_value_change_edit).props('prefix=R$ outlined').classes('w-2/3 rounded-md')
                        edit_inputs['dias_input'] = ui.number(label='Dias', placeholder='0', min=0, on_change=on_value_change_edit).props('outlined').classes('w-1/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        edit_inputs['observacoes_hospedagem_input'] = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none"')

#              ────────Serviços───────────────────── 

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Serviços').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Descrição').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        edit_inputs['descricao_servico_input'] = ui.input(label='Descrição do serviço').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor total dos serviços').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        edit_inputs['valor_total_servicos_input'] = ui.number(label='Valor total dos serviços', placeholder='0.00', min=0, format='%.2f', on_change=on_value_change_edit).props('prefix=R$ outlined').classes('w-2/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        edit_inputs['observacoes_servico_input'] = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none"')

        #              ─────────Total─────────────────────────

                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        with ui.column().classes("w-full"):
                            ui.label('Valor Total').classes('text-sm font-medium mb-1')
                            edit_inputs['valor_total_input'] = ui.number(label='Valor Total', placeholder='0.00',min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-full rounded-md')

                
        with ui.row().classes("justify-end gap-2 q-mt-lg w-full"):
            ui.button('Confirmar', on_click=lambda: edit_orcamento(grid_ref,
                                                                    edit_inputs['id_produto'].value,
                                                                    edit_inputs['id_cliente'].value,

                                                                    edit_inputs['pais_saida_ida'].value,
                                                                    edit_inputs['cidade_saida_ida'].value,
                                                                    edit_inputs['aeroporto_saida_ida'].value,
                                                                    edit_inputs['data_saida_ida'].value,
                                                                    edit_inputs['hora_saida_ida'].value,
                                                                    edit_inputs['pais_destino_ida'].value,
                                                                    edit_inputs['cidade_destino_ida'].value,
                                                                    edit_inputs['aeroporto_destino_ida'].value,
                                                                    edit_inputs['data_chegada_ida'].value,
                                                                    edit_inputs['hora_chegada_ida'].value,
                                                                    edit_inputs['valor_passagem_ida'].value,
                                                                    edit_inputs['qtd_passagens_ida'].value,
                                                                    edit_inputs['id_companhia_ida'].value,
                                                                    edit_inputs['obs_ida'].value,

                                                                    edit_inputs['pais_saida_volta'].value,
                                                                    edit_inputs['cidade_saida_volta'].value,
                                                                    edit_inputs['aeroporto_saida_volta'].value,
                                                                    edit_inputs['data_saida_volta'].value,
                                                                    edit_inputs['hora_saida_volta'].value,
                                                                    edit_inputs['pais_destino_volta'].value,
                                                                    edit_inputs['cidade_destino_volta'].value,
                                                                    edit_inputs['aeroporto_destino_volta'].value,
                                                                    edit_inputs['data_chegada_volta'].value,
                                                                    edit_inputs['hora_chegada_volta'].value,
                                                                    edit_inputs['valor_passagem_volta'].value,
                                                                    edit_inputs['qtd_passagens_volta'].value,
                                                                    edit_inputs['id_companhia_volta'].value,
                                                                    edit_inputs['obs_volta'].value,

                                                                    edit_inputs['endereco_hospedagem_input'].value,
                                                                    edit_inputs['diaria_input'].value,
                                                                    edit_inputs['dias_input'].value,
                                                                    edit_inputs['observacoes_hospedagem_input'].value,

                                                                    edit_inputs['descricao_servico_input'].value,
                                                                    edit_inputs['valor_total_servicos_input'].value,
                                                                    edit_inputs['observacoes_servico_input'].value,

                                                                    edit_inputs['valor_total_input'].value,
                                                                    edit_dialog,
                                                                    selected_row)).classes('button button-primary').style('margin-right: 8px;')
            ui.button('Cancelar', on_click=lambda: edit_dialog.close()).classes('button button-secondary')
            ui.button('Excluir', on_click=lambda: delete_selected(grid_ref, selected_row, edit_dialog),color='red').classes('button button-danger ml-auto').style('margin-right: 8px;')
            ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao editar orçamento'))
        
        # Load options for edit selects
        produtos = db_connection.get_produtos()
        edit_inputs['nome_produto'].options = {p['id_produto']: p['nome_produto'] for p in produtos} if produtos else {}

        clientes = db_connection.get_clientes()
        edit_inputs['id_cliente'].options = {c['id_cliente']: f"{c['nome']}" for c in clientes} if clientes else {}

        with ui.dialog() as adicionar_cliente, ui.card().classes('w-160').style('padding: 20px'):
            ui.label('Adicionar Cliente').classes('text-lg font-bold mb-4')
            with ui.row().classes("w-full"):
                with ui.row().classes('w-full no-wrap'):
                    ui.label('Nome completo').classes('text-sm font-medium mb-1 w-3/4 align-self-start')
                    ui.label('Sexo').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                with ui.row().classes("w-full no-wrap"):
                    nome_cliente_input = ui.input(label='Nome do cliente', placeholder='Nome do cliente').classes('w-3/4').props('outlined rounded')
                    sexo_cliente_input = ui.select(['F', 'M'], label='Sexo').classes('w-1/4').props('outlined rounded')
                    
                with ui.row().classes('w-full no-wrap'):
                    ui.label('CPF').classes('text-sm font-medium mb-1 w-2/6 align-self-start')
                    ui.label('Data de nascimento').classes('text-sm font-medium mb-1 w-2/6 align-self-start')
                    ui.label('Telefone').classes('text-sm font-medium mb-1 w-2/6 align-self-start')
                with ui.row().classes('w-full no-wrap'):
                    cpf_cliente_input = ui.input(label='CPF', placeholder='CPF').classes('w-2/6').props('mask="###.###.###-##" unmasked-value outlined rounded')
                    data_nascimento_input = ui.date_input(label='Data de nascimento', placeholder='Data de nascimento').classes('w-2/6').props('outlined rounded')
                    telefone_cliente_input = ui.input(label='Telefone', placeholder='Telefone').classes('w-2/6').props('mask="(##) #####-####" unmasked-value outlined rounded')
                
            with ui.row().classes("justify-end gap-2 q-mt-lg w-full"):
                    ui.button('Adicionar', on_click=lambda: db_connection.add_cliente(nome_cliente_input.value, sexo_cliente_input.value, data_nascimento_input.value, cpf_cliente_input.value, telefone_cliente_input.value, adicionar_cliente, edit_inputs['id_cliente'])).classes('button button-primary').style('margin-right: 8px;')
                    ui.button('Cancelar', on_click=lambda: adicionar_cliente.close()).classes('button button-secondary')

        
        
        

            
def update_grid(grid_ref,
                id_produto,
                id_cliente,

                pais_saida_ida,
                cidade_saida_ida,
                aeroporto_saida_ida,
                data_saida_ida,
                hora_saida_ida,
                pais_destino_ida,
                cidade_destino_ida,
                aeroporto_destino_ida,
                data_chegada_ida,
                hora_chegada_ida,
                valor_passagem_ida,
                qtd_passagens_ida,
                id_companhia_ida,
                obs_ida,
                pais_saida_volta,
                cidade_saida_volta,
                aeroporto_saida_volta,
                data_saida_volta,
                hora_saida_volta,
                pais_destino_volta,
                cidade_destino_volta,
                aeroporto_destino_volta,
                data_chegada_volta,
                hora_chegada_volta,
                valor_passagem_volta,
                qtd_passagens_volta,
                id_companhia_volta,
                obs_volta,

                endereco_hospedagem,
                diaria,
                qtd_dias,
                obs_hospedagem,

                descricao_servico,
                valor_total_servicos,
                obs_servicos,

                valor_total,
                dialog):

    dt_hr_chegada_ida = f'{data_chegada_ida}T{hora_chegada_ida}:00' if data_chegada_ida and hora_chegada_ida else None
    dt_hr_saida_ida = f'{data_saida_ida}T{hora_saida_ida}:00' if data_saida_ida and hora_saida_ida else None

    dt_hr_chegada_volta = f'{data_chegada_volta}T{hora_chegada_volta}:00' if data_chegada_volta and hora_chegada_volta else None
    dt_hr_saida_volta = f'{data_saida_volta}T{hora_saida_volta}:00' if data_saida_volta and hora_saida_volta else None

    db_connection.add_orcamento(id_produto,
                                id_cliente,
                                pais_saida_ida,
                                cidade_saida_ida,
                                aeroporto_saida_ida,
                                dt_hr_saida_ida,
                                pais_destino_ida,
                                cidade_destino_ida,
                                aeroporto_destino_ida,
                                dt_hr_chegada_ida,
                                valor_passagem_ida,
                                qtd_passagens_ida,
                                id_companhia_ida,
                                obs_ida,
                                pais_saida_volta,
                                cidade_saida_volta,
                                aeroporto_saida_volta,
                                dt_hr_saida_volta,
                                pais_destino_volta,
                                cidade_destino_volta,
                                aeroporto_destino_volta,
                                dt_hr_chegada_volta,
                                valor_passagem_volta,
                                qtd_passagens_volta,
                                id_companhia_volta,
                                obs_volta,
                                endereco_hospedagem,
                                diaria,
                                qtd_dias,
                                obs_hospedagem,
                                descricao_servico,
                                valor_total_servicos,
                                obs_servicos,
                                valor_total)
    dialog.close()
    
    novos_valores = format_orcamentos_for_grid(db_connection.teste_get_orcamentos())
    
    # Update AG Grid Data
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

def edit_orcamento(grid_ref,
                    id_produto,
                    id_cliente,
                    
                    pais_saida_ida,
                    cidade_saida_ida,
                    aeroporto_saida_ida,
                    data_saida_ida,
                    hora_saida_ida,
                    pais_destino_ida,
                    cidade_destino_ida,
                    aeroporto_destino_ida,
                    data_chegada_ida,
                    hora_chegada_ida,
                    valor_passagem_ida,
                    qtd_passagens_ida,
                    id_companhia_ida,
                    obs_ida,

                    pais_saida_volta,
                    cidade_saida_volta,
                    aeroporto_saida_volta,
                    data_saida_volta,
                    hora_saida_volta,
                    pais_destino_volta,
                    cidade_destino_volta,  
                    aeroporto_destino_volta,
                    data_chegada_volta,
                    hora_chegada_volta,
                    valor_passagem_volta,
                    qtd_passagens_volta,
                    id_companhia_volta,
                    obs_volta,

                    endereco_hospedagem,
                    diaria,
                    qtd_dias,
                    obs_hospedagem,

                    descricao_servico,
                    valor_total_servicos,
                    obs_servicos,

                    valor_total,

                    dialog,
                    selected_row):

    dt_hr_chegada_ida = f'{data_chegada_ida}T{hora_chegada_ida}:00' if data_chegada_ida and hora_chegada_ida else None
    dt_hr_saida_ida = f'{data_saida_ida}T{hora_saida_ida}:00' if data_saida_ida and hora_saida_ida else None

    dt_hr_chegada_volta = f'{data_chegada_volta}T{hora_chegada_volta}:00' if data_chegada_volta and hora_chegada_volta else None
    dt_hr_saida_volta = f'{data_saida_volta}T{hora_saida_volta}:00' if data_saida_volta and hora_saida_volta else None

    row_data = selected_row['data']
    if not row_data:
        ui.notify('Nenhum orçamento selecionado', type='warning')
        return
    
    id_orcamento = row_data.get('id_orcamento')
    id_hospedagem = row_data.get('id_hospedagem')
    id_servico = row_data.get('id_servico')

    db_connection.update_orcamento(id_produto,
                                    id_cliente,
                                    id_orcamento,
                                    
                                    
                                    pais_saida_ida,
                                    cidade_saida_ida,
                                    aeroporto_saida_ida,
                                    dt_hr_saida_ida,
                                    pais_destino_ida,
                                    cidade_destino_ida,
                                    aeroporto_destino_ida,
                                    dt_hr_chegada_ida,
                                    valor_passagem_ida,
                                    qtd_passagens_ida,
                                    id_companhia_ida,
                                    obs_ida,

                                    pais_saida_volta,
                                    cidade_saida_volta,
                                    aeroporto_saida_volta,
                                    dt_hr_saida_volta,
                                    pais_destino_volta,
                                    cidade_destino_volta,  
                                    aeroporto_destino_volta,
                                    dt_hr_chegada_volta,
                                    valor_passagem_volta,
                                    qtd_passagens_volta,
                                    id_companhia_volta,
                                    obs_volta,

                                    id_hospedagem,
                                    endereco_hospedagem,
                                    diaria,
                                    qtd_dias,
                                    obs_hospedagem,

                                    id_servico,
                                    descricao_servico,
                                    valor_total_servicos,
                                    obs_servicos,

                                    valor_total,
                                    )
    dialog.close()
    
    novos_valores = format_orcamentos_for_grid(db_connection.teste_get_orcamentos())
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

async def delete_selected(grid_ref, selected_row, edit_dialog):

    row_data = selected_row['data']
    grid = grid_ref.get('grid')
    id_orcamento = row_data.get('id_orcamento')
    id_hospedagem = row_data.get('id_hospedagem')
    id_servico = row_data.get('id_servico')

    with ui.dialog() as dialog, ui.card().classes('p-7'):
        
        ui.label('Deseja excluir o orçamento?')
        with ui.row(align_items='center').classes('w-full justify-center'):
            ui.button('Confirmar', on_click=lambda: dialog.submit(True))
            ui.button('Cancelar', on_click=lambda: dialog.submit(False))

    result = await dialog

    if result == True:

        db_connection.delete_orcamento(id_orcamento,id_hospedagem,id_servico)
        data = format_orcamentos_for_grid(db_connection.teste_get_orcamentos())
        grid.options['rowData'] = data
        grid.update()
        ui.notify('Orçamento excluído com sucesso', type='info')
    
    else :
        ui.notify('Operação cancelada', type='info')

    edit_dialog.close()


