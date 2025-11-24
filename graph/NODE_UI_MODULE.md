# Reusable Node UI Module

## Overview

The Node UI module provides a set of reusable components for creating node-based graphical interfaces. It separates core visualization and port management logic from application-specific business logic, making it easy to build custom node-graph editors.

## Architecture

The module is organized into several components:

### 1. **node_ui_base.py** - Base Node Visualization
- `BaseNodeUI`: Core node rendering class with title, body, and theming
- `NodeColorScheme`: Helper for managing color themes
- Pre-defined color schemes (DEFAULT, HIGHLIGHTED, SPECIAL)

### 2. **node_ui_ports.py** - Port Management
- `PortManagementMixin`: Reusable port add/remove logic
- `PortConnectionHelper`: Utilities for working with port connections

### 3. **Existing Components** (used as-is)
- `port_item.py`: Individual port visualization
- `bulk_area_item.py`: Bulk connection area visualization
- `constants.py`: Visual constants and styling

## Usage

### Basic Node Implementation

```python
from graph.node_ui_base import BaseNodeUI
from graph.node_ui_ports import PortManagementMixin
from graph.port_item import PortItem
from graph.bulk_area_item import BulkAreaItem

class MyNode(PortManagementMixin, BaseNodeUI):
    """Custom node implementation"""
    
    def __init__(self, title, **kwargs):
        super().__init__(title)
        # Add custom initialization
    
    def create_port_item(self, port_name, port_obj, is_input):
        """Create a port item - required by PortManagementMixin"""
        return PortItem(self, port_name, port_obj, is_input)
    
    def create_bulk_area_item(self, is_input):
        """Create bulk area - required by PortManagementMixin"""
        return BulkAreaItem(self, is_input)
    
    def layout_ports(self):
        """Layout logic - required by PortManagementMixin"""
        # Implement your layout strategy
        pass

# Usage
node = MyNode("Audio Input")
node.add_port_to_node("port1", port_obj, is_input=True)
```

### Custom Colors

```python
from graph.node_ui_base import NodeColorScheme

# Define a custom color scheme
my_scheme = NodeColorScheme(
    title_bg_light=QColor(200, 255, 200),
    title_bg_dark=QColor(50, 100, 50),
    body_bg_light=QColor(240, 255, 240),
    body_bg_dark=QColor(40, 60, 40)
)

class MyNode(BaseNodeUI):
    def get_paint_colors(self, option, is_selected):
        """Override to use custom colors"""
        border_color = constants.SELECTION_BORDER_COLOR if is_selected else option.palette.color(QPalette.ColorRole.WindowText)
        
        is_light_mode = option.palette.color(QPalette.ColorRole.Base).lightnessF() > 0.7
        title_bg, body_bg, separator = my_scheme.get_colors(is_light_mode)
        
        return body_bg, title_bg, separator, border_color
```

### Extending for Application Logic

The base classes provide visualization. Applications add specific features:

```python
class AudioNodeItem(PortManagementMixin, BaseNodeUI):
    """Node with audio-specific features"""
    
    def __init__(self, client_name, jack_handler, config_manager):
        super().__init__(client_name)
        self.jack_handler = jack_handler
        self.config_manager = config_manager
        # Add audio-specific state
    
    def contextMenuEvent(self, event):
        """Add custom context menu"""
        menu = QMenu()
        menu.addAction("Disconnect All", self._disconnect_all)
        menu.addAction("Mute", self._toggle_mute)
        menu.exec(event.screenPos())
    
    def _disconnect_all(self):
        """Application-specific disconnect logic"""
        # Use jack_handler to disconnect
        pass
```

## Design Principles

### Separation of Concerns

1. **BaseNodeUI**: Pure visualization (painting, layout, selection)
2. **PortManagementMixin**: Generic port operations (add, remove, query)
3. **Application Subclass**: Business logic (JACK, config, menus)

### Extensibility

- Override `get_paint_colors()` for custom appearance
- Override `toggle_fold()` for custom fold behavior
- Override event handlers for custom interactions
- Implement mixin requirements for port functionality

### Reusability

The module can be used for:
- Audio routing applications (like Cable)
- MIDI matrix editors
- Visual programming environments
- Data flow diagrams
- Any node-based UI

## Integration with Cable

The existing `NodeItem` class in Cable has been kept intact to maintain backward compatibility. It contains:

- All Cable-specific features (JACK integration, virtual sinks, unify toggle)
- Split/fold handlers
- Configuration persistence
- Context menus with Cable-specific actions

To gradually adopt the reusable module:

1. New features can extend `BaseNodeUI` + `PortManagementMixin`
2. Common code can be factored out to the base classes
3. Existing `NodeItem` can eventually delegate to base classes

## API Reference

### BaseNodeUI

**Constructor:**
```python
BaseNodeUI(title: str, width: float = None, title_height: float = None)
```

**Key Methods:**
- `get_paint_colors(option, is_selected) -> tuple[QColor, ...]`: Get colors for rendering
- `paint(painter, option, widget)`: Render the node
- `toggle_fold()`: Toggle folded state
- `bring_to_front()`: Z-order management
- `has_ports() -> bool`: Check if node has ports
- `get_all_ports() -> list`: Get all port items

### PortManagementMixin

**Port Operations:**
- `add_port_to_node(port_name, port_obj, is_input) -> bool`: Add a port
- `remove_port_from_node(port_name) -> bool`: Remove a port
- `clear_all_ports()`: Remove all ports
- `get_port(port_name) -> PortItem | None`: Get specific port
- `has_port(port_name) -> bool`: Check if port exists

**Port Queries:**
- `get_input_port_names() -> list[str]`: All input port names
- `get_output_port_names() -> list[str]`: All output port names
- `get_all_port_names() -> list[str]`: All port names

**Required Implementations:**
- `create_port_item(port_name, port_obj, is_input) -> PortItem`
- `create_bulk_area_item(is_input) -> BulkAreaItem`
- `layout_ports()`: Recalculate layout

### PortConnectionHelper

**Static Methods:**
- `get_connected_ports(port_item) -> list[PortItem]`: Get connected ports
- `has_connections(port_item) -> bool`: Check for connections
- `get_connection_count(port_item) -> int`: Count connections
- `disconnect_all(port_item)`: Disconnect all connections

## Future Enhancements

Potential improvements to the reusable module:

1. **Layout Strategies**: Abstract layout algorithms as pluggable strategies
2. **Port Filtering**: Built-in support for port filtering/grouping
3. **Animation**: Smooth transitions for fold/unfold
4. **Accessibility**: Better keyboard navigation and screen reader support
5. **Serialization**: Generic save/load for node state
6. **Undo/Redo**: Framework for node operations

## Contributing

When adding features:

1. **Keep base classes generic**: Don't add application-specific dependencies
2. **Use mixins for optional features**: Allow cherry-picking functionality
3. **Document clearly**: Update this README with usage examples
4. **Maintain backward compatibility**: Existing code should continue to work

## License

This module is part of Cable and follows the same license as the main project.
