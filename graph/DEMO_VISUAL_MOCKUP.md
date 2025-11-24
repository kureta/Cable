# Visual Mockup of the Node Graph GUI Demo

## Application Screenshot Description

### Window Layout

The application window consists of three main areas:

1. **Top Toolbar** (height: ~40px)
   - "Execute Graph" button (blue, left side)
   - "Clear Output" button (gray, left side)
   - Help text (right side): "Drag nodes to move | Drag from output to input to connect | Double-click constants to edit | Delete key to remove"

2. **Main Canvas** (expandable, dark background #28282E)
   - Interactive node graph area
   - Nodes appear as rounded rectangles
   - Connections shown as lines between ports
   - Zoomable and pannable

3. **Output Panel** (height: ~100px, bottom)
   - Dark background (#2A2A2A)
   - Green monospace text (#00FF00)
   - Shows execution results

### Node Visual Design

Each node is a rounded rectangle (180x120px) with:

#### Structure
```
┌─────────────────────┐
│  ●  Node Title   ●  │  ← Title bar (dark blue-gray)
├─────────────────────┤
│                     │
│ ●  port_in   12.34  │  ← Left: input ports (blue circles)
│                     │     Center: value display (for constants)
│ ●  port_out      ●  │     Right: output ports (blue circles)
│                     │
└─────────────────────┘
```

#### Colors
- **Body**: #3C3C50 (blue-gray)
- **Selected**: #46465A with cyan border (#64B4FF)
- **Title bar**: #323246 (darker blue-gray)
- **Ports**: #649BFF (bright blue circles)
- **Port hover**: #96C8FF (lighter blue)

### Initial Node Layout

```
  Y=-200  ┌─────────────┐
          │ Constant 1  │
          │    5.00   ● │───┐
          └─────────────┘   │
                            │    ┌─────────────┐
  Y=-50   ┌─────────────┐   └───→│ ●  Add    ● │───┐
          │ Constant 2  │        │ ●        ● │   │
          │    3.00   ● │───────→│             │   │
          └─────────────┘        └─────────────┘   │
                                                    │
                                                    │    ┌─────────────┐
  Y=100   ┌─────────────┐                          └───→│ ● Multiply● │───┐
          │ Constant 3  │                               │ ●        ● │   │
          │    2.00   ● │──────────────────────────────→│             │   │
          └─────────────┘                               └─────────────┘   │
                                                                           │
                                                                           │
  Y=250   ┌─────────────┐                                                 │
          │ Constant 4  │                                                 │
          │   10.00   ● │                                                 │
          └─────────────┘                                                 │
                                                                           │
                                X=500                                      │
                                ┌─────────────┐                           │
                                │ ● Print     │←──────────────────────────┘
                                │ ●  Result   │
                                │             │
                                └─────────────┘

          X=-400      X=-100       X=200
```

### Connection Visual

Connections are drawn as lines:
- **Color**: #5096DC (light blue)
- **Width**: 2px
- **Style**: Solid when connected, dashed during dragging
- **Hover**: Slightly thicker and brighter

During connection creation:
- Temporary dashed line follows mouse cursor
- Line goes from source port to cursor position
- Line disappears if released on invalid target

### Interactive States

#### Node States
1. **Normal**: Blue-gray body, thin border
2. **Selected**: Lighter body, cyan border (2px)
3. **Dragging**: Follows mouse, connections update in real-time
4. **Hover**: Slight highlight (for future enhancement)

#### Port States
1. **Normal**: Blue circle
2. **Hover**: Light blue circle, slightly larger
3. **Connected**: Same as normal (connection line indicates state)
4. **During drag**: Source port stays highlighted

#### Connection States
1. **Normal**: Solid light blue line
2. **Selected**: Thicker cyan line (for future enhancement)
3. **Creating**: Dashed line following cursor

### Double-Click Edit Dialog

When double-clicking a constant node:

```
┌───────────────────────────────┐
│ Edit Constant 1           [X] │
├───────────────────────────────┤
│                               │
│  Value: [     5.00      ] ↕  │  ← Spin box with +/- buttons
│                               │
│         [ OK ] [ Cancel ]     │
│                               │
└───────────────────────────────┘
```

### Output Panel Examples

#### After Execution
```
┌──────────────────────────────────────────────┐
│ Output:                                      │
│ Result: 16.0                                 │
└──────────────────────────────────────────────┘
```

#### With Error
```
┌──────────────────────────────────────────────┐
│ Output:                                      │
│ Error executing Divide: division by zero     │
└──────────────────────────────────────────────┘
```

#### No Connections
```
┌──────────────────────────────────────────────┐
│ Output:                                      │
│ No output produced. Connect nodes and try    │
│ again.                                       │
└──────────────────────────────────────────────┘
```

## Example Workflows

### Workflow 1: Basic Calculation

1. **Initial State**: 7 nodes visible, no connections
2. **Action**: Drag from Constant 1 output to Add input `a`
   - Blue dashed line follows mouse
   - Port highlights on hover
3. **Result**: Solid blue line connects nodes
4. **Repeat**: Connect remaining nodes
5. **Execute**: Click "Execute Graph" button
6. **Output**: "Result: 16.0" appears in output panel

### Workflow 2: Edit Value

1. **Action**: Double-click Constant 1 node
2. **Dialog**: Edit dialog appears
3. **Action**: Change value to 10.00
4. **Result**: Value display updates to "10.00"
5. **Execute**: Click "Execute Graph"
6. **Output**: New result based on updated value

### Workflow 3: Delete Connection

1. **Action**: Click on connection line
2. **Result**: Line becomes selected (cyan)
3. **Action**: Press Delete key
4. **Result**: Line disappears, ports disconnected

### Workflow 4: Delete Node

1. **Action**: Click on node
2. **Result**: Node border turns cyan
3. **Action**: Press Delete key
4. **Result**: Node and all connected lines disappear

## Color Palette Reference

```
Background:     #28282E  ████  Dark gray-blue
Node body:      #3C3C50  ████  Blue-gray
Node selected:  #46465A  ████  Lighter blue-gray
Title bar:      #323246  ████  Dark blue-gray
Port normal:    #649BFF  ████  Bright blue
Port hover:     #96C8FF  ████  Light blue
Connection:     #5096DC  ████  Medium blue
Selection:      #64B4FF  ████  Cyan
Text:           #FFFFFF  ████  White
Text dim:       #888888  ████  Gray
Output bg:      #2A2A2A  ████  Very dark gray
Output text:    #00FF00  ████  Bright green
Error text:     #FF4444  ████  Bright red
```

## Keyboard Shortcuts

- **Delete**: Remove selected node or connection
- **Mouse wheel**: Zoom in/out
- **Middle-click + drag**: Pan view
- **Double-click node**: Edit constant value (for constant nodes)

## Mouse Interactions

- **Left-click node**: Select
- **Left-drag node**: Move
- **Left-click port**: Start connection
- **Left-drag from port**: Create connection
- **Left-release on port**: Complete connection
- **Left-release on empty**: Cancel connection
- **Middle-drag**: Pan view
- **Wheel**: Zoom

## Future Visual Enhancements

1. **Bezier curve connections**: Smooth curved lines instead of straight
2. **Port type colors**: Different colors for number/string/boolean ports
3. **Node execution animation**: Highlight nodes as they execute
4. **Mini-map**: Small overview of entire graph
5. **Grid background**: Optional snap-to-grid
6. **Node shadows**: Depth effect for better visual hierarchy
7. **Connection labels**: Show data values on connections
8. **Port value tooltips**: Hover to see current port value
9. **Node categories**: Color-code nodes by function (math, logic, I/O)
10. **Theme switcher**: Light/dark mode toggle
