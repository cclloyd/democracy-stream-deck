from .base import BasePage
from ..buttons.armory import ButtonArmory
from ..buttons.elgato import ButtonElgato
from ..buttons.exit import ButtonExit
from ..buttons.loadouts import ButtonLoadouts
from ..buttons.quick import ButtonQuickLoadout


class PageHome(BasePage):
    ICON_TYPE_MAP = [
        None,
        None,
        None,
        ButtonElgato,
        ButtonExit,
        # Row 2
        None,
        ButtonLoadouts,
        ButtonArmory,
        ButtonQuickLoadout,
        None,
        # Row 3
        None,
        None,
        None,
        None,
        None,
    ]