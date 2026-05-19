import re
import traceback

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class LoadoutSaveWindow(QDialog):
    def __init__(self, dsd, data, parent=None):
        super().__init__(parent)
        self.dsd = dsd
        self.data = data

        self.setWindowTitle('Save Loadout')
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit(data.get('name') or '')
        self.name_input.setPlaceholderText('New Loadout')

        self.id_input = QLineEdit(data.get('id') or '')
        self.id_input.setPlaceholderText('new_loadout')

        self.hint_input = QLineEdit(data.get('hint') or '')
        self.hint_input.setPlaceholderText('Optional description')

        self.icon1_input = QLineEdit(data.get('icon1') or '')
        self.icon2_input = QLineEdit(data.get('icon2') or '')
        self.icon3_input = QLineEdit(data.get('icon3') or '')
        self.icon4_input = QLineEdit(data.get('icon4') or '')

        self.name_input.textChanged.connect(self.update_default_id)

        form.addRow('Name:', self.name_input)
        form.addRow('ID:', self.id_input)
        form.addRow('Hint:', self.hint_input)
        form.addRow('Icon 1:', self.icon1_input)
        form.addRow('Icon 2:', self.icon2_input)
        form.addRow('Icon 3:', self.icon3_input)
        form.addRow('Icon 4:', self.icon4_input)

        layout.addLayout(form)

        stratagem_ids = data.get('stratagems') or []
        stratagem_names = []
        for stratagem_id in stratagem_ids:
            stratagem = self.dsd.stratagems.get(stratagem_id)
            stratagem_names.append(stratagem.name if stratagem else stratagem_id)

        summary = QLabel('Stratagems: ' + (', '.join(stratagem_names) if stratagem_names else 'None selected'))
        summary.setWordWrap(True)
        layout.addWidget(summary)

        icon_buttons = QHBoxLayout()
        icon1_button = QPushButton('Use first stratagem icon')
        icon2_button = QPushButton('Use second stratagem icon')
        icon3_button = QPushButton('Use third stratagem icon')
        icon4_button = QPushButton('Use fourth stratagem icon')

        icon1_button.clicked.connect(lambda: self.use_stratagem_icon(self.icon1_input, 0))
        icon2_button.clicked.connect(lambda: self.use_stratagem_icon(self.icon2_input, 1))
        icon3_button.clicked.connect(lambda: self.use_stratagem_icon(self.icon3_input, 2))
        icon4_button.clicked.connect(lambda: self.use_stratagem_icon(self.icon4_input, 3))

        icon_buttons.addWidget(icon1_button)
        icon_buttons.addWidget(icon2_button)
        icon_buttons.addWidget(icon3_button)
        icon_buttons.addWidget(icon4_button)
        layout.addLayout(icon_buttons)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def update_default_id(self):
        if self.id_input.text().strip():
            return

        name = self.name_input.text().strip().lower()
        loadout_id = re.sub(r'[^a-z0-9]+', '_', name).strip('_')
        self.id_input.setText(loadout_id)

    def use_stratagem_icon(self, input_widget, index):
        stratagem_ids = self.data.get('stratagems') or []
        if index >= len(stratagem_ids):
            return

        stratagem = self.dsd.stratagems.get(stratagem_ids[index])
        if stratagem:
            input_widget.setText(str(stratagem.id))

    def save(self):
        try:
            name = self.name_input.text().strip() or 'New Loadout'
            loadout_id = self.id_input.text().strip() or re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_') or 'new_loadout'
            config = {
                'id': loadout_id,
                'name': name,
                'hint': self.hint_input.text().strip() or None,
                'icon1': self.icon1_input.text().strip() or None,
                'icon2': self.icon2_input.text().strip() or None,
                'icon3': self.icon3_input.text().strip() or None,
                'icon4': self.icon4_input.text().strip() or None,
                'stratagems': self.data.get('stratagems') or [],
            }

            saved = self.dsd.loadouts.save_loadout(config)
            if not saved:
                response = QMessageBox.question(
                    self,
                    'Overwrite Loadout?',
                    f'A loadout with ID "{loadout_id}" already exists. Overwrite it?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if response != QMessageBox.StandardButton.Yes:
                    return

                self.dsd.loadouts.save_loadout(config, overwrite=True)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return
        self.accept()