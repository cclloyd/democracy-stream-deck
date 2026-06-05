from dsdultra.util import is_linux


class InstallerWizard:
    wizard = None

    def __init__(self):
        if is_linux():
            from .linux import LinuxInstallerWizard
            self.wizard = LinuxInstallerWizard()

    def silent_install(self):
        if self.wizard:
            self.wizard.silent_install()

    def prompt_library_install(self):
        if self.wizard is not None:
            self.wizard.prompt_library_install()

    def create_shortcut(self):
        if self.wizard:
            self.wizard.create_shortcut()

    def __getattr__(self, name):
        return getattr(self.wizard, name)
