import traceback
from colorsys import rgb_to_hsv, hsv_to_rgb
from pathlib import Path
from PIL import Image
from PIL import ImageFont
from PIL import ImageEnhance
from PIL import ImageChops
from PIL import ImageDraw
from StreamDeck.ImageHelpers import PILHelper
from dsdultra import ASSETS_DIR
from dsdultra.armory.stratagems import Stratagem
from dsdultra.buttons.base import ButtonBase
from typing import TYPE_CHECKING

from dsdultra.buttons.loadout import ButtonLoadout

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra

BORDERS = {
    'yellow': {
        'half': ASSETS_DIR / 'icons/borders/Yellow Half.png',
        'full': ASSETS_DIR / 'icons/borders/Yellow Full.png',
    },
    'blue': {
        'half': ASSETS_DIR / 'icons/borders/Blue Half.png',
        'full': ASSETS_DIR / 'icons/borders/Blue Full.png',
    },
    'green': {
        'half': ASSETS_DIR / 'icons/borders/Green Half.png',
        'full': ASSETS_DIR / 'icons/borders/Green Full.png',
    },
    'red': {
        'half': ASSETS_DIR / 'icons/borders/Red Half.png',
        'full': ASSETS_DIR / 'icons/borders/Red Full.png',
    },
    'rainbow': {
        'half': ASSETS_DIR / 'icons/borders/Rainbow.png',
        'full': ASSETS_DIR / 'icons/borders/Rainbow.png',
    },
    'none': {
        'half': None,
        'full': None,
    }
}


