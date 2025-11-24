"""
Base Node UI Module - Reusable node visualization components

This module provides the foundation for node-based UI components that can be
reused in different applications. It separates the core visualization logic
from application-specific business logic.

The base classes provide:
- Node rendering with title, ports, and body
- Port management (add/remove)
- Theme-aware colors
- Layout calculations
- Basic selection and highlighting

The module is completely decoupled from any specific domain (audio, JACK, etc.)
and can be used for:
- Mathematical operations
- Data flow diagrams
- Visual programming
- Audio/MIDI routing (as one specific use case)
- Any node-graph application

Applications can extend these base classes to add specific features like:
- Custom context menus
- Application-specific port types
- Domain-specific computations
- State persistence
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Any, Callable
from PyQt6.QtWidgets import (
    QGraphicsItem, QGraphicsTextItem, QStyleOptionGraphicsItem, QWidget, QStyle
)
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QPainterPath, QFont, QPalette
)
from PyQt6.QtCore import Qt, QRectF, QPointF

from . import constants

if TYPE_CHECKING:
    from .port_item import PortItem
    from .bulk_area_item import BulkAreaItem
    from .generic_node import GenericNode


class BaseNodeUI(QGraphicsItem):
    """
    Base class for node visualization in a node graph.
    
    This class provides the core rendering and port management functionality
    that can be reused across different applications. It handles:
    
    - Visual rendering of nodes (title, body, borders)
    - Port container management (input/output ports dictionary)
    - Basic layout calculations
    - Theme-aware coloring
    - Selection and highlighting
    
    Subclasses should implement application-specific features such as:
    - Port type validation
    - Context menus
    - State persistence
    - Custom interactions
    """
    
    def __init__(self, title: str, width: float = None, title_height: float = None, node_model: Optional[GenericNode] = None):
        """
        Initialize the base node UI.
        
        Args:
            title: Display title for the node
            width: Node width (default from constants.NODE_WIDTH)
            title_height: Title bar height (default from constants.NODE_TITLE_HEIGHT)
            node_model: Optional GenericNode for data model separation
        """
        super().__init__()
        
        # Visual properties
        self.title_text = title
        self._node_width = width if width is not None else constants.NODE_WIDTH
        self._calculated_title_height = title_height if title_height is not None else constants.NODE_TITLE_HEIGHT
        self._bounding_rect = QRectF(0, 0, self._node_width, self._calculated_title_height)
        self._header_rect = QRectF(0, 0, self._node_width, self._calculated_title_height)
        
        # Port containers
        self.input_ports: Dict[str, PortItem] = {}
        self.output_ports: Dict[str, PortItem] = {}
        self.input_area_item: Optional[BulkAreaItem] = None
        self.output_area_item: Optional[BulkAreaItem] = None
        
        # Visual state flags
        self.is_folded = False
        
        # Optional data model (for Model-View separation)
        self.node_model = node_model
        
        # Configure item flags
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        
        # Title text item
        self.title_item = QGraphicsTextItem(title, self)
        font = QFont()
        font.setBold(True)
        self.title_item.setFont(font)
    
    # --- Core Rendering Methods ---
    
    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle for this item."""
        return self._bounding_rect
    
    def get_paint_colors(self, option: QStyleOptionGraphicsItem, is_selected: bool) -> tuple[QColor, QColor, QColor, QColor]:
        """
        Determine colors for painting the node based on theme and selection.
        
        This method can be overridden to provide custom coloring schemes.
        
        Args:
            option: Style option containing palette information
            is_selected: Whether the node is currently selected
            
        Returns:
            Tuple of (body_bg_color, title_bg_color, separator_color, border_color)
        """
        border_color = constants.SELECTION_BORDER_COLOR if is_selected else option.palette.color(QPalette.ColorRole.WindowText)
        
        original_node_body_bg = option.palette.color(QPalette.ColorRole.Base)
        is_light_mode = original_node_body_bg.lightnessF() > 0.7
        
        # Default colors - can be customized by subclasses
        if is_light_mode:
            title_bg_color = QColor(220, 220, 220)
            node_body_bg_color = QColor(240, 240, 240)
            final_separator_color = QColor(192, 192, 192)
        else:
            title_bg_color = option.palette.color(QPalette.ColorRole.Button)
            node_body_bg_color = original_node_body_bg
            final_separator_color = option.palette.color(QPalette.ColorRole.Mid)
        
        return node_body_bg_color, title_bg_color, final_separator_color, border_color
    
    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None):
        """
        Paint the node with title bar and body.
        
        This method renders the visual representation of the node. The actual
        port items are child QGraphicsItems and will paint themselves.
        """
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        is_selected = bool(option.state & QStyle.StateFlag.State_Selected)
        node_body_bg_color, title_bg_color, final_separator_color, border_color = self.get_paint_colors(option, is_selected)
        border_width = 1.5 if is_selected else 1
        
        # Draw base rounded rectangle (border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(border_color, border_width))
        painter.drawRoundedRect(self.boundingRect(), 5, 5)
        
        # Draw title background
        painter.setBrush(title_bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        title_rect = QRectF(0, 0, self.boundingRect().width(), self._calculated_title_height)
        
        # Create clipping path for rounded corners
        clip_path = QPainterPath()
        clip_rect_for_fill = self.boundingRect().adjusted(
            border_width / 2, border_width / 2, -border_width / 2, -border_width / 2
        )
        clip_path.addRoundedRect(clip_rect_for_fill, 5, 5)
        
        # Draw title with clipping
        title_fill_candidate_path = QPainterPath()
        title_fill_candidate_path.addRect(title_rect)
        actual_title_fill_path = clip_path.intersected(title_fill_candidate_path)
        painter.drawPath(actual_title_fill_path)
        
        # Draw node body and separator (only if not folded)
        if not self.is_folded:
            # Fill body area below title
            painter.setBrush(node_body_bg_color)
            painter.setPen(Qt.PenStyle.NoPen)
            body_rect = QRectF(
                0, self._calculated_title_height,
                self.boundingRect().width(),
                self.boundingRect().height() - self._calculated_title_height
            )
            
            body_fill_candidate_path = QPainterPath()
            body_fill_candidate_path.addRect(body_rect)
            actual_body_fill_path = clip_path.intersected(body_fill_candidate_path)
            painter.drawPath(actual_body_fill_path)
            
            # Draw title separator line
            painter.setPen(QPen(final_separator_color, 0.5))
            y_separator = int(self._calculated_title_height)
            painter.drawLine(
                int(border_width), y_separator,
                int(self.boundingRect().width() - border_width), y_separator
            )
    
    # --- Port Management Methods ---
    
    def has_ports(self) -> bool:
        """Check if the node has any ports."""
        return bool(self.input_ports or self.output_ports)
    
    def get_all_ports(self) -> list[PortItem]:
        """Get a list of all ports (input and output)."""
        return list(self.input_ports.values()) + list(self.output_ports.values())
    
    def get_port_count(self) -> tuple[int, int]:
        """
        Get the number of input and output ports.
        
        Returns:
            Tuple of (input_count, output_count)
        """
        return len(self.input_ports), len(self.output_ports)
    
    # --- Utility Methods ---
    
    def bring_to_front(self):
        """Bring this node to the front of other nodes in the scene."""
        if self.scene():
            current_max_z = 0
            for item in self.scene().items():
                if item != self and isinstance(item, BaseNodeUI):
                    current_max_z = max(current_max_z, item.zValue())
            self.setZValue(current_max_z + 1)
    
    def get_header_rect(self) -> QRectF:
        """Get the header/title bar rectangle."""
        return self._header_rect
    
    def update_bounding_rect(self, width: float, height: float):
        """
        Update the node's bounding rectangle.
        
        Args:
            width: New width
            height: New height
        """
        self.prepareGeometryChange()
        self._bounding_rect = QRectF(0, 0, width, height)
        self._header_rect = QRectF(0, 0, width, self._calculated_title_height)
    
    # --- Event Handlers ---
    
    def mousePressEvent(self, event):
        """Handle mouse press events - bring node to front."""
        super().mousePressEvent(event)
        self.bring_to_front()
    
    def mouseDoubleClickEvent(self, event):
        """
        Handle double-click events on the title bar to toggle fold state.
        
        Subclasses can override to provide custom double-click behavior.
        """
        if self._header_rect.contains(event.pos()):
            self.toggle_fold()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
    
    def toggle_fold(self):
        """
        Toggle the folded state of the node.
        
        This base implementation just sets the flag. Subclasses should
        override to handle layout updates and port visibility.
        """
        self.is_folded = not self.is_folded
        self.update()


class NodeColorScheme:
    """
    Helper class to define and manage color schemes for nodes.
    
    This can be used to provide different visual themes or to highlight
    nodes based on their state or type.
    """
    
    def __init__(self, 
                 title_bg_light: QColor = None,
                 title_bg_dark: QColor = None,
                 body_bg_light: QColor = None,
                 body_bg_dark: QColor = None,
                 separator_light: QColor = None,
                 separator_dark: QColor = None):
        """
        Initialize a color scheme.
        
        Args:
            title_bg_light: Title background for light mode
            title_bg_dark: Title background for dark mode
            body_bg_light: Body background for light mode
            body_bg_dark: Body background for dark mode
            separator_light: Separator color for light mode
            separator_dark: Separator color for dark mode
        """
        self.title_bg_light = title_bg_light or QColor(220, 220, 220)
        self.title_bg_dark = title_bg_dark or QColor(80, 80, 80)
        self.body_bg_light = body_bg_light or QColor(240, 240, 240)
        self.body_bg_dark = body_bg_dark or QColor(60, 60, 60)
        self.separator_light = separator_light or QColor(192, 192, 192)
        self.separator_dark = separator_dark or QColor(90, 90, 90)
    
    def get_colors(self, is_light_mode: bool) -> tuple[QColor, QColor, QColor]:
        """
        Get colors for the current theme mode.
        
        Args:
            is_light_mode: Whether light mode is active
            
        Returns:
            Tuple of (title_bg, body_bg, separator)
        """
        if is_light_mode:
            return self.title_bg_light, self.body_bg_light, self.separator_light
        else:
            return self.title_bg_dark, self.body_bg_dark, self.separator_dark


# Pre-defined color schemes that can be used by applications
DEFAULT_SCHEME = NodeColorScheme()

HIGHLIGHTED_SCHEME = NodeColorScheme(
    title_bg_light=QColor(240, 190, 210),
    title_bg_dark=QColor(90, 50, 70),
    body_bg_light=QColor(250, 240, 245),
    body_bg_dark=QColor(70, 60, 65)
)

SPECIAL_SCHEME = NodeColorScheme(
    title_bg_light=QColor(200, 220, 255),
    title_bg_dark=QColor(50, 70, 100),
    body_bg_light=QColor(230, 240, 255),
    body_bg_dark=QColor(45, 55, 70)
)
