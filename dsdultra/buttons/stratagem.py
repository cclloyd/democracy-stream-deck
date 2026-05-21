from time import sleep

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase
from dsdultra.logging import log

try:
    from pynput.keyboard import Controller as _KbController
    from pynput.keyboard import Key as _KbKey
    _kb = _KbController()
except Exception:
    log.warn('WARNING: No keyboard input available.')
    _kb = None


class ButtonStratagem(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 60
    border_size = 90
    toggle_id = 'stratagems'

    def run(self):
        from dsdultra.pages.quick import PageQuickInfo

        # Active on edit page when swap button is pressed to swap 2 slots
        if self.page.select_active('swap'):
            if len(self.page.selected('swap')) == 0:
                self.page.add_select('swap', self)
            else:
                selected = self.page.selected(self.toggle_id)
                swap_item = self.page.selected('swap')[0]
                i = next(i for i, item in enumerate(selected) if item.config['id'] == swap_item.config['id'])
                j = next(i for i, item in enumerate(selected) if item.config['id'] == self.config['id'])
                selected[i], selected[j] = selected[j], selected[i]
                self.page.clear_select('swap')
                self.page.set_select_active('swap', False)
                self.page.set_highlight('swap', False)

        # Active on edit page when delete button is pressed to remove stratagem from selection
        elif self.page.select_active('remove'):
            self.page.set_highlight('remove', False, False)
            self.page.set_select_active('remove', False, False)
            self.page.remove_select('stratagems', self)

        # Active when still selecting stratagems for a loadout
        elif self.page.select_active('stratagems'):
            if self.is_selected():
                self.page.remove_select('stratagems', self, False)
            else:
                self.page.add_select('stratagems', self, False)
            self.page.app.render(True)

        # Do keyboard input
        elif not isinstance(self.page, PageQuickInfo):
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
