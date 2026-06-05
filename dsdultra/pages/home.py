from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BasePage
from ..buttons.armory import ButtonArmory
from ..buttons.elgato import ButtonElgato
from ..buttons.exit import ButtonExitConfirm
from ..buttons.loadouts.loadouts import ButtonLoadouts
from ..buttons.quick import ButtonQuickLoadout

if TYPE_CHECKING:
    from ..dsd import DSDUltra


class PageHome(BasePage):
    ICON_TYPE_MAP = [
        None,
        None,
        None,
        ButtonElgato,
        ButtonExitConfirm,
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

    def __init__(self, dsd: DSDUltra, *args, **kwargs):
        super().__init__(dsd, *args, **kwargs)
        dsd.state.register_app(self, 'dsd')
