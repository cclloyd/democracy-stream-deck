from __future__ import annotations

import traceback
import uuid
from typing import Optional, TYPE_CHECKING

from PIL import Image

from dsdultra.buttons.back import ButtonBack
from dsdultra.buttons.base import ButtonBase
from dsdultra.buttons.exit import ButtonExit
from dsdultra.buttons.nav import ButtonPrev, ButtonNext
from dsdultra.logging import log

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra


class BasePage:
    id: str
    ICON_TYPE_MAP: list[None | ButtonBase | str] = [None] * 15

    # For scrollable pages
    appname: str = None
    MAX_CONTENT = 10
    page_num = 0
    content_class = ButtonExit
    content: Optional[dict | list] = None
    prev_index = None
    next_index = None
    select_limits: dict[str, int] = {
        'stratagems': 5,
    }
    nav_up_callback = None

    @property
    def app(self) -> 'BasePage':
        return self.dsd.state.apps.get(self.appname, None)

    def close(self):
        self.dsd.apps.pop(self.appname, None)

    def nav_callback(self):
        pass

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config: dict = {}, app: str = None):
        self.id = str(uuid.uuid4())
        self.dsd: 'DSDUltra' = dsd
        self.parent: Optional[BasePage] = parent
        self.buttons: list[ButtonBase] = []
        self.icons: list[bytes] = []
        self.images: list[Image.Image] = []
        self.content = content or self.content
        self.content_class = content_class or self.content_class
        self.page_num = page_num
        self.appname = app or self.appname or self.parent.appname

        if app and app not in self.dsd.state.apps:
            self.dsd.state.register_app(self, app)

        self.config = config

    def is_highlight_active(self, highlight_type: str) -> bool:
        return bool(self.dsd.state.highlight_active[self.appname].get(highlight_type, False))

    def toggle_highlight(self, highlight_type, rerender=True, force=True):
        self.dsd.state.highlight_active[self.appname][highlight_type] = not self.dsd.state.highlight_active[self.appname].get(highlight_type, False)
        if rerender:
            self.render(force)

    def set_highlight(self, highlight_type, value: bool, rerender=True, force=True):
        self.dsd.state.highlight_active[self.appname][highlight_type] = value
        if rerender:
            self.render(force)

    def get_highlight(self, highlight_type):
        return self.dsd.state.highlight_active[self.appname].get(highlight_type, False)

    def select_active(self, select_type) -> bool:
        if select_type is None:
            return False
        return self.dsd.state.select_active[self.appname].get(select_type, False)

    def toggle_select(self, select_type, rerender=True, force=True):
        self.dsd.state.select_active[self.appname][select_type] = not self.dsd.state.select_active[self.appname].get(select_type, False)
        if rerender:
            self.render(force)

    def set_select_active(self, select_type, active, rerender=True, force=True):
        self.dsd.state.select_active[self.appname][select_type] = active
        if rerender:
            self.render(force)

    def select_limit(self, select_type) -> int | None:
        limit = self.dsd.state.select_limit.get(self.appname, {}).get(select_type, None)
        return limit if limit is not None else self.dsd.deck.key_count()

    def selected(self, select_type):
        if self.dsd.state.selected[self.appname].get(select_type, None) is None:
            self.dsd.state.selected[self.appname][select_type] = []
        return self.dsd.state.selected[self.appname][select_type]

    def add_select(self, select_type: str, item: ButtonBase | list[ButtonBase], rerender=True, force=True):
        if isinstance(item, list):
            for i in item:
                if i.config['id'] not in [b.config['id'] for b in self.dsd.state.selected[self.appname][select_type]]:
                    self.dsd.state.selected[self.appname][select_type].append(i)
        else:
            if item.config['id'] not in [b.config['id'] for b in self.dsd.state.selected[self.appname][select_type]]:
                self.dsd.state.selected[self.appname][select_type].append(item)
        if rerender:
            self.render(force)

    def set_select(self, select_type: str, item: ButtonBase | list[ButtonBase], rerender=True, force=True):
        if isinstance(item, list):
            self.dsd.state.selected[self.appname][select_type] = item
        else:
            self.dsd.state.selected[self.appname][select_type] = [item]
        if rerender:
            self.render(force)

    def remove_select(self, select_type, item, rerender=True, force=True):
        if item.config['id'] in [b.config['id'] for b in self.dsd.state.selected[self.appname][select_type]]:
            idx = next((i for i, b in enumerate(self.dsd.state.selected[self.appname][select_type])
                        if b.config['id'] == item.config['id']), -1)
            if idx >= 0:
                self.dsd.state.selected[self.appname][select_type].pop(idx)
        if rerender:
            self.render(force)

    def clear_select(self, select_type, rerender=True, force=True):
        self.dsd.state.selected[self.appname][select_type] = []
        if rerender:
            self.render(force)

    def swap_select(self, select_type, item, rerender=True, force=True):
        if len(self.dsd.state.selected[self.appname][select_type]) == 0:
            self.add_select(select_type, item, rerender=False)
        else:
            pass
        if rerender:
            self.render(force)

    def set_store(self, store_type, item, rerender=True, force=True):
        if self.appname not in self.dsd.state.store:
            self.dsd.state.store[self.appname] = {}
        self.dsd.state.store[self.appname][store_type] = item

    def get_store(self, store_type):
        if self.appname not in self.dsd.state.store:
            self.dsd.state.store[self.appname] = {}
        return self.dsd.state.store[self.appname].get(store_type, None)

    def get_buttons_cb(self, cls: type, k: int, added: int):
        pass

    def get_buttons(self, force=False):
        if len(self.buttons) > 0 and not force:
            return self.buttons
        buttons = []
        added = 0
        data = (self.content or [])[self.page_num * self.MAX_CONTENT:(self.page_num + 1) * self.MAX_CONTENT]
        for k, cls in enumerate(self.ICON_TYPE_MAP):
            config = {}

            if cls is None:
                buttons.append(None)
            elif cls == 'app':
                buttons.append(self.app.ICON_TYPE_MAP[k](self.dsd, page=self))
            elif cls == 'parent':
                buttons.append(self.parent.ICON_TYPE_MAP[k](self.dsd, page=self))
            elif cls == 'content' and self.content_class is not None:
                if added < len(data):
                    if data[added]:
                        if isinstance(data[added], dict):
                            config.update(data[added])
                        else:
                            config.update(data[added].config)

                    if data[added] is None:
                        buttons.append(None)
                    else:
                        buttons.append(self.content_class(self.dsd, page=self, config=config))
                    added += 1
                else:  # We ran out of content
                    buttons.append(None)
            # Replace buttons with Page Navigation buttons, but only if length of content is greater than the allotted spots, and only if a spot for the nav buttons were specified, either via ICON_MAP or nav indexes.
            elif (len(self.content or []) > self.ICON_TYPE_MAP.count('content') and k == self.prev_index) or cls == ButtonPrev and isinstance(cls, type):
                buttons.append(ButtonPrev(self.dsd, page=self, config={
                    'enabled': self.page_num > 0,
                    'page_num': self.page_num,
                }))
            elif (len(self.content or []) > self.ICON_TYPE_MAP.count('content') and k == self.next_index) or cls == ButtonNext and isinstance(cls, type):
                buttons.append(ButtonNext(self.dsd, page=self, config={
                    'enabled': len(self.content or []) - (self.page_num * self.MAX_CONTENT) > self.MAX_CONTENT,
                    'page_num': self.page_num,
                }))
            # Append button class directly
            elif isinstance(cls, type):
                buttons.append(cls(self.dsd, page=self))
            else:
                buttons.append(None)

        # Highlight togglable buttons
        for b in buttons:
            if b:
                if ((b.page.select_active(b.toggle_id) and b.is_selected()) or
                        b.page.is_highlight_active(b.toggle_id)):
                    b.highlight = True

        self.buttons = buttons
        return self.buttons

    def get_icons(self, force=False):
        if len(self.icons) > 0 and not force:
            return self.icons
        icons = []
        for b in self.get_buttons(force=force):
            if b is None or not b.should_render():
                icons.append(None)
                continue
            icons.append(b.draw_image(native=True) or self.dsd.icons.draw_icon(b, native=True))
        self.icons = [i[0] if i else None for i in icons]
        self.images = [i[1] if i else None for i in icons]
        return self.icons

    def refresh(self):
        self.buttons = []
        self.icons = []

    def render(self, force=False):
        if force:
            self.refresh()
        key_count = self.dsd.deck.key_count()
        # Draw icons sequentially across keys (assume enough space per user)
        for k, img in enumerate(self.get_icons(force=force)):
            if k >= key_count:
                break  # don't exceed available keys
            try:
                self.dsd.set_image(k, img)
            except Exception as e:
                traceback.print_exc()
                # If something goes wrong with an icon, skip it and continue
                print(f"Warn: failed to draw icon for key {k} ({self.buttons[k]}): {e}")

        # Register key state callback
        self.dsd.deck.set_key_callback(self.callback)

    def next_page(self):
        self.refresh()
        self.page_num += 1

    def prev_page(self):
        self.refresh()
        self.page_num -= 1

    def callback(self, deck, key, pressed):
        button = self.buttons[key]
        try:
            if button and pressed:
                button.run()
        except Exception as e:
            log.error(f'Error running button: {e}, {button}')
            traceback.print_exc()


class ScrollPage(BasePage):
    ICON_TYPE_MAP = [
        ButtonBack,
        ButtonPrev,
        'app',
        ButtonNext,
        ButtonExit,
        # Row 2
        'content',
        'content',
        'content',
        'content',
        'content',
        # Row 3
        'content',
        'content',
        'content',
        'content',
        'content',
    ]
