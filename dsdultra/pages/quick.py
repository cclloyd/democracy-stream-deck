import traceback

from .base import ScrollPage
from .loadouts import PageLoadouts
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

    config = None
    select_active = False

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

    select_limit = 2
    # TODO: Support multiple select type per page
    select_type = 'swap'
    _selected = []

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

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, value):
        if value != self._selected:
            print(f"selected changed: {self._selected!r} -> {value!r}")
            traceback.print_stack()
        self._selected = value

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config=None, app: str = None):
        super().__init__(dsd, parent=parent, content=content, content_class=content_class, page_num=page_num, config=config, app=app)
        self.content = self.content or []

    # def refresh(self):
    #     self.content = self.app.selected[:] # Clone list
    #     super().refresh()
