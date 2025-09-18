import traceback
from pathlib import Path

from PIL import Image, ImageFont, ImageEnhance, ImageChops
from StreamDeck.ImageHelpers import PILHelper

from dsdultra.buttons.base import ButtonBase

BORDERS = {
    'yellow': {
        'half': 'dsdultra/assets/icons/borders/Yellow Half.png',
        'full': 'dsdultra/assets/icons/borders/Yellow Full.png',
    },
    'blue': {
        'half': 'dsdultra/assets/icons/borders/Blue Half.png',
        'full': 'dsdultra/assets/icons/borders/Blue Full.png',
    },
    'green': {
        'half': 'dsdultra/assets/icons/borders/Green Half.png',
        'full': 'dsdultra/assets/icons/borders/Green Full.png',
    },
    'red': {
        'half': 'dsdultra/assets/icons/borders/Red Half.png',
        'full': 'dsdultra/assets/icons/borders/Red Full.png',
    },
    'rainbow': {
        'half': 'dsdultra/assets/icons/borders/Rainbow.png',
        'full': 'dsdultra/assets/icons/borders/Rainbow.png',
    }
}


class IconGenerator:
    bg = None
    font_path = 'dsdultra/assets/fonts/Orbitron-v.ttf'

    def __init__(self, dsd):
        self.dsd = dsd
        self.size = dsd.deck.KEY_PIXEL_WIDTH
        if not self.bg:
            bg_path = 'dsdultra/assets/icons/Background.png'
            selected_path = 'dsdultra/assets/icons/borders/Selected2.png'
            icon_mask_path = 'dsdultra/assets/icons/groups/mask72.png'
            gild_path = 'dsdultra/assets/icons/groups/Gild Half.png'
            gild_path_full = 'dsdultra/assets/icons/groups/Gild Full.png'
            # Precompute a blank background at the correct key size
            self.bg = PILHelper.create_image(self.dsd.deck)
            self.bg_img = Image.open(bg_path).convert("RGBA")
            self.selected_img = Image.open(selected_path).convert("RGBA")
            self.icon_mask_img = Image.open(icon_mask_path).convert("L")
            self.gild_img = Image.open(gild_path).convert("RGBA")
            self.gild_img_full = Image.open(gild_path_full).convert("RGBA")

    def get_font(self, size):
        return ImageFont.truetype(self.font_path, size)

    def _paste_center(self, base_img: Image.Image, layer_img: Image.Image, pct: float, keep_aspect: bool = True):
        """Paste `layer_img` centered on `base_img` scaled to `pct`% of base size."""
        target_w = int(base_img.width * (pct / 100.0))
        target_h = int(base_img.height * (pct / 100.0))
        if keep_aspect:
            layer = layer_img.copy()
            layer.thumbnail((target_w, target_h), Image.LANCZOS)
        else:
            layer = layer_img.resize((target_w, target_h), Image.LANCZOS)
        x = (base_img.width - layer.width) // 2
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

    def make_image(self, button: ButtonBase):
        icon_path = button.icon
        border_path = BORDERS[button.color]['full' if button.full else 'half']
        enabled = button.config.get('enabled', True)

        if not Path(icon_path).exists():
            icon_path = 'dsdultra/assets/icons/groups/Unknown.png'

        # Load layers
        icon_img = Image.open(icon_path).convert("RGBA")
        icon_img = self.resize_for_iconbox(icon_img, button.icon_size)
        # bg_img = Image.open(bg_path).convert("RGBA")
        border_img = Image.open(border_path).convert("RGBA")

        key_img = self.bg.copy()

        # Mask the icon to remove the gild corners from the default icon set (we add them back later if we want them)
        icon_alpha = icon_img.getchannel("A")
        mask = self.icon_mask_img
        if mask.size != icon_img.size:
            mask = mask.resize(icon_img.size, Image.LANCZOS)
        combined_alpha = ImageChops.multiply(icon_alpha, mask)
        icon_img.putalpha(combined_alpha)

        # Adjust saturation levels for icons to display better on streamdeck
        if button.color == 'red':
            icon_img = ImageEnhance.Color(icon_img).enhance(4)
        if button.color == 'green':
            icon_img = ImageEnhance.Color(icon_img).enhance(4)
        if button.color == 'blue':
            icon_img = ImageEnhance.Color(icon_img).enhance(3)

        if button.icon_rotate != 0:
            icon_img = icon_img.rotate(button.icon_rotate, expand=True)

        # Assemble the image
        # Background fills 100%, stretched to key size
        self._paste_center(key_img, self.bg_img, 100, keep_aspect=True)
        # Paste the glow for selected items
        if (button.page.select_active or button.page.app.select_active) and button.config.get('selected', False):
            self._paste_center(key_img, self.selected_img, 100, keep_aspect=True)
        # Paste the colored border
        self._paste_center(key_img, border_img, button.border_size, keep_aspect=True)
        # Paste the icon
        self._paste_center(key_img, icon_img, 100, keep_aspect=True)
        
        if button.config.get('hint', None) and button.page.app.select_active:
            from PIL import ImageDraw
            draw = ImageDraw.Draw(key_img)
            hint_text = str(button.config['hint'])
            font_size = 8
            font = self.get_font(font_size)
            text_length = draw.textlength(font=font, text=hint_text)
            draw.text((key_img.width - text_length - 8, 6), hint_text, fill="white", font=font)

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
