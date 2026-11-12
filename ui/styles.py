"""Qt stylesheet (QSS) that gives the whole app its custom look.

The drop-down / spin-box arrows and the checkbox / radio-button indicators are small
PNG files in the assets/ folder. When you style a widget's border with QSS, Qt stops
drawing its built-in arrows, so we supply our own images (@ASSETS@ below).

Colours: indigo for headers and buttons, white cards on a light grey-blue page.
Widgets opt in to special looks through setObjectName(...), for example
button.setObjectName("primary") picks up the QPushButton#primary rule.
"""

_STYLE_TEMPLATE = """
QWidget {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 14px;
    color: #1f2937;
}
QMainWindow, QDialog { background-color: #f3f5fa; }
QLabel { background: transparent; }

/* ----- text styles ----- */
QLabel#title     { font-size: 28px; font-weight: bold; color: #312e81; }
QLabel#subtitle  { color: #6b7280; }
QLabel#heading   { font-size: 18px; font-weight: bold; color: #312e81; }
QLabel#question  { font-size: 20px; font-weight: bold; color: #111827; }
QLabel#bigScore  { font-size: 54px; font-weight: bold; color: #312e81; }
QLabel#statValue { font-size: 26px; font-weight: bold; color: #4f46e5; }
QLabel#statTitle { color: #6b7280; }
QLabel#hint      { color: #6b7280; font-size: 12px; }
QLabel#errorHint { color: #dc2626; font-size: 12px; font-weight: bold; }

/* ----- cards ----- */
QFrame#card {
    background-color: white;
    border: 1px solid #dfe3ee;
    border-radius: 12px;
}
QGroupBox {
    background-color: white;
    border: 1px solid #dfe3ee;
    border-radius: 12px;
    margin-top: 14px;
    padding: 14px;
    font-weight: bold;
}
QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 6px; color: #312e81; }

/* ----- buttons ----- */
QPushButton {
    background-color: #e5e9f5;
    border: none;
    border-radius: 8px;
    padding: 9px 18px;
    min-width: 70px;
    font-weight: 600;
}
QPushButton:hover    { background-color: #d5dbef; }
QPushButton:disabled { background-color: #e5e7eb; color: #9ca3af; }
QPushButton#primary       { background-color: #4f46e5; color: white; }
QPushButton#primary:hover { background-color: #4338ca; }
QPushButton#primary:disabled { background-color: #c7c9f0; color: white; }
QPushButton#danger        { background-color: #dc2626; color: white; }
QPushButton#danger:hover  { background-color: #b91c1c; }

/* ----- inputs ----- */
QLineEdit, QTextEdit {
    background-color: white;
    border: 1px solid #cbd2e1;
    border-radius: 6px;
    padding: 6px;
}
QLineEdit:hover, QTextEdit:hover { border: 1px solid #a5b0d6; }
QLineEdit:focus, QTextEdit:focus { border: 2px solid #4f46e5; }

/* drop-down list (QComboBox) with a visible arrow button */
QComboBox {
    background-color: white;
    border: 1px solid #cbd2e1;
    border-radius: 6px;
    padding: 6px 36px 6px 8px;
    min-height: 22px;
}
QComboBox:hover { border: 1px solid #a5b0d6; }
QComboBox:focus { border: 2px solid #4f46e5; }
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 30px;
    background-color: #eef0fb;
    border-left: 1px solid #cbd2e1;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}
QComboBox::drop-down:hover { background-color: #dfe3f7; }
QComboBox::down-arrow { image: url("@ASSETS@/arrow_down.png"); width: 14px; height: 14px; }
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #cbd2e1;
    selection-background-color: #e0e7ff;
    selection-color: #1f2937;
    outline: 0;
    padding: 4px;
}

/* number box (QSpinBox) with visible up / down buttons */
QSpinBox {
    background-color: white;
    border: 1px solid #cbd2e1;
    border-radius: 6px;
    padding: 6px 34px 6px 8px;
    min-height: 26px;
}
QSpinBox:hover { border: 1px solid #a5b0d6; }
QSpinBox:focus { border: 2px solid #4f46e5; }
QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 28px;
    background-color: #eef0fb;
    border-left: 1px solid #cbd2e1;
    border-bottom: 1px solid #cbd2e1;
    border-top-right-radius: 6px;
}
QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 28px;
    background-color: #eef0fb;
    border-left: 1px solid #cbd2e1;
    border-bottom-right-radius: 6px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #dfe3f7; }
QSpinBox::up-button:pressed, QSpinBox::down-button:pressed { background-color: #c7d2fe; }
QSpinBox::up-arrow   { image: url("@ASSETS@/arrow_up_small.png");   width: 10px; height: 10px; }
QSpinBox::down-arrow { image: url("@ASSETS@/arrow_down_small.png"); width: 10px; height: 10px; }

/* radio buttons: each answer looks like a clickable card */
QRadioButton {
    padding: 10px 12px;
    font-size: 15px;
    spacing: 12px;
    border: 1px solid transparent;
    border-radius: 8px;
}
QRadioButton:hover   { background-color: #eef0fb; }
QRadioButton:checked { background-color: #e0e7ff; border: 1px solid #4f46e5; font-weight: bold; }
QRadioButton::indicator { width: 20px; height: 20px; }
QRadioButton::indicator:unchecked { image: url("@ASSETS@/radio_off.png"); }
QRadioButton::indicator:checked   { image: url("@ASSETS@/radio_on.png"); }

QCheckBox { spacing: 10px; }
QCheckBox::indicator { width: 20px; height: 20px; }
QCheckBox::indicator:unchecked { image: url("@ASSETS@/check_off.png"); }
QCheckBox::indicator:checked   { image: url("@ASSETS@/check_on.png"); }

QToolTip {
    background-color: #312e81;
    color: white;
    border: none;
    padding: 5px 8px;
}
QSlider::groove:horizontal { height: 6px; background: #d5dbef; border-radius: 3px; }
QSlider::handle:horizontal {
    background: #4f46e5; width: 18px; margin: -6px 0; border-radius: 9px;
}
QSlider::sub-page:horizontal { background: #4f46e5; border-radius: 3px; }

/* ----- progress bars ----- */
QProgressBar { background-color: #e5e7eb; border: none; border-radius: 5px; }
QProgressBar::chunk { background-color: #4f46e5; border-radius: 5px; }

/* ----- tables ----- */
QTableWidget {
    background-color: white;
    alternate-background-color: #f7f8fc;
    border: 1px solid #dfe3ee;
    gridline-color: transparent;
}
QTableWidget::item { padding: 5px; }
QTableWidget::item:selected { background-color: #c7d2fe; color: #1f2937; }
QHeaderView::section {
    background-color: #312e81;
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
}

/* ----- menu bar and status bar ----- */
QMenuBar { background-color: #312e81; }
QMenuBar::item { color: white; padding: 7px 14px; background: transparent; }
QMenuBar::item:selected { background-color: #4338ca; }
QMenu { background-color: white; border: 1px solid #cbd2e1; }
QMenu::item { padding: 7px 30px; }
QMenu::item:selected { background-color: #e0e7ff; color: #1f2937; }
QMenu::item:disabled { color: #9ca3af; }
QStatusBar { background-color: #e5e9f5; }
"""

# Fill in the real location of the images. as_posix() gives forward slashes, which Qt
# understands on every operating system (and the path is built from this file, so it is
# not hard-coded).
import config

APP_STYLE = _STYLE_TEMPLATE.replace("@ASSETS@", config.ASSETS_DIR.as_posix())
