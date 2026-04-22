from nicegui import ui,app,APIRouter
from modules import db_connection

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
    instagram = db_connection.get_data_from_db()
    ui.label(f"postID: {instagram[0][0]}, account_id: {instagram[0][1]}, account_type: {instagram[0][2]}")
    
    ui.button('Atualizar tabela Instagram', on_click=db_connection.update_instagram_table)
    limit = 100
    for post in instagram:
        ui.label(f"postID: {post[0]}, account_id: {post[1]}, account_type: {post[2]}, follower_count: {post[3]}, media_type: {post[4]}, content_category: {post[5]}, traffic_source: {post[6]}, has_call_to_action: {post[7]}, post_datetime: {post[8]}, post_date: {post[9]}, post_hour: {post[10]}, day_of_week: {post[11]}, likes: {post[12]}, comments: {post[13]}, shares: {post[14]}, saves: {post[15]}, reach: {post[16]}, impression: {post[17]}, engagement_rate: {post[18]}, followers_gained: {post[19]}, caption_length: {post[20]}, hashtags_count: {post[21]}, performance_bucket_label: {post[22]}")
        if instagram.index(post) == limit:
            break

