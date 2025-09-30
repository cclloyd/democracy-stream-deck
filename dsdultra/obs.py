from os import getenv
from typing import TYPE_CHECKING
import obsws_python as obs

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra

class OBS:
    dsd: 'DSDUltra' = None

    # TODO: Add tray menu option to edit config settings

    def __init__(self, dsd: 'DSDUltra'):
        self.dsd = dsd
        self.OBS_HOST = getenv('OBS_HOST', 'localhost')
        self.OBS_PORT = getenv('OBS_PORT', 4455)
        self.OBS_PASSWORD = getenv('OBS_PASSWORD', None)

    def open(self):
        pass

    def close(self):
        pass

    def record(self):
        if self.OBS_PASSWORD is None:
            return
        cl = obs.ReqClient(host=self.OBS_HOST, port=self.OBS_PORT, password=self.OBS_PASSWORD, timeout=5)
        try:
            # Optional: ensure replay buffer is running
            try:
                status = cl.get_replay_buffer_status()
                if not getattr(status, "output_active", False):
                    cl.start_replay_buffer()
            except Exception as e:
                print(f"Could not query/start replay buffer: {e}")
            # ... existing code ...
            # Save the replay buffer
            cl.save_replay_buffer()
            print("Replay saved.")
        finally:
            try:
                cl.disconnect()
            except Exception:
                pass

