#!/usr/bin/env python3
import sys
from nuitka.__main__ import main as nuitka_main

if __name__ == '__main__':
    sys.argv = [
        'nuitka',  # dummy program name
        '--onefile',
        '--include-data-dir=dsdultra/assets=assets',
        '--standalone',
        '--assume-yes-for-downloads',
        '--output-filename=dsd.exe',
        '--windows-console-mode=disable', # or attach
        '--windows-icon-from-ico=dsdultra/assets/icons/DSDIcon.ico',
        'dsdultra/__main__.py',
    ]
    nuitka_main()
