from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import ImageDraw, Image
from StreamDeck.ImageHelpers import PILHelper

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase

if TYPE_CHECKING:
    from dsdultra.pages.quick import PageQuickInfo, PageQuickLoadout


class ButtonQuickLoadout(ButtonBase):
    icon = ASSETS_DIR / 'icons/borders/SE.png'
    icon_size = 45
    border_size = 90
    full = True
    gild = True
    toggle_id = 'stratagems'

    def should_render(self):
        return self.page.appname in ('quick', 'dsd')

    def run(self):
        from dsdultra.armory.loadouts import Loadout
        from dsdultra.pages.armory import PageArmory
        from dsdultra.pages.quick import PageQuickInfo
        from dsdultra.pages.home import PageHome
        page = PageArmory(self.dsd, parent=self.page.app.parent if isinstance(self.page, PageQuickInfo) else self.page, app='quick')
        page.app.set_select_active(self.toggle_id, True, rerender=False)
        page.set_store('active_loadout', page.get_store('active_loadout') or Loadout(self.dsd, new=True), rerender=False)
        if isinstance(self.page, PageHome):
            page.set_store('active_loadout', Loadout(self.dsd, new=True), rerender=False)
            page.set_select('stratagems', [], rerender=False)
        page.render(True)


class ButtonQuickInfo(ButtonBase):
    toggle_id = 'stratagems'
    page: PageQuickLoadout | PageQuickInfo

    def run(self):
        from dsdultra.pages.loadouts import PageLoadouts
        from dsdultra.pages.quick import PageQuickInfo
        if not isinstance(self.page, PageQuickInfo):
            if isinstance(self.page.app, PageLoadouts):
                content = self.page.content[5:]
            else:
                content = self.page.get_store('active_loadout').stratagems
                # self.dsd.loadouts.unsaved.stratagems = content
            page = PageQuickInfo(
                self.dsd,
                parent=self.page,
                config=self.page.config if isinstance(self.page.app, PageLoadouts) else self.page.parent.config,
                content=content,
            )
            page.app.set_select_active(self.toggle_id, False, rerender=False)
            page.render(True)

    def draw_image(self, native=False):
        key_img = self.dsd.icons.bg.copy()
        self.dsd.icons._paste_img(key_img, self.dsd.icons.bg_img, 100, keep_aspect=False)
        draw = ImageDraw.Draw(key_img)
        current = len(self.page.app.selected(self.toggle_id))
        limit = self.page.app.select_limit(self.toggle_id)
        draw.text((36, 15), 'SELECTED', fill='white', anchor='mm', font=self.dsd.icons.get_font(9))
        draw.text((36, 45), f'{current} / {limit}', fill='white' if current < limit-1 else '#F6D535', anchor='mm', font=self.dsd.icons.get_font(18))

        # Convert to native key format and set image
        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        if native:
            return native_img, key_img
        return native_img

    def should_render(self):
        return self.page.appname in ('quick', 'loadouts')


class ButtonQuickStart(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Hellpod1.png'
    icon_size = 45
    toggle_id = 'stratagems'

    def should_render(self):
        return self.page.appname in ('quick', 'loadouts')

    def draw_image(self, native=False):
        key_img = self.dsd.icons.bg.copy()
        self.dsd.icons._paste_img(key_img, self.dsd.icons.bg_img, 100, keep_aspect=False)
        draw = ImageDraw.Draw(key_img)
        draw.text((36, 14), 'START', fill='white', anchor='mm', font=self.dsd.icons.get_font(14))

        icon_img = Image.open(self.icon).convert('RGBA')
        icon_img = self.dsd.icons.resize_for_iconbox(icon_img, self.icon_size)
        icon_pos = ((key_img.width - icon_img.width) // 2, int(key_img.height * 0.6) - icon_img.height // 2)
        key_img.paste(icon_img, icon_pos, icon_img)

        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        if native:
            return native_img, key_img
        return native_img

    def run(self):
        from dsdultra.pages.quick import PageQuickLoadout
        content = self.page.app.selected(self.toggle_id)
        self.page.app.set_select_active(self.toggle_id, False, rerender=False)
        page = PageQuickLoadout(self.dsd, parent=self.page, content=content)
        page.render(True)