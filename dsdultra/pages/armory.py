from .base import ScrollPage
from ..buttons.back import ButtonBack
from ..buttons.exit import ButtonExit
from ..buttons.group import ButtonGroup
from ..buttons.nav import ButtonPrev, ButtonNext
from ..buttons.quick import ButtonQuickInfo, ButtonQuickStart, ButtonQuickLoadout
from ..nav.armory import ARMORY


class PageArmory(ScrollPage):
    content_class = ButtonGroup

    content = list(ARMORY.values())

    config = None
    select_active = False
    select_limit = 5
    selected = []

    ICON_TYPE_MAP = [
        ButtonBack,
        ButtonQuickLoadout,
        ButtonQuickInfo,
        ButtonQuickStart,
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

