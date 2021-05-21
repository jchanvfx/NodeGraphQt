#!/usr/bin/python
from distutils.version import LooseVersion

from Qt import QtGui, QtCore

from ..constants import (PIPE_LAYOUT_CURVED,
                         PIPE_LAYOUT_STRAIGHT,
                         PIPE_LAYOUT_ANGLE,
                         NODE_LAYOUT_VERTICAL,
                         NODE_LAYOUT_HORIZONTAL,
                         NODE_LAYOUT_DIRECTION)


# menu
def setup_context_menu(graph):
    """
    populate the specified graph's context menu with essential menus commands.

    example code:

    .. code-block:: python
        :linenos:

        from NodeGraphQt import NodeGraph, setup_context_menu

        graph = NodeGraph()
        setup_context_menu(graph)

    result:

    .. image:: _images/menu_hotkeys.png
        :width: 300px

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    root_menu = graph.get_context_menu('graph')

    file_menu = root_menu.add_menu('&File')
    edit_menu = root_menu.add_menu('&Edit')

    # create "File" menu.
    file_menu.add_command('Open...', _open_session, QtGui.QKeySequence.Open)
    file_menu.add_command('Import...', _import_session)
    file_menu.add_command('Save...', _save_session, QtGui.QKeySequence.Save)
    file_menu.add_command('Save As...', _save_session_as, 'Ctrl+Shift+S')
    file_menu.add_command('New Session', _new_session)

    file_menu.add_separator()

    file_menu.add_command('Zoom In', _zoom_in, '=')
    file_menu.add_command('Zoom Out', _zoom_out, '-')
    file_menu.add_command('Reset Zoom', _reset_zoom, 'H')

    # create "Edit" menu.
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
    edit_menu.add_command('Clear Undo History', _clear_undo)
    edit_menu.add_command('Show Undo History', _show_undo_view)
    edit_menu.add_separator()

    edit_menu.add_command('Copy', _copy_nodes, QtGui.QKeySequence.Copy)
    edit_menu.add_command('Cut', _cut_nodes, QtGui.QKeySequence.Cut)
    edit_menu.add_command('Paste', _paste_nodes, QtGui.QKeySequence.Paste)
    edit_menu.add_command('Delete', _delete_items, QtGui.QKeySequence.Delete)

    edit_menu.add_separator()

    edit_menu.add_command('Select all', _select_all_nodes, 'Ctrl+A')
    edit_menu.add_command('Deselect all', _clear_node_selection, 'Ctrl+Shift+A')
    edit_menu.add_command('Enable/Disable', _disable_nodes, 'D')

    edit_menu.add_command('Duplicate', _duplicate_nodes, 'Alt+C')
    edit_menu.add_command('Center Selection', _fit_to_selection, 'F')

    edit_menu.add_separator()

    edit_menu.add_command(
        'Auto Layout Up Stream', _layout_graph_up, 'L')
    edit_menu.add_command(
        'Auto Layout Down Stream', _layout_graph_down, 'Ctrl+L')

    edit_menu.add_separator()

    edit_menu.add_command('Jump In', _jump_in, 'I')
    edit_menu.add_command('Jump Out', _jump_out, 'O')

    edit_menu.add_separator()

    pipe_menu = edit_menu.add_menu('&Pipe')
    pipe_menu.add_command('Curved Pipe', _curved_pipe)
    pipe_menu.add_command('Straight Pipe', _straight_pipe)
    pipe_menu.add_command('Angle Pipe', _angle_pipe)

    bg_menu = edit_menu.add_menu('&Grid Mode')
    bg_menu.add_command('None', _bg_grid_none)
    bg_menu.add_command('Lines', _bg_grid_lines)
    bg_menu.add_command('Dots', _bg_grid_dots)

    edit_menu.add_separator()


# --- menu command functions. ---


def _zoom_in(graph):
    """
    Set the node graph to zoom in by 0.1

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    zoom = graph.get_zoom() + 0.1
    graph.set_zoom(zoom)


