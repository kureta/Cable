# Node Graph GUI Demo Application

## Overview

This is a complete example GUI application demonstrating the generic node system. It provides a visual, interactive node graph editor where you can:

- Create and connect nodes
- Edit constant values
- Execute the graph
- See results in real-time

## Features

### Nodes Included

1. **Addition Node** - Adds two numbers (inputs: `a`, `b` → output: `result`)
2. **Multiplication Node** - Multiplies two numbers (inputs: `a`, `b` → output: `result`)
3. **Print Node** - Displays the result (input: `value` → output: `value`)
4. **Constant Nodes** (4x) - Editable number boxes with single output

### Interactions

- **Move Nodes**: Click and drag nodes to reposition them
- **Create Connections**: Click and drag from an output port (right side) to an input port (left side)
- **Edit Constants**: Double-click on a constant node to edit its value
- **Delete**: Select items and press Delete key to remove nodes or connections
- **Execute**: Click "Execute Graph" button to run the computation
- **Zoom/Pan**: Mouse wheel to zoom, middle-click drag to pan

## Running the Application

### Prerequisites

```bash
pip install PyQt6
```

### Launch

```bash
python3 graph/demo_node_gui.py
```

Or from the repository root:

```bash
cd /home/runner/work/Cable/Cable
python3 graph/demo_node_gui.py
```

## Testing Without GUI

To test the node execution logic without PyQt6:

```bash
python3 graph/test_demo_logic.py
```

This verifies that the computational graph works correctly.

## Application Structure

```
┌─────────────────────────────────────────────────────────┐
│  Node Graph GUI Demo                              [_][□][x]│
├─────────────────────────────────────────────────────────┤
│ [Execute Graph] [Clear Output]            Instructions  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────┐         ┌─────────┐        ┌─────────┐   │
│   │Const 1  │ ─────── │  Add    │ ────── │Multiply │   │
│   │  5.00   │         │         │        │         │   │
│   └─────────┘    ┌─── │         │    ┌── │         │   │
│                  │    └─────────┘    │   └─────────┘   │
│   ┌─────────┐   │                   │         │        │
│   │Const 2  │ ──┘                   │         │        │
│   │  3.00   │                       │         │        │
│   └─────────┘                       │         │        │
│                                     │         ↓        │
│   ┌─────────┐                       │   ┌─────────┐   │
│   │Const 3  │ ──────────────────────┘   │ Print   │   │
│   │  2.00   │                           │ Result  │   │
│   └─────────┘                           └─────────┘   │
│                                                          │
│   ┌─────────┐                                           │
│   │Const 4  │                                           │
│   │ 10.00   │                                           │
│   └─────────┘                                           │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ Output:                                                  │
│ Result: 16.0                                             │
│ (5.0 + 3.0) * 2.0 = 16.0                                │
└─────────────────────────────────────────────────────────┘
```

## Example Usage

### Default Setup

The application starts with 4 constant nodes, an addition node, a multiplication node, and a print node. No connections are made initially.

### Example Calculation 1: (5 + 3) * 2

1. Connect Constant 1 (5.0) → Add input `a`
2. Connect Constant 2 (3.0) → Add input `b`
3. Connect Add output `result` → Multiply input `a`
4. Connect Constant 3 (2.0) → Multiply input `b`
5. Connect Multiply output `result` → Print input `value`
6. Click "Execute Graph"
7. Result: `16.0` appears in the output area

### Example Calculation 2: Custom Values

1. Double-click Constant 1, change to `10.0`
2. Double-click Constant 2, change to `20.0`
3. Create connections as above
4. Click "Execute Graph"
5. Result: `(10.0 + 20.0) * 2.0 = 60.0`

## Code Architecture

### Main Components

#### `VisualPort` (Lines 58-95)
- Graphical representation of a port
- Handles hover effects
- Manages connections
- Displays port name

#### `Connection` (Lines 98-129)
- Visual line between ports
- Updates position when nodes move
- Connects data model ports
- Can be destroyed with Delete key

#### `VisualNode` (Lines 132-266)
- Graphical representation of a node
- Displays node title
- Shows current value for constants
- Handles double-click to edit constants
- Updates connections when moved

