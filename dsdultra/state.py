from __future__ import annotations
from typing import TYPE_CHECKING, Any

from dsdultra.pages.base import BasePage

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra

class StateManager:
    dsd: 'DSDUltra' = None
    apps: dict[str, BasePage] = {}
    select_active: dict[str, dict[str, bool]]  # {appname: {select_type: bool}}
    selected: dict[str, dict[str, list[Any]]] = {} # {appname: {select_type: list_of_selected_items}}
    select_limit: dict[str, dict[str, int]] = {} # {appname: {select_type: int}}
    highlight_active: dict[str, dict[str, bool | str]] = {}
    store: dict[str, dict[str, Any]] = {}

    def __init__(self, dsd: 'DSDUltra'):
        self.dsd = dsd
        self.select_active = {}
        self.selected = {}
        self.select_limit = {}
        self.highlight_active = {}
        self.store = {}

    def register_app(self, app: BasePage, appname: str):
        app.appname = app.appname if app.appname else appname
        self.apps[app.appname] = app
        self.selected[app.appname] = {}
        self.select_active[app.appname] = {}
        self.select_limit[app.appname] = app.select_limits or {}
        self.highlight_active[app.appname] = {}
