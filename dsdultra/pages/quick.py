from __future__ import annotations
from typing import TYPE_CHECKING

from .base import ScrollPage
from ..armory.stratagems import Stratagem
from ..buttons.loadouts.loadout import ButtonRefreshLoadout

if TYPE_CHECKING:
    from ..armory.loadouts import Loadout
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
    loadout: Loadout = None

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

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config=None, app: str = None, loadout=None):
        super().__init__(dsd, parent=parent, content=content, content_class=content_class, page_num=page_num, config=config, app=app)
        from .loadouts import PageLoadouts
        self.static_row = [
            self.dsd.armory.common['common_reinforce'],
            self.dsd.armory.common['common_resupply'],
            self.dsd.armory.mission['mission_hellbomb'],
            self.dsd.armory.common['common_eagle_rearm'],
            self.dsd.armory.mission['mission_seaf'],
        ]
        self.content = self.static_row + (self.content or [])
        if isinstance(parent, PageLoadouts):
            self.ICON_TYPE_MAP[0] = ButtonBack
        else:
            self.ICON_TYPE_MAP[0] = ButtonHomeConfirm
        self.loadout = loadout

    def refresh(self):
        self.content = self.static_row + Stratagem.parse_stratagems(self.dsd, self.get_store('active_loadout').stratagems)


class PageQuickInfo(ScrollPage):
    content_class = ButtonStratagem

    ICON_TYPE_MAP = [
        ButtonQuickLoadout,
        None,
        ButtonQuickInfo,
        ButtonQuickStart,
        ButtonExit,
        # Row 2
        ButtonRefreshLoadout,
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

    def __init__(self, dsd, *args, **kwargs):
        super().__init__(dsd, *args, **kwargs)
        self.content = self.get_store('active_loadout').stratagems
        from dsdultra.pages.loadouts import PageLoadouts
        if isinstance(self.parent, PageLoadouts):
            self.ICON_TYPE_MAP[0] = ButtonBack
        else:
            self.ICON_TYPE_MAP[0] = ButtonQuickLoadout

    def refresh(self):
        self.content = Stratagem.parse_stratagems(self.dsd, self.get_store('active_loadout').stratagems)
