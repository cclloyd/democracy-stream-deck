from os import getenv
from typing import TYPE_CHECKING
import obsws_python as obs

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra

class StateManager:
    dsd: DSDUltra = None


    def __init__(self, dsd: DSDUltra):
        self.dsd = dsd

