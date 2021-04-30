STYLE_QGROUPBOX = '''
QGroupBox {
    background-color: rgba(0, 0, 0, 0);
    border: 0px solid rgba(0, 0, 0, 0);
    margin-top: 1px;
    padding-top: $PADDING_TOP;
    padding-bottom: 2px;
    padding-left: 1px;
    padding-right: 1px;
    font-size: 8pt;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: rgba(255, 255, 255, 85);
    padding: 0px;
    left:-4px;
}
'''

STYLE_QLINEEDIT = '''
QLineEdit {
    border: 1px solid rgb(90, 90, 90);
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

