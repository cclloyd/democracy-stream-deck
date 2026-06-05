import sys

from nuitka.__main__ import main as nuitka_main


def build_executable():
    sys.argv = [
        'nuitka',  # dummy program name
        '--standalone',
        '--assume-yes-for-downloads',
        '--output-filename=dsd',
        '--nofollow-import-to=dsdultra.build',
        '--no-deployment-flag=self-execution',
        '--include-data-dir=dsdultra/assets=dsdultra/assets',
        '--include-distribution-metadata=pillow',
        '--enable-plugin=pyqt6',
        '--include-package=StreamDeck',
        '--include-package=Xlib',
        '--output-dir=build',
        'dsdultra/',
    ]
    nuitka_main()
