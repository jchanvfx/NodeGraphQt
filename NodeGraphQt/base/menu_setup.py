#!/usr/bin/python
from distutils.version import LooseVersion

from PySide2 import QtGui, QtCore


def setup_context_menu(graph):
    """
    build the default node graph context menu.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph controller.
    """
    root_menu = graph.context_menu()

    file_menu = root_menu.add_menu('&File')
    edit_menu = root_menu.add_menu('&Edit')

    # File menu.
    file_menu.add_command('Open...',
                          lambda: open_session(graph),
                          QtGui.QKeySequence.Open)
    file_menu.add_command('Save...',
                          lambda: save_session(graph),
                          QtGui.QKeySequence.Save)
    file_menu.add_command('Save As...',
                          lambda: save_session_as(graph),
                          'Ctrl+Shift+s')
    file_menu.add_command('Clear', lambda: clear_session(graph))

    file_menu.add_separator()

    file_menu.add_command('Zoom In', lambda: zoom_in(graph), '=')
    file_menu.add_command('Zoom Out', lambda: zoom_out(graph), '-')
    file_menu.add_command('Reset Zoom', graph.reset_zoom, 'h')

    # Edit menu.
    undo_actn = graph.undo_stack().createUndoAction(graph.viewer(), '&Undo')
    if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
        undo_actn.setShortcutVisibleInContextMenu(True)
    undo_actn.setShortcuts(QtGui.QKeySequence.Undo)
    edit_menu.qmenu.addAction(undo_actn)

    redo_actn = graph.undo_stack().createRedoAction(graph.viewer(), '&Redo')
    if LooseVersion(QtCore.qVersion()) >= LooseVersion('5.10'):
        redo_actn.setShortcutVisibleInContextMenu(True)
    redo_actn.setShortcuts(QtGui.QKeySequence.Redo)
    edit_menu.qmenu.addAction(redo_actn)

    edit_menu.add_separator()
    edit_menu.add_command('Clear Undo History', lambda: clear_undo(graph))
    edit_menu.add_separator()

    edit_menu.add_command('Copy', graph.copy_nodes, QtGui.QKeySequence.Copy)
    edit_menu.add_command('Paste', graph.paste_nodes, QtGui.QKeySequence.Paste)
    edit_menu.add_command('Delete',
                          lambda: graph.delete_nodes(graph.selected_nodes()),
                          QtGui.QKeySequence.Delete)

    edit_menu.add_separator()

    edit_menu.add_command('Select all', graph.select_all, 'Ctrl+A')
    edit_menu.add_command('Deselect all', graph.clear_selection, 'Ctrl+Shift+A')
    edit_menu.add_command('Enable/Disable',
                          lambda: graph.disable_nodes(graph.selected_nodes()),
                          'd')

    edit_menu.add_command('Duplicate',
                          lambda: graph.duplicate_nodes(graph.selected_nodes()),
                          'Alt+c')
    edit_menu.add_command('Center Selection',
                          graph.fit_to_selection,
                          'f')

    edit_menu.add_separator()


# --- menu command functions. ---


def zoom_in(graph):
    zoom = graph.get_zoom() + 0.1
    graph.set_zoom(zoom)


def zoom_out(graph):
    zoom = graph.get_zoom() - 0.2
    graph.set_zoom(zoom)


def open_session(graph):
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.load_dialog(current)
    if file_path:
        graph.load_session(file_path)


def save_session(graph):
    current = graph.current_session()
    if current:
        graph.save_session(current)
        msg = 'Session layout saved:\n{}'.format(current)
        viewer = graph.viewer()
        viewer.message_dialog(msg, title='Session Saved')
    else:
        save_session_as(graph)


def save_session_as(graph):
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.save_dialog(current)
    if file_path:
        graph.save_session(file_path)


def clear_session(graph):
    viewer = graph.viewer()
    if viewer.question_dialog('Clear Session', 'Clear Current Session?'):
        graph.clear_session()


def clear_undo(graph):
    viewer = graph.viewer()
    msg = 'Clear all undo history, Are you sure?'
    if viewer.question_dialog('Clear Undo History', msg):
        graph.undo_stack().clear()
