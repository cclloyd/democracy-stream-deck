from dsdultra.args import parse_args
from dsdultra.util import is_frozen, is_windows


def show_console(dsd=None, *args, **kwargs):
    if not is_frozen():
        return
    if not is_windows():
        return
    args = parse_args()
