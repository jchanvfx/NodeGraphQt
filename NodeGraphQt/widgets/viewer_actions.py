#!/usr/bin/python
from PySide import QtGui


def setup_viewer_actions(viewer):
    menu_file = viewer.add_menu('File')
    menu_edit = viewer.add_menu('Edit')
    menu_nodes = viewer.add_menu('Nodes')

    # "File" actions.
    open_actn = QtGui.QAction('Open File...', viewer)
    open_actn.setShortcut('Ctrl+o')
    open_actn.triggered.connect(viewer.load_dialog)
    menu_file.addAction(open_actn)

    save_actn = QtGui.QAction('Save As...', viewer)
    save_actn.setShortcut('Ctrl+s')
    save_actn.triggered.connect(viewer.save_dialog)
    menu_file.addAction(save_actn)

    menu_file.addSeparator()

    zoom_in = QtGui.QAction('Zoom in', viewer)
    zoom_in.setShortcut('=')
    zoom_in.triggered.connect(viewer.zoom_in)
    menu_file.addAction(zoom_in)

    zoom_out = QtGui.QAction('Zoom out', viewer)
    zoom_out.setShortcut('-')
    zoom_out.triggered.connect(viewer.zoom_out)
    menu_file.addAction(zoom_out)

    zoom_reset = QtGui.QAction('Reset zoom', viewer)
    zoom_reset.triggered.connect(viewer.set_zoom)
    menu_file.addAction(zoom_reset)

    # "Edit" actions.
    undo_actn = viewer._undo_stack.createUndoAction(viewer, '&Undo')
    undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
    menu_edit.addAction(undo_actn)
    redo_actn = viewer._undo_stack.createRedoAction(viewer, '&Redo')
    redo_actn.setShortcuts(QtGui.QKeySequence.Redo)
    menu_edit.addAction(redo_actn)

    menu_edit.addSeparator()

    node_copy = QtGui.QAction('Copy', viewer)
    node_copy.setShortcut(QtGui.QKeySequence.Copy)
    node_copy.triggered.connect(viewer.copy_to_clipboard)
    menu_edit.addAction(node_copy)

    node_paste = QtGui.QAction('Paste', viewer)
    node_paste.setShortcut(QtGui.QKeySequence.Paste)
    node_paste.triggered.connect(viewer.paste_from_clipboard)
    menu_edit.addAction(node_paste)

    node_delete = QtGui.QAction('Delete', viewer)
    node_delete.setShortcuts(['Del', 'Backspace'])
    node_delete.triggered.connect(viewer.delete_selected_nodes)
    menu_edit.addAction(node_delete)

    menu_edit.addSeparator()

    node_sel_all = QtGui.QAction('Select all', viewer)
    node_sel_all.setShortcut('Ctrl+A')
    node_sel_all.triggered.connect(viewer.select_all_nodes)
    menu_edit.addAction(node_sel_all)

    node_desel_all = QtGui.QAction('Deselect all', viewer)
    node_desel_all.setShortcut('Ctrl+Shift+A')
    node_desel_all.triggered.connect(viewer.clear_selection)
    menu_edit.addAction(node_desel_all)

    node_disability = QtGui.QAction('Enable/Disable', viewer)
    node_disability.setShortcut('d')
    node_disability.triggered.connect(viewer.toggle_nodes_disability)
    menu_edit.addAction(node_disability)

    node_duplicate = QtGui.QAction('Duplicate', viewer)
    node_duplicate.setShortcut('Alt+c')
    node_duplicate.triggered.connect(viewer.duplicate_nodes)
    menu_edit.addAction(node_disability)

    fit_zoom = QtGui.QAction('Center Selection', viewer)
    fit_zoom.setShortcut('f')
    fit_zoom.triggered.connect(viewer.set_zoom)
    fit_zoom.triggered.connect(viewer.center_selection)
    menu_edit.addAction(fit_zoom)

    menu_edit.addSeparator()

    for menu in (menu_file, menu_edit):
        viewer.addActions(menu.actions())
