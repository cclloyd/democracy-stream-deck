from PIL import ImageDraw, ImageFont, Image
from StreamDeck.ImageHelpers import PILHelper

from dsdultra.buttons.base import ButtonBase
from dsdultra import ASSETS_DIR


class ButtonQuickLoadout(ButtonBase):
    icon = ASSETS_DIR / 'icons/borders/SE.png'
    icon_size = 45
    border_size = 90
    color = 'yellow'
    full = True
    gild = True

    def should_render(self):
        return self.page.appname == 'quick' or self.page.appname == 'dsd'

    def run(self):
        from dsdultra.pages.armory import PageArmory
        page = PageArmory(self.dsd, parent=self.page, app='quick', config={
            'select_active': True,
            'select_limit': 5,
        })
        page.render()


class ButtonQuickInfo(ButtonBase):
    def run(self):
        from dsdultra.pages.quick import PageQuickInfo
        if type(self.page) != PageQuickInfo:
            page = PageQuickInfo(self.dsd, parent=self.page, app='quick', config=self.page.parent.config, content=self.page.app.selected)
            page.render()

    def draw_image(self):
        key_img = self.dsd.icons.bg.copy()
        self.dsd.icons._paste_center(key_img, self.dsd.icons.bg_img, 100, keep_aspect=False)
        draw = ImageDraw.Draw(key_img)

        current = len(self.page.app.selected)
        limit = self.page.app.select_limit
        draw.text((36, 15), "SELECTED", fill="white", anchor="mm", font=self.dsd.icons.get_font(9))
        draw.text((36, 45), f'{current} / {limit}', fill='white' if current < limit else '#F6D535', anchor="mm", font=self.dsd.icons.get_font(18))

        # Convert to native key format and set image
        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        return native_img

    def should_render(self):
        return self.page.appname == 'quick'



class ButtonQuickStart(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Hellpod1.png'
    icon_size = 45

    def should_render(self):
        return self.page.appname == 'quick'

    def draw_image(self):
        key_img = self.dsd.icons.bg.copy()
        self.dsd.icons._paste_center(key_img, self.dsd.icons.bg_img, 100, keep_aspect=False)
        draw = ImageDraw.Draw(key_img)
        draw.text((36, 14), "START", fill="white", anchor="mm", font=self.dsd.icons.get_font(14))

        icon_img = Image.open(self.icon).convert("RGBA")
        icon_img = self.dsd.icons.resize_for_iconbox(icon_img, self.icon_size)
        icon_pos = ((key_img.width - icon_img.width) // 2, int(key_img.height * 0.6) - icon_img.height // 2)
        key_img.paste(icon_img, icon_pos, icon_img)

        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        return native_img

    def run(self):
        from dsdultra.pages.quick import PageQuickLoadout
        content = self.page.app.selected
        page = PageQuickLoadout(self.dsd, parent=self.page, app='quick', config={ 'select_active': False }, content=content)
        page.app.select_active = False
        page.render()