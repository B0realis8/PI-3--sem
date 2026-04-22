import nicegui as ng
from nicegui import ui,app
import psycopg2 as pg
from modules import db_connection
from routes import page2, produto, instagram,root

app.add_static_files(url_path='src/intercambio_para_todos/assets', local_directory='.')

db_connection.get_data_from_db()

ui.run(native=True,storage_secret='my_secret_key', title='Intercâmbio para Todos', favicon='src/intercambio_para_todos/assets/css/images/logo.png')