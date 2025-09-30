from .base import ScrollPage
from ..buttons.back import ButtonBack
from ..buttons.exit import ButtonExit
from ..buttons.home import ButtonHome
from ..buttons.quick import ButtonQuickStart, ButtonQuickInfo, ButtonQuickLoadout
from ..buttons.stratagem import ButtonStratagem
from ..buttons.swap import ButtonSwap
from ..nav.armory import ARMORY


class PageQuickLoadout(ScrollPage):
    content_class = ButtonStratagem

    config = None
    select_active = False
    select_limit = 2
    selected = []

    ICON_TYPE_MAP = [
        ButtonHome,
        None,
        None,
        None,
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

    def __init__(self, dsd, parent=None, content=None, content_class=None, page_num=0, config=None, app: str = None):
        super().__init__(dsd, parent=parent, content=content, content_class=content_class, page_num=page_num, config=config, app=app)
        firstRow = [
            ARMORY['common']['content']['common_reinforce'],
            ARMORY['common']['content']['common_resupply'],
            ARMORY['mission']['content']['mission_hellbomb'],
            ARMORY['common']['content']['common_eagle_rearm'],
            ARMORY['mission']['content']['mission_seaf'],
        ]
        self.content = firstRow + (self.content or [])
        # Unselect items so they aren't highlighted
        # self.content = [item.update({'selected': False}) or item if item is not None else None for item in self.content]


class PageQuickInfo(ScrollPage):
    content_class = ButtonStratagem

    select_limit = 2
    # TODO: Support multiple select type per page
    select_type = 'swap'

    ICON_TYPE_MAP = [
        ButtonBack,
        ButtonQuickLoadout,
        ButtonQuickInfo,
        ButtonQuickStart,
        ButtonExit,
        # Row 2
        None,
        None,
        None,
        None,
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
        
    def refresh(self):
        super().refresh()
        print('refreshing content')
        # print(self.content)
        # print(self.app.select_type)
        # print(self.content[0].config)
        # self.content = [item for item in self.content if item is not None and item.config.get('selected', {}).get(self.app.select_type)]
        # print(self.content)
