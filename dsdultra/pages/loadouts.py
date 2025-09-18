from .base import BasePage
from ..buttons.back import ButtonBack
from ..buttons.exit import ButtonExit
from ..buttons.group import ButtonGroup
from ..buttons.nav import ButtonNext, ButtonPrev


class PageLoadouts(BasePage):
    content_class = ButtonGroup

    ICON_TYPE_MAP = [
        ButtonBack,
        ButtonExit,
        None,
        ButtonPrev,
        ButtonNext,
        # Row 2
        None,
        None,
        None,
        None,
        None,
        # Row 3
        None,
        None,
        None,
        None,
        None,
    ]

    def get_buttons_cb(self, cls: type):
        return cls(self.dsd, page=self)

    def get_content(self):
        if not self.content:
            loadouts = self.dsd.config.get('loadouts', [])
            self.content = loadouts
        return self.content
