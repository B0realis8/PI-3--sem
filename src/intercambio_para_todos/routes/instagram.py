from nicegui import ui,app,APIRouter
from modules import db_connection
from routes import index, page2, produto

@ui.page('/mostrar_instagram')
def mostrar_instagram():

    with ui.header().classes(replace='row items-center') as header:
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.left_drawer().classes('bg-blue-100') as left_drawer:
        ui.button('Clique aqui', on_click=lambda: index.redirect_page2())
        ui.button('Mostrar Produtos', on_click=lambda: ui.navigate.to('/mostrar_produtos'))
        ui.button('Mostrar Instagram', on_click=lambda: ui.navigate.to('/mostrar_instagram'))

    instagram = db_connection.get_data_from_db()
    ui.label(f"postID: {instagram[0][0]}, account_id: {instagram[0][1]}, account_type: {instagram[0][2]}")
    
    ui.button('Atualizar tabela Instagram', on_click=db_connection.update_instagram_table)
    limit = 100
    for post in instagram:
        ui.label(f"postID: {post[0]}, account_id: {post[1]}, account_type: {post[2]}, follower_count: {post[3]}, media_type: {post[4]}, content_category: {post[5]}, traffic_source: {post[6]}, has_call_to_action: {post[7]}, post_datetime: {post[8]}, post_date: {post[9]}, post_hour: {post[10]}, day_of_week: {post[11]}, likes: {post[12]}, comments: {post[13]}, shares: {post[14]}, saves: {post[15]}, reach: {post[16]}, impression: {post[17]}, engagement_rate: {post[18]}, followers_gained: {post[19]}, caption_length: {post[20]}, hashtags_count: {post[21]}, performance_bucket_label: {post[22]}")
        if instagram.index(post) == limit:
            break