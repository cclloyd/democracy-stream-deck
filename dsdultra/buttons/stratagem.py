from time import sleep

from dsdultra.buttons.base import ButtonBase

try:
    from pynput.keyboard import Controller as _KbController
    from pynput.keyboard import Key as _KbKey
    _kb = _KbController()
except Exception:
    print('WARNING: No keyboard input available.')
    _kb = None


class ButtonStratagem(ButtonBase):
    icon = 'dsdultra/assets/icons/groups/Close.png'
    icon_size = 60
    border_size = 90
    color = 'blue'

    def run(self):
        # Select stratagem instead of activating it
        from dsdultra.pages.armory import PageArmory
        app: PageArmory = self.page.app
        if app and app.select_active:
            if len(app.selected) < app.select_limit:
                if not any(item.get('id') == self.config.get('id') for item in app.selected):
                    app.selected.append(self.config)
                else:
                    app.selected = [item for item in app.selected if item.get('id') != self.config.get('id')]
                self.page.render(True)
                self.page.app.refresh()
        # Do keyboard input
        else:
            ACTION_DELAY = 32  # Delay in ms between inputs
            KEYUP_DELAY = 32  # Delay in ms before releasing key
            if self.config and self.config.get('code'):
                if _kb is not None:
                    mapping = {
                        'up': _KbKey.up,
                        'down': _KbKey.down,
                        'left': _KbKey.left,
                        'right': _KbKey.right,
                    }
                    _kb.press(_KbKey.end)
                    sleep(ACTION_DELAY / 1000.0)
                    for step in self.config['code']:
                        key = mapping.get(str(step).lower())
                        if key is None:
                            continue
                        _kb.press(key)
                        sleep(KEYUP_DELAY / 1000.0)
                        _kb.release(key)
                        sleep(ACTION_DELAY / 1000.0)
                    sleep(ACTION_DELAY / 1000.0)
                    _kb.release(_KbKey.end)
