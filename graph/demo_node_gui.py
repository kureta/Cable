#!/usr/bin/env python3
"""
Example Node Graph GUI Application

This demonstrates the generic node system with a visual interface.
Features:
- Addition node
- Multiplication node
- Print node
- 4 editable constant number nodes
- Interactive connections between nodes
- Editable number values

Run with: python3 graph/demo_node_gui.py
"""

import sys
from typing import Dict, Optional, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsScene, QGraphicsView,
    QGraphicsItem, QGraphicsTextItem, QGraphicsEllipseItem,
    QGraphicsLineItem, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QLineEdit, QDialog, QDialogButtonBox,
    QDoubleSpinBox, QFormLayout
)
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath, QFont,
    QWheelEvent, QPalette
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF, pyqtSignal

from generic_node import (
    GenericNode, AddNode, MultiplyNode, PrintNode, ConstantNode, NodeFactory
)
from generic_port import GenericPort, PortDirection, PortDataType


# --- Visual Constants ---
NODE_WIDTH = 180
NODE_HEIGHT = 120
PORT_RADIUS = 8
PORT_SPACING = 25
PORT_OFFSET = 30
TITLE_HEIGHT = 30


class VisualPort(QGraphicsEllipseItem):
    """Visual representation of a port"""
    
    def __init__(self, port: GenericPort, node_ui: 'VisualNode', is_input: bool):
        # Create ellipse centered at origin
        super().__init__(-PORT_RADIUS, -PORT_RADIUS, PORT_RADIUS * 2, PORT_RADIUS * 2)
        
        self.port = port
        self.node_ui = node_ui
        self.is_input = is_input
        self.connections = []
        
        # Visual properties
        self.setBrush(QBrush(QColor(100, 150, 255)))
        self.setPen(QPen(QColor(50, 100, 200), 2))
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Port label
        self.label = QGraphicsTextItem(port.name, self)
        self.label.setDefaultTextColor(QColor(50, 50, 50))
        font = QFont()
        font.setPointSize(9)
        self.label.setFont(font)
        
        # Position label
        if is_input:
            self.label.setPos(PORT_RADIUS + 5, -PORT_RADIUS)
        else:
            label_width = self.label.boundingRect().width()
            self.label.setPos(-label_width - PORT_RADIUS - 5, -PORT_RADIUS)
    
    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor(150, 200, 255)))
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor(100, 150, 255)))
        super().hoverLeaveEvent(event)
    
    def get_connection_point(self) -> QPointF:
        """Get the point where connections should attach"""
        return self.scenePos()
    
    def add_connection(self, connection: 'Connection'):
        """Add a connection to this port"""
        if connection not in self.connections:
            self.connections.append(connection)
    
    def remove_connection(self, connection: 'Connection'):
        """Remove a connection from this port"""
        if connection in self.connections:
            self.connections.remove(connection)


class Connection(QGraphicsLineItem):
    """Visual representation of a connection between ports"""
    
    def __init__(self, source_port: VisualPort, dest_port: VisualPort):
        super().__init__()
        
        self.source_port = source_port
        self.dest_port = dest_port
        
        # Visual properties
        pen = QPen(QColor(80, 150, 220), 2)
        self.setPen(pen)
        self.setZValue(-1)  # Draw behind nodes
        
        # Register with ports
        source_port.add_connection(self)
        dest_port.add_connection(self)
        
        # Connect the data model
        source_port.port.connect(dest_port.port)
        
        self.update_position()
    
    def update_position(self):
        """Update the line position based on port positions"""
        start = self.source_port.get_connection_point()
        end = self.dest_port.get_connection_point()
        self.setLine(QLineF(start, end))
    
    def destroy(self):
        """Remove this connection"""
        self.source_port.remove_connection(self)
        self.dest_port.remove_connection(self)
        self.source_port.port.disconnect(self.dest_port.port)
        
        if self.scene():
            self.scene().removeItem(self)


