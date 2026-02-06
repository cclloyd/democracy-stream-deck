from PIL import ImageDraw, ImageFont, Image
from StreamDeck.ImageHelpers import PILHelper

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase

class ButtonSave(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Save.png'
    icon_size = 35
    border_size = 90
    color = 'yellow'
    full = True
    highlight_hue = 77

    def run(self):
        from dsdultra.pages.save import PageSave
        if not isinstance(self.page, PageSave):
            page = PageSave(self.dsd, parent=self.page, app='save', config={'select_active': False})
            page.render()


class ButtonLabelIcon(ButtonBase):

    def run(self):
        self.page.app.select_active = False
        self.page.render()

    def draw_image(self):
        key_img = self.dsd.icons.bg.copy()
        self.dsd.icons._paste_center(key_img, self.dsd.icons.bg_img, 100, keep_aspect=False)
        draw = ImageDraw.Draw(key_img)

        draw.text((36, 20), 'CHOOSE', fill='white', anchor='mm', font=self.dsd.icons.get_font(12))
        draw.text((36, 45), 'ICON', fill='white', anchor='mm', font=self.dsd.icons.get_font(12))

        # Convert to native key format and set image
        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        return native_img


class ButtonLabelBorder(ButtonBase):

    def run(self):
        from dsdultra.pages.save import PageBorder
        if not isinstance(self.page, PageBorder):
            page = PageBorder(self.dsd, parent=self.page, config={'select_active': False})
            page.render(True)

    def draw_image(self):
        key_img = self.dsd.icons.bg.copy()
        self.dsd.icons._paste_center(key_img, self.dsd.icons.bg_img, 100, keep_aspect=False)
        draw = ImageDraw.Draw(key_img)

        draw.text((36, 20), 'CHOOSE', fill='white', anchor='mm', font=self.dsd.icons.get_font(12))
        draw.text((36, 45), 'BORDER', fill='white', anchor='mm', font=self.dsd.icons.get_font(11))

        # Convert to native key format and set image
        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        return native_img


class ButtonSelectBorder(ButtonBase):
    color = 'yellow'
    full = False

    def run(self):
        self.page.app.select_active = False
        self.page.render()


