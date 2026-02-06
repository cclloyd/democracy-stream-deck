from .base import ScrollPage
from ..buttons.exit import ButtonExit
from ..buttons.loadouts.save import ButtonLabelIcon, ButtonLabelBorder, ButtonSave, ButtonSelectBorder
from ..buttons.stratagem import ButtonStratagem


class PageSave(ScrollPage):
    content_class = ButtonStratagem

    ICON_TYPE_MAP = [
        ButtonLabelIcon,
        ButtonLabelBorder,
        None,
        ButtonSave,
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
        self.content = self.content or []

    def refresh(self):
        self.content = self.app.selected[:] # Clone list
        super().refresh()


class PageBorder(ScrollPage):
    content_class = ButtonSelectBorder

    ICON_TYPE_MAP = [
        ButtonLabelIcon,
        ButtonLabelBorder,
        None,
        ButtonSave,
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
        self.content = self.content or []

    def refresh(self):
        self.content = self.app.selected[:] # Clone list
        super().refresh()
