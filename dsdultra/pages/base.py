import traceback
import uuid
from typing import Optional

from dsdultra import logging
from dsdultra.buttons.back import ButtonBack
from dsdultra.buttons.base import ButtonBase
from dsdultra.buttons.exit import ButtonExit
from dsdultra.buttons.nav import ButtonPrev, ButtonNext
from dsdultra.logging import log


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
        del self.dsd.apps[self.appname]

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config: dict = {}, app: str = None):
        self.id = str(uuid.uuid4())
        self.dsd = dsd
        self.parent = parent
        self.buttons = []
        self.icons = []
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

    def add_select(self, select_type: str, item: ButtonBase, rerender=True, force=True):
        if item.config['id'] not in [b.config['id'] for b in self.dsd.state.selected[self.appname][select_type]]:
            self.dsd.state.selected[self.appname][select_type].append(item)
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
        return
        if len(page.selected) == 0:
            page.selected.append(self)
            self.page.render(True)
        elif len(page.selected) >= 1:
            page.selected.append(self)
            # Find indices of selected items in page.content
            idx1 = next((i for i, item in enumerate(page.app.selected)
                         if item and item.config.get('id') == page.selected[0].config.get('id')), -1)
            idx2 = next((i for i, item in enumerate(page.app.selected)
                         if item and item.config.get('id') == page.selected[1].config.get('id')), -1)
            # Swap items if both found
            if idx1 >= 0 and idx2 >= 0:
                page.app.selected[idx1], page.app.selected[idx2] = page.app.selected[idx2], page.app.selected[idx1]
            # Reset selection
            page.selected = []
            return self.page.render(True)

    def get_buttons_cb(self, cls: type, k: int, added: int):
        pass

    def get_content(self):
        return self.content

    def get_buttons(self):
        if len(self.buttons) > 0:
            return self.buttons
        buttons = []
        added = 0
        data = (self.get_content() or [])[self.page_num * self.MAX_CONTENT:(self.page_num + 1) * self.MAX_CONTENT]
        for k, cls in enumerate(self.ICON_TYPE_MAP):
            config = {}
            if type(self) == ScrollPage:
                config = {'app': self.appname or self.parent}
            config.update({'selected': {}})

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

                    # if self.select_type:
                    #     config['selected'][self.select_type] = any(item.config.get('id') == config.get('id') for item in self.selected)
                    # elif self.app.select_type:
                    #     config['selected'][app.select_type] = any(item.config.get('id') == config.get('id') for item in app.selected)

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
                    'enabled': len(self.get_content()) - (self.page_num * self.MAX_CONTENT) > self.MAX_CONTENT,
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

    def get_icons(self):
        if len(self.icons) > 0:
            return self.icons
        icons = []
        for b in self.get_buttons():
            if b is None or not b.should_render():
                icons.append(None)
                continue
            icons.append(b.draw_image() or self.dsd.icons.draw_icon(b))
        self.icons = icons
        return self.icons

    def refresh(self):
        self.buttons = []
        self.icons = []

    def render(self, force=False):
        if force:
            self.refresh()
        key_count = self.dsd.deck.key_count()
        # Draw icons sequentially across keys (assume enough space per user)
        for k, img in enumerate(self.get_icons()):
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
            traceback.print_exc()
            log.info(f'Error running button', e, button)


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
