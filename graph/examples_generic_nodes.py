"""
Generic Node System Examples

This file demonstrates how to use the generic node system for
various purposes beyond audio/JACK.
"""

from graph.generic_node import (
    GenericNode, AddNode, MultiplyNode, StringConcatNode,
    CompareNode, ConstantNode, PrintNode, LambdaNode, NodeFactory
)
from graph.generic_port import (
    GenericPort, PortDirection, PortDataType,
    create_number_port, create_string_port
)


def example_1_basic_math():
    """Example 1: Simple mathematical computation"""
    print("\n=== Example 1: Basic Math ===")
    
    # Create nodes
    add_node = AddNode("Add Two Numbers")
    multiply_node = MultiplyNode("Multiply Result")
    constant = ConstantNode("Ten", value=10.0)
    print_result = PrintNode("Show Result")
    
    # Set up computation: (5 + 3) * 10
    add_node.get_port("a").set_value(5)
    add_node.get_port("b").set_value(3)
    
    # Execute the add node
    add_node.execute()
    add_result = add_node.get_port("result").get_value()
    print(f"5 + 3 = {add_result}")
    
    # Connect result to multiply
    multiply_node.get_port("a").set_value(add_result)
    multiply_node.get_port("b").set_value(10)
    multiply_node.execute()
    
    multiply_result = multiply_node.get_port("result").get_value()
    print(f"{add_result} * 10 = {multiply_result}")


def example_2_string_operations():
    """Example 2: String manipulation"""
    print("\n=== Example 2: String Operations ===")
    
    # Create string nodes
    concat1 = StringConcatNode("First Concat")
    concat2 = StringConcatNode("Second Concat")
    
    # Build: "Hello" + " " + "World" + "!"
    concat1.get_port("str1").set_value("Hello")
    concat1.get_port("str2").set_value(" World")
    concat1.execute()
    
    first_result = concat1.get_port("result").get_value()
    print(f"First concatenation: '{first_result}'")
    
    concat2.get_port("str1").set_value(first_result)
    concat2.get_port("str2").set_value("!")
    concat2.execute()
    
    final_result = concat2.get_port("result").get_value()
    print(f"Final result: '{final_result}'")


def example_3_comparisons():
    """Example 3: Comparison operations"""
    print("\n=== Example 3: Comparisons ===")
    
    compare = CompareNode("Compare Values")
    
    # Test different values
    test_cases = [
        (5, 3),
        (3, 5),
        (4, 4)
    ]
    
    for a, b in test_cases:
        compare.get_port("a").set_value(a)
        compare.get_port("b").set_value(b)
        compare.execute()
        
        greater = compare.get_port("greater").get_value()
        equal = compare.get_port("equal").get_value()
        less = compare.get_port("less").get_value()
        
        print(f"{a} vs {b}: greater={greater}, equal={equal}, less={less}")


def example_4_custom_lambda():
    """Example 4: Custom lambda node"""
    print("\n=== Example 4: Custom Lambda Node ===")
    
    # Create a node that computes the average of two numbers
    def average_function(inputs):
        a = inputs.get("num1", 0)
        b = inputs.get("num2", 0)
        return {"average": (a + b) / 2}
    
    avg_node = LambdaNode(
        "Average",
        function=average_function,
        input_names=["num1", "num2"],
        output_names=["average"]
    )
    
    # Test it
    avg_node.get_port("num1").set_value(10)
    avg_node.get_port("num2").set_value(20)
    avg_node.execute()
    
    result = avg_node.get_port("average").get_value()
    print(f"Average of 10 and 20: {result}")


def example_5_node_factory():
    """Example 5: Using the node factory"""
    print("\n=== Example 5: Node Factory ===")
    
    print(f"Available node types: {NodeFactory.get_available_types()}")
    
    # Create nodes using factory
    add = NodeFactory.create("add", "Factory Add")
    mult = NodeFactory.create("multiply", "Factory Multiply")
    
    # Compute: (7 + 3) * 2
    add.get_port("a").set_value(7)
    add.get_port("b").set_value(3)
    add.execute()
    
    result1 = add.get_port("result").get_value()
    print(f"7 + 3 = {result1}")
    
    mult.get_port("a").set_value(result1)
    mult.get_port("b").set_value(2)
    mult.execute()
    
    result2 = mult.get_port("result").get_value()
    print(f"{result1} * 2 = {result2}")


