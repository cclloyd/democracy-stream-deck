import sys
import traceback
import importlib


def resolve_class(dotted_path: str):
    """Resolve a dotted class path, e.g., 'my.module.MyClass'."""
    module_name, _, class_name = dotted_path.rpartition('.')
    if not module_name:
        raise ImportError(f"Cannot resolve class: '{dotted_path}' (needs a module path)")
    module = importlib.import_module(module_name)
    return getattr(module, class_name)


class ButtonBase:
    icon = 'dsdultra/assets/icons/groups/Unknown.png'
    icon_size = 50
    icon_rotate = 0
    border_size = 90
    color = 'yellow'
    full = False

    page = None
    config = None
    content = None
    content_class = None


    def __init__(self, dsd, page=None, config: dict = None):
        from dsdultra.dsd import DSDUltra
        self.dsd: DSDUltra = dsd
        self.page = page
        if not config:
            config = dict()
        self.config = config
        if config.get('icon', None) is not None:
            self.icon = config['icon']
        if config.get('content', None) is not None:
            self.content = config['content']
        if config.get('icon_size', None) is not None:
            self.icon_size = config['icon_size']
        if config.get('icon_rotate', None) is not None:
            self.icon_rotate = config['icon_rotate']
        if config.get('border_size', None) is not None:
            self.border_size = config['border_size']
        if config.get('color', None) is not None:
            self.color = config['color']
        if config.get('full', None) is not None:
            self.full = config['full']

        self.content = config.get('content', self.content)
        tmp_cls = config.get('content_class', None)
        if isinstance(tmp_cls, str):
            resolved = resolve_class(tmp_cls)
            if resolved is None:
                raise ImportError(f"Could not resolve content_class '{tmp_cls}'")
            self.content_class = resolved
        else:
            self.content_class = tmp_cls

    def run(self):
        if not self.config.get('enabled', True):
            return
        try:
            if self.content:
                from dsdultra.pages.base import ScrollPage
                page = ScrollPage(self.dsd, parent=self.page, content=list(self.content.values()) if isinstance(self.content, dict) else self.content, content_class=self.content_class, app=self.config.get('app', None) or self.page.appname)
                page.render()
            else:
                print('Default button action')
                self.dsd.deck.reset()
                self.dsd.deck.close()
                sys.exit(0)
        except:
            traceback.print_exc()
            sys.exit(-1)

    def should_render(self):
        return True

    def draw_image(self):
        pass
