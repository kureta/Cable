# Reusable Node UI Module

## Overview

The Node UI module provides a **completely generic, domain-agnostic** framework for creating node-based graphical interfaces. It is fully decoupled from audio, JACK, Pipewire, or any specific domain, making it suitable for:

- **Mathematical computations** (add, multiply, etc.)
- **Data transformations** (string manipulation, format conversion)
- **Logic operations** (comparisons, boolean algebra)
- **Visual programming** (custom data flow)
- **Audio/MIDI routing** (as one specific use case through adapters)
- **Any node-graph application**

The architecture follows **Model-View separation**: the core node logic is independent of the UI, and adapters bridge to specific domains.

## Architecture

The module is organized in layers:

### Layer 1: Generic Data Model (Domain-Agnostic)

#### **generic_port.py** - Universal Port System
- `GenericPort`: Pure data model for ports (no UI, no domain knowledge)
- `PortDirection`: Enum for INPUT/OUTPUT
- `PortDataType`: Extensible data types (NUMBER, STRING, BOOLEAN, etc.)
- `PortRegistry`: Port collection management
- Helper functions: `create_number_port()`, `create_string_port()`, etc.

#### **generic_node.py** - Universal Node System
- `GenericNode`: Abstract base for computational nodes
- Built-in node types:
  - `AddNode`, `MultiplyNode` - Math operations
  - `StringConcatNode` - String operations
  - `CompareNode` - Comparisons
  - `ConstantNode` - Constant values
  - `PrintNode` - Debug output
  - `LambdaNode` - Custom functions
- `NodeFactory`: Factory for creating nodes

### Layer 2: UI Visualization (Domain-Agnostic)

#### **node_ui_base.py** - Base Node Visualization
- `BaseNodeUI`: Core node rendering (title, body, theming)
- `NodeColorScheme`: Color theme management
- Pre-defined color schemes (DEFAULT, HIGHLIGHTED, SPECIAL)
- Supports optional Model-View linking

#### **node_ui_ports.py** - Port Management UI
- `PortManagementMixin`: Reusable port add/remove logic
- `PortConnectionHelper`: Utilities for port connections

#### **Existing Components** (Reusable)
- `port_item.py`: Individual port visualization
- `bulk_area_item.py`: Bulk connection area visualization
- `constants.py`: Visual constants and styling

### Layer 3: Domain Adapters (Optional)

#### **audio_node_adapter.py** - Audio/JACK Bridge
- `AudioPort`, `MIDIPort`: Wrappers for JACK ports
- `AudioNode`: Node subclass with JACK integration
- `PortAdapter`: Converter between generic and JACK ports
- `PortFactory`: Create ports from JACK clients

*Note: This layer is only needed if you're building audio applications.*

## Quick Start

### Running the Examples

```bash
cd /home/runner/work/Cable/Cable
python3 -m graph.examples_generic_nodes
```

This will run 8 examples demonstrating:
1. Basic math operations
2. String manipulation
3. Comparison operations
4. Custom lambda functions
5. Node factory usage
6. Port connections
7. Creating custom node classes
8. Data validation

### Creating Your First Node

```python
# 1. Import the system
from graph.generic_node import GenericNode, NodeFactory
from graph.generic_port import create_number_port, PortDirection

# 2. Define your node
class SquareNode(GenericNode):
    def __init__(self, name="Square"):
        super().__init__(name)
        self.add_input_port(create_number_port("input", PortDirection.INPUT))
        self.add_output_port(create_number_port("output", PortDirection.OUTPUT))
    
    def compute(self, inputs):
        value = inputs.get("input", 0)
        return {"output": value ** 2}

# 3. Use it
square = SquareNode()
square.get_port("input").set_value(5)
square.execute()
print(square.get_port("output").get_value())  # Output: 25

# 4. Register for reuse
NodeFactory.register_node_type("square", SquareNode)
```

### Three-Minute Tutorial

