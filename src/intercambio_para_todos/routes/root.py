from nicegui import ui,app,APIRouter
import json
from pathlib import Path
from functools import wraps

import header
import routes.instagram
import routes.cadastro_venda

with open('C:\\Users\\Renan\\Desktop\\Fatec\\PI 3º sem\\src\\intercambio_para_todos\\config.json', encoding='utf-8') as f:
    config = json.load(f)

appName    = config["appName"]
appVersion = config["appVersion"]
appPort    = config["appPort"]

# ── Logo singleton — one instance shared across requests to avoid reload cost ──────
logo_image = None

def get_logo_image():
    global logo_image
    if logo_image is None:
        logo_image = ui.image('assets/css/images/logo.png').style('width: 5rem; height: auto;')
    return logo_image

# ── Base layout decorator — applies theme, global CSS and sidebar shell ────────────
def with_base_layout(route_handler):
    @wraps(route_handler)
    def wrapper(*args, **kwargs):
        
        ui.colors(primary='#18181b', secondary='#f4f4f5', positive='#4caf50', negative='#ef4444', warning='#f59e0b', info='#3b82f6', accent='#e4e4e7')
        ui.add_head_html("<style>" + open(Path(__file__).parent.parent / "assets" / "css" / "global-css.css").read() + "</style>", shared=True)
        ui.add_head_html('<link rel="stylesheet" href="../assets/css/fonts/icons.css">', shared=True)
        ui.add_head_html('<meta charset="UTF-8">')
        
        # Preload avoids a layout-shift flash when the sidebar logo first renders
        ui.add_head_html('<link rel="preload" href="../assets/css/images/logo.png" as="image">')

        if 'sidebar-collapsed' not in app.storage.user:
            app.storage.user['sidebar-collapsed'] = True

        with header.frame(title=appName, version=appVersion,  get_logo_func=get_logo_image):
            return route_handler(*args, **kwargs)
    return wrapper

@ui.page('/')
@with_base_layout
def root():
    ui.sub_pages({
    '/': cadastro_venda,
    '/mostrar_instagram': mostrar_instagram
    })

    # ── Sub-page handlers ────────────────────────────────────────────────────────────

def cadastro_venda():
    routes.cadastro_venda.content()

def mostrar_instagram():
    routes.instagram.content()

def redirect_page2():
    ui.notify('Redirecionando...')
    ui.navigate.to('/page2')