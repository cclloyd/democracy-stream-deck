from time import sleep

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase

try:
    from pynput.keyboard import Controller as _KbController
    from pynput.keyboard import Key as _KbKey
    _kb = _KbController()
except Exception:
    print('WARNING: No keyboard input available.')
    _kb = None


class ButtonStratagem(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 60
    border_size = 90
    color = 'blue'

    def run(self):
        # Select stratagem instead of activating it
        from dsdultra.pages.armory import PageArmory
        from dsdultra.pages.quick import PageQuickInfo
        app: PageArmory = self.page.app
        page: PageQuickInfo = self.page

        # Run select for page
        if page.select_active == 'swap':
            if len(page.selected) == 0:
                page.selected.append(self)
                self.page.render(True)
            elif len(page.selected) >= 1:
                page.selected.append(self)
                # Find indices of selected items in page.content
                idx1 = next((i for i, item in enumerate(page.content)
                             if item and item.config.get('id') == page.selected[0].config.get('id')), -1)
                idx2 = next((i for i, item in enumerate(page.content)
                             if item and item.config.get('id') == page.selected[1].config.get('id')), -1)
                # Swap items if both found
                if idx1 >= 0 and idx2 >= 0:
                    page.content[idx1], page.content[idx2] = page.content[idx2], page.content[idx1]
                # Reset selection
                page.selected = []
                # page.select_active = False
                # page.toggle_active['swap'] = False
                self.page.render(True)
        elif page.select_active == 'remove':
            page.app.selected = [item for item in page.app.selected if item.config['id'] != self.config['id']]
            page.select_active = None
            page.toggle_active['remove'] = False
            page.render(True)


        # Run select for app
        elif app and app.select_active:
            if len(app.selected) < app.select_limit:
                if not any(item.config.get('id') == self.config.get('id') for item in app.selected):
                    app.selected.append(self)
                else:
                    app.selected = [item for item in app.selected if item.config.get('id') != self.config.get('id')]
                self.page.app.render(True)

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
