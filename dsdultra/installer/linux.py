import os
import shutil
import sys
from pathlib import Path


class LinuxInstallerWizard:
    def silent_install(self):
        current_file = Path(sys.argv[0]).expanduser().resolve()
        user_bin_dir = Path('~/.local/bin').expanduser()
        global_bin_dir = Path('/usr/local/bin')
        bin_dir = global_bin_dir if os.getuid() == 0 else user_bin_dir

        dest = (bin_dir / 'dsd').resolve()
        shutil.copy2(current_file, dest)

        try:
            print(f'Copying binary to {dest}...')
            mode = dest.stat().st_mode
            dest.chmod(mode | 0o111)
            self.create_shortcut()
        except OSError:
            pass
        if os.getuid() == 0:
            print('Installed.')
        else:
            print(f'Installed for current user. To install system-wide, run: `sudo ./dsd install`')


    def prompt_library_install(self):
        pass

    def create_shortcut(self):
        asset_path = Path('dsdultra/assets/icons/DSDIcon.png')
        if os.getuid() == 0:
            icon_path = Path('/usr/share/icons/hicolor/256x256/apps/dsd.png')
            desktop_path = Path('/usr/share/applications/dsd.desktop')
        else:
            icon_path = Path('~/.local/share/icons/hicolor/256x256/apps/dsd.png').expanduser()
            desktop_path = Path('~/.local/share/applications/dsd.desktop').expanduser()

        contents = f'[Desktop Entry]\n' \
                   f'Type=Application\n' \
                   f'Name=Democracy StreamDeck\n' \
                   f'Exec={self._get_executable_call()}\n' \
                   f'Terminal=false\n' \
                   f'Categories=Utility;Game;\n' \
                   f'StartupNotify=false\n' \
                   f'Icon=dsd\n' \
                   f'Keywords=streamdeck;deck;elgato;dsdultra;dsd;helldivers\n'

        with desktop_path.open('w') as f:
            f.write(contents)
            print(f'Created application shortcut: {desktop_path}')
            f.close()
        shutil.copy(asset_path, icon_path)
        print(f'Copied icon to: {icon_path}')

    def _get_executable_call(self):
        main_mod = sys.modules.get('__main__')
        spec = getattr(main_mod, '__spec__', None)
        spec_name = getattr(spec, 'name', '') or ''

        if spec_name == 'dsdultra.__main__' or spec_name.startswith('dsdultra.'):
            return f'python -m dsdultra'
        return str(Path(sys.argv[0]).expanduser().resolve())