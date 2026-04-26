from nicegui import ui,app,APIRouter
from modules import db_connection
from services.notifications import notify

@ui.page('/mostrar_instagram')

def content() -> None:

        # ── Header ──────────────────────────────────────────────────
    with ui.row().classes('w-full items-center justify-between mb-2'):
        with ui.column().classes('gap-0'):
            ui.label('Instagram Analytics').classes('page-title')
            ui.label('Live overview · refreshes on demand').classes('text-sm text-muted')
        refresh_btn = ui.button('Refresh', icon='refresh', color='white') \
            .props('flat no-caps').classes('button button-outline')

    ui.element('div').classes('divider mb-4')

    mostrar_instagram()

def mostrar_instagram():
    #ui.label(f"postID: {instagram[0][0]}, account_id: {instagram[0][1]}, account_type: {instagram[0][2]}")
    
    ui.button('Atualizar tabela Instagram', on_click=db_connection.update_instagram_table)
    limit = 20
    column_defs = [
        {'field': 'post_id', 'headerName': 'Post ID', 'sortable': True},
        {'field': 'account_id', 'headerName': 'Account ID', 'sortable': True},
        {'field': 'account_type', 'headerName': 'Account Type', 'sortable': True},
        {'field': 'follower_count', 'headerName': 'Follower Count', 'sortable': True},
        {'field': 'media_type', 'headerName': 'Media Type', 'sortable': True},
        {'field': 'content_category', 'headerName': 'Content Category', 'sortable': True},
        {'field': 'traffic_source', 'headerName': 'Traffic Source', 'sortable': True},
        {'field': 'has_call_to_action', 'headerName': 'Has Call To Action', 'sortable': True},
        {'field': 'post_datetime', 'headerName': 'Post Datetime', 'sortable': True},
        {'field': 'post_date', 'headerName': 'Post Date', 'sortable': True},
        {'field': 'post_hour', 'headerName': 'Post Hour', 'sortable': True},
        {'field': 'day_of_week', 'headerName': 'Day Of Week', 'sortable': True},
        {'field': 'likes', 'headerName': 'Likes', 'sortable': True},
        {'field': 'comments', 'headerName': 'Comments', 'sortable': True},
        {'field': 'shares', 'headerName': 'Shares', 'sortable': True},
        {'field': 'saves', 'headerName': 'Saves', 'sortable': True},
        {'field': 'reach', 'headerName': 'Reach', 'sortable': True},
        {'field': 'impression', 'headerName': 'Impression', 'sortable': True},
        {'field': 'engagement_rate', 'headerName': 'Engagement Rate', 'sortable': True},
        {'field': 'followers_gained', 'headerName': 'Followers Gained', 'sortable': True},
        {'field': 'caption_length', 'headerName': 'Caption Length', 'sortable': True},
        {'field': 'hashtags_count', 'headerName': 'Hashtags Count', 'sortable': True},
        {'field': 'performance_bucket_label', 'headerName': 'Performance Bucket', 'sortable': True},
    ]

    grid_ref = {}
    with ui.row().classes('w-full items-center gap-3 mb-3 flex-wrap'):
        search = ui.input(placeholder='Search shipments…').classes('flex-1').props('outlined rounded dense clearable')
        search.add_slot('prepend', '<q-icon name="search" />')
        # ui.button('Export', color='white',
        #           on_click=lambda: notify('Export started', type='info', title='Export')).props('flat no-caps').classes('button button-outline button-sm')

    grid = ui.aggrid({
        'columnDefs': column_defs,
        'rowData': db_connection.get_data_from_db(),
        'rowSelection': {'mode': 'multiRow'},
        'defaultColDef': {'sortable': True},
    }, html_columns=[4]).classes('w-full')
    grid_ref['grid'] = grid

    search.on('update:model-value', lambda e: grid.run_grid_method(
        'setGridOption', 'quickFilterText', e.args or ''))
    
    with ui.row():
        name = ui.input('Name')
        age = ui.number('Age')

    ui.button('Add User', on_click=lambda: db_connection.add_user(name.value, age.value))

