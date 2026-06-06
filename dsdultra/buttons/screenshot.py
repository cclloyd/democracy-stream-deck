import threading
import traceback

from dsdultra.buttons.base import ButtonBase
from dsdultra.logging import log


class ButtonScreenshot(ButtonBase):
    icon = 'icons/groups/Unknown.png'
    color = 'none'
    icon_size = 70
    border_size = 90
    full = True
    toggle_id = 'screenshot'
    highlight_hue = 77
    toggle_timeout = 1

    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)
        if self.page.get_highlight('screenshot') == 'error':
            self.highlight_hue = 310

    def run(self):
        # Automatically reset the toggle after 3 seconds
        def _reset():
            # Only reset if still active
            if self.page.is_highlight_active(self.toggle_id):
                self.page.set_highlight(self.toggle_id, False)

        t = threading.Timer(self.toggle_timeout, _reset)
        t.daemon = True
        try:
            self.dsd.state.screenshot(self.page)
        except Exception as e:
            log.error(e)
            traceback.print_exc()
            self.highlight_hue = 310
            self.page.set_highlight(self.toggle_id, 'error', rerender=False)
        t.start()
        if not self.page.is_highlight_active(self.toggle_id):
            self.page.set_highlight(self.toggle_id, True, rerender=False)
        self.page.render(True)