def example_6_port_connections():
    """Example 6: Port connections and data flow"""
    print("\n=== Example 6: Port Connections ===")
    
    # Create a chain: Constant -> Add -> Print
    const5 = ConstantNode("Five", value=5.0)
    const3 = ConstantNode("Three", value=3.0)
    adder = AddNode("Sum")
    printer = PrintNode("Result")
    
    # Get ports
    const5_out = const5.get_port("value")
    const3_out = const3.get_port("value")
    add_in_a = adder.get_port("a")
    add_in_b = adder.get_port("b")
    add_out = adder.get_port("result")
    print_in = printer.get_port("value")
    
    # Connect ports
    const5_out.connect(add_in_a)
    const3_out.connect(add_in_b)
    add_out.connect(print_in)
    
    print(f"Connections established:")
    print(f"  {const5.name} -> {adder.name}")
    print(f"  {const3.name} -> {adder.name}")
    print(f"  {adder.name} -> {printer.name}")
    
    # Execute the graph
    const5.execute()
    const3.execute()
    
    # Transfer values through connections
    add_in_a.set_value(const5_out.get_value())
    add_in_b.set_value(const3_out.get_value())
    
    adder.execute()
    
    # Transfer to printer
    print_in.set_value(add_out.get_value())
    printer.execute()


def example_7_custom_node():
    """Example 7: Creating a custom node class"""
    print("\n=== Example 7: Custom Node ===")
    
    class PowerNode(GenericNode):
        """Node that raises a number to a power"""
        
        def __init__(self, name="Power"):
            super().__init__(name)
            self.add_input_port(create_number_port("base", PortDirection.INPUT, 2.0))
            self.add_input_port(create_number_port("exponent", PortDirection.INPUT, 2.0))
            self.add_output_port(create_number_port("result", PortDirection.OUTPUT))
        
        def compute(self, inputs):
            base = inputs.get("base", 1)
            exponent = inputs.get("exponent", 1)
            return {"result": base ** exponent}
    
    # Register with factory
    NodeFactory.register_node_type("power", PowerNode)
    
    # Use it
    power = NodeFactory.create("power", "Square")
    power.get_port("base").set_value(5)
    power.get_port("exponent").set_value(2)
    power.execute()
    
    result = power.get_port("result").get_value()
    print(f"5^2 = {result}")
    
    # Try cube
    power.get_port("base").set_value(3)
    power.get_port("exponent").set_value(3)
    power.execute()
    
    result = power.get_port("result").get_value()
    print(f"3^3 = {result}")


def example_8_data_validation():
    """Example 8: Port validation"""
    print("\n=== Example 8: Port Validation ===")
    
    # Create a port with validation
    positive_port = create_number_port("positive_number", PortDirection.INPUT, 1.0)
    positive_port.validator = lambda x: x > 0
    
    # Try valid value
    try:
        positive_port.set_value(5.0)
        print(f"Set valid value: {positive_port.get_value()}")
    except ValueError as e:
        print(f"Validation failed: {e}")
    
    # Try invalid value
    try:
        positive_port.set_value(-3.0)
        print(f"Set invalid value: {positive_port.get_value()}")
    except ValueError as e:
        print(f"Validation failed (expected): {e}")


def run_all_examples():
    """Run all examples"""
    print("=" * 60)
    print("GENERIC NODE SYSTEM EXAMPLES")
    print("=" * 60)
    
    example_1_basic_math()
    example_2_string_operations()
    example_3_comparisons()
    example_4_custom_lambda()
    example_5_node_factory()
    example_6_port_connections()
    example_7_custom_node()
    example_8_data_validation()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_examples()
