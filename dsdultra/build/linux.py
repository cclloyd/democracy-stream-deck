import sys

from nuitka.__main__ import main as nuitka_main


def build_executable():
    sys.argv = [
        'nuitka',  # dummy program name
        '--onefile',
        '--include-data-dir=dsdultra/assets=dsdultra/assets',
        '--standalone',
        '--assume-yes-for-downloads',
        f'--output-filename=dsd',
        '--enable-plugin=tk-inter',
        '--no-deployment-flag=self-execution',
        '--windows-console-mode=disable',  # force/hide/disable/attach
        '--windows-icon-from-ico=dsdultra/assets/icons/DSDIcon.ico',
        '--nofollow-import-to=dsdultra.build',
        '--output-dir=build',
        'dsdultra/__main__.py',
    ]
    nuitka_main()
