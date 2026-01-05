# Democracy StreamDeck

Democracy StreamDeck is an application meant to run on any Elgato StreamDeck with a 5x3 layout.  It is a companion app for Helldivers 2 to have loadout and quick drop support, allowing you to macro your stratagems to StreamDeck buttons.

## Quickstart

Windows:
- Download the exe from the Releases page and run it.  Make sure the Elgato StreamDeck app is fully closed while running this.
- If you don't have `hidapi.dll` in some folder that's included in your `$PATH` variable, it will prompt you to install.

Linux: (Note: Linux binary only for x64 systems)
- Instll `hidapi` using your package manager.
- Download `dsd` binary, mark +x and run.

### Running from source

Windows:
- Install `hidapi.dll` as above.
- Install python and python dependencies from `requirements.txt`
- From project dir, run `python -m dsdultra`

Linux:
- Install `hidapi` using your package manager.
- Install python3 and python dependencies from `requirements.txt`.
- From project dir, run `python -m dsdultra`

## Development


1. Install hidapi
- Windows: Copy the dll to a folder in your `$PATH` (system32 works)
- Arch: `sudo pacman -S tk hidapi`
2. Install requirements.txt
3. Run `python -m dsdultra`

### Building

Just run `python -m dsdultra build`.  The resulting exe is located in `build/dsd.exe`.

## Resources

- [abcminiuser/python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck?tab=readme-ov-file) for StreamDeck interface
- [nvigneux/Helldivers-2-Stratagems-icons-svg](https://github.com/nvigneux/Helldivers-2-Stratagems-icons-svg) for vanilla Helldivers Icons
