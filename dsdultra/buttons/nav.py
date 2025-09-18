from dsdultra.buttons.base import ButtonBase


class ButtonPrev(ButtonBase):
    def __init__(self, dsd, page=None, config=None):
        super().__init__(dsd, page=page, config=config)

    icon = 'dsdultra/assets/icons/groups/Arrow.png'
    icon_size = 35
    icon_rotate = 270
    color = 'yellow'
    full = True
    gild = True

    def run(self):
        if not self.config.get('enabled', True):
            return
        self.page.prev_page()
        self.page.render()

class ButtonNext(ButtonBase):
    def __init__(self, dsd, page=None, config=None):
        super().__init__(dsd, page=page, config=config)

    icon = 'dsdultra/assets/icons/groups/Arrow.png'
    icon_size = 35
    icon_rotate = 90
    color = 'yellow'
    full = True

    def run(self):
        if not self.config.get('enabled', True):
            return
        self.page.next_page()
        self.page.render()