```python
# Import what you need
from graph.generic_node import AddNode, MultiplyNode
from graph.generic_port import GenericPort, PortDirection, PortDataType

# Create nodes
add = AddNode()
mult = MultiplyNode()

# Set values
add.get_port("a").set_value(3)
add.get_port("b").set_value(4)

# Compute
add.execute()  # 3 + 4 = 7

# Chain nodes
result = add.get_port("result").get_value()
mult.get_port("a").set_value(result)
mult.get_port("b").set_value(2)
mult.execute()  # 7 * 2 = 14

print(mult.get_port("result").get_value())  # 14
```

### Example 1: Pure Computation (No Audio)

```python
from graph.generic_node import AddNode, MultiplyNode

# Create nodes for computation
add = AddNode("Sum")
multiply = MultiplyNode("Product")

# Set inputs
add.get_port("a").set_value(5)
add.get_port("b").set_value(3)

# Execute computation
add.execute()
result = add.get_port("result").get_value()
print(f"5 + 3 = {result}")  # Output: 8

# Chain computations
multiply.get_port("a").set_value(result)
multiply.get_port("b").set_value(2)
multiply.execute()
print(f"8 * 2 = {multiply.get_port('result').get_value()}")  # Output: 16
```

### Example 2: Custom Computation Node

```python
from graph.generic_node import GenericNode
from graph.generic_port import create_number_port, PortDirection

class AverageNode(GenericNode):
    """Node that computes average of inputs"""
    
    def __init__(self, name="Average"):
        super().__init__(name)
        self.add_input_port(create_number_port("a", PortDirection.INPUT))
        self.add_input_port(create_number_port("b", PortDirection.INPUT))
        self.add_output_port(create_number_port("result", PortDirection.OUTPUT))
    
    def compute(self, inputs):
        a = inputs.get("a", 0)
        b = inputs.get("b", 0)
        return {"result": (a + b) / 2}

# Use it
avg = AverageNode()
avg.get_port("a").set_value(10)
avg.get_port("b").set_value(20)
avg.execute()
print(avg.get_port("result").get_value())  # Output: 15.0
```

### Example 3: String Processing

```python
from graph.generic_node import StringConcatNode

concat = StringConcatNode("Join")
concat.get_port("str1").set_value("Hello")
concat.get_port("str2").set_value(" World")
concat.execute()
print(concat.get_port("result").get_value())  # Output: "Hello World"
```

### Example 4: Using the Node Factory

```python
from graph.generic_node import NodeFactory, LambdaNode

# List available node types
print(NodeFactory.get_available_types())
# Output: ['add', 'multiply', 'concat', 'compare', 'constant', 'print']

# Create nodes using factory
add = NodeFactory.create("add", "My Adder")
mult = NodeFactory.create("multiply")

# Register custom node type
class PowerNode(GenericNode):
    # ... implementation ...

NodeFactory.register_node_type("power", PowerNode)
power = NodeFactory.create("power", "Square")
```

### Example 5: Building a UI Node (Generic)

```python
from graph.node_ui_base import BaseNodeUI
from graph.node_ui_ports import PortManagementMixin
from graph.generic_node import AddNode

class ComputationalNodeUI(PortManagementMixin, BaseNodeUI):
    """UI for any computational node"""
    
    def __init__(self, node_model: GenericNode):
        super().__init__(node_model.name, node_model=node_model)
        self.sync_ports_from_model()
    
    def sync_ports_from_model(self):
        """Create UI ports from the model's ports"""
        for port in self.node_model.get_input_ports():
            # Create UI representation of port
            # (Implementation depends on your port_item.py)
            pass
    
    def execute_node(self):
        """Execute the underlying computation"""
        self.node_model.execute()
        self.update_output_displays()

# Usage
add_model = AddNode("Sum")
add_ui = ComputationalNodeUI(add_model)
# add_ui can now be added to a QGraphicsScene
```

### Example 6: Audio Routing (Domain-Specific)

