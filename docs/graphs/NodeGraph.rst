:hide-rtoc:

NodeGraph
#########

.. autosummary::
    NodeGraphQt.NodeGraph

.. code-block:: python
    :linenos:

    from PyQt6 import QtWidgets
    from NodeGraphQt import NodeGraph

    if __name__ == '__main__':
        app = QtWidgets.QApplication([])

        node_graph = NodeGraph()

        widget = node_graph.widget
        widget.show()

        app.exec()

---

.. autoclass:: NodeGraphQt.NodeGraph
    :members:
    :member-order: bysource
    :exclude-members: staticMetaObject
