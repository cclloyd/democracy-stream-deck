from .base import BasePage
from ..buttons.back import ButtonBack
from ..buttons.exit import ButtonExit
from ..buttons.group import ButtonGroup
from ..buttons.nav import ButtonNext, ButtonPrev


class PageLoadouts(BasePage):
    content_class = ButtonGroup

    ICON_TYPE_MAP = [
        ButtonBack,
        ButtonPrev,
        None,
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

    def __init__(self, *args, content=None, parent=None, **kwargs):
        super().__init__(*args, content=content, parent=parent, **kwargs)
        self.content = content or [c for c in self.dsd.loadouts.loadouts]

    def get_buttons_cb(self, cls: type):
        return cls(self.dsd, page=self)

    # TODO: Add Loadout button that run() loads PageQuick or whatever the final run page for a loadout is
    # TODO: Make loadout button icon show the 4 weapon icons, and then add the faction icon, and other icon options