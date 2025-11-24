#!/usr/bin/env python3
"""
Headless test for the demo node graph logic

This verifies that the node execution logic works without needing PyQt6.
"""

import sys
sys.path.insert(0, '/home/runner/work/Cable/Cable')

from graph.generic_node import AddNode, MultiplyNode, PrintNode, ConstantNode
from graph.generic_port import GenericPort


def test_node_graph():
    """Test a simple node graph execution"""
    print("=" * 60)
    print("Testing Node Graph Execution Logic")
    print("=" * 60)
    
    # Create nodes
    const1 = ConstantNode("Constant 1", value=5.0)
    const2 = ConstantNode("Constant 2", value=3.0)
    const3 = ConstantNode("Constant 3", value=2.0)
    add_node = AddNode("Add")
    mult_node = MultiplyNode("Multiply")
    print_node = PrintNode("Result")
    
    # Get ports
    const1_out = const1.get_port("value")
    const2_out = const2.get_port("value")
    const3_out = const3.get_port("value")
    
    add_in_a = add_node.get_port("a")
    add_in_b = add_node.get_port("b")
    add_out = add_node.get_port("result")
    
    mult_in_a = mult_node.get_port("a")
    mult_in_b = mult_node.get_port("b")
    mult_out = mult_node.get_port("result")
    
    print_in = print_node.get_port("value")
    
    # Connect: const1 + const2, then * const3
    const1_out.connect(add_in_a)
    const2_out.connect(add_in_b)
    add_out.connect(mult_in_a)
    const3_out.connect(mult_in_b)
    mult_out.connect(print_in)
    
    print("\nGraph structure:")
    print("  Constant 1 (5.0) ─┐")
    print("                     ├─> Add ─┐")
    print("  Constant 2 (3.0) ─┘         │")
    print("                              ├─> Multiply ─> Print")
    print("  Constant 3 (2.0) ───────────┘")
    print()
    
    # Execute nodes in order
    print("Executing nodes...")
    
    # Execute constants
    const1.execute()
    const2.execute()
    const3.execute()
    print(f"  Constant 1 output: {const1_out.get_value()}")
    print(f"  Constant 2 output: {const2_out.get_value()}")
    print(f"  Constant 3 output: {const3_out.get_value()}")
    
    # Transfer values to add node
    add_in_a.set_value(const1_out.get_value())
    add_in_b.set_value(const2_out.get_value())
    add_node.execute()
    print(f"  Add output: {add_out.get_value()}")
    
    # Transfer values to multiply node
    mult_in_a.set_value(add_out.get_value())
    mult_in_b.set_value(const3_out.get_value())
    mult_node.execute()
    print(f"  Multiply output: {mult_out.get_value()}")
    
    # Transfer to print node
    print_in.set_value(mult_out.get_value())
    print("\n" + "=" * 60)
    print_node.execute()
    print("=" * 60)
    
    # Verify result
    expected = (5.0 + 3.0) * 2.0
    actual = mult_out.get_value()
    
    print(f"\nExpected result: {expected}")
    print(f"Actual result: {actual}")
    
    if abs(expected - actual) < 0.001:
        print("✓ Test PASSED")
        return True
    else:
        print("✗ Test FAILED")
        return False


if __name__ == "__main__":
    success = test_node_graph()
    sys.exit(0 if success else 1)