class IconGenerator:
    dsd: 'DSDUltra' = None
    bg = None
    font_path = ASSETS_DIR / 'fonts/Orbitron-v.ttf'

    def __init__(self, dsd):
        self.dsd = dsd
        self.size = dsd.deck.KEY_PIXEL_WIDTH

        if not self.bg:
            bg_path = ASSETS_DIR / 'icons/Background.png'
            selected_path = ASSETS_DIR / 'icons/borders/Selected2.png'
            icon_mask_path = ASSETS_DIR / 'icons/groups/mask72-1.png'
            gild_path = ASSETS_DIR / 'icons/groups/Gild Half.png'
            gild_path_full = ASSETS_DIR / 'icons/groups/Gild Full.png'
            # Precompute a blank background at the correct key size
            self.bg = PILHelper.create_image(self.dsd.deck)
            self.bg_img = Image.open(bg_path).convert("RGBA")
            self.selected_img = Image.open(selected_path).convert("RGBA")
            self.icon_mask_img = Image.open(icon_mask_path).convert("L")
            self.gild_img = Image.open(gild_path).convert("RGBA")
            self.gild_img_full = Image.open(gild_path_full).convert("RGBA")

    def get_font(self, size):
        return ImageFont.truetype(self.font_path, size)

    def _paste_img(
            self,
            base_img: Image.Image,
            layer_img: Image.Image,
            pct: float,
            keep_aspect: bool = True,
            x: int | None = None,
            y: int | None = None,
    ):
        """Paste `layer_img` on `base_img` scaled to `pct`% of base size.

        Defaults to centered placement unless `x` and/or `y` are provided.
        """
        target_w = int(base_img.width * (pct / 100.0))
        target_h = int(base_img.height * (pct / 100.0))

        if keep_aspect:
            layer = layer_img.copy()
            layer.thumbnail((target_w, target_h), Image.LANCZOS)
        else:
            layer = layer_img.resize((target_w, target_h), Image.LANCZOS)

        if x is None:
            x = (base_img.width - layer.width) // 2
        if y is None:
            y = (base_img.height - layer.height) // 2

        base_img.paste(layer, (x, y), layer)
        return base_img

    def resize_for_iconbox(self, img: Image.Image, pct: float, keep_aspect: bool = True) -> Image.Image:
        canvas_size = self.size
        box = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        target_side = int(canvas_size * (pct / 100.0))

        if keep_aspect:
            icon = img.copy()
            icon.thumbnail((target_side, target_side), Image.LANCZOS)
        else:
            icon = img.resize((target_side, target_side), Image.LANCZOS)

        x = (canvas_size - icon.width) // 2
        y = (canvas_size - icon.height) // 2
        box.paste(icon, (x, y), icon)
        return box

    # TODO: Move the functions that draws the button and icon to the button itself, that accepts suggestions from the page, and maybe make more dynamic (might not be needed if moved to button)
    def make_image_multi(self, button: ButtonLoadout):
        icon_ids = [i for i in (button.config['icon1'], button.config['icon2'], button.config['icon3'], button.config['icon4']) if i is not None]
        icon_paths = []
        icon_stratagems = []
        for k in icon_ids:
            s = self.dsd.armory.all[k]
            icon_paths.append(s.icon)
            icon_stratagems.append(s)
        border_path = BORDERS[button.config['color']]['full' if button.full else 'half']
        enabled = button.config.get('enabled', True)

        # Load layers
        icon_imgs = [Image.open(p).convert("RGBA") for p in icon_paths]
        icon_imgs = [self.resize_for_iconbox(img, button.icon_size) for img in icon_imgs] # TODO: Need to resize/recenter manually
        border_img = Image.open(border_path).convert("RGBA")

        key_img = self.bg.copy()

        # Adjust saturation levels for icons to display better on streamdeck
        for i, img in enumerate(icon_imgs):
            if img is not None:
                if icon_stratagems[i].color == 'red':
                    img = ImageEnhance.Color(img).enhance(4)
                if icon_stratagems[i].color == 'green':
                    img = ImageEnhance.Color(img).enhance(4)
                if icon_stratagems[i].color == 'blue':
                    img = ImageEnhance.Color(img).enhance(3)

                if button.icon_rotate != 0:
                    img = img.rotate(button.icon_rotate, expand=True)
                icon_imgs[i] = img

        selected = False
        if button.page.select_active and button.config.get('selected', {}).get(button.page.select_type, False):
            selected = True
        if button.page.app and button.page.app.select_active and button.config.get('selected', {}).get(button.page.app.select_type, False):
            selected = True
        if button.config.get('highlight', False):
            selected = True

        # Assemble the image
        # Background fills 100%, stretched to key size
        self._paste_img(key_img, self.bg_img, 100, keep_aspect=True)
        # Paste the glow for selected items
        if selected:
            selected_img = self.selected_img.copy()
            if button.highlight_hue:
                pixels = selected_img.load()
                width, height = selected_img.size
                for x in range(width):
                    for y in range(height):
                        r, g, b, a = pixels[x, y]
                        h, s, v = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                        h = (h + button.highlight_hue / 360.0) % 1.0
                        r, g, b = hsv_to_rgb(h, s, v)
                        pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)

            self._paste_img(key_img, selected_img, 100, keep_aspect=True)
        # Paste the colored border
        if border_path:
            self._paste_img(key_img, border_img, button.border_size, keep_aspect=True)

        if button.icon_text is not None: # TODO: Adjust title text for Loadout button specifically, currently unused
            draw = ImageDraw.Draw(key_img)
            icon_text = str(button.icon_text)
            font = self.get_font(button.icon_text_size)
            bbox = draw.textbbox((0, 0), icon_text, font=font, stroke_width=2)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (key_img.width - text_width) / 2 - bbox[0]
            text_y = (key_img.height - text_height) / 2 - bbox[1]
            draw.text(
                (text_x, text_y),
                icon_text,
                fill="white",
                font=font,
                stroke_width=2,
                stroke_fill="black",
            )
        icon_count = len(icon_imgs)
        key_size = key_img.width

        if icon_count == 1:
            self._paste_img(key_img, icon_imgs[0], 100, keep_aspect=True)
        elif icon_count == 2:
            icon_pct = 65
            offset = int(key_size * 0.30)
            self._paste_img(key_img, icon_imgs[0], icon_pct, keep_aspect=True, x=offset, y=offset)
            self._paste_img(
                key_img,
                icon_imgs[1],
                icon_pct,
                keep_aspect=True,
                x=key_size - int(key_size * icon_pct / 100) - offset,
                y=key_size - int(key_size * icon_pct / 100) - offset,
            )
        elif icon_count == 3:
            icon_pct = 60
            top_x = (key_size - int(key_size * icon_pct / 100)) // 2
            top_y = int(key_size * 0.05)
            bottom_y = key_size - int(key_size * icon_pct / 100) - int(key_size * 0.07)
            self._paste_img(key_img, icon_imgs[0], icon_pct, keep_aspect=True, x=top_x, y=top_y)
            self._paste_img(key_img, icon_imgs[1], icon_pct, keep_aspect=True, x=int(key_size * 0.03), y=bottom_y)
            self._paste_img(
                key_img,
                icon_imgs[2],
                icon_pct,
                keep_aspect=True,
                x=key_size - int(key_size * icon_pct / 100) - int(key_size * 0.03),
                y=bottom_y,
            )
        elif icon_count >= 4:
            icon_pct = 50
            icon_size = int(key_size * icon_pct / 100)
            offset = int(icon_size * 0.20)

            positions = (
                (offset, offset),
                (key_size - icon_size - offset, offset),
                (offset, key_size - icon_size - offset),
                (key_size - icon_size - offset, key_size - icon_size - offset),
            )

            for img, (x, y) in zip(icon_imgs[:4], positions):
                self._paste_img(key_img, img, icon_pct, keep_aspect=True, x=x, y=y)
    
        if button.config.get('hint', None) and button.page.app.select_active:
            draw = ImageDraw.Draw(key_img)
            hint_text = str(button.config['hint'])
            font_size = 8
            font = self.get_font(font_size)
            text_length = draw.textlength(font=font, text=hint_text)
            draw.text((key_img.width - text_length - 12, 10), hint_text, fill="white", font=font)

        # Darken entire image if disabled
        if not enabled:
            key_img = key_img.point(lambda x: x * 0.3)

        # Convert to native key format and set image
        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        return native_img

    def make_image(self, button: ButtonBase):
        if isinstance(button, ButtonLoadout):
            return self.make_image_multi(button)
        icon_path = button.icon
        border_path = BORDERS[button.color]['full' if button.full else 'half']
        enabled = button.config.get('enabled', True)

        icon_img = None
        if icon_path is not None:
            if not Path(icon_path).exists():
                icon_path = ASSETS_DIR / 'icons/groups/Unknown.png'

            # Load layers
            icon_img = Image.open(icon_path).convert("RGBA")
            icon_img = self.resize_for_iconbox(icon_img, button.icon_size)

        if border_path:
            border_img = Image.open(border_path).convert("RGBA")

        key_img = self.bg.copy()

        # Mask the icon to remove the gild corners from the default icon set (we add them back later if we want them)
        if border_path and icon_img is not None:
            icon_alpha = icon_img.getchannel("A")
            mask = self.icon_mask_img
            if mask.size != icon_img.size:
                mask = mask.resize(icon_img.size, Image.LANCZOS)
            combined_alpha = ImageChops.multiply(icon_alpha, mask)
            icon_img.putalpha(combined_alpha)

        # Adjust saturation levels for icons to display better on streamdeck
        if icon_img is not None:
            if button.color == 'red':
                icon_img = ImageEnhance.Color(icon_img).enhance(4)
            if button.color == 'green':
                icon_img = ImageEnhance.Color(icon_img).enhance(4)
            if button.color == 'blue':
                icon_img = ImageEnhance.Color(icon_img).enhance(3)

            if button.icon_rotate != 0:
                icon_img = icon_img.rotate(button.icon_rotate, expand=True)

        selected = False
        if button.page.select_active and button.config.get('selected', {}).get(button.page.select_type, False):
            selected = True
        if button.page.app and button.page.app.select_active and button.config.get('selected', {}).get(button.page.app.select_type, False):
            selected = True
        if button.config.get('highlight', False):
            selected = True

        # Assemble the image
        # Background fills 100%, stretched to key size
        self._paste_img(key_img, self.bg_img, 100, keep_aspect=True)
        # Paste the glow for selected items
        if selected:
            selected_img = self.selected_img.copy()
            if button.highlight_hue:
                pixels = selected_img.load()
                width, height = selected_img.size
                for x in range(width):
                    for y in range(height):
                        r, g, b, a = pixels[x, y]
                        h, s, v = rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
                        h = (h + button.highlight_hue / 360.0) % 1.0
                        r, g, b = hsv_to_rgb(h, s, v)
                        pixels[x, y] = (int(r * 255), int(g * 255), int(b * 255), a)

            self._paste_img(key_img, selected_img, 100, keep_aspect=True)
        # Paste the colored border
        if border_path:
            self._paste_img(key_img, border_img, button.border_size, keep_aspect=True)

        if button.icon_text is not None:
            draw = ImageDraw.Draw(key_img)
            icon_text = str(button.icon_text)
            font = self.get_font(button.icon_text_size)
            bbox = draw.textbbox((0, 0), icon_text, font=font, stroke_width=2)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (key_img.width - text_width) / 2 - bbox[0]
            text_y = (key_img.height - text_height) / 2 - bbox[1]
            draw.text(
                (text_x, text_y),
                icon_text,
                fill="white",
                font=font,
                stroke_width=2,
                stroke_fill="black",
            )
        elif icon_img is not None:
            # Paste the icon
            self._paste_img(key_img, icon_img, 100, keep_aspect=True)

        if button.config.get('hint', None) and button.page.app.select_active:
            draw = ImageDraw.Draw(key_img)
            hint_text = str(button.config['hint'])
            font_size = 8
            font = self.get_font(font_size)
            text_length = draw.textlength(font=font, text=hint_text)
            draw.text((key_img.width - text_length - 12, 10), hint_text, fill="white", font=font)

        # Darken entire image if disabled
        if not enabled:
            key_img = key_img.point(lambda x: x * 0.3)

        # Convert to native key format and set image
        native_img = PILHelper.to_native_key_format(self.dsd.deck, key_img)
        return native_img

    def draw_icons(self, entries):
        key_count = self.dsd.deck.key_count()
        # Draw icons sequentially across keys (assume enough space per user)
        for k, icon in enumerate(entries):
            if k >= key_count:
                break  # don't exceed available keys
            try:
                native_img = self.make_image(icon)
                self.dsd.set_image(k, native_img)
            except Exception as e:
                traceback.print_exc()
                # If something goes wrong with an icon, skip it and continue
                print(f"Warn: failed to draw icon for key {k} ({icon['name']}): {e}")

    def draw_icon(self, button):
            try:
                return self.make_image(button)
            except Exception as e:
                traceback.print_exc()
