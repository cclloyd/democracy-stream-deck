from __future__ import annotations
from .base import ScrollPage
from ..buttons.back import ButtonBack
from ..buttons.elgato import ButtonElgato
from ..buttons.exit import ButtonExit
from ..buttons.group import ButtonGroup
from ..buttons.quick import ButtonQuickInfo, ButtonQuickStart, ButtonQuickLoadout


class PageArmory(ScrollPage):
    content_class = ButtonGroup

    config = None
    prev_index = 1
    next_index = 3

    ICON_TYPE_MAP = [
        ButtonBack,
        None,
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

    def __init__(self, *args, content=None, parent=None, **kwargs):
        super().__init__(*args, content=content, parent=parent, **kwargs)
        self.content = content or [c for c in self.dsd.armory.categories.values() if 'parent' not in c]
        if self.appname == 'armory':
            self.ICON_TYPE_MAP[3] = ButtonElgato
        else:
            self.ICON_TYPE_MAP[3] = ButtonQuickStart
