#!/usr/bin/python

def build_context_menu(graph):
    """
    populate the node graph's context menu with essential menus commands.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph controller.
    """
    from Qt import QtGui, QtCore
    context_menu = graph.get_context_menu('graph')

    # "File" menu.
    # --------------------------------------------------------------------------
    file_menu = context_menu.add_menu('&File')

    file_menu.add_command('Open...', _open_session, QtGui.QKeySequence.Open)
    file_menu.add_command('Import...', _import_session)
    file_menu.add_command('Save...', _save_session, QtGui.QKeySequence.Save)
    file_menu.add_command('Save As...', _save_session_as, 'Ctrl+Shift+S')
    file_menu.add_command('New Session', _new_session)

    # "Edit" menu.
    # --------------------------------------------------------------------------
    edit_menu = context_menu.add_menu('&Edit')

    edit_menu.add_separator()
    edit_menu.add_command('Clear Undo History', _clear_undo)
    edit_menu.add_command('Show Undo History', _show_undo_view)
    edit_menu.add_separator()

    edit_menu.add_command('Copy', _copy_nodes, QtGui.QKeySequence.Copy)
    edit_menu.add_command('Cut', _cut_nodes, QtGui.QKeySequence.Cut)
    edit_menu.add_command('Paste', _paste_nodes, QtGui.QKeySequence.Paste)
    edit_menu.add_command('Delete', _delete_nodes, QtGui.QKeySequence.Delete)

    edit_menu.add_separator()

    edit_menu.add_command('Select all', _select_all_nodes, 'Ctrl+A')
    edit_menu.add_command('Deselect all', _clear_node_selection, 'Ctrl+Shift+A')
    edit_menu.add_command('Enable/Disable', _disable_nodes, 'D')

    edit_menu.add_command('Duplicate', _duplicate_nodes, 'Alt+C')
    edit_menu.add_command('Center Selection', _fit_to_selection, 'F')

    edit_menu.add_separator()

    edit_menu.add_command('Zoom In', _zoom_in, '=')
    edit_menu.add_command('Zoom Out', _zoom_out, '-')
    edit_menu.add_command('Reset Zoom', _reset_zoom, 'H')

    context_menu.add_separator()

    # "Node" menu.
    # --------------------------------------------------------------------------
    graph_menu = context_menu.add_menu('&Graph')

    bg_menu = graph_menu.add_menu('&Background')
    bg_menu.add_command('None', _bg_grid_none, 'Alt+1')
    bg_menu.add_command('Lines', _bg_grid_lines, 'Alt+2')
    bg_menu.add_command('Dots', _bg_grid_dots, 'Alt+3')

    layout_menu = graph_menu.add_menu('&Layout')
    layout_menu.add_command('Horizontal', _layout_h_mode, 'Shift+1')
    layout_menu.add_command('Vertical', _layout_v_mode, 'Shift+2')

    # "Node" menu.
    # --------------------------------------------------------------------------
    node_menu = context_menu.add_menu('&Nodes')
    node_menu.add_command('Node Search', _toggle_node_search, 'Tab')
    node_menu.add_separator()
    node_menu.add_command(
        'Auto Layout Up Stream', _layout_graph_up, 'L')
    node_menu.add_command(
        'Auto Layout Down Stream', _layout_graph_down, 'Ctrl+L')
    node_menu.add_separator()
    node_menu.add_command(
        'Expand Group Node', _expand_group_node,
        QtGui.QKeySequence(QtCore.Qt.ALT + QtCore.Qt.Key_Return))

    # "Pipe" menu.
    # --------------------------------------------------------------------------
    pipe_menu = context_menu.add_menu('&Pipes')
    pipe_menu.add_command('Curved', _curved_pipe)
    pipe_menu.add_command('Straight', _straight_pipe)
    pipe_menu.add_command('Angle', _angle_pipe)

# ------------------------------------------------------------------------------
# --- menu command functions ---
# ------------------------------------------------------------------------------


def _zoom_in(graph):
    """
    Set the node graph to zoom in by 0.1
    """
    zoom = graph.get_zoom() + 0.1
    graph.set_zoom(zoom)


def _zoom_out(graph):
    """
    Set the node graph to zoom in by 0.1
    """
    zoom = graph.get_zoom() - 0.2
    graph.set_zoom(zoom)


def _reset_zoom(graph):
    """
    Reset zoom level.
    """
    graph.reset_zoom()


def _layout_h_mode(graph):
    """
    Set node graph layout direction to horizontal.
    """
    graph.set_layout_direction(0)


def _layout_v_mode(graph):
    """
    Set node graph layout direction to vertical.
    """
    graph.set_layout_direction(1)


