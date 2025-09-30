import traceback
from typing import Optional

from dsdultra.buttons.back import ButtonBack
from dsdultra.buttons.base import ButtonBase
from dsdultra.buttons.exit import ButtonExit
from dsdultra.buttons.nav import ButtonPrev, ButtonNext


class BasePage:
    ICON_TYPE_MAP: list[None | ButtonBase | str] = [None] * 15


    # For scrollable pages
    appname: str = None
    MAX_CONTENT = 10
    page_num = 0
    content_class = ButtonExit
    content: Optional[dict | list] = None

    # For selectable pages
    select_active = None
    select_limit = 5
    selected = []
    select_type = None
    toggle_active = {}

    @property
    def app(self):
        return self.dsd.apps.get(self.appname, None)

    def close(self):
        del self.dsd.apps[self.appname]

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config=None, app: str = None):
        self.dsd = dsd
        self.parent = parent
        self.buttons = []
        self.icons = []
        self.content = content or self.content
        self.content_class = content_class or self.content_class
        self.page_num = page_num
        self.appname = app or self.appname or self.parent.appname

        if app:
            if app not in self.dsd.apps:
                self.dsd.apps[app] = self
                self.appname = app

        self.config = config or {}
        self.select_active = self.config.get('select_active', False)
        self.select_limit = self.config.get('select_limit', 5)
        self.selected = self.config.get('selected', [])

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
            app = self.app
            if cls is None:
                buttons.append(None)
            elif cls == 'app':
                buttons.append(self.app.ICON_TYPE_MAP[k](self.dsd, page=self))
            elif cls == 'parent':
                buttons.append(self.parent.ICON_TYPE_MAP[k](self.dsd, page=self))
            elif cls == 'content' and self.content_class is not None:
                if added < len(data):
                    if data[added]:
                        config.update(data[added] if isinstance(data[added], dict) else data[added].config)
                    if self.select_type:
                        config['selected'][self.select_type] = any(item.config.get('id') == config.get('id') for item in self.selected)
                    elif self.app.select_type:
                        config['selected'][app.select_type] = any(item.config.get('id') == config.get('id') for item in app.selected)
                    if data[added] is None:
                        buttons.append(None)
                    else:
                        buttons.append(self.content_class(self.dsd, page=self, config=config))
                    added += 1
                else:  # We ran out of content
                    buttons.append(None)
            elif cls == ButtonPrev and isinstance(cls, type):
                buttons.append(cls(self.dsd, page=self, config={
                    'enabled': self.page_num > 0,
                    'page_num': self.page_num,
                }))
            elif cls == ButtonNext and isinstance(cls, type):
                buttons.append(cls(self.dsd, page=self, config={
                    'enabled': len(self.get_content()) - (self.page_num * self.MAX_CONTENT) > self.MAX_CONTENT,
                    'page_num': self.page_num,
                }))
            elif isinstance(cls, type):
                buttons.append(cls(self.dsd, page=self))
            else:
                buttons.append(None)

        # Highlight togglable buttons
        for b in buttons:
            if b and b.page.toggle_active.get(b.toggle_id, None):
                b.config['highlight'] = True

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
            print(f'Error running button', e, button)


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