```python
from graph.audio_node_adapter import AudioNode, AudioPort, PortAdapter

# Create an audio node (bridges to JACK)
audio_node = AudioNode("MyAudioApp", jack_handler)

# Add ports from JACK
for jack_port in jack_handler.get_ports():
    generic_port = PortAdapter.from_jack_port(jack_port)
    if generic_port.is_input:
        audio_node.add_input_port(generic_port)
    else:
        audio_node.add_output_port(generic_port)

# The audio node now works with the generic system
# while maintaining JACK integration
```

## Key Features

### Complete Domain Independence

The generic node system has **zero dependencies** on:
- Audio processing libraries
- JACK/Pipewire
- MIDI
- Any specific data domain

It works with:
- Numbers (int, float)
- Strings
- Booleans
- Lists, dictionaries
- Arbitrary Python objects
- Custom data types

### Model-View Separation

```
┌─────────────────────────────────────┐
│   Generic Node (Data Model)        │
│   - Ports (data holders)            │
│   - Compute logic                   │
│   - No UI code                      │
└─────────────────────────────────────┘
              ↕ (optional link)
┌─────────────────────────────────────┐
│   BaseNodeUI (View)                 │
│   - Visual rendering                │
│   - User interaction                │
│   - No computation logic            │
└─────────────────────────────────────┘
```

You can:
1. Use `GenericNode` alone for headless computation
2. Use `BaseNodeUI` alone for visualization
3. Link them together with `node_model` parameter
4. Keep them completely separate

### Type Safety and Validation

```python
from graph.generic_port import create_number_port, PortDirection

# Create port with validation
port = create_number_port("value", PortDirection.INPUT, default=0.0)
port.validator = lambda x: x >= 0  # Only accept non-negative

port.set_value(5)    # OK
port.set_value(-1)   # Raises ValueError
```

### Extensible Data Types

```python
from graph.generic_port import PortDataType

# Define custom data type
class CustomDataType(PortDataType):
    IMAGE = auto()
    VIDEO = auto()
    NEURAL_NETWORK = auto()

# Use in ports
image_port = GenericPort("input", PortDirection.INPUT, CustomDataType.IMAGE)
```

## Integration with Cable

The existing `NodeItem` class in Cable remains **unchanged** for backward compatibility. It contains all Cable-specific features:

- JACK/Pipewire integration
- Virtual sink management
- Split/fold handlers
- Configuration persistence
- Audio-specific context menus

### Migration Path (Optional)

To gradually adopt the generic system in Cable:

#### Option 1: Keep Existing (Recommended for Now)
- Current `NodeItem` continues to work as-is
- Generic system available for new features
- No breaking changes

#### Option 2: Refactor Over Time
```python
# Future: NodeItem could delegate to base classes
class NodeItem(PortManagementMixin, BaseNodeUI):
    def __init__(self, client_name, jack_handler, config_manager):
        # Use generic system for UI
        super().__init__(client_name)
        
        # Add Cable-specific features
        self.jack_handler = jack_handler
        self.config_manager = config_manager
        self.fold_handler = NodeFoldHandler(self)
        self.split_handler = NodeSplitHandler(self)
        # ... etc
```

#### Option 3: Use Adapter Pattern
```python
from graph.audio_node_adapter import AudioNode, PortAdapter

# Create generic node from JACK client
audio_node = AudioNode(client_name, jack_handler)

# Sync ports from JACK
for jack_port in jack_handler.get_ports_for_client(client_name):
    generic_port = PortAdapter.from_jack_port(jack_port)
    audio_node.add_input_port(generic_port) if generic_port.is_input else audio_node.add_output_port(generic_port)

# Link to UI
node_ui = BaseNodeUI(client_name, node_model=audio_node)
```

### Why This Design?

1. **No Breaking Changes**: Existing Cable code untouched
2. **Future Flexibility**: Can migrate incrementally
3. **Reusability**: Generic system usable in other projects
4. **Testability**: Pure computation nodes easy to test
5. **Extensibility**: Easy to add new node types

## Files Created

### Core Generic System (Domain-Agnostic)
- `graph/generic_port.py` - Universal port abstraction (287 lines)
- `graph/generic_node.py` - Universal node system with examples (418 lines)
- `graph/examples_generic_nodes.py` - Runnable examples (252 lines)

### UI Base Classes (Domain-Agnostic)
- `graph/node_ui_base.py` - Base visualization (updated with model support)
- `graph/node_ui_ports.py` - Port management mixin

### Domain Adapters (Optional)
- `graph/audio_node_adapter.py` - Bridge to JACK/audio (316 lines)

### Documentation
- `graph/NODE_UI_MODULE.md` - Comprehensive guide (updated)

### Total
**~1,500 lines of new, reusable, domain-agnostic code** that works with any data type.

## Testing the Generic System

Since there's no existing test infrastructure, here's manual verification:

```bash
# Test computation nodes
python3 -m graph.examples_generic_nodes

# Should output results from 8 examples including:
# - Math operations (addition, multiplication)
# - String concatenation
# - Comparisons
# - Custom lambda functions
# - Node factory usage
# - Port connections
# - Custom node classes
# - Data validation
```

## API Reference

### GenericPort

**Constructor:**
```python
GenericPort(name: str, direction: PortDirection, 
            data_type: PortDataType = ANY,
            default_value: Any = None,
            metadata: dict = None)
```

**Properties:**
- `is_input: bool` - Check if input port
- `is_output: bool` - Check if output port  
- `is_connected: bool` - Check if has connections

**Methods:**
- `set_value(value, validate=True)` - Set port value
- `get_value() -> Any` - Get port value
- `can_connect_to(other) -> bool` - Check connection compatibility
- `connect(other)` - Connect to another port
- `disconnect(other)` - Disconnect from port
- `disconnect_all()` - Disconnect from all ports

### GenericNode

**Constructor:**
```python
GenericNode(name: str)
```

**Methods:**
- `add_input_port(port) -> bool` - Add input port
- `add_output_port(port) -> bool` - Add output port
- `remove_port(port_name) -> bool` - Remove port
- `get_port(port_name) -> GenericPort | None` - Get port by name
- `get_input_ports() -> list` - Get all input ports
- `get_output_ports() -> list` - Get all output ports
- `execute()` - Execute the node computation
- `compute(inputs: dict) -> dict` - **Abstract** - implement in subclasses

### Built-in Nodes

- `AddNode` - Adds two numbers
- `MultiplyNode` - Multiplies two numbers
- `StringConcatNode` - Concatenates strings
- `CompareNode` - Compares two numbers
- `ConstantNode` - Outputs a constant
- `PrintNode` - Prints value (debugging)
- `LambdaNode` - Custom function node

### NodeFactory

**Methods:**
- `create(type_name, name=None, **kwargs) -> GenericNode` - Create node
- `register_node_type(type_name, node_class)` - Register custom type
- `get_available_types() -> list` - List all registered types

### BaseNodeUI

**Constructor:**
```python
BaseNodeUI(title: str, width: float = None, 
           title_height: float = None,
           node_model: GenericNode = None)
```

**Key Methods:**
- `get_paint_colors(option, is_selected)` - Get colors for rendering
- `paint(painter, option, widget)` - Render the node
- `toggle_fold()` - Toggle folded state
- `bring_to_front()` - Z-order management
- `has_ports() -> bool` - Check if has ports
- `get_all_ports() -> list` - Get all port items

### PortManagementMixin

**Port Operations:**
- `add_port_to_node(port_name, port_obj, is_input) -> bool`
- `remove_port_from_node(port_name) -> bool`
- `clear_all_ports()`
- `get_port(port_name) -> PortItem | None`
- `has_port(port_name) -> bool`

**Port Queries:**
- `get_input_port_names() -> list[str]`
- `get_output_port_names() -> list[str]`
- `get_all_port_names() -> list[str]`

**Required Implementations:**
- `create_port_item(port_name, port_obj, is_input) -> PortItem`
- `create_bulk_area_item(is_input) -> BulkAreaItem`
- `layout_ports()`

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
