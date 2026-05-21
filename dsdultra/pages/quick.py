import traceback

from .base import ScrollPage
from ..buttons.back import ButtonBack
from ..buttons.edit import ButtonSwap, ButtonRemove, ButtonEdit
from ..buttons.elgato import ButtonElgato
from ..buttons.exit import ButtonExit, ButtonExitConfirm
from ..buttons.home import ButtonHomeConfirm
from ..buttons.loadouts.save import ButtonSave
from ..buttons.obs import ButtonRecord
from ..buttons.quick import ButtonQuickStart, ButtonQuickInfo, ButtonQuickLoadout
from ..buttons.stratagem import ButtonStratagem


class PageQuickLoadout(ScrollPage):
    content_class = ButtonStratagem

    ICON_TYPE_MAP = [
        ButtonHomeConfirm,
        ButtonExitConfirm,
        ButtonQuickInfo,
        ButtonElgato,
        ButtonRecord,
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

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config=None, app: str = None):
        super().__init__(dsd, parent=parent, content=content, content_class=content_class, page_num=page_num, config=config, app=app)
        from .loadouts import PageLoadouts
        static_row = [
            self.dsd.armory.common['common_reinforce'],
            self.dsd.armory.common['common_resupply'],
            self.dsd.armory.mission['mission_hellbomb'],
            self.dsd.armory.common['common_eagle_rearm'],
            self.dsd.armory.mission['mission_seaf'],
        ]
        self.content = static_row + (self.content or [])
        if isinstance(parent, PageLoadouts):
            self.ICON_TYPE_MAP[0] = ButtonBack
        else:
            self.ICON_TYPE_MAP[0] = ButtonHomeConfirm


class PageQuickInfo(ScrollPage):
    content_class = ButtonStratagem

    ICON_TYPE_MAP = [
        ButtonBack,
        ButtonQuickLoadout,
        ButtonQuickInfo,
        ButtonQuickStart,
        ButtonExit,
        # Row 2
        None,
        ButtonEdit,
        ButtonSave,
        ButtonRemove,
        ButtonSwap,
        # Row 3
        'content',
        'content',
        'content',
        'content',
        'content',
    ]

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config=None, app: str = None):
        super().__init__(dsd, parent=parent, content=content, content_class=content_class, page_num=page_num, config=config, app=app)
        self.content = self.content or []
