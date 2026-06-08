from nicegui import ui,app,APIRouter,events
from modules import db_connection
from services.notifications import notify
import re
import datetime


@ui.page('/vendas')

def content() -> None:

    ui.add_head_html('<style>.ag-row { cursor: pointer; }</style>')
    ui.add_head_html('<style>.ag-theme-balham { overflow: visible !important; }</style>')
    ui.add_head_html('''
                        <style>
                        .cell-fail { background-color: #ef4444; font-weight: bold; color: white; }
                        .cell-pass { background-color: #4caf50; font-weight: bold; color: white; }
                        .cell-pending { background-color: #f59e0b; font-weight: bold; color: white; }
                        </style>
                        ''')

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Vendas').classes('page-title').style('color: #3393F1 !important;')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Atualizar', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')
    

    column_defs = [
        {'field': 'id_venda', 'headerName': 'Venda #', 'sortable': True, 'editable': False, 'sort': 'desc'},
        {'field': 'data_venda', 'headerName': 'Data da Venda', 'sortable': True, 'editable': True,'filter': 'agDateColumnFilter', 'valueFormatter': 'value ? value.split("-").reverse().join("/") : "N/A"'},
        {'field': 'id_orcamento', 'headerName': 'Orcamento #', 'sortable': True, 'editable': True},
        {'field': 'nome', 'headerName': 'Cliente', 'sortable': True, 'editable': True, 'wrapText': False,  'cellStyle': {'white-space': 'nowrap' }},
        {'field': 'valor_total', 'headerName': 'Valor Total', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'forma_pgto', 'headerName': 'Forma de Pagamento', 'sortable': True, 'editable': True},
        {'field': 'entrada', 'headerName': 'Entrada', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'n_parcelas', 'headerName': 'Número de Parcelas', 'sortable': True, 'editable': True},
        {'field': 'valor_parcelas', 'headerName': 'Valor das Parcelas', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'comissao', 'headerName': 'Comissão', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'valor_final', 'headerName': 'Valor Total', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'status_venda','headerName': 'Status','editable': True, 'cellEditor': 'agSelectCellEditor',  'cellEditorParams': {'values': ['Pendente', 'Concluída', 'Cancelada']},'singleClickEdit': True,'cellClassRules': {
            'cell-fail': 'x === "Cancelada"',
            'cell-pass': 'x === "Concluída"',
            'cell-pending': 'x === "Pendente"',
        }},
        {'field': 'valor_total_gasto', 'headerName': 'Valor Total Gasto', 'sortable': True, 'editable': False, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},

    ]

    grid_ref = {}
    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Buscar…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')
    
    

    with ui.column().classes('w-full flex-grow').style('height: calc(100vh - 400px); overflow-y: auto;'):

        grid = ui.aggrid({
            'columnDefs': column_defs,
            'rowData': db_connection.get_vendas(),
            'defaultColDef': {'sortable': True,'singleClickEdit': True},
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
        
        
        

    def on_selection_change_orcamento(event):
        
        selected_id = event.value
        # Fetch new data
        data = db_connection.teste_get_orcamentos()
        # notify(str(data), type='info')
        for row in data:
            if row['id_orcamento'] == selected_id:
                data = row
                notify(f"Orcamento selecionado: {data['id_orcamento']}, {data['pais_saida_ida']}, {data['cidade_saida_ida']}, {data['aeroporto_saida_ida']}", type='success')
                break
        if data:

            # Update inputs

            nome_produto.set_value(data['nome_produto'])
            tipo_produto.set_value(data['tipo'])
            pais_produto.set_value(data['pais'])
            cidade_produto.set_value(data['cidade'])
            preco_minimo_input.set_value(data['valor_minimo'])
            id_cliente.set_value(data['id_cliente'])
            nome_cliente.set_value(data['nome'])
            sexo_cliente.set_value(data['sexo'])
            cpf_cliente.set_value(data['cpf'])
            data_nascimento.set_value(data['data_nascimento'])
            telefone_cliente.set_value(data['telefone'])

            pais_saida_ida.set_value(data['pais_saida_ida'])
            cidade_saida_ida.set_value(data['cidade_saida_ida'])
            aeroporto_saida_ida.set_value(data['aeroporto_saida_ida'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino_ida.set_value(data['pais_destino_ida'])
            cidade_destino_ida.set_value(data['cidade_destino_ida'])
            aeroporto_destino_ida.set_value(data['aeroporto_destino_ida'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            companhia_ida.set_value(data['nome_companhia_ida'])
            valor_passagem_ida.set_value(data['valor_passagem_ida'])
            qtd_passagens_ida.set_value(data['qtd_passagens_ida'])
            observacoes_ida.set_value(data['obs_ida'])

            pais_saida_volta.set_value(data['pais_saida_volta'])
            cidade_saida_volta.set_value(data['cidade_saida_volta'])
            aeroporto_saida_volta.set_value(data['aeroporto_saida_volta'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino_volta.set_value(data['pais_destino_volta'])
            cidade_destino_volta.set_value(data['cidade_destino_volta'])
            aeroporto_destino_volta.set_value(data['aeroporto_destino_volta'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            companhia_volta.set_value(data['nome_companhia_volta'])
            valor_passagem_volta.set_value(data['valor_passagem_volta'])
            qtd_passagens_volta.set_value(data['qtd_passagens_volta'])
            observacoes_volta.set_value(data['obs_volta'])

            endereco_hospedagem_input.set_value(data['endereco'])
            diaria_input.set_value(data['diaria'])
            dias_input.set_value(data['dias'])
            observacoes_hospedagem_input.set_value(data['obs'])

            descricao_servico_input.set_value(data['descricao'])
            valor_total_servicos_input.set_value(data['valor_total_servicos'])
            observacoes_servico_input.set_value(data['obs_servicos'])
        

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', on_click=lambda: add_venda_dialog.open(), color='primary').props('fab')
    
    def on_comissao_change(e):
        valor_final_input.value = float(valor_total_servicos_input.value) + (int(qtd_passagens_ida.value) * float(valor_passagem_ida.value)) + (int(qtd_passagens_volta.value) * float(valor_passagem_volta.value)) + (int(dias_input.value) * float(diaria_input.value)) + (float(comissao_input.value) if comissao_input.value else 0)
    
    def on_parcelas_change(e):
        if parcelas_input.value and valor_final_input.value:
            valor_parcelas_input.value = (float(valor_final_input.value)-float(entrada_input.value or 0)) / int(parcelas_input.value)
        else:
            valor_parcelas_input.value = 0.00

    with ui.dialog() as add_venda_dialog, ui.card().classes('w-400').style('padding: 20px'):
        with ui.row().classes('w-full'):
            ui.label('Adicionar Venda').classes('text-xl font-bold mb-4')
            ui.separator()
            ui.label('Selecione o orçamento').classes('text-md font-medium mb-1')
        with ui.row().classes('w-full'):    
            id_orcamento_input = ui.select([], label='Selecione o orçamento', with_input=True,on_change=on_selection_change_orcamento).classes('w-' \
            '100 rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left" popup-content-style="text-align: left;" menu-class="left-align-menu"')
        with ui.row().classes('w-full no-wrap'):
            
            with ui.column().classes("w-1/3 no-wrap"):
                #       ────────Produto─────────────────────

                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Produto').classes('text-sm font-medium mb-1')
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
                            pais_saida_ida = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined readonly')
                            cidade_saida_ida = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined readonly')
                            aeroporto_saida_ida = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined readonly')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_saida_ida = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-1/4 rounded-md').props('outlined readonly')
                            hora_saida_ida = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-1/4 rounded-md').props('outlined readonly')
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_destino_ida = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            cidade_destino_ida = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            aeroporto_destino_ida = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_chegada_ida = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-1/4 rounded-md').props('outlined readonly')
                            hora_chegada = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-1/4 rounded-md').props('format24h outlined readonly')
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            companhia_ida = ui.input(label='Companhia aérea').props('outlined readonly').classes('w-2/3 rounded-md')
                            valor_passagem_ida = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            qtd_passagens_ida = ui.number(label='Qtd. de passagens', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            observacoes_ida = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none" readonly')

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
                            pais_saida_volta = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined readonly')
                            cidade_saida_volta = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined readonly')
                            aeroporto_saida_volta = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined readonly')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_saida_volta = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-2/4 rounded-md').props('outlined readonly')
                            hora_saida_volta = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-2/4 rounded-md').props('outlined readonly format24h')
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_destino_volta = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            cidade_destino_volta = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            aeroporto_destino_volta = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_chegada_volta = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-2/4 rounded-md').props('outlined readonly') 
                            hora_chegada_volta = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-2/4 rounded-md').props('format24h outlined readonly')
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            companhia_volta = ui.input(label='Companhia aérea').props('outlined readonly').classes('w-2/3 rounded-md')
                            valor_passagem_volta = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            qtd_passagens_volta = ui.number(label='Qtd. de passagens', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            observacoes_volta = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none" readonly')    
                            

        
        #              ────────Cliente─────────────────────
            with ui.column().classes("w-1/3 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Cliente').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        id_cliente = ui.input(label='ID do cliente', placeholder='ID do cliente').classes('hidden')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Nome completo').classes('text-sm font-medium mb-1 w-3/4 align-self-start')
                        ui.label('Sexo').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                    with ui.row().classes("w-full no-wrap"):
                        nome_cliente = ui.input(label='Nome do cliente', placeholder='Nome do cliente').classes('w-3/4 rounded-md').props('outlined readonly')
                        sexo_cliente = ui.select(['F', 'M'], label='Sexo').classes('w-1/4 rounded-md').props('outlined readonly')
                        
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('CPF').classes('text-sm font-medium mb-1 w-3/6 align-self-start')
                        ui.label('Data de nascimento').classes('text-sm font-medium mb-1 w-3/6 align-self-start rounded-md').props('readonly outlined')
                        
                    with ui.row().classes('w-full no-wrap'):
                        cpf_cliente = ui.input(label='CPF', placeholder='CPF').classes('w-3/6 rounded-md').props('mask="###.###.###-##" unmasked-value outlined  readonly')
                        data_nascimento = ui.input(label='Data de nascimento', placeholder='Data de nascimento').classes('w-3/6 rounded-md').props('outlined readonly')
                        
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Telefone').classes('text-sm font-medium mb-1 w-2/6 align-self-start')

                    with ui.row().classes('w-full no-wrap'):
                        telefone_cliente = ui.input(label='Telefone', placeholder='Telefone').classes('w-2/6 rounded-md').props('mask="(##) #####-####" unmasked-value outlined readonly')

                #              ────────Hospedagem─────────────────────   

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Hospedagem').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Endereço').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        endereco_hospedagem_input = ui.input(label='Selecione o cliente').classes('w-full rounded-md').props('outlined readonly')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Diária').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        ui.label('Dias').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        diaria_input = ui.number(label='Diária', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')
                        dias_input = ui.number(label='Dias', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_hospedagem_input = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none" readonly')

        #              ────────Serviços───────────────────── 

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Serviços').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Descrição').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        descricao_servico_input = ui.input(label='Descrição do serviço').classes('w-full rounded-md').props('outlined readonly')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor total dos serviços').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        valor_total_servicos_input = ui.number(label='Valor total dos serviços', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_servico_input = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none" readonly')

        #              ────────Venda─────────────────────
            
        
            with ui.column().classes("w-2/7 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Venda').classes('text-lg font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        ui.label('Data da venda').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        data_venda_input = ui.date_input(label='Data da venda', placeholder='Data da venda',value=datetime.datetime.now().strftime('%Y-%m-%d')).classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('gap-2 w-1/2'):
                        ui.label('Comissão').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        comissao_input = ui.number(label='Comissão', placeholder='0.00', min=0, format='%.2f', on_change=on_comissao_change).props('prefix=R$ unmasked-value').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('gap-2 w-full h-20'):
                        ui.space()
                        ui.separator()
                        ui.space()
                    with ui.row().classes('gap-2 w-full justify-end'):
                        ui.label('Valor final').classes('text-lg font-bold mb-1')
                    with ui.row().classes('gap-2 w-full justify-end'):
                        valor_final_input = ui.number(label='Valor final', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ unmasked-value').classes('w-1/2 text-l font-bold rounded-md').props('readonly input-class="text-right text-lg"')
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Entrada').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-2/3'):
                        entrada_input = ui.number(label='Entrada', placeholder='0.00', min=0, format='%.2f', on_change=on_comissao_change).props('prefix=R$ unmasked-value').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Forma de pagamento').classes('text-sm font-medium mb-1 w-2/3')
                        ui.label('Parcelas').classes('text-sm font-medium mb-1 w-1/3')
                    with ui.row().classes('w-full no-wrap'):
                        forma_pgto_input = ui.select(['Boleto', 'Cartão de crédito', 'Cartão de débito','PIX','Dinheiro'], label='Forma de pagamento').classes('text-sm font-medium mb-1 w-2/3 rounded-md').props('outlined')
                        parcelas_input = ui.number(label='Número de parcelas', placeholder='0', min=0, on_change=on_parcelas_change).props('outlined').classes('w-1/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor das parcelas').classes('text-sm font-medium mb-1 w-2/3')
                    with ui.row().classes('w-full no-wrap'):
                        valor_parcelas_input = ui.number(label='Valor das parcelas', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')

        with ui.row().classes("justify-end gap-2 q-mt-lg"):
                    ui.button('Cadastrar', on_click=lambda: update_grid(grid_ref, data_venda_input.value, id_orcamento_input.value, forma_pgto_input.value, valor_final_input.value, entrada_input.value, parcelas_input.value, valor_parcelas_input.value, comissao_input.value, add_venda_dialog)).classes('button button-primary').style('margin-right: 8px;')
                    ui.button('Cancelar', on_click=lambda: add_venda_dialog.close()).classes('button button-secondary')
                    ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao adicionar produto'))
                    
        

            

    orcamentos = db_connection.get_orcamento_simplificado()
    id_orcamento_input.options = {o['id_orcamento']: "Orçamento #"+str(o['id_orcamento'])+" - "+o['nome'] for o in orcamentos} if orcamentos else {}
    id_orcamento_input.update()

    selected_row = {'data': None}

    def on_selection_change_orcamento_edit(event):
        
        selected_id = event.value
        # Fetch new data
        if not selected_id:
            return
        data = db_connection.teste_get_orcamentos()
        # notify(str(data), type='info')
        
        for row in data:
            if row['id_orcamento'] == selected_id:
                data = row
                notify(f"Orcamento selecionado: {data['id_orcamento']}, {data['pais_saida_ida']}, {data['cidade_saida_ida']}, {data['aeroporto_saida_ida']}", type='success')
                break
        if data:

            # Update inputs

            nome_produto_edit.set_value(data['nome_produto'])
            tipo_produto_edit.set_value(data['tipo'])
            pais_produto_edit.set_value(data['pais'])
            cidade_produto_edit.set_value(data['cidade'])
            preco_minimo_input_edit.set_value(data['valor_minimo'])
            id_cliente_edit.set_value(data['id_cliente'])
            nome_cliente_edit.set_value(data['nome'])
            sexo_cliente_edit.set_value(data['sexo'])
            cpf_cliente_edit.set_value(data['cpf'])
            data_nascimento_edit.set_value(data['data_nascimento'])
            telefone_cliente_edit.set_value(data['telefone'])

            pais_saida_ida_edit.set_value(data['pais_saida_ida'])
            cidade_saida_ida_edit.set_value(data['cidade_saida_ida'])
            aeroporto_saida_ida_edit.set_value(data['aeroporto_saida_ida'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino_ida_edit.set_value(data['pais_destino_ida'])
            cidade_destino_ida_edit.set_value(data['cidade_destino_ida'])
            aeroporto_destino_ida_edit.set_value(data['aeroporto_destino_ida'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            companhia_ida_edit.set_value(data['nome_companhia_ida'])
            valor_passagem_ida_edit.set_value(data['valor_passagem_ida'])
            qtd_passagens_ida_edit.set_value(data['qtd_passagens_ida'])
            observacoes_ida_edit.set_value(data['obs_ida'])

            pais_saida_volta_edit.set_value(data['pais_saida_volta'])
            cidade_saida_volta_edit.set_value(data['cidade_saida_volta'])
            aeroporto_saida_volta_edit.set_value(data['aeroporto_saida_volta'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino_volta_edit.set_value(data['pais_destino_volta'])
            cidade_destino_volta_edit.set_value(data['cidade_destino_volta'])
            aeroporto_destino_volta_edit.set_value(data['aeroporto_destino_volta'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            companhia_volta_edit.set_value(data['nome_companhia_volta'])
            valor_passagem_volta_edit.set_value(data['valor_passagem_volta'])
            qtd_passagens_volta_edit.set_value(data['qtd_passagens_volta'])
            observacoes_volta_edit.set_value(data['obs_volta'])

            endereco_hospedagem_input_edit.set_value(data['endereco'])
            diaria_input_edit.set_value(data['diaria'])
            dias_input_edit.set_value(data['dias'])
            observacoes_hospedagem_input_edit.set_value(data['obs'])

            descricao_servico_input_edit.set_value(data['descricao'])
            valor_total_servicos_input_edit.set_value(data['valor_total_servicos'])
            observacoes_servico_input_edit.set_value(data['obs_servicos'])
    

   #------------------------------Editar Venda---------------------------- 
    def on_parcelas_change_edit(e):
        if parcelas_input_edit.value and valor_final_input_edit.value:
            valor_parcelas_input_edit.value = (float(valor_final_input_edit.value)-float(entrada_input_edit.value or 0)) / int(parcelas_input_edit.value)
        else:
            valor_parcelas_input_edit.value = 0.00
    def on_comissao_change_edit(e):
        valor_final_input_edit.value = float(valor_total_servicos_input_edit.value) + (int(qtd_passagens_ida_edit.value) * float(valor_passagem_ida_edit.value)) + (int(qtd_passagens_volta_edit.value) * float(valor_passagem_volta_edit.value)) + (int(dias_input_edit.value) * float(diaria_input_edit.value)) + (float(comissao_input_edit.value) if comissao_input_edit.value else 0)

    with ui.dialog() as edit_venda_dialog, ui.card().classes('w-400').style('padding: 20px'):
        with ui.row().classes('w-full'):
            ui.label('Adicionar Venda').classes('text-xl font-bold mb-4')
            ui.separator()
            ui.label('Selecione o orçamento').classes('text-md font-medium mb-1')
        with ui.row().classes('w-full'):    
            id_orcamento_input_edit = ui.select([], label='Selecione o orçamento', with_input=True,on_change=on_selection_change_orcamento_edit).classes('w-' \
            '100 rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left" popup-content-style="text-align: left;" menu-class="left-align-menu"')
        with ui.row().classes('w-full no-wrap'):
            
            with ui.column().classes("w-1/3 no-wrap"):
                #       ────────Produto─────────────────────

                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Produto').classes('text-sm font-medium mb-1')
                        nome_produto_edit = ui.input(label='Nome do produto', placeholder='Produto').classes('hidden').props('readonly')
                    with ui.row().classes("w-full no-wrap"):
                        with ui.column().classes('w-1/2'):
                            ui.label('Tipo do produto').classes('text-sm font-medium mb-1')
                            tipo_produto_edit = ui.input(label='Tipo do produto', placeholder='Tipo').classes('w-full').props('readonly')
                        with ui.column().classes('w-1/2'):
                            ui.label('País').classes('text-sm font-medium mb-1')
                            pais_produto_edit = ui.input(label='País', placeholder='País').classes('w-full').props('readonly')
                    with ui.row().classes("w-full no-wrap"):
                        with ui.column().classes('w-1/2'):
                            ui.label('Cidade').classes('text-sm font-medium mb-1')
                            cidade_produto_edit = ui.input(label='Cidade', placeholder='Cidade').classes('w-full').props('readonly')
                        with ui.column().classes('w-1/2'):
                            ui.label('Preço mínimo').classes('text-sm font-medium mb-1')
                            preco_minimo_input_edit = ui.number(label='Preço mínimo', placeholder='0.00', min=0, format='%.2f').props('readonly prefix=R$').classes('w-full')

                        
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
                            pais_saida_ida_edit = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined readonly')
                            cidade_saida_ida_edit = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined readonly')
                            aeroporto_saida_ida_edit = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined readonly')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_saida_ida_edit = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-1/4 rounded-md').props('outlined readonly')
                            hora_saida_ida_edit = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-1/4 rounded-md').props('outlined readonly')
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_destino_ida_edit = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            cidade_destino_ida_edit = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            aeroporto_destino_ida_edit = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_chegada_ida_edit = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-1/4 rounded-md').props('outlined readonly')
                            hora_chegada_edit = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-1/4 rounded-md').props('format24h outlined readonly')
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            companhia_ida_edit = ui.input(label='Companhia aérea').props('outlined readonly').classes('w-2/3 rounded-md')
                            valor_passagem_ida_edit = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            qtd_passagens_ida_edit = ui.number(label='Qtd. de passagens', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            observacoes_ida_edit = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none" readonly')

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
                            pais_saida_volta_edit = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined readonly')
                            cidade_saida_volta_edit = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined readonly')
                            aeroporto_saida_volta_edit = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined readonly')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Data de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_saida_volta_edit = ui.date_input(label='Data de saída', placeholder='Data de saída').classes('w-2/4 rounded-md').props('outlined readonly')
                            hora_saida_volta_edit = ui.time_input(label='Horário de saída', placeholder='Horário de saída').classes('w-2/4 rounded-md').props('outlined readonly format24h')
                        ui.space()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Chegada').classes('text-medium font-medium mb-1')
                        ui.separator()
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('País de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Cidade de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                            ui.label('Aeroporto de destino').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            pais_destino_volta_edit = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            cidade_destino_volta_edit = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                            aeroporto_destino_volta_edit = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined readonly')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                            ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-2/4 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            data_chegada_volta_edit = ui.date_input(label='Data de chegada', placeholder='Data de chegada').classes('w-2/4 rounded-md').props('outlined readonly') 
                            hora_chegada_volta_edit = ui.time_input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-2/4 rounded-md').props('format24h outlined readonly')
                            

                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                            ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            companhia_volta_edit = ui.input(label='Companhia aérea').props('outlined readonly').classes('w-2/3 rounded-md')
                            valor_passagem_volta_edit = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes('w-full no-wrap'):
                            ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        with ui.row().classes('w-full no-wrap'):
                            qtd_passagens_volta_edit = ui.number(label='Qtd. de passagens', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                        with ui.row().classes("w-full no-wrap"):
                            ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        with ui.row().classes("w-full no-wrap"):    
                            observacoes_volta_edit = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none" readonly')    
                            

        
        #              ────────Cliente─────────────────────
            with ui.column().classes("w-1/3 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Cliente').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        id_cliente_edit = ui.input(label='ID do cliente', placeholder='ID do cliente').classes('hidden')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Nome completo').classes('text-sm font-medium mb-1 w-3/4 align-self-start')
                        ui.label('Sexo').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                    with ui.row().classes("w-full no-wrap"):
                        nome_cliente_edit = ui.input(label='Nome do cliente', placeholder='Nome do cliente').classes('w-3/4 rounded-md').props('outlined readonly')
                        sexo_cliente_edit = ui.select(['F', 'M'], label='Sexo').classes('w-1/4 rounded-md').props('outlined readonly')
                        
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('CPF').classes('text-sm font-medium mb-1 w-3/6 align-self-start')
                        ui.label('Data de nascimento').classes('text-sm font-medium mb-1 w-3/6 align-self-start rounded-md').props('readonly outlined')
                        
                    with ui.row().classes('w-full no-wrap'):
                        cpf_cliente_edit = ui.input(label='CPF', placeholder='CPF').classes('w-3/6 rounded-md').props('mask="###.###.###-##" unmasked-value outlined readonly')
                        data_nascimento_edit = ui.input(label='Data de nascimento', placeholder='Data de nascimento').classes('w-3/6 rounded-md').props('outlined readonly')
                        
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Telefone').classes('text-sm font-medium mb-1 w-2/6 align-self-start')

                    with ui.row().classes('w-full no-wrap'):
                        telefone_cliente_edit = ui.input(label='Telefone', placeholder='Telefone').classes('w-2/6 rounded-md').props('mask="(##) #####-####" unmasked-value outlined readonly')

                #              ────────Hospedagem─────────────────────   

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Hospedagem').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Endereço').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        endereco_hospedagem_input_edit = ui.input(label='Selecione o cliente').classes('w-full rounded-md').props('outlined readonly')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Diária').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        ui.label('Dias').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        diaria_input_edit = ui.number(label='Diária', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')
                        dias_input_edit = ui.number(label='Dias', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_hospedagem_input_edit = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none" readonly')

        #              ────────Serviços───────────────────── 

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Serviços').classes('text-lg font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Descrição').classes('text-sm font-medium mb-1')
                    with ui.row().classes('w-full no-wrap'):
                        descricao_servico_input_edit = ui.input(label='Descrição do serviço').classes('w-full rounded-md').props('outlined readonly')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor total dos serviços').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        valor_total_servicos_input_edit = ui.number(label='Valor total dos serviços', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_servico_input_edit = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-40 filled input-style="resize: none" readonly')

        #              ────────Venda─────────────────────
            
        
            with ui.column().classes("w-2/7 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Venda').classes('text-lg font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        ui.label('Data da venda').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        data_venda_input_edit = ui.date_input(label='Data da venda', placeholder='Data da venda',value=datetime.datetime.now().strftime('%Y-%m-%d')).classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('gap-2 w-1/2'):
                        ui.label('Comissão').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        comissao_input_edit = ui.number(label='Comissão', placeholder='0.00', min=0, format='%.2f', on_change=on_comissao_change_edit).props('prefix=R$ unmasked-value').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('gap-2 w-full h-20'):
                        ui.space()
                        ui.separator()
                        ui.space()
                    with ui.row().classes('gap-2 w-full justify-end'):
                        ui.label('Valor final').classes('text-lg font-bold mb-1')
                    with ui.row().classes('gap-2 w-full justify-end'):
                        valor_final_input_edit = ui.number(label='Valor final', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ unmasked-value').classes('w-1/2 text-l font-bold rounded-md').props('readonly input-class="text-right text-lg"')
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Entrada').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-2/3'):
                        entrada_input_edit = ui.number(label='Entrada', placeholder='0.00', min=0, format='%.2f', on_change=on_comissao_change_edit).props('prefix=R$ unmasked-value').classes('w-full rounded-md').props('outlined')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Forma de pagamento').classes('text-sm font-medium mb-1 w-2/3')
                        ui.label('Parcelas').classes('text-sm font-medium mb-1 w-1/3')
                    with ui.row().classes('w-full no-wrap'):
                        forma_pgto_input_edit = ui.select(['Boleto', 'Cartão de crédito', 'Cartão de débito','PIX','Dinheiro'], label='Forma de pagamento').classes('text-sm font-medium mb-1 w-2/3 rounded-md').props('outlined')
                        parcelas_input_edit = ui.number(label='Número de parcelas', placeholder='0', min=0, on_change=on_parcelas_change_edit).props('outlined').classes('w-1/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor das parcelas').classes('text-sm font-medium mb-1 w-2/3')
                    with ui.row().classes('w-full no-wrap'):
                        valor_parcelas_input_edit = ui.number(label='Valor das parcelas', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Valor total gasto').classes('text-sm font-medium mb-1 w-2/3')
                    with ui.row().classes('w-full no-wrap'):
                        valor_total_gasto_input_edit = ui.number(label='Valor total gasto', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined').classes('w-2/3 rounded-md')

        with ui.row().classes("justify-end gap-2 q-mt-lg w-full"):
                    ui.button('Confirmar', on_click=lambda: edit_venda(grid_ref,
                                                                        selected_row,
                                                                        data_venda_input_edit.value,
                                                                        id_orcamento_input_edit.value,
                                                                        forma_pgto_input_edit.value,
                                                                        valor_final_input_edit.value,
                                                                        entrada_input_edit.value,
                                                                        parcelas_input_edit.value,
                                                                        valor_parcelas_input_edit.value,
                                                                        comissao_input_edit.value,
                                                                        valor_total_gasto_input_edit.value,
                                                                        edit_venda_dialog)).classes('button button-primary').style('margin-right: 8px;')
                    ui.button('Cancelar', on_click=lambda: edit_venda_dialog.close()).classes('button button-secondary')
                    ui.button('Excluir', on_click=lambda: delete_selected(grid_ref, selected_row, edit_venda_dialog),color='red').classes('button button-danger ml-auto').style('margin-right: 8px;')
                    ui.on_exception(lambda e: notify(str(e), type='error', title='Erro ao editar produto'))   
                    
    # orcamentos_edit = db_connection.get_orcamento_simplificado()
    # id_orcamento_input_edit.options = {o['id_orcamento']: "Orçamento #"+str(o['id_orcamento'])+" - "+o['nome'] for o in orcamentos_edit} if orcamentos_edit else {}
    # id_orcamento_input_edit.update()
                    
    async def on_row_selected(event):
        # Exclude status_venda column from triggering row selection

        #notify(f"Event args: {event.args.get('colId')}", type='info')
        
        column_field = {event.args.get('colId')}
        #notify(f"Column field: {column_field}", type='info')

        if column_field == {'status_venda'}:
            return

        selected_rows = await grid.get_selected_rows()
        selected_row['data'] = selected_rows[0] if selected_rows else None

        if selected_rows:
            selected_id = selected_rows[0]['id_orcamento']
        else:
            notify("Nenhum orçamento selecionado.", type='warning')
            return
        # Fetch new data
        data = db_connection.teste_get_orcamentos()

        for row in data:
            if row['id_orcamento'] == selected_id:
                data = row
                
                break
        #notify(str(data), type='info')
        if data:

           # notify(f"Orcamento selecionado: {data['id_orcamento']}, {data['pais_saida_ida']}, {data['cidade_saida_ida']}, {data['aeroporto_saida_ida']}", type='success')

            orcamentos_edit = db_connection.get_orcamento_simplificado(data['id_orcamento'])
            id_orcamento_input_edit.options = {o['id_orcamento']: "Orçamento #"+str(o['id_orcamento'])+" - "+o['nome'] for o in orcamentos_edit} if orcamentos_edit else {}
            id_orcamento_input_edit.update()

            edit_venda_dialog.open()

            # Update inputs

            id_orcamento_input_edit.set_value(data['id_orcamento'])

            nome_produto_edit.set_value(data['nome_produto'])
            tipo_produto_edit.set_value(data['tipo'])
            pais_produto_edit.set_value(data['pais'])
            cidade_produto_edit.set_value(data['cidade'])
            preco_minimo_input_edit.set_value(data['valor_minimo'])
            id_cliente_edit.set_value(data['id_cliente'])
            nome_cliente_edit.set_value(data['nome'])
            sexo_cliente_edit.set_value(data['sexo'])
            cpf_cliente_edit.set_value(data['cpf'])
            data_nascimento_edit.set_value(data['data_nascimento'])
            telefone_cliente_edit.set_value(data['telefone'])

            pais_saida_ida_edit.set_value(data['pais_saida_ida'])
            cidade_saida_ida_edit.set_value(data['cidade_saida_ida'])
            aeroporto_saida_ida_edit.set_value(data['aeroporto_saida_ida'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino_ida_edit.set_value(data['pais_destino_ida'])
            cidade_destino_ida_edit.set_value(data['cidade_destino_ida'])
            aeroporto_destino_ida_edit.set_value(data['aeroporto_destino_ida'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            companhia_ida_edit.set_value(data['nome_companhia_ida'])
            valor_passagem_ida_edit.set_value(data['valor_passagem_ida'])
            qtd_passagens_ida_edit.set_value(data['qtd_passagens_ida'])
            observacoes_ida_edit.set_value(data['obs_ida'])

            pais_saida_volta_edit.set_value(data['pais_saida_volta'])
            cidade_saida_volta_edit.set_value(data['cidade_saida_volta'])
            aeroporto_saida_volta_edit.set_value(data['aeroporto_saida_volta'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino_volta_edit.set_value(data['pais_destino_volta'])
            cidade_destino_volta_edit.set_value(data['cidade_destino_volta'])
            aeroporto_destino_volta_edit.set_value(data['aeroporto_destino_volta'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            companhia_volta_edit.set_value(data['nome_companhia_volta'])
            valor_passagem_volta_edit.set_value(data['valor_passagem_volta'])
            qtd_passagens_volta_edit.set_value(data['qtd_passagens_volta'])
            observacoes_volta_edit.set_value(data['obs_volta'])

            endereco_hospedagem_input_edit.set_value(data['endereco'])
            diaria_input_edit.set_value(data['diaria'])
            dias_input_edit.set_value(data['dias'])
            observacoes_hospedagem_input_edit.set_value(data['obs'])

            descricao_servico_input_edit.set_value(data['descricao'])
            valor_total_servicos_input_edit.set_value(data['valor_total_servicos'])
            observacoes_servico_input_edit.set_value(data['obs_servicos'])

            forma_pgto_input_edit.set_value(data['forma_pgto'])
            valor_final_input_edit.set_value(data['valor_final'])
            entrada_input_edit.set_value(data['entrada'])
            parcelas_input_edit.set_value(data['n_parcelas'])
            valor_parcelas_input_edit.set_value(data['valor_parcelas'])
            comissao_input_edit.set_value(data['comissao'])
            valor_total_gasto_input_edit.set_value(data['valor_total_gasto'])

    grid.on('cellClicked', on_row_selected)
    grid.on('cellValueChanged', lambda event: on_cell_edit(grid_ref, selected_row))
    #grid.on('cellValueChanged', lambda event: notify("Valor da célula editado", type='success'))

# --------------- Funções ---------------

    

def update_grid(grid_ref, data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, dialog):
    notify("ID orcamento: " + str(id_orcamento), type='success')
    db_connection.add_venda(data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao)
    dialog.close()
    
    novos_valores = db_connection.get_vendas()
    
    # 3. Update AG Grid Data
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()
            
def edit_venda(grid_ref, selected_row, data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, valor_total_gasto, dialog):
    notify(str(selected_row), type='success')
    row_data = selected_row['data']
    if not row_data:
        ui.notify('Nenhum produto selecionado', type='warning')
        return
    
    id_venda = row_data.get('id_venda')
    
    db_connection.update_venda(data_venda, id_orcamento, forma_pgto, valor_final, entrada, n_parcelas, valor_parcelas, comissao, id_venda, valor_total_gasto)
    dialog.close()

    db_connection.update_dw()
    
    novos_valores = db_connection.get_vendas()
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

def delete_selected(grid_ref, selected_row, dialog):
    row_data = selected_row['data']
    if not row_data:
        ui.notify('Nenhum produto selecionado', type='warning')
        return
    
    id_venda = row_data.get('id_venda')
    
    db_connection.delete_venda(id_venda)
    dialog.close()
    
    novos_valores = db_connection.get_vendas()
    grid = grid_ref.get('grid')
    grid.options['rowData'] = novos_valores
    grid.update()

async def on_cell_edit(grid_ref, selected_row):

    grid = grid_ref.get('grid')
    
    selected_rows = await grid.get_selected_rows()
    selected_row['data'] = selected_rows[0] if selected_rows else None

    if selected_rows:
        id_venda = selected_rows[0]['id_venda']
        status = selected_rows[0]['status_venda']
        ui.notify('Venda selecionada:' + str(id_venda) + ' Status: ' + status, type='warning')
    #ui.notify('Venda selecionada:' + str(), type='warning')

    db_connection.update_status_venda(status, id_venda)
    db_connection.update_dw()


    novos_valores = db_connection.get_vendas()

    grid.options['rowData'] = novos_valores
    grid.update()
    


