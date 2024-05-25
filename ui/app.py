from nicegui import ui
from ui.pages.eval_results import __init__
from ui.pages.input import __init__

ui.run(storage_secret="storage_secret", reconnect_timeout=100)
