Port Overview
#############

Creating Custom Shapes
**********************

| (*Implemented on* ``v0.1.1``)

To have custom port shapes the :meth:`NodeGraphQt.BaseNode.add_input` and
:meth:`NodeGraphQt.BaseNode.add_output` functions now have a ``painter_func``
argument where you specify you custom port painter function.

.. image:: ../_images/custom_ports.png
        :width: 178px

|

Example Triangle Port
*********************

Here's an example function for drawing a triangle port.

.. code-block:: python
    :linenos:

    def draw_triangle_port(painter, rect, info):
        """
        Custom paint function for drawing a Triangle shaped port.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): port rect used to describe parameters needed to draw.
            info (dict): information describing the ports current state.
                {
                    'port_type': 'in',
                    'color': (0, 0, 0),
                    'border_color': (255, 255, 255),
                    'multi_connection': False,
                    'connected': False,
                    'hovered': False,
                }
        """
        painter.save()

        # create triangle polygon.
        size = int(rect.height() / 2)
        triangle = QtGui.QPolygonF()
        triangle.append(QtCore.QPointF(-size, size))
        triangle.append(QtCore.QPointF(0.0, -size))
        triangle.append(QtCore.QPointF(size, size))

        # map polygon to port position.
        transform = QtGui.QTransform()
        transform.translate(rect.center().x(), rect.center().y())
        port_poly = transform.map(triangle)

        # mouse over port color.
        if info['hovered']:
            color = QtGui.QColor(14, 45, 59)
            border_color = QtGui.QColor(136, 255, 35)
        # port connected color.
        elif info['connected']:
            color = QtGui.QColor(195, 60, 60)
            border_color = QtGui.QColor(200, 130, 70)
        # default port color
        else:
            color = QtGui.QColor(*info['color'])
            border_color = QtGui.QColor(*info['border_color'])

        pen = QtGui.QPen(border_color, 1.8)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)

        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawPolygon(port_poly)

        painter.restore()

The ``draw_triangle_port`` painter function can then be passed to the ``painter_func`` arg.

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    from NodeGraphQt import BaseNode

    class MyListNode(BaseNode):

        def __init__(self):
            super(MyListNode, self).__init__()
            # create a input port with custom painter function.
            self.add_input('triangle', painter_func=draw_triangle_port)

|

Example Square Port
*******************

And here's another example function for drawing a Square port.

.. code-block:: python
    :linenos:

    def draw_square_port(painter, rect, info):
        """
        Custom paint function for drawing a Square shaped port.

        Args:
            painter (QtGui.QPainter): painter object.
            rect (QtCore.QRectF): port rect used to describe parameters needed to draw.
            info (dict): information describing the ports current state.
                {
                    'port_type': 'in',
                    'color': (0, 0, 0),
                    'border_color': (255, 255, 255),
                    'multi_connection': False,
                    'connected': False,
                    'hovered': False,
                }
        """
        painter.save()

        # mouse over port color.
        if info['hovered']:
            color = QtGui.QColor(14, 45, 59)
            border_color = QtGui.QColor(136, 255, 35, 255)
        # port connected color.
        elif info['connected']:
            color = QtGui.QColor(195, 60, 60)
            border_color = QtGui.QColor(200, 130, 70)
        # default port color
        else:
            color = QtGui.QColor(*info['color'])
            border_color = QtGui.QColor(*info['border_color'])

        pen = QtGui.QPen(border_color, 1.8)
        pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)

        painter.setPen(pen)
        painter.setBrush(color)
        painter.drawRect(rect)

        painter.restore()


Connection Constrains
*********************

From version ``v0.6.0`` port object can now have pipe connection constraints the functions implemented are:

 - :meth:`NodeGraphQt.Port.add_accept_port_type`
 - :meth:`NodeGraphQt.Port.add_reject_port_type`

this can also be set on the ``BaseNode`` level as well with:

 - :meth:`NodeGraphQt.BaseNode.add_accept_port_type`
 - :meth:`NodeGraphQt.BaseNode.add_accept_port_type`


Here's an example snippet to add pipe connection constraints to a port.

.. code-block:: python
    :linenos:

    from NodeGraphQt import BaseNode
    from NodeGraphQt.constants import PortTypeEnum


    class BasicNodeA(BaseNode):

        # unique node identifier.
        __identifier__ = 'io.github.jchanvfx'

        # initial default node name.
        NODE_NAME = 'node A'

        def __init__(self):
            super(BasicNode, self).__init__()

            # create node output ports.
            self.add_output('output 1')
            self.add_output('output 2')


    class BasicNodeB(BaseNode):

        # unique node identifier.
        __identifier__ = 'io.github.jchanvfx'

        # initial default node name.
        NODE_NAME = 'node B'

        def __init__(self):
            super(BasicNode, self).__init__()

            # create node inputs.

            # port "in A" will only accept pipe connections from port "output 1"
            # under the node "BasicNodeA".
            in_port_a = self.add_input('in A')
            in_port_a.add_accept_port_type(
                port_name='output 1',
                port_type=PortTypeEnum.OUT.value,
                node_type='io.github.jchanvfx.BasicNodeA'
            )

            # port "in A" will reject pipe connections from port "output 1"
            # under the node "BasicNodeA".
            in_port_b = self.add_input('in B')
            in_port_b.add_reject_port_type(
                port_name='output 1',
                port_type=PortTypeEnum.OUT.value,
                node_type='io.github.jchanvfx.BasicNodeA'
            )
