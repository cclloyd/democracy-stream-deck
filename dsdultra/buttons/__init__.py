from PIL import ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper

# DEPRECATED - other than the prompt for text
class ButtonEngine:
    def __init__(self, dsd):
        from dsdultra.dsd import DSDUltra
        self.dsd: DSDUltra = dsd

    def render_text_key(self, text):
        """Create a native key image with centered text."""
        # Create a new image that matches the key's native resolution/orientation
        image = PILHelper.create_image(self.dsd.deck)
        draw = ImageDraw.Draw(image)
        # Use a default bitmap font if you don't have a TTF handy
        try:
            font = ImageFont.truetype('arial.ttf', 18)
        except Exception:
            font = ImageFont.load_default()

        # Use textbbox instead of deprecated/removed textsize (Pillow >= 10)
        bbox = draw.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((image.width - w) / 2, (image.height - h) / 2),
                  text, font=font, fill='white')

        # Convert to native Stream Deck pixel format
        return PILHelper.to_native_key_format(self.dsd.deck, image)


    def on_key_change(self, deck, key, pressed):
        self.update_key(key, pressed)

        # If second-to-last button pressed, prompt for text
        if pressed and key == self.dsd.deck.key_count() - 2:
            text = self.prompt_for_text("Input Required", "Enter text to type:")
            if text:
                # _type_text(text) TODO
                pass
            return

        # Type the key index on key-down (except the Exit key)
        if pressed and key < self.dsd.deck.key_count() - 1:
            # _type_text(str(key)) TODO
            pass


        # If last button pressed, reset & close
        if pressed and key == self.dsd.deck.key_count() - 1:
            with self.dsd.deck:
                self.dsd.deck.reset()
                self.dsd.deck.close()


    def update_key(self, key, pressed):
        """(Re)draw a key when its state changes."""
        if key >= self.dsd.deck.key_count():
            return  # touch strip on SD+ is beyond key indexes

        label = 'Exit' if key == self.dsd.deck.key_count() - 1 else (f'#{key}' if not pressed else 'OK')
        img = self.render_text_key(label)
        with self.dsd.deck:  # thread-safe
            self.dsd.deck.set_key_image(key, img)

    # New helper to show an OS-native input dialog
    def prompt_for_text(self, title='Input', prompt='Enter text:'):
        '''
        Shows a native OS popup to ask for a string.
        Returns the entered text, or None if canceled or unavailable.
        '''
        try:
            from PyQt6.QtWidgets import QApplication, QInputDialog
            app = QApplication.instance() or QApplication([])
            result, accepted = QInputDialog.getText(
                None,
                title,
                prompt,
            )
            return result if accepted else None
        except Exception as e:
            print(f'Warn: failed to show input dialog: {e}')
            return None

