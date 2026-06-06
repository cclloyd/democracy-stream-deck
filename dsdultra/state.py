from __future__ import annotations

import traceback
from pathlib import Path
from time import strftime
from typing import TYPE_CHECKING, Any

from PIL import Image, ImageDraw, ImageChops

from dsdultra.logging import log
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
    active_page: BasePage

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

    def _rounded_key_mask(self, width, height, radius):
        scale = 4
        mask = Image.new('L', (width * scale, height * scale), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle(
            (0, 0, width * scale - 1, height * scale - 1),
            radius=radius * scale,
            fill=255,
        )
        return mask.resize((width, height), Image.Resampling.LANCZOS)

    def screenshot(self, page=None) -> Path | False:
        try:
            if page is None:
                page = self.active_page
            icons = page.images  # List of PIL.Image.Image
            key_width = self.dsd.deck.KEY_PIXEL_WIDTH
            key_height = self.dsd.deck.KEY_PIXEL_HEIGHT
            key_count = self.dsd.deck.key_count()
            cols = self.dsd.deck.KEY_COLS
            rows = self.dsd.deck.KEY_ROWS
            key_gap = round(min(key_width, key_height) * 0.18)
            corner_radius = round(min(key_width, key_height) * 0.15)
            deck_icon_path = self.dsd.config.asset_dir / 'icons/stream_deck_light.png'
            deck_icon_height = round(key_height * 0.4)
            deck_icon_top = key_gap
            glass_overlay_path = self.dsd.config.asset_dir / 'icons/groups/glass72.png'

            grid_width = cols * key_width + (cols + 1) * key_gap
            grid_height = rows * key_height + (rows + 1) * key_gap
            header_height = deck_icon_top + deck_icon_height

            screenshot_width = grid_width
            screenshot_height = header_height + grid_height
            screenshot = Image.new('RGB', (screenshot_width, screenshot_height), 'black')
            key_mask = self._rounded_key_mask(key_width, key_height, corner_radius)

            deck_icon = Image.open(deck_icon_path).convert('RGBA')
            deck_icon.thumbnail((screenshot_width - 2 * key_gap, deck_icon_height), Image.Resampling.LANCZOS)
            deck_icon.putalpha(deck_icon.getchannel('A').point(lambda alpha: round(alpha * 0.8)))
            deck_icon_x = (screenshot_width - deck_icon.width) // 2
            screenshot.paste(deck_icon.convert('RGB'), (deck_icon_x, deck_icon_top), deck_icon)

            glass_overlay = Image.open(glass_overlay_path).convert('RGBA')
            if glass_overlay.size != (key_width, key_height):
                glass_overlay = glass_overlay.resize((key_width, key_height), Image.Resampling.LANCZOS)
            glass_overlay.putalpha(ImageChops.multiply(glass_overlay.getchannel('A'), key_mask))

            key_grid_top = header_height

            for key_index in range(key_count):
                icon = icons[key_index] if key_index < len(icons) else None

                if icon is None:
                    bg_color = 1
                    icon = Image.new('RGBA', (key_width, key_height), (bg_color, bg_color, bg_color, 255))
                elif icon.size != (key_width, key_height):
                    icon = icon.resize((key_width, key_height), Image.Resampling.LANCZOS)

                icon = icon.convert('RGBA')
                icon.putalpha(ImageChops.multiply(icon.getchannel('A'), key_mask))

                x = key_gap + (key_index % cols) * (key_width + key_gap)
                y = key_grid_top + key_gap + (key_index // cols) * (key_height + key_gap)

                icon.alpha_composite(glass_overlay)

                screenshot.paste(icon.convert('RGB'), (x, y), icon)

            screenshots_dir = self.dsd.config.config_dir / 'screenshots'
            screenshots_dir.mkdir(parents=True, exist_ok=True)

            filename = screenshots_dir / f'streamdeck-{strftime("%Y%m%d-%H%M%S")}.png'
            screenshot.save(filename)


            log.info(f'Saved screenshot to {filename.absolute()}')
            return filename
        except Exception as e:
            log.error(f'Failed to save screenshot: {e}')
            traceback.print_exc()
            return False