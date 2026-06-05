import sys

from nuitka.__main__ import main as nuitka_main


def build_executable():
    sys.argv = [
        'dsd',
        '--onefile',
        '--standalone',
        '--include-package=PIL',
        '--include-distribution-metadata=pillow',
        '--include-data-dir=dsdultra/assets=dsdultra/assets',
        '--assume-yes-for-downloads',
        '--output-filename=dsd.exe',
        '--enable-plugin=pyqt6',
        '--include-package=StreamDeck',
        '--no-deployment-flag=self-execution',
        '--windows-console-mode=hide',  # force/hide/disable/attach
        '--windows-icon-from-ico=dsdultra/assets/icons/DSDIcon.ico',
        '--nofollow-import-to=dsdultra.build',
        '--output-dir=build',
        'dsdultra/',
    ]
    nuitka_main()