#### `NodeGraphScene` (Lines 269-351)
- Manages all nodes and connections
- Handles mouse interactions for creating connections
- Implements Delete key functionality
- Provides temporary connection line during dragging

#### `NodeGraphView` (Lines 354-375)
- View with zoom and pan
- Mouse wheel zoom
- Drag to pan
- Dark background

#### `NodeGraphWindow` (Lines 378-503)
- Main application window
- Toolbar with Execute and Clear buttons
- Instructions display
- Output text area
- Graph execution logic

### Execution Logic

The `execute_graph()` method (lines 448-496) implements a simple execution strategy:

1. Iterate through all nodes multiple times (up to 10 passes)
2. For each node, check if all input dependencies are satisfied
3. If ready, transfer values from connected ports and execute
4. Capture output from Print nodes
5. Display results in the output area

**Note**: This is a simplified execution model. A production system would use topological sorting for optimal execution order.

## Extending the Demo

### Adding New Node Types

1. Create a new node class inheriting from `GenericNode`
2. Implement the `compute()` method
3. Register with `NodeFactory` if desired
4. Create instances with `VisualNode(YourNode("Name"), x, y)`

Example:

```python
class DivideNode(GenericNode):
    def __init__(self, name="Divide"):
        super().__init__(name)
        from graph.generic_port import create_number_port, PortDirection
        self.add_input_port(create_number_port("dividend", PortDirection.INPUT))
        self.add_input_port(create_number_port("divisor", PortDirection.INPUT, 1.0))
        self.add_output_port(create_number_port("result", PortDirection.OUTPUT))
    
    def compute(self, inputs):
        dividend = inputs.get("dividend", 0)
        divisor = inputs.get("divisor", 1)
        if divisor == 0:
            return {"result": float('inf')}
        return {"result": dividend / divisor}

# Add to scene
divide_node = VisualNode(DivideNode("Divide"), 0, 100)
scene.addItem(divide_node)
```

### Adding Node Persistence

To save/load graphs:

1. Serialize node positions and types
2. Serialize connections (source node + port → dest node + port)
3. Serialize constant values
4. Store as JSON
5. Reconstruct on load

## Limitations

### Current Implementation

- **Simple execution**: No topological sorting (works for acyclic graphs)
- **No undo/redo**: Delete operations are permanent
- **No error handling UI**: Errors appear in output, not as visual feedback
- **No node palette**: Nodes are pre-created, can't add new ones dynamically
- **No validation feedback**: Invalid connections fail silently

### Potential Enhancements

1. **Node Palette**: Drag-and-drop to create nodes
2. **Topological Sorting**: Optimal execution order
3. **Visual Feedback**: Highlight nodes during execution
4. **Error Display**: Show errors on nodes
5. **Undo/Redo**: Command pattern implementation
6. **Save/Load**: JSON persistence
7. **Copy/Paste**: Duplicate node subgraphs
8. **Multi-selection**: Select and move multiple nodes
9. **Alignment Tools**: Snap to grid, align nodes
10. **Connection Routing**: Bezier curves, avoid overlaps

## Technical Details

### Dependencies

- **PyQt6**: GUI framework
- **graph.generic_node**: Node computation models
- **graph.generic_port**: Port data models

### Color Scheme

- **Background**: Dark gray (#282832)
- **Nodes**: Blue-gray (#3c3c50)
- **Selected**: Lighter blue-gray with cyan border
- **Ports**: Blue (#649fff)
- **Connections**: Light blue (#5096dc)
- **Text**: White/light gray

### Performance

- Handles dozens of nodes easily
- Connection updates are O(n) per node move
- Graph execution is O(n*m) where n=nodes, m=max iterations

## License

Part of the Cable project. See main LICENSE file.

## Questions?

This demo showcases the generic node system's capabilities. For more information on the underlying node system, see:

- `graph/NODE_UI_MODULE.md` - API documentation
- `graph/IMPLEMENTATION_SUMMARY.md` - Architecture overview
- `graph/examples_generic_nodes.py` - Headless examples
