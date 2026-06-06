import threading

from dsdultra.buttons.base import ButtonBase


class ButtonHome(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = 'icons/borders/SE.png'
    color = 'rainbow'
    icon_size = 50
    border_size = 90
    full = True
    gild = True

    def run(self):
        self.page.app.close()
        self.dsd.apps.get('dsd').render(True)


class ButtonHomeConfirm(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = 'icons/borders/SE.png'
    color = 'rainbow'
    icon_size = 50
    border_size = 90
    full = True
    gild = True
    toggle_id = 'home'
    highlight_hue = 320

    def run(self):
        if self.page.is_highlight_active(self.toggle_id):
            self.page.set_highlight(self.toggle_id, False, rerender=False)
            self.page.app.close()
            from dsdultra.pages.home import PageHome
            app = self.dsd.apps.get('dsd', PageHome(self.dsd, app='dsd'))
            app.render(True)
        else:
            self.page.set_highlight('home', True)
            def _reset():
                # Only reset if still active
                if self.page.is_highlight_active(self.toggle_id):
                    self.page.set_highlight(self.toggle_id, False)

            t = threading.Timer(self.toggle_timeout, _reset)
            t.daemon = True
            t.start()
