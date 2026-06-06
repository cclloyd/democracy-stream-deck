from datetime import datetime
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
VERSION = f'dev-{datetime.now().strftime("%Y%m%d%H%M%S")}'
