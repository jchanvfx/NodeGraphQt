#!/usr/bin/python
# -*- coding: utf-8 -*-
import signal
from pathlib import Path

from Qt import QtCore, QtWidgets

# import example nodes from the "nodes" sub-package
from examples.nodes import basic_nodes, custom_ports_node, group_node, widget_nodes
from NodeGraphQt import (
    NodeGraph,
    NodesPaletteWidget,
    NodesTreeWidget,
    PropertiesBinWidget,
)
from NodeGraphQt.constants import LayoutDirectionEnum

BASE_PATH = Path(__file__).parent.resolve()


def main():
    # handle SIGINT to make the app terminate on CTRL+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QtWidgets.QApplication([])

    # create graph controller.
    graph = NodeGraph()

    # set up context menu for the node graph.
    hotkey_path = Path(BASE_PATH, 'hotkeys', 'hotkeys.json')
    graph.set_context_menu_from_file(hotkey_path, 'graph')

    # registered example nodes.
    graph.register_nodes([
        basic_nodes.BasicNodeA,
        basic_nodes.BasicNodeB,
        basic_nodes.CircleNode,
        basic_nodes.SVGNode,
        custom_ports_node.CustomPortsNode,
        group_node.MyGroupNode,
        widget_nodes.DropdownMenuNode,
        widget_nodes.TextInputNode,
        widget_nodes.SpinBoxNode,
        widget_nodes.CheckboxNode
    ])

    # show the node graph widget.
    graph_widget = graph.widget
    graph_widget.resize(1100, 800)
    graph_widget.setWindowTitle("NodeGraphQt Example")
    graph_widget.show()

    # create node with custom text color and disable it.
    n_basic_a = graph.create_node(
        'nodes.basic.BasicNodeA', text_color='#feab20')
    n_basic_a.set_disabled(True)

    # create node with vertial alignment
    n_basic_a_vertical = graph.create_node(
        "nodes.basic.BasicNodeA", name="Vertical Node", text_color="#feab20"
    )

    # adjust layout of node to be vertical
    n_basic_a_vertical.set_layout_direction(1)

    # create node and set a custom icon.
    n_basic_b = graph.create_node(
        'nodes.basic.BasicNodeB', name='custom icon')
    n_basic_b.set_icon(str(Path(BASE_PATH, 'img', 'star.png')))

    # create node with the custom port shapes.
    n_custom_ports = graph.create_node(
        'nodes.custom.ports.CustomPortsNode', name='custom ports')

    # create node with the embedded QLineEdit widget.
    n_text_input = graph.create_node(
        'nodes.widget.TextInputNode', name='text node', color='#0a1e20')

    # create node with the embedded QSpinBox widget.
    n_spinbox_input = graph.create_node(
        'nodes.widget.SpinBoxNode', name='spinbox node', color='#0a1e20')

    # create node with the embedded QCheckBox widgets.
    n_checkbox = graph.create_node(
        'nodes.widget.CheckboxNode', name='checkbox node')

    # create node with the QComboBox widget.
    n_combo_menu = graph.create_node(
        'nodes.widget.DropdownMenuNode', name='combobox node')

    # crete node with the circular design.
    n_circle = graph.create_node(
        'nodes.basic.CircleNode', name='circle node')

    # crete node with the circular design.
    n_svg = graph.create_node(
        'nodes.basic.SVGNode', name='svg node')
    
    n_svg_file = graph.create_node(
        'nodes.basic.SVGNode', name='svg file')
    n_svg_file.set_svg(str(Path(BASE_PATH, 'img', 'cirlce-diamond.svg')))
    
    n_svg_file_vertical = graph.create_node(
        'nodes.basic.SVGNode', name='svg file', color='#0a1e20')
    
    n_svg_file_vertical.set_svg(str(Path(BASE_PATH, 'img', 'cirlce-diamond.svg')))
    # adjust layout of node to be vertical
    n_svg_file_vertical.set_layout_direction(1)
    
    # create group node.
    n_group = graph.create_node('nodes.group.MyGroupNode')

    # make node connections.

    # (connect nodes using the .set_output method)
    n_text_input.set_output(0, n_custom_ports.input(0))
    n_text_input.set_output(0, n_checkbox.input(0))
    n_text_input.set_output(0, n_combo_menu.input(0))
    # (connect nodes using the .set_input method)
    n_group.set_input(0, n_custom_ports.output(1))
    n_basic_b.set_input(2, n_checkbox.output(0))
    n_basic_b.set_input(2, n_combo_menu.output(1))
    # (connect nodes using the .connect_to method from the port object)
    port = n_basic_a.input(0)
    port.connect_to(n_basic_b.output(0))

    # auto layout nodes.
    graph.auto_layout_nodes()

    # crate a backdrop node and wrap it around
    # "custom port node" and "group node".
    n_backdrop = graph.create_node('Backdrop')
    n_backdrop.wrap_nodes([n_custom_ports, n_combo_menu])

    # fit nodes to the viewer.
    graph.clear_selection()
    graph.fit_to_selection()

    # adjust layout of node to be vertical (for all nodes).
    # graph.set_layout_direction(LayoutDirectionEnum.VERTICAL.value)

    # Custom builtin widgets from NodeGraphQt
    # ---------------------------------------

    # create a node properties bin widget.
    properties_bin = PropertiesBinWidget(node_graph=graph, parent=graph_widget)
    properties_bin.setWindowFlags(QtCore.Qt.Tool)

    # example show the node properties bin widget when a node is double-clicked.
    def display_properties_bin(node):
        if not properties_bin.isVisible():
            properties_bin.show()

    # wire function to "node_double_clicked" signal.
    graph.node_double_clicked.connect(display_properties_bin)

    # create a nodes tree widget.
    nodes_tree = NodesTreeWidget(node_graph=graph)
    nodes_tree.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_tree.set_category_label('nodes.custom.ports', 'Custom Port Nodes')
    nodes_tree.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_tree.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_tree.set_category_label('nodes.group', 'Group Nodes')
    # nodes_tree.show()

    # create a node palette widget.
    nodes_palette = NodesPaletteWidget(node_graph=graph)
    nodes_palette.set_category_label('nodeGraphQt.nodes', 'Builtin Nodes')
    nodes_palette.set_category_label('nodes.custom.ports', 'Custom Port Nodes')
    nodes_palette.set_category_label('nodes.widget', 'Widget Nodes')
    nodes_palette.set_category_label('nodes.basic', 'Basic Nodes')
    nodes_palette.set_category_label('nodes.group', 'Group Nodes')
    # nodes_palette.show()

    app.exec_()


if __name__ == '__main__':
    main()