class VisualNode(QGraphicsItem):
    """Visual representation of a node"""
    
    def __init__(self, node_model: GenericNode, x: float = 0, y: float = 0):
        super().__init__()
        
        self.node_model = node_model
        self.visual_ports: Dict[str, VisualPort] = {}
        
        # Visual properties
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setPos(x, y)
        
        # Title
        self.title = QGraphicsTextItem(node_model.name, self)
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.title.setFont(font)
        self.title.setDefaultTextColor(QColor(255, 255, 255))
        
        # Center title
        title_width = self.title.boundingRect().width()
        self.title.setPos((NODE_WIDTH - title_width) / 2, 5)
        
        # Create visual ports
        self._create_ports()
        
        # For editable constants, add value display
        if isinstance(node_model, ConstantNode):
            self.value_label = QGraphicsTextItem("", self)
            self.value_label.setDefaultTextColor(QColor(200, 200, 200))
            font = QFont()
            font.setPointSize(12)
            self.value_label.setFont(font)
            self.update_value_display()
        else:
            self.value_label = None
    
    def _create_ports(self):
        """Create visual representations of ports"""
        input_ports = self.node_model.get_input_ports()
        output_ports = self.node_model.get_output_ports()
        
        # Position input ports on the left
        for i, port in enumerate(input_ports):
            y_pos = PORT_OFFSET + i * PORT_SPACING
            visual_port = VisualPort(port, self, is_input=True)
            visual_port.setParentItem(self)
            visual_port.setPos(0, y_pos)
            self.visual_ports[port.name] = visual_port
        
        # Position output ports on the right
        for i, port in enumerate(output_ports):
            y_pos = PORT_OFFSET + i * PORT_SPACING
            visual_port = VisualPort(port, self, is_input=False)
            visual_port.setParentItem(self)
            visual_port.setPos(NODE_WIDTH, y_pos)
            self.visual_ports[port.name] = visual_port
    
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, NODE_WIDTH, NODE_HEIGHT)
    
    def paint(self, painter: QPainter, option, widget=None):
        # Determine if selected
        is_selected = bool(option.state & QGraphicsItem.GraphicsItemFlag.ItemIsSelected)
        
        # Draw node body
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        if is_selected:
            painter.setBrush(QBrush(QColor(70, 70, 90)))
            painter.setPen(QPen(QColor(100, 180, 255), 2))
        else:
            painter.setBrush(QBrush(QColor(60, 60, 80)))
            painter.setPen(QPen(QColor(80, 80, 100), 1))
        
        painter.drawRoundedRect(self.boundingRect(), 5, 5)
        
        # Title bar
        title_rect = QRectF(0, 0, NODE_WIDTH, TITLE_HEIGHT)
        painter.setBrush(QBrush(QColor(50, 50, 70)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Clip to rounded corners
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 5, 5)
        painter.setClipPath(path)
        painter.drawRect(title_rect)
    
    def mouseDoubleClickEvent(self, event):
        """Double-click to edit value for constant nodes"""
        if isinstance(self.node_model, ConstantNode):
            self.edit_constant_value()
        super().mouseDoubleClickEvent(event)
    
    def edit_constant_value(self):
        """Open dialog to edit constant value"""
        dialog = QDialog()
        dialog.setWindowTitle(f"Edit {self.node_model.name}")
        
        layout = QFormLayout()
        
        spin_box = QDoubleSpinBox()
        spin_box.setRange(-999999, 999999)
        spin_box.setDecimals(2)
        spin_box.setValue(self.node_model.constant_value)
        
        layout.addRow("Value:", spin_box)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_value = spin_box.value()
            self.node_model.constant_value = new_value
            self.node_model.get_port("value").set_value(new_value)
            self.update_value_display()
    
    def update_value_display(self):
        """Update the displayed value for constant nodes"""
        if self.value_label and isinstance(self.node_model, ConstantNode):
            value = self.node_model.constant_value
            self.value_label.setPlainText(f"{value:.2f}")
            
            # Center the label
            label_width = self.value_label.boundingRect().width()
            self.value_label.setPos(
                (NODE_WIDTH - label_width) / 2,
                NODE_HEIGHT / 2
            )
    
    def itemChange(self, change, value):
        """Handle item changes - update connections when moved"""
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for visual_port in self.visual_ports.values():
                for connection in visual_port.connections:
                    connection.update_position()
        
        return super().itemChange(change, value)


class NodeGraphScene(QGraphicsScene):
    """Scene for the node graph"""
    
    def __init__(self):
        super().__init__()
        self.setSceneRect(-2000, -2000, 4000, 4000)
        
        # Connection state
        self.temp_connection_line = None
        self.connection_start_port = None
    
    def mousePressEvent(self, event):
        """Handle mouse press for starting connections"""
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        
        if isinstance(item, VisualPort) and event.button() == Qt.MouseButton.LeftButton:
            # Start connection
            self.connection_start_port = item
            
            # Create temporary line
            self.temp_connection_line = QGraphicsLineItem()
            pen = QPen(QColor(150, 200, 255), 2, Qt.PenStyle.DashLine)
            self.temp_connection_line.setPen(pen)
            self.addItem(self.temp_connection_line)
            
            start = item.get_connection_point()
            self.temp_connection_line.setLine(QLineF(start, event.scenePos()))
            
            event.accept()
            return
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Update temporary connection line"""
        if self.temp_connection_line and self.connection_start_port:
            start = self.connection_start_port.get_connection_point()
            self.temp_connection_line.setLine(QLineF(start, event.scenePos()))
            event.accept()
            return
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Complete connection on release"""
        if self.temp_connection_line and self.connection_start_port:
            # Remove temporary line
            self.removeItem(self.temp_connection_line)
            self.temp_connection_line = None
            
            # Check if released on a port
            item = self.itemAt(event.scenePos(), self.views()[0].transform())
            
            if isinstance(item, VisualPort) and item != self.connection_start_port:
                # Check if connection is valid
                source_port = self.connection_start_port
                dest_port = item
                
                # Ensure source is output and dest is input
                if not source_port.is_input and dest_port.is_input:
                    if source_port.port.can_connect_to(dest_port.port):
                        # Create connection
                        connection = Connection(source_port, dest_port)
                        self.addItem(connection)
                elif source_port.is_input and not dest_port.is_input:
                    # User dragged backwards, swap them
                    if dest_port.port.can_connect_to(source_port.port):
                        connection = Connection(dest_port, source_port)
                        self.addItem(connection)
            
            self.connection_start_port = None
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Delete:
            # Delete selected items
            for item in self.selectedItems():
                if isinstance(item, Connection):
                    item.destroy()
                elif isinstance(item, VisualNode):
                    # Remove node and its connections
                    for visual_port in item.visual_ports.values():
                        for connection in list(visual_port.connections):
                            connection.destroy()
                    self.removeItem(item)
        
        super().keyPressEvent(event)


class NodeGraphView(QGraphicsView):
    """View for the node graph with zoom/pan"""
    
    def __init__(self, scene: NodeGraphScene):
        super().__init__(scene)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Background
        self.setBackgroundBrush(QBrush(QColor(40, 40, 50)))
    
    def wheelEvent(self, event: QWheelEvent):
        """Zoom with mouse wheel"""
        # Zoom factor
        zoom_factor = 1.15
        
        if event.angleDelta().y() > 0:
            # Zoom in
            self.scale(zoom_factor, zoom_factor)
        else:
            # Zoom out
            self.scale(1 / zoom_factor, 1 / zoom_factor)


class NodeGraphWindow(QMainWindow):
    """Main window for the node graph demo"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Generic Node System Demo")
        self.resize(1200, 800)
        
        # Create scene and view
        self.scene = NodeGraphScene()
        self.view = NodeGraphView(self.scene)
        
        # Create central widget with layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        execute_btn = QPushButton("Execute Graph")
        execute_btn.clicked.connect(self.execute_graph)
        toolbar.addWidget(execute_btn)
        
        clear_btn = QPushButton("Clear Output")
        clear_btn.clicked.connect(self.clear_output)
        toolbar.addWidget(clear_btn)
        
        toolbar.addStretch()
        
        info_label = QLabel("Drag nodes to move | Drag from output to input to connect | Double-click constants to edit | Delete key to remove")
        info_label.setStyleSheet("color: #888; font-size: 10px;")
        toolbar.addWidget(info_label)
        
        layout.addLayout(toolbar)
        
        # Add view
        layout.addWidget(self.view, stretch=1)
        
        # Output area
        self.output_text = QLabel("Output will appear here after execution")
        self.output_text.setStyleSheet("background-color: #2a2a2a; color: #00ff00; padding: 10px; font-family: monospace;")
        self.output_text.setMinimumHeight(100)
        self.output_text.setWordWrap(True)
        layout.addWidget(self.output_text)
        
        # Create initial nodes
        self.create_initial_nodes()
    
    def create_initial_nodes(self):
        """Create the initial node setup"""
        # Create 4 constant nodes
        const1 = VisualNode(ConstantNode("Constant 1", value=5.0), -400, -200)
        const2 = VisualNode(ConstantNode("Constant 2", value=3.0), -400, -50)
        const3 = VisualNode(ConstantNode("Constant 3", value=2.0), -400, 100)
        const4 = VisualNode(ConstantNode("Constant 4", value=10.0), -400, 250)
        
        # Create operation nodes
        add_node = VisualNode(AddNode("Add"), -100, -125)
        mult_node = VisualNode(MultiplyNode("Multiply"), 200, 0)
        
        # Create print node
        print_node = VisualNode(PrintNode("Result"), 500, 0)
        
        # Add to scene
        for node in [const1, const2, const3, const4, add_node, mult_node, print_node]:
            self.scene.addItem(node)
        
        # Store for easy access
        self.nodes = {
            'const1': const1,
            'const2': const2,
            'const3': const3,
            'const4': const4,
            'add': add_node,
            'mult': mult_node,
            'print': print_node
        }
    
    def execute_graph(self):
        """Execute all nodes in the graph"""
        output_lines = []
        
        # Collect all visual nodes
        visual_nodes = [item for item in self.scene.items() if isinstance(item, VisualNode)]
        
        # Execute each node (simple execution, not topologically sorted)
        # For a more sophisticated system, implement topological sort
        executed = set()
        max_iterations = 10
        
        for _ in range(max_iterations):
            made_progress = False
            
            for visual_node in visual_nodes:
                node = visual_node.node_model
                
                if node in executed:
                    continue
                
                # Check if all input dependencies are met
                inputs_ready = True
                for port in node.get_input_ports():
                    if not port.connected_to:
                        continue
                    
                    # Check if source node has been executed
                    for connected_port in port.connected_to:
                        source_node = self._find_node_for_port(connected_port)
                        if source_node and source_node not in executed:
                            inputs_ready = False
                            break
                
                if inputs_ready:
                    # Transfer values from connected ports
                    for port in node.get_input_ports():
                        for connected_port in port.connected_to:
                            port.set_value(connected_port.get_value(), validate=False)
                    
                    # Execute
                    try:
                        node.execute()
                        executed.add(node)
                        made_progress = True
                        
                        # Capture output from print nodes
                        if isinstance(node, PrintNode):
                            value = node.get_port("value").get_value()
                            output_lines.append(f"{node.name}: {value}")
                        
                    except Exception as e:
                        output_lines.append(f"Error executing {node.name}: {e}")
            
            if not made_progress:
                break
        
        # Display output
        if output_lines:
            self.output_text.setText("\n".join(output_lines))
        else:
            self.output_text.setText("No output produced. Connect nodes and try again.")
    
    def _find_node_for_port(self, port: GenericPort) -> Optional[GenericNode]:
        """Find the GenericNode that owns a port"""
        visual_nodes = [item for item in self.scene.items() if isinstance(item, VisualNode)]
        
        for visual_node in visual_nodes:
            if port in visual_node.node_model.get_input_ports() or port in visual_node.node_model.get_output_ports():
                return visual_node.node_model
        
        return None
    
    def clear_output(self):
        """Clear the output display"""
        self.output_text.setText("Output cleared. Execute graph to see results.")


def main():
    """Run the demo application"""
    app = QApplication(sys.argv)
    
    # Set dark theme
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    app.setPalette(palette)
    
    window = NodeGraphWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
