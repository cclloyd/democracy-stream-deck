from typing import TYPE_CHECKING

from .base import BasePage
if TYPE_CHECKING:
    from ..armory.loadouts import Loadout
from ..buttons.back import ButtonBack
from ..buttons.exit import ButtonExit
from ..buttons.loadout import ButtonLoadout
from ..buttons.nav import ButtonNext, ButtonPrev


class PageLoadouts(BasePage):
    content_class = ButtonLoadout
    content: list[Loadout]

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
