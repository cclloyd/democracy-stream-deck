from __future__ import annotations

from typing import TYPE_CHECKING

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase
from dsdultra.buttons.stratagem import ButtonStratagem

if TYPE_CHECKING:
    from dsdultra.pages.armory import PageArmory
    from dsdultra.pages.quick import PageQuickInfo


class ButtonGroup(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Armory.png'
    icon_size = 45
    border_size = 90
    color = 'rainbow'
    full = True
    page: PageArmory | PageQuickInfo

    def __init__(self, dsd, page=None, config: dict = None):
        super().__init__(dsd, page=page, config=config)

    def run(self):
        # Get subcategories or stratagems, then pass to and render next page.
        cls = type(self.page)
        if len(self.config.get('children', [])) > 0:
            # Populate from categories, using children as a filter
            content = [c for c in self.dsd.armory.categories.values() if c['id'] in self.config['children']]
        else:
            # Populate from stratagems in that category
            content = []
            for i in self.dsd.armory.all.values():
                if i.type != self.config['filter_type']:
                    continue
                if not i.filter(self.config.get('filter_attributes', None)):
                    continue
                content.append(i)
        # Content class is either this if there are subcategories, or ButtonStratagem
        page = cls(self.dsd, parent=self.page, content=content, content_class=self.__class__ if len(self.config.get('children', [])) > 0 else ButtonStratagem)
        return page.render(True)

    def __str__(self):
        return f'<ButtonGroup:{self.config['id']}>'

    def __repr__(self):
        return str(self)