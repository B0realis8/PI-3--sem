from nicegui import ui,app,APIRouter

@ui.page('/cadastro_orçamento')
def cadastro_orçamento():
    ui.label('Cadastro de Orçamento')
    ui.button('Voltar para a página inicial', on_click=lambda: ui.navigate.to('/'))

def content() -> None:

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Cadastrar orçamento').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Refresh', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline')

    ui.element('div').classes('divider mb-4')