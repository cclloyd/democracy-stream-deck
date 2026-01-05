import shutil
from pathlib import Path
import sys
import shutil as _shutil


class LinuxInstallerWizard:
    def silent_install(self):
        pass

    def prompt_library_install(self):
        pass

    def create_shortcut(self):
        asset_path = Path('dsdultra/assets/icons/DSDIcon.png')
        icon_path = Path('~/.local/share/icons/hicolor/256x256/apps/dsdultra.png').expanduser()
        desktop_path = Path('~/.local/share/applications/dsdultra.desktop').expanduser()


        contents = f'[Desktop Entry]\n' \
                   f'Type=Application\n' \
                   f'Name=Democracy StreamDeck\n' \
                   f'Exec={self._get_executable_call()}\n' \
                   f'Terminal=false\n' \
                   f'Categories=Utility;Game;\n' \
                   f'StartupNotify=true\n' \
                   f'Icon=dsdultra\n' \
                   f'Keywords=streamdeck;deck;elgato;dsdultra;dsd;helldivers\n'

        with desktop_path.open('w') as f:
            f.write(contents)
            f.close()

        shutil.copy(asset_path, icon_path)

    def _get_executable_call(self):
        main_mod = sys.modules.get("__main__")
        spec = getattr(main_mod, "__spec__", None)
        spec_name = getattr(spec, "name", "") or ""

        if spec_name == "dsdultra.__main__" or spec_name.startswith("dsdultra."):
            return f'python -m dsdultra'
        return str(Path(sys.argv[0]).expanduser().resolve())