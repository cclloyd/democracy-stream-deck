import traceback
from pathlib import Path

from PyQt6.QtGui import QIntValidator, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QDialogButtonBox,
    QComboBox,
    QKeySequenceEdit,
    QLabel,
)

from dsdultra.config import DEFAULT_VALUES


class ConfigWindow(QDialog):
    def __init__(self, dsd, parent=None):
        super().__init__(parent)
        self.dsd = dsd
        self.config = dsd.config

        self.setWindowTitle('Democracy StreamDeck Config')
        self.setMinimumWidth(720)

        layout = QFormLayout(self)

        self.config_dir_input = QLineEdit(str(self.config.config_dir))
        self.config_dir_button = QPushButton('Browse...')
        self.config_dir_button.clicked.connect(self.browse_config_dir)

        self.elgato_path_input = QLineEdit(str(self.config.elgato_path))
        self.elgato_path_button = QPushButton('Browse...')
        self.elgato_path_button.clicked.connect(self.browse_elgato_path)

        obs_host_text = '' if self.config.obs_host == DEFAULT_VALUES['obs_host'] else str(self.config.obs_host or '')
        self.obs_host_input = QLineEdit(obs_host_text)
        self.obs_host_input.setPlaceholderText(str(DEFAULT_VALUES['obs_host']))

        obs_port_text = '' if self.config.obs_port == DEFAULT_VALUES['obs_port'] else str(self.config.obs_port or '')
        self.obs_port_input = QLineEdit(obs_port_text)
        self.obs_port_input.setPlaceholderText(str(DEFAULT_VALUES['obs_port']))
        self.obs_port_input.setValidator(QIntValidator(1, 65535, self))

        self.obs_password_input = QLineEdit(str(self.config.obs_password or ''))
        self.obs_password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.recording_app_input = QComboBox()
        self.recording_app_input.addItem('OBS Studio', 'obs')
        self.recording_app_input.addItem('Keyboard Shortcut', 'keycombo')
        recording_app_index = self.recording_app_input.findData(self.config.recording_app)
        if recording_app_index == -1:
            recording_app_index = self.recording_app_input.findData('obs')
        self.recording_app_input.setCurrentIndex(recording_app_index)

        self.record_key_combo_input = QKeySequenceEdit()
        self.record_key_combo_input.setKeySequence(QKeySequence(self.config.record_key_combo or 'Alt+Z'))

        self.recording_app_input.currentIndexChanged.connect(self.update_recording_app_fields_visibility)

        elgato_layout = QHBoxLayout()
        elgato_layout.addWidget(self.elgato_path_input)
        elgato_layout.addWidget(self.elgato_path_button)


        config_dir_layout = QHBoxLayout()
        config_dir_layout.addWidget(self.config_dir_input)
        config_dir_layout.addWidget(self.config_dir_button)

        self.obs_host_label = QLabel('OBS host:')
        self.obs_port_label = QLabel('OBS port:')
        self.obs_password_label = QLabel('OBS password:')
        self.record_key_combo_label = QLabel('Record key combo:')

        layout.addRow('Config directory:', config_dir_layout)
        layout.addRow('Elgato StreamDeck path:', elgato_layout)
        layout.addRow('Game clips app:', self.recording_app_input)
        layout.addRow(self.obs_host_label, self.obs_host_input)
        layout.addRow(self.obs_port_label, self.obs_port_input)
        layout.addRow(self.obs_password_label, self.obs_password_input)
        layout.addRow(self.record_key_combo_label, self.record_key_combo_input)

        self.update_recording_app_fields_visibility()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def update_recording_app_fields_visibility(self):
        show_obs_fields = self.recording_app_input.currentData() == 'obs'
        self.obs_host_label.setVisible(show_obs_fields)
        self.obs_host_input.setVisible(show_obs_fields)
        self.obs_port_label.setVisible(show_obs_fields)
        self.obs_port_input.setVisible(show_obs_fields)
        self.obs_password_label.setVisible(show_obs_fields)
        self.obs_password_input.setVisible(show_obs_fields)

        show_key_combo = self.recording_app_input.currentData() == 'keycombo'
        self.record_key_combo_label.setVisible(show_key_combo)
        self.record_key_combo_input.setVisible(show_key_combo)

    def browse_elgato_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select StreamDeck executable',
            self.elgato_path_input.text(),
            'Executable files (*.exe);;All files (*)',
        )

        if file_path:
            self.elgato_path_input.setText(file_path)

    def browse_config_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            'Select config directory',
            self.config_dir_input.text(),
        )

        if directory:
            self.config_dir_input.setText(directory)

    def save(self):
        try:
            self.config.obs_host = self.obs_host_input.text().strip() or 'localhost'
            self.config.obs_port = int(self.obs_port_input.text().strip() or 4455)
            self.config.obs_password = self.obs_password_input.text()
            self.config.elgato_path = Path(self.elgato_path_input.text().strip())
            self.config.config_dir = Path(self.config_dir_input.text().strip())
            self.config.loadout_path = self.config.config_dir / 'loadouts.json'
            self.config.recording_app = self.recording_app_input.currentData()
            self.config.record_key_combo = self.record_key_combo_input.keySequence().toString()

            self.config.save()

            if hasattr(self.dsd, 'obs') and self.dsd.obs is not None:
                self.dsd.obs.OBS_HOST = self.config.obs_host
                self.dsd.obs.OBS_PORT = self.config.obs_port
                self.dsd.obs.OBS_PASSWORD = self.config.obs_password
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e

        self.accept()