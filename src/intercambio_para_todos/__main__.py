import nicegui as ng
from nicegui import ui,app
import psycopg2 as pg
from modules import db_connection
from routes import page2, produto, instagram,root
import os
from pathlib import Path

app.add_static_files(url_path='/assets', local_directory=str(Path(__file__).resolve().parent / 'assets'))

db_connection.get_data_from_db()

ui.run(native=True,storage_secret='my_secret_key', title='Intercâmbio para Todos', favicon='src/intercambio_para_todos/assets/css/images/logo.png')

app.add_static_files(url_path='/assets/css/fonts/inter-600.woff2', local_directory=str(Path(__file__).resolve().parent / 'assets/css/fonts'))
app.add_static_files(url_path='/assets/css/fonts/inter-600.woff', local_directory=str(Path(__file__).resolve().parent / 'assets/css/fonts'))