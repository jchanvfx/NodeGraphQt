import re

from NodeGraphQt.constants import ICON_DOWN_ARROW

# Reformat the icon path on Windows OS.
match = re.match('(\\w:)', ICON_DOWN_ARROW)
if match:
    ICON_DOWN_ARROW = ICON_DOWN_ARROW[len(match.group(1)):]
    ICON_DOWN_ARROW = ICON_DOWN_ARROW.replace('\\', '/')

STYLE_QGROUPBOX = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    border: 0px solid rgba(0, 0, 0, 0);
    margin-top: 1px;
    padding-top: $PADDING_TOP;
    padding-bottom: 2px;
    padding-left: 1px;
    padding-right: 1px;
    font-size: 10pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: rgba(255, 255, 255, 85);
}
'''

STYLE_QLINEEDIT = '''
QLineEdit {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    color: rgba(255, 255, 255, 150);
    background: rgba(0, 0, 0, 80);
    selection-background-color: rgba(255, 198, 10, 155);
}
'''

STYLE_QTEXTEDIT = '''
QTextEdit {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    color: rgba(255, 255, 255, 150);
    background: rgba(0, 0, 0, 80);
    selection-background-color: rgba(255, 198, 10, 155);
}
'''

STYLE_TABSEARCH = '''
QLineEdit {
    border: 2px solid rgba(170, 140, 0, 255);
    border-radius: 0px;
    padding: 2px;
    margin: 4px;
    color: rgba(255, 255, 255, 150);
    background: rgba(20, 20, 20, 255);
    selection-background-color: rgba(219, 158, 0, 255);
}
'''


STYLE_TABSEARCH_LIST = '''
QListView {
    background-color: rgba(40, 40, 40, 255);
    border: 1px solid rgba(20, 20, 20, 255);
    color: rgba(255, 255, 255, 150);
    padding-top: 4px;
}
'''

STYLE_QCOMBOBOX = '''
QComboBox {
    border: 1px solid rgba(255, 255, 255, 50);
    border-radius: 0px;
    margin-left: 2px;
    margin-right: 2px;
    margin-top: 1px;
    margin-bottom: 1px;
    padding-left: 4px;
    padding-right: 4px;
}
QComboBox:hover {
    border: 1px solid rgba(255, 255, 255, 80);
}
QComboBox:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(10, 10, 10, 80);
}
QComboBox:!editable,
QComboBox::drop-down:editable {
    color: rgba(255, 255, 255, 150);
    background: rgba(80, 80, 80, 80);
}
/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on,
QComboBox::drop-down:editable:on {
    background: rgba(150, 150, 150, 150);
}
QComboBox::drop-down {
    background: rgba(80, 80, 80, 80);
    border-left: 1px solid rgba(80, 80, 80, 255);
    width: 20px;
}
QComboBox::down-arrow {
    image: url($ICON_DOWN_ARROW);
}
QComboBox::down-arrow:on {
    /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}'''.replace('$ICON_DOWN_ARROW', ICON_DOWN_ARROW)

STYLE_QLISTVIEW = '''
QListView {
    background: rgba(80, 80, 80, 255);
    border: 0px solid rgba(0, 0, 0, 0);
}
QListView::item {
    color: rgba(255, 255, 255, 120);
    background: rgba(60, 60, 60, 255);
    border-bottom: 1px solid rgba(0, 0, 0, 0);
    border-radius: 0px;
    margin: 0px;
    padding: 2px;
}
QListView::item:selected {
    color: rgba(98, 68, 10, 255);
    background: rgba(219, 158, 0, 255);
    border-bottom: 1px solid rgba(255, 255, 255, 5);
    border-radius: 0px;
    margin:0px;
    padding: 2px;
}
'''

STYLE_QMENU = '''
QMenu {
    color: rgba(255, 255, 255, 200);
    background-color: rgba(47, 47, 47, 255);
    border: 1px solid rgba(0, 0, 0, 30);
}

QMenu::item {
    padding: 5px 18px 2px;
    background-color: transparent;
}
QMenu::item:selected {
    color: rgba(98, 68, 10, 255);
    background-color: rgba(219, 158, 0, 255);
}
QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 50);
    margin: 4px 8px;
}
'''

STYLE_QCHECKBOX = '''
QCheckBox {
    color: rgba(255, 255, 255, 150);
    spacing: 8px 2px;
    padding-top: 2px;
    padding-bottom: 2px;
}
QCheckBox::indicator {
    width: 13px;
    height: 13px;
}
'''
