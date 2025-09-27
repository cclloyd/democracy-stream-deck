# Democracy StreamDeck

Democracy StreamDeck is an application meant to run on any Elgato StreamDeck with a 5x3 layout.  It is a companion app for Helldivers 2 to have loadout and quick drop support, allowing you to macro your stratagems to StreamDeck buttons.

## Quickstart

Download the exe from the Releases page and run it.  Make sure the Elgato StreamDeck app is fully closed while running this.

If you don't have `hidapi.dll` in some folder that's included in your `$PATH` variable, it will prompt you to install.


## Development

1. Install hidapi.dll
2. Install requirements.txt
3. Run `python -m dsdultra`

### Building

Just run `python -m dsdultra build`.  The resulting exe is located in `build/dsd.exe`.

## Resources

- [abcminiuser/python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck?tab=readme-ov-file) for StreamDeck interface
- [nvigneux/Helldivers-2-Stratagems-icons-svg](https://github.com/nvigneux/Helldivers-2-Stratagems-icons-svg) for vanilla Helldivers Icons