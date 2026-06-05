import sys

from nuitka.__main__ import main as nuitka_main


def build_executable():
    sys.argv = [
        'dsd',
        '--onefile',
        '--standalone',
        '--output-dir=build',
        '--output-filename=dsd.exe',
        '--nofollow-import-to=dsdultra.build',
        '--no-deployment-flag=self-execution',
        '--assume-yes-for-downloads',
        '--include-distribution-metadata=pillow',
        '--include-data-dir=dsdultra/assets=dsdultra/assets',
        '--include-data-file=dsdultra/assets/lib/hidapi.dll=hidapi.dll',
        '--enable-plugin=pyqt6',
        '--include-package=PIL',
        '--include-package=StreamDeck',
        '--windows-icon-from-ico=dsdultra/assets/icons/DSDIcon.ico',
        '--windows-console-mode=hide',  # force/hide/disable/attach
        'dsdultra/',
    ]
    nuitka_main()
