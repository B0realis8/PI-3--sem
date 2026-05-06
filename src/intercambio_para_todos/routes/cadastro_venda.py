from nicegui import ui,app,APIRouter,events
from modules import db_connection
from services.notifications import notify
import re
import datetime


@ui.page('/vendas')

def content() -> None:

    ui.add_head_html('<style>.ag-row { cursor: pointer; }</style>')

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Vendas').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Atualizar', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline').on('click', lambda: grid.update())

    ui.element('div').classes('divider mb-4')
    

    column_defs = [
        {'field': 'id_venda', 'headerName': 'ID', 'sortable': True, 'editable': False, 'hide': True},
        {'field': 'data_venda', 'headerName': 'Nome', 'sortable': True, 'editable': True},
        {'field': 'id_orcamento', 'headerName': 'Tipo', 'sortable': True, 'editable': True},
        {'field': 'quantidade', 'headerName': 'Valor Mínimo', 'sortable': True, 'editable': True, 'valueFormatter': 'x.toLocaleString("pt-BR", {style: "currency", currency: "BRL"})'},
        {'field': 'forma_pgto', 'headerName': 'País', 'sortable': True, 'editable': True},
        {'field': 'entrada', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
        {'field': 'n_parcelas', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
        {'field': 'valor_parcelas', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
        {'field': 'comissao', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
        {'field': 'lucro_total', 'headerName': 'Cidade', 'sortable': True, 'editable': True},
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
        }, html_columns=[4]).classes('w-full flex-grow')
        grid_ref['grid'] = grid

        search.on('update:model-value', lambda e: grid.run_grid_method(
            'setGridOption', 'quickFilterText', e.args or ''))  #verificar diferentes condições de filtro
        

    def on_selection_change_orcamento(event):
        selected_id = event.value
        # Fetch new data
        data = db_connection.get_orcamento_vendas()
        # notify(str(data), type='info')
        for row in data:
            if row['id_orcamento'] == selected_id:
                data = row
                notify(f"Orcamento selecionado: {data['id_orcamento']}, {data['pais_saida']}, {data['cidade_saida']}, {data['aeroporto_saida']}", type='success')
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
            sexo_cliente_input.set_value(data['sexo'])
            cpf_cliente_input.set_value(data['cpf'])
            data_nascimento_input.set_value(data['data_nascimento'])
            telefone_cliente_input.set_value(data['telefone'])
            pais_saida.set_value(data['pais_saida'])
            cidade_saida.set_value(data['cidade_saida'])
            aeroporto_saida.set_value(data['aeroporto_saida'])
            #data_saida.set_value(data['data_saida']) adicionar no bd
            #hora_saida.set_value(data['hora_saida']) adicionar no bd
            pais_destino.set_value(data['pais_destino'])
            cidade_destino.set_value(data['cidade_destino'])
            aeroporto_destino.set_value(data['aeroporto_destino'])
            #data_destino.set_value(data['data_destino']) adicionar no bd
            id_companhia_input.set_value(data['id_companhia'])
            nome_companhia_input.set_value(data['nome_companhia'])
            valor_passagem.set_value(data['valor_passagem'])
            qtd_passagens_input.set_value(data['qtd_passagens'])
            valor_total_passagem.set_value(data['valor_total'])
            observacoes_input.set_value(data['obs'])

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20).classes('flex items-end gap-3'):
        with ui.column().classes('items-center gap-3'):
            ui.button(icon='add', on_click=lambda: add_venda_dialog.open(), color='primary').props('fab')
    
    
    with ui.dialog() as add_venda_dialog, ui.card().classes('w-400').style('padding: 20px'):
        with ui.row().classes('w-full'):
            ui.label('Adicionar Venda').classes('text-xl font-bold mb-4')
            ui.separator()
            ui.label('Selecione o orçamento').classes('text-md font-medium mb-1')
        with ui.row().classes('w-full'):    
            id_orcamento_input = ui.select([], label='Selecione o orçamento', with_input=True,on_change=on_selection_change_orcamento).classes('w-50 rounded-md').props('hide-selected outlined input-class="text-left" menu-anchor="bottom left" menu-self="top left" popup-content-style="text-align: left;" menu-class="left-align-menu"')
        with ui.row().classes('w-full no-wrap'):
            with ui.column().classes("w-3/7 no-wrap"):
                with ui.card().classes("w-full"):
        #              ─────────Voo─────────────────────────

                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Voo').classes('text-lg font-medium mb-1')
                        ui.icon('flight', color="#DFDFDF", size="md").classes('ml-auto justify-self-end h-full')
                    with ui.row().classes("w-full no-wrap"):
                        ui.label('Saída').classes('text-medium font-medium mb-1')
                    ui.separator()        
                    with ui.row().classes("w-full no-wrap"):
                        ui.label('País de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        ui.label('Cidade de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        ui.label('Aeroporto de saída').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        pais_saida = ui.input(label='País de saída', placeholder='País de saída').classes('w-full rounded-md').props('outlined readonly')
                        cidade_saida = ui.input(label='Cidade de saída', placeholder='Cidade de saída').classes('w-full rounded-md').props('outlined readonly')
                        aeroporto_saida = ui.input(label='Aeroporto de saída', placeholder='Aeroporto de saída').classes('w-full rounded-md').props('outlined readonly')
                    with ui.row().classes("w-full no-wrap"):
                        ui.label('Data de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        ui.label('Horário de saída').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        data_saida = ui.input(label='Data de saída', placeholder='Data de saída').classes('w-1/4 rounded-md').props('outlined readonly')
                        hora_saida = ui.input(label='Horário de saída', placeholder='Horário de saída').classes('w-1/4 rounded-md').props('outlined readonly')
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
                        pais_destino = ui.input(label='País de destino', placeholder='País de destino').classes('w-1/3 rounded-md').props('outlined').props('readonly')
                        cidade_destino = ui.input(label='Cidade de destino', placeholder='Cidade de destino').classes('w-1/3 rounded-md').props('outlined').props('readonly')
                        aeroporto_destino = ui.input(label='Aeroporto de destino', placeholder='Aeroporto de destino').classes('w-1/3 rounded-md').props('outlined').props('readonly')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Data de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                        ui.label('Horário de chegada').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        data_chegada = ui.input(label='Data de chegada', placeholder='Data de chegada').classes('w-1/4 rounded-md').props('outlined').props('readonly')
                        hora_chegada = ui.input(label='Horário de chegada', placeholder='Horário de chegada').classes('w-1/4 rounded-md').props('format24h outlined readonly')
                        

                    with ui.row().classes("w-full no-wrap"):
                        ui.label('Companhia aérea').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        ui.label('Valor da passagem').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                    with ui.row().classes('w-full no-wrap'):
                        nome_companhia_input = ui.input(label='Selecione a companhia aérea').props('outlined readonly').classes('w-2/3 rounded-md')
                        valor_passagem = ui.number(label='Valor da passagem', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-1/3 rounded-md')
                        id_companhia_input = ui.input(label='ID da companhia aérea', placeholder='ID da companhia aérea').classes('hidden').props('readonly')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Qtd. de passagens').classes('text-sm font-medium mb-1 w-1/3 align-self-start')
                        ui.label('Valor total da passagem').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):
                        qtd_passagens_input = ui.number(label='Quantidade de passagens', placeholder='0', min=0).props('outlined readonly').classes('w-1/3 rounded-md')
                        valor_total_passagem = ui.number(label='Valor total da passagem', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ outlined readonly').classes('w-2/3 rounded-md')

                    with ui.row().classes("w-full no-wrap"):
                        ui.label('Observações').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                    with ui.row().classes("w-full no-wrap"):    
                        observacoes_input = ui.textarea(label='Observações').classes('!w-full tight-textarea').props('input-class=h-50 filled input-style="resize: none" readonly')
            

        #       ────────Produto─────────────────────
            with ui.column().classes("w-2/7 no-wrap"):
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

        #              ────────Cliente─────────────────────

                with ui.card().classes("w-full"):
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Cliente').classes('text-sm font-medium mb-1 w-2/3 align-self-start')
                        id_cliente = ui.input(label='ID do cliente', placeholder='ID do cliente').classes('hidden')
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Nome completo').classes('text-sm font-medium mb-1 w-3/4 align-self-start')
                        ui.label('Sexo').classes('text-sm font-medium mb-1 w-1/4 align-self-start')
                    with ui.row().classes("w-full no-wrap"):
                        nome_cliente = ui.input(label='Nome do cliente', placeholder='Nome do cliente').classes('w-3/4').props('outlined rounded readonly')
                        sexo_cliente_input = ui.select(['F', 'M'], label='Sexo').classes('w-1/4').props('outlined rounded readonly')
                        
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('CPF').classes('text-sm font-medium mb-1 w-3/6 align-self-start')
                        ui.label('Data de nascimento').classes('text-sm font-medium mb-1 w-3/6 align-self-start')
                        
                    with ui.row().classes('w-full no-wrap'):
                        cpf_cliente_input = ui.input(label='CPF', placeholder='CPF').classes('w-3/6').props('mask="###.###.###-##" unmasked-value outlined rounded readonly')
                        data_nascimento_input = ui.input(label='Data de nascimento', placeholder='Data de nascimento').classes('w-3/6').props('outlined rounded readonly')
                        
                    with ui.row().classes('w-full no-wrap'):
                        ui.label('Telefone').classes('text-sm font-medium mb-1 w-2/6 align-self-start')

                    with ui.row().classes('w-full no-wrap'):
                        telefone_cliente_input = ui.input(label='Telefone', placeholder='Telefone').classes('w-2/6').props('mask="(##) #####-####" unmasked-value outlined rounded readonly')

        #              ────────Venda─────────────────────
            def on_comissao_change(e):
                if comissao_input.value != None:
                    valor_final_input.value = float(valor_total_passagem.value) + float(comissao_input.value)

            with ui.column().classes("w-2/7 no-wrap"):
                with ui.card().classes("w-full"):
                    with ui.row().classes('gap-2 w-full'):
                        ui.label('Venda').classes('text-lg font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        ui.label('Data da venda').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        data_venda_input = ui.date_input(label='Data da venda', placeholder='Data da venda',value=datetime.datetime.now().strftime('%Y-%m-%d')).classes('w-full').props('outlined rounded')
                    with ui.row().classes('gap-2 w-1/2'):
                        ui.label('Comissão').classes('text-sm font-medium mb-1')
                    with ui.row().classes('gap-2 w-1/2'):
                        comissao_input = ui.number(label='Comissão', placeholder='0.00', min=0, format='%.2f', on_change=on_comissao_change).props('prefix=R$ unmasked-value').classes('w-full').props('outlined rounded')
                    with ui.row().classes('gap-2 w-full h-20'):
                        ui.space()
                        ui.separator()
                        ui.space()
                    with ui.row().classes('gap-2 w-full justify-end'):
                        ui.label('Valor final').classes('text-lg font-bold mb-1')
                    with ui.row().classes('gap-2 w-full justify-end'):
                        valor_final_input = ui.number(label='Valor final', placeholder='0.00', min=0, format='%.2f').props('prefix=R$ unmasked-value').classes('w-1/2 text-l font-bold').props('readonly input-class="text-right text-lg"')

            

    produtos = db_connection.get_orcamentos()
    id_orcamento_input.options = {p['id_orcamento']: "Orçamento #"+str(p['id_orcamento']) for p in produtos} if produtos else {}
    id_orcamento_input.update()

# --------------- Funções ---------------

    


            