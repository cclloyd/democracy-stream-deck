def capture_warnings_into_logging() -> None:
    logging.captureWarnings(True)
    warnings.simplefilter("default")

import logging
import sys
import warnings
from pathlib import Path


# Keep state so we can close/revert cleanly.
_ORIG_STDOUT = sys.__stdout__
_ORIG_STDERR = sys.__stderr__
_TEE_FILE = None


def configure_logging_to_file(log_path: str | Path):
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8")],
        force=True,  # override any prior logging config
    )


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data: str) -> int:
        for s in self.streams:
            s.write(data)
            s.flush()
        return len(data)

    def flush(self) -> None:
        for s in self.streams:
            s.flush()


def redirect_output_to_file(log_path: Path) -> Path:
    global _TEE_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # If we were already logging, close prior handles first.
    close_log_file()

    _TEE_FILE = open(log_path, "a", encoding="utf-8", buffering=1)
    sys.stdout = Tee(_ORIG_STDOUT, _TEE_FILE)
    sys.stderr = Tee(_ORIG_STDERR, _TEE_FILE)

    configure_logging_to_file(log_path)
    return log_path


def close_log_file() -> None:
    global _TEE_FILE

    # Restore stdout/stderr first, so prints during shutdown don't touch the file.
    try:
        sys.stdout = _ORIG_STDOUT
    except Exception:
        pass
    try:
        sys.stderr = _ORIG_STDERR
    except Exception:
        pass

    # Close the tee file we opened.
    try:
        if _TEE_FILE is not None:
            _TEE_FILE.close()
    finally:
        _TEE_FILE = None

    # Close all logging handlers that may be holding the file open.
    root = logging.getLogger()
    for h in list(root.handlers):
        try:
            h.flush()
        except Exception:
            pass
        try:
            h.close()
        except Exception:
            pass
        try:
            root.removeHandler(h)
        except Exception:
            pass

    # Final logging cleanup
    try:
        logging.shutdown()
    except Exception:
        pass