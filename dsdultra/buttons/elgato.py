import subprocess
import threading

from dsdultra.buttons.base import ButtonBase


class ButtonElgato(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = 'icons/groups/elgato.png'
    color = 'none'
    icon_size = 65
    border_size = 90
    full = True
    toggle_id = 'elgato'
    highlight_hue = 210

    def run(self):
        if not self.enabled or self.should_disable():
            return

        if self.page.is_highlight_active(self.toggle_id):
            elgato_path = self.dsd.config.elgato_path
            subprocess.Popen([str(elgato_path)], close_fds=True)
            self.shutdown()
        else:
            self.page.set_highlight(self.toggle_id, True)

            def _reset():
                # Only reset if still active
                if self.page.is_highlight_active(self.toggle_id):
                    self.page.set_highlight(self.toggle_id, False)

            t = threading.Timer(self.toggle_timeout, _reset)
            t.daemon = True
            t.start()

    def should_disable(self):
        return not self.dsd.config.elgato_enabled
