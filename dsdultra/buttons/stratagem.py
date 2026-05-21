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

        # TODO: Should this swap/remove logic be moved to those respective buttons if possible?

        # Active on edit page when swap button is pressed to swap 2 slots
        if self.page.select_active('swap'):
            if len(self.page.selected('swap')) == 0:
                self.page.add_select('swap', self)
            else:
                item1 = self.page.selected('swap')[0]
                item2 = self
                selected = self.page.selected(self.toggle_id)
                i = next(i for i, item in enumerate(selected) if item.config['id'] == item1.config['id'])
                j = next(i for i, item in enumerate(selected) if item.config['id'] == item2.config['id'])
                selected[i], selected[j] = selected[j], selected[i]
                self.page.clear_select('swap', rerender=False)
                self.page.set_select_active('swap', False, rerender=False)
                self.page.set_highlight('swap', False, rerender=False)
                self.page.content = [*selected]  # Write changes back to page content to persist rerendering
                self.page.get_store('active_loadout').set_stratagems(self.dsd, self.page.content)
                self.page.render(True)

        # Active on edit page when delete button is pressed to remove stratagem from selection
        elif self.page.select_active('remove'):
            self.page.set_highlight('remove', False, rerender=False)
            self.page.set_select_active('remove', False, rerender=False)
            self.page.remove_select('stratagems', self, rerender=False)
            self.page.content = self.page.selected('stratagems')
            self.page.get_store('active_loadout').set_stratagems(self.dsd, self.page.content)

            # self.page.refresh()

        # Active when still selecting stratagems for a loadout
        elif self.page.select_active('stratagems'):
            if self.is_selected():
                self.page.remove_select('stratagems', self, False)
                self.page.get_store('active_loadout').set_stratagems(self.dsd, self.page.selected('stratagems'))
            else:
                self.page.add_select('stratagems', self, False)
                self.page.get_store('active_loadout').set_stratagems(self.dsd, self.page.selected('stratagems'))
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