def _zoom_out(graph):
    """
    Set the node graph to zoom in by 0.1

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    zoom = graph.get_zoom() - 0.2
    graph.set_zoom(zoom)


def _reset_zoom(graph):
    graph.reset_zoom()


def _open_session(graph):
    """
    Prompts a file open dialog to load a session.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.load_dialog(current)
    if file_path:
        graph.load_session(file_path)


def _import_session(graph):
    """
    Prompts a file open dialog to load a session.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.load_dialog(current)
    if file_path:
        graph.import_session(file_path)


def _save_session(graph):
    """
    Prompts a file save dialog to serialize a session if required.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
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

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    current = graph.current_session()
    viewer = graph.viewer()
    file_path = viewer.save_dialog(current)
    if file_path:
        graph.save_session(file_path)


def _new_session(graph):
    """
    Prompts a warning dialog to new a node graph session.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    viewer = graph.viewer()
    if viewer.question_dialog('Clear Current Session?', 'Clear Session'):
        graph.clear_session()


def _clear_undo(graph):
    """
    Prompts a warning dialog to clear undo.

    Args:
        graph (NodeGraphQt.NodeGraph): node graph.
    """
    viewer = graph.viewer()
    msg = 'Clear all undo history, Are you sure?'
    if viewer.question_dialog('Clear Undo History', msg):
        graph.clear_undo_stack()


def _copy_nodes(graph):
    graph.copy_nodes()


def _cut_nodes(graph):
    graph.cut_nodes()


def _paste_nodes(graph):
    graph.paste_nodes()


def _delete_items(graph):
    graph.delete_nodes(graph.selected_nodes())
    graph.delete_pipes(graph._viewer.selected_pipes())


def _select_all_nodes(graph):
    graph.select_all()


def _clear_node_selection(graph):
    graph.clear_selection()


def _disable_nodes(graph):
    graph.disable_nodes(graph.selected_nodes())


def _duplicate_nodes(graph):
    graph.duplicate_nodes(graph.selected_nodes())


def _fit_to_selection(graph):
    graph.fit_to_selection()


def _jump_in(graph):
    nodes = graph.selected_nodes()
    if nodes:
        graph.set_node_space(nodes[0])


def _jump_out(graph):
    node = graph.get_node_space()
    if node:
        if node.parent() is not None:
            graph.set_node_space(node.parent())


def _show_undo_view(graph):
    graph.undo_view.show()


def _curved_pipe(graph):
    graph.set_pipe_style(PIPE_LAYOUT_CURVED)


def _straight_pipe(graph):
    graph.set_pipe_style(PIPE_LAYOUT_STRAIGHT)


def _angle_pipe(graph):
    graph.set_pipe_style(PIPE_LAYOUT_ANGLE)


def _bg_grid_none(graph):
    graph.set_grid_mode(0)


def _bg_grid_dots(graph):
    graph.set_grid_mode(1)


def _bg_grid_lines(graph):
    graph.set_grid_mode(2)


def _layout_graph_down(graph):
    nodes = graph.selected_nodes() or graph.all_nodes()
    graph.auto_layout_nodes(nodes=nodes, down_stream=True)


def _layout_graph_up(graph):
    nodes = graph.selected_nodes() or graph.all_nodes()
    graph.auto_layout_nodes(nodes-nodes, down_stream=False)


# topological_sort


def get_input_nodes(node):
    """
    Get input nodes of node.

    Args:
        node (NodeGraphQt.BaseNode).
    Returns:
        list[NodeGraphQt.BaseNode].
    """

    nodes = {}
    for p in node.input_ports():
        for cp in p.connected_ports():
            n = cp.node()
            nodes[n.id] = n
    return list(nodes.values())


def get_output_nodes(node, cook=True):
    """
    Get output nodes of node.

    Args:
        node (NodeGraphQt.BaseNode).
        cook (bool): call this function for cook node.
    Returns:
        list[NodeGraphQt.BaseNode].
    """

    nodes = {}
    for p in node.output_ports():
        for cp in p.connected_ports():
            n = cp.node()
            if cook and n.has_property('graph_rect'):
                n.mark_node_to_be_cooked(cp)
            nodes[n.id] = n
    return list(nodes.values())


def _has_input_node(node):
    """
    Returns whether the node has input node.

    Args:
        node (NodeGraphQt.BaseNode).
    Returns:
        bool.
    """

    for p in node.input_ports():
        if p.view.connected_pipes:
            return True
    return False


def _has_output_node(node):
    """
    Returns whether the node has output node.

    Args:
        node (NodeGraphQt.BaseNode).
    Returns:
        bool.
    """

    for p in node.output_ports():
        if p.view.connected_pipes:
            return True
    return False


def _build_down_stream_graph(start_nodes):
    """
    Build a graph by down stream nodes.

    Args:
        start_nodes (list[NodeGraphQt.BaseNode]).
    Returns:
        dict {node0: [output nodes of node0], ...}.
    """

    graph = {}
    for node in start_nodes:
        output_nodes = get_output_nodes(node)
        graph[node] = output_nodes
        while output_nodes:
            _output_nodes = []
            for n in output_nodes:
                if n not in graph:
                    nodes = get_output_nodes(n)
                    graph[n] = nodes
                    _output_nodes.extend(nodes)
            output_nodes = _output_nodes
    return graph


def _build_up_stream_graph(start_nodes):
    """
    Build a graph by up stream nodes.

    Args:
        start_nodes (list[NodeGraphQt.BaseNode]).
    Returns:
        dict {node0: [input nodes of node0], ...}.
    """

    graph = {}
    for node in start_nodes:
        input_nodes = get_input_nodes(node)
        graph[node] = input_nodes
        while input_nodes:
            _input_nodes = []
            for n in input_nodes:
                if n not in graph:
                    nodes = get_input_nodes(n)
                    graph[n] = nodes
                    _input_nodes.extend(nodes)
            input_nodes = _input_nodes
    return graph


def _sort_nodes(graph, start_nodes, reverse=True):
    """
    Sort nodes in graph.

    Args:
        graph (dict): generate from '_build_up_stream_graph' or '_build_down_stream_graph'.
        start_nodes (list[NodeGraphQt.BaseNode]): graph start nodes.
        reverse (bool): reverse the result.
    Returns:
        list[NodeGraphQt.BaseNode]: sorted nodes.
    """

    if not graph:
        return []

    visit = dict((node, False) for node in graph.keys())

    sorted_nodes = []

    def dfs(start_node):
        for end_node in graph[start_node]:
            if not visit[end_node]:
                visit[end_node] = True
                dfs(end_node)
        sorted_nodes.append(start_node)

    for start_node in start_nodes:
        if not visit[start_node]:
            visit[start_node] = True
            dfs(start_node)

    if reverse:
        sorted_nodes.reverse()

    return sorted_nodes


def __remove_BackdropNode(nodes):
    from .node import BackdropNode
    for node in nodes[:]:
        if isinstance(node, BackdropNode):
            nodes.remove(node)
    return nodes


def topological_sort_by_down(start_nodes=None, all_nodes=None):
    """
    Topological sort method by down stream direction.
    'start_nodes' and 'all_nodes' only one needs to be given.

    Args:
        start_nodes (list[NodeGraphQt.BaseNode]):
            (Optional) the start update nodes of the graph.
        all_nodes (list[NodeGraphQt.BaseNode]):
            (Optional) if 'start_nodes' is None the function can calculate
            start nodes from 'all_nodes'.

    Returns:
        list[NodeGraphQt.BaseNode]: sorted nodes.
    """
    if not start_nodes and not all_nodes:
        return []
    if start_nodes:
        start_nodes = __remove_BackdropNode(start_nodes)
    if all_nodes:
        all_nodes = __remove_BackdropNode(all_nodes)

    if not start_nodes:
        start_nodes = [n for n in all_nodes if not _has_input_node(n)]
    if not start_nodes:
        return []
    if not [n for n in start_nodes if _has_output_node(n)]:
        return start_nodes

    graph = _build_down_stream_graph(start_nodes)

    return _sort_nodes(graph, start_nodes, True)


def topological_sort_by_up(start_nodes=None, all_nodes=None):
    """
    Topological sort method by up stream direction.
    'start_nodes' and 'all_nodes' only one needs to be given.

    Args:
        start_nodes (list[NodeGraphQt.BaseNode]):
            (Optional) the end update nodes of the graph.
        all_nodes (list[NodeGraphQt.BaseNode]):
            (Optional) if 'start_nodes' is None the function can calculate
            start nodes from 'all_nodes'.
    Returns:
        list[NodeGraphQt.BaseNode]: sorted nodes.
    """
    if not start_nodes and not all_nodes:
        return []
    if start_nodes:
        start_nodes = __remove_BackdropNode(start_nodes)
    if all_nodes:
        all_nodes = __remove_BackdropNode(all_nodes)

    if not start_nodes:
        start_nodes = [n for n in all_nodes if not _has_output_node(n)]
    if not start_nodes:
        return []
    if not [n for n in start_nodes if _has_input_node(n)]:
        return start_nodes

    graph = _build_up_stream_graph(start_nodes)

    return _sort_nodes(graph, start_nodes, False)


def _update_nodes(nodes):
    """
    Run nodes.

    Args:
        nodes (list[NodeGraphQt.BaseNode]): nodes to be run.
    """
    for node in nodes:
        if node.disabled():
            continue
        try:
            node.run()
        except Exception as error:
            print("Error Update Node : {}\n{}" .format(node, str(error)))
            break


def update_node_down_stream(node):
    """
    Run nodes by node down stream direction.

    Args:
        node (NodeGraphQt.BaseNode): the start node of the update stream.
    """

    _update_nodes(topological_sort_by_down(start_nodes=[node]))


def update_node_up_stream(node):
    """
    Run nodes by node up stream direction.

    Args:
        node (NodeGraphQt.BaseNode): the end node of the update stream.
    """

    _update_nodes(topological_sort_by_up(start_nodes=[node]))


def update_nodes_by_down(nodes):
    """
    Run nodes by down stream direction.

    Args:
        nodes (list[NodeGraphQt.BaseNode]): nodes to be run.
    """

    _update_nodes(topological_sort_by_down(all_nodes=nodes))


def update_nodes_by_up(nodes):
    """
    Run nodes by up stream direction.

    Args:
        nodes (list[NodeGraphQt.BaseNode]): nodes to be run.
    """

    _update_nodes(topological_sort_by_up(all_nodes=nodes))


# garbage collect

def minimize_node_ref_count(node):
    """
    Minimize node reference count for garbage collect.

    Args:
        node (NodeGraphQt.NodeObject): node.
    """
    if node.graph is None or node.id not in node.graph.model.nodes:
        if hasattr(node, 'deleted'):
            del node
            return
        from .node import BaseNode
        from .graph import SubGraph
        node._parent = None
        if isinstance(node, BaseNode):
            try:
                [wid.deleteLater() for wid in node.view._widgets.values()]
            except:
                pass
            node.view._widgets.clear()
            for port in node._inputs:
                port.model.node = None
            for port in node._outputs:
                port.model.node = None

            if isinstance(node, SubGraph):
                node._children.clear()
                node.sub_graph_input_nodes.clear()
                node.sub_graph_output_nodes.clear()
            # if isinstance(node, QtCore.QObject):
            #     node.deleteLater()
        node.deleted = True
        del node