def _open_session(graph):
    """
    Prompts a file open dialog to load a session.
    """
    current = graph.current_session()
    file_path = graph.load_dialog(current)
    if file_path:
        graph.load_session(file_path)


def _import_session(graph):
    """
    Prompts a file open dialog to load a session.
    """
    current = graph.current_session()
    file_path = graph.load_dialog(current)
    if file_path:
        graph.import_session(file_path)


def _save_session(graph):
    """
    Prompts a file save dialog to serialize a session if required.
    """
    current = graph.current_session()
    if current:
        graph.save_session(current)
        msg = 'Session layout saved:\n{}'.format(current)
        viewer = graph.viewer()
        viewer.message_dialog(msg, title='Session Saved')
    else:
        _save_session_as(graph)


def _save_session_as(graph):
    """
    Prompts a file save dialog to serialize a session.
    """
    current = graph.current_session()
    file_path = graph.save_dialog(current)
    if file_path:
        graph.save_session(file_path)


def _new_session(graph):
    """
    Prompts a warning dialog to new a node graph session.
    """
    if graph.question_dialog('Clear Current Session?', 'Clear Session'):
        graph.clear_session()


def _clear_undo(graph):
    """
    Prompts a warning dialog to clear undo.
    """
    viewer = graph.viewer()
    msg = 'Clear all undo history, Are you sure?'
    if viewer.question_dialog('Clear Undo History', msg):
        graph.clear_undo_stack()


def _copy_nodes(graph):
    """
    Copy nodes to the clipboard.
    """
    graph.copy_nodes()


def _cut_nodes(graph):
    """
    Cut nodes to the clip board.
    """
    graph.cut_nodes()


def _paste_nodes(graph):
    """
    Pastes nodes copied from the clipboard.
    """
    graph.paste_nodes()


def _delete_nodes(graph):
    """
    Delete selected node.
    """
    graph.delete_nodes(graph.selected_nodes())


def _select_all_nodes(graph):
    """
    Select all nodes.
    """
    graph.select_all()


def _clear_node_selection(graph):
    """
    Clear node selection.
    """
    graph.clear_selection()


def _disable_nodes(graph):
    """
    Toggle disable on selected nodes.
    """
    graph.disable_nodes(graph.selected_nodes())


def _duplicate_nodes(graph):
    """
    Duplicated selected nodes.
    """
    graph.duplicate_nodes(graph.selected_nodes())


def _expand_group_node(graph):
    """
    Expand selected group node.
    """
    selected_nodes = graph.selected_nodes()
    if not selected_nodes:
        graph.message_dialog('Please select a "GroupNode" to expand.')
        return
    graph.expand_group_node(selected_nodes[0])


def _fit_to_selection(graph):
    """
    Sets the zoom level to fit selected nodes.
    """
    graph.fit_to_selection()


def _show_undo_view(graph):
    """
    Show the undo list widget.
    """
    graph.undo_view.show()


def _curved_pipe(graph):
    """
    Set node graph pipes layout as curved.
    """
    from NodeGraphQt.constants import PipeLayoutEnum
    graph.set_pipe_style(PipeLayoutEnum.CURVED.value)


def _straight_pipe(graph):
    """
    Set node graph pipes layout as straight.
    """
    from NodeGraphQt.constants import PipeLayoutEnum
    graph.set_pipe_style(PipeLayoutEnum.STRAIGHT.value)


def _angle_pipe(graph):
    """
    Set node graph pipes layout as angled.
    """
    from NodeGraphQt.constants import PipeLayoutEnum
    graph.set_pipe_style(PipeLayoutEnum.ANGLE.value)


def _bg_grid_none(graph):
    """
    Turn off the background patterns.
    """
    from NodeGraphQt.constants import ViewerEnum
    graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_NONE.value)


def _bg_grid_dots(graph):
    """
    Set background node graph background with grid dots.
    """
    from NodeGraphQt.constants import ViewerEnum
    graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_DOTS.value)


def _bg_grid_lines(graph):
    """
    Set background node graph background with grid lines.
    """
    from NodeGraphQt.constants import ViewerEnum
    graph.set_grid_mode(ViewerEnum.GRID_DISPLAY_LINES.value)


def _layout_graph_down(graph):
    """
    Auto layout the nodes down stream.
    """
    nodes = graph.selected_nodes() or graph.all_nodes()
    graph.auto_layout_nodes(nodes=nodes, down_stream=True)


def _layout_graph_up(graph):
    """
    Auto layout the nodes up stream.
    """
    nodes = graph.selected_nodes() or graph.all_nodes()
    graph.auto_layout_nodes(nodes=nodes, down_stream=False)


def _toggle_node_search(graph):
    """
    show/hide the node search widget.
    """
    graph.toggle_node_search()
