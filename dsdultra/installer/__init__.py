import sys


class InstallerWizard:
    def __init__(self):
        if sys.platform == 'Windows':
            from .win import WindowsInstallerWizard
            self.wizard = WindowsInstallerWizard()
        else:
            from .linux import LinuxInstallerWizard
            self.wizard = LinuxInstallerWizard()

    def silent_install(self):
        self.wizard.silent_install()

    def prompt_library_install(self):
        self.wizard.prompt_library_install()

    def create_shortcut(self):
        self.wizard.create_shortcut()

    def __getattr__(self, name):
        return getattr(self.wizard, name)
