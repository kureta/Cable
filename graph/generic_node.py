"""
Generic Node System - Domain-agnostic node abstraction

This module provides a completely generic node system that can perform
arbitrary computations on arbitrary data types. It's decoupled from all
audio/JACK/Pipewire concepts and can be used for:

- Mathematical operations (add, multiply, etc.)
- Data transformations (format conversion, filtering)
- Logic operations (AND, OR, comparisons)
- String operations (concatenation, parsing)
- Custom application-specific functions
"""

from __future__ import annotations
from typing import Any, Optional, Callable, Dict, List
from abc import ABC, abstractmethod

from .generic_port import GenericPort, PortDirection, PortDataType, PortRegistry


class GenericNode(ABC):
    """
    Abstract base class for a generic computational node.
    
    A node has:
    - Input ports (receive data)
    - Output ports (produce data)
    - A compute function (processes inputs -> outputs)
    
    This is a pure data/logic model with no UI code.
    """
    
    def __init__(self, name: str):
        """
        Initialize a generic node.
        
        Args:
            name: Display name for the node
        """
        self.name = name
        self.port_registry = PortRegistry()
        self.metadata: Dict[str, Any] = {}
        self.enabled = True
    
    def add_input_port(self, port: GenericPort) -> bool:
        """
        Add an input port to this node.
        
        Args:
            port: Port to add (must be INPUT direction)
            
        Returns:
            bool: True if added successfully
            
        Raises:
            ValueError: If port is not an input port
        """
        if not port.is_input:
            raise ValueError(f"Port {port.name} is not an input port")
        
        return self.port_registry.register(port)
    
    def add_output_port(self, port: GenericPort) -> bool:
        """
        Add an output port to this node.
        
        Args:
            port: Port to add (must be OUTPUT direction)
            
        Returns:
            bool: True if added successfully
            
        Raises:
            ValueError: If port is not an output port
        """
        if not port.is_output:
            raise ValueError(f"Port {port.name} is not an output port")
        
        return self.port_registry.register(port)
    
    def remove_port(self, port_name: str) -> bool:
        """
        Remove a port from this node.
        
        Args:
            port_name: Name of the port to remove
            
        Returns:
            bool: True if removed successfully
        """
        return self.port_registry.unregister(port_name)
    
    def get_port(self, port_name: str) -> Optional[GenericPort]:
        """Get a port by name."""
        return self.port_registry.get(port_name)
    
    def get_input_ports(self) -> List[GenericPort]:
        """Get all input ports."""
        return self.port_registry.get_all_inputs()
    
    def get_output_ports(self) -> List[GenericPort]:
        """Get all output ports."""
        return self.port_registry.get_all_outputs()
    
    def get_input_values(self) -> Dict[str, Any]:
        """
        Get all input port values as a dictionary.
        
        Returns:
            Dict mapping port names to their current values
        """
        return {port.name: port.get_value() for port in self.get_input_ports()}
    
    def set_output_values(self, values: Dict[str, Any]):
        """
        Set output port values from a dictionary.
        
        Args:
            values: Dict mapping port names to values
        """
        for port_name, value in values.items():
            port = self.get_port(port_name)
            if port and port.is_output:
                port.set_value(value)
    
    def execute(self):
        """
        Execute the node's computation.
        
        This reads input values, calls compute(), and sets output values.
        """
        if not self.enabled:
            return
        
        # Get input values
        inputs = self.get_input_values()
        
        # Perform computation
        outputs = self.compute(inputs)
        
        # Set output values
        if outputs:
            self.set_output_values(outputs)
    
    @abstractmethod
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute output values from input values.
        
        This is the core logic of the node. Subclasses must implement this.
        
        Args:
            inputs: Dictionary of input port names -> values
            
        Returns:
            Dictionary of output port names -> computed values
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


# Example node implementations

class AddNode(GenericNode):
    """Node that adds two numbers."""
    
    def __init__(self, name: str = "Add"):
        super().__init__(name)
        
        # Create input ports
        from .generic_port import create_number_port
        self.add_input_port(create_number_port("a", PortDirection.INPUT, 0.0))
        self.add_input_port(create_number_port("b", PortDirection.INPUT, 0.0))
        
        # Create output port
        self.add_output_port(create_number_port("result", PortDirection.OUTPUT))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Add the two input values."""
        a = inputs.get("a", 0)
        b = inputs.get("b", 0)
        return {"result": a + b}


class MultiplyNode(GenericNode):
    """Node that multiplies two numbers."""
    
    def __init__(self, name: str = "Multiply"):
        super().__init__(name)
        
        from .generic_port import create_number_port
        self.add_input_port(create_number_port("a", PortDirection.INPUT, 1.0))
        self.add_input_port(create_number_port("b", PortDirection.INPUT, 1.0))
        self.add_output_port(create_number_port("result", PortDirection.OUTPUT))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Multiply the two input values."""
        a = inputs.get("a", 1)
        b = inputs.get("b", 1)
        return {"result": a * b}


class StringConcatNode(GenericNode):
    """Node that concatenates two strings."""
    
    def __init__(self, name: str = "Concat"):
        super().__init__(name)
        
        from .generic_port import create_string_port
        self.add_input_port(create_string_port("str1", PortDirection.INPUT, ""))
        self.add_input_port(create_string_port("str2", PortDirection.INPUT, ""))
        self.add_output_port(create_string_port("result", PortDirection.OUTPUT))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Concatenate the two input strings."""
        str1 = inputs.get("str1", "")
        str2 = inputs.get("str2", "")
        return {"result": str1 + str2}


class CompareNode(GenericNode):
    """Node that compares two numbers."""
    
    def __init__(self, name: str = "Compare"):
        super().__init__(name)
        
        from .generic_port import create_number_port, create_boolean_port
        self.add_input_port(create_number_port("a", PortDirection.INPUT, 0.0))
        self.add_input_port(create_number_port("b", PortDirection.INPUT, 0.0))
        self.add_output_port(create_boolean_port("greater", PortDirection.OUTPUT))
        self.add_output_port(create_boolean_port("equal", PortDirection.OUTPUT))
        self.add_output_port(create_boolean_port("less", PortDirection.OUTPUT))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Compare the two input values."""
        a = inputs.get("a", 0)
        b = inputs.get("b", 0)
        return {
            "greater": a > b,
            "equal": a == b,
            "less": a < b
        }


class ConstantNode(GenericNode):
    """Node that outputs a constant value."""
    
    def __init__(self, name: str = "Constant", value: Any = 0.0, data_type: PortDataType = PortDataType.NUMBER):
        super().__init__(name)
        
        from .generic_port import GenericPort
        self.constant_value = value
        self.add_output_port(GenericPort("value", PortDirection.OUTPUT, data_type, value))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Output the constant value."""
        return {"value": self.constant_value}


class PrintNode(GenericNode):
    """Node that prints its input (useful for debugging)."""
    
    def __init__(self, name: str = "Print"):
        super().__init__(name)
        
        from .generic_port import create_any_port
        self.add_input_port(create_any_port("value", PortDirection.INPUT))
        self.add_output_port(create_any_port("value", PortDirection.OUTPUT))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Print the input value and pass it through."""
        value = inputs.get("value")
        print(f"{self.name}: {value}")
        return {"value": value}


class LambdaNode(GenericNode):
    """
    Node that applies a custom lambda function.
    
    This is a flexible node that can perform any computation
    defined by a Python function.
    """
    
    def __init__(self, name: str, function: Callable, input_names: List[str], output_names: List[str]):
        """
        Initialize a lambda node.
        
        Args:
            name: Node name
            function: Callable that takes inputs dict and returns outputs dict
            input_names: Names of input ports
            output_names: Names of output ports
        """
        super().__init__(name)
        self.function = function
        
        from .generic_port import create_any_port
        for input_name in input_names:
            self.add_input_port(create_any_port(input_name, PortDirection.INPUT))
        
        for output_name in output_names:
            self.add_output_port(create_any_port(output_name, PortDirection.OUTPUT))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Apply the custom function."""
        return self.function(inputs)


# Node factory for easy node creation

class NodeFactory:
    """Factory for creating nodes of various types."""
    
    # Registry of node types
    _node_types: Dict[str, type] = {
        "add": AddNode,
        "multiply": MultiplyNode,
        "concat": StringConcatNode,
        "compare": CompareNode,
        "constant": ConstantNode,
        "print": PrintNode,
    }
    
    @classmethod
    def register_node_type(cls, type_name: str, node_class: type):
        """
        Register a custom node type.
        
        Args:
            type_name: Identifier for the node type
            node_class: Class that inherits from GenericNode
        """
        cls._node_types[type_name] = node_class
    
    @classmethod
    def create(cls, type_name: str, name: str = None, **kwargs) -> GenericNode:
        """
        Create a node of the specified type.
        
        Args:
            type_name: Type of node to create
            name: Optional custom name for the node
            **kwargs: Additional arguments for node constructor
            
        Returns:
            GenericNode instance
            
        Raises:
            ValueError: If type_name is not registered
        """
        if type_name not in cls._node_types:
            raise ValueError(f"Unknown node type: {type_name}")
        
        node_class = cls._node_types[type_name]
        
        if name:
            return node_class(name=name, **kwargs)
        else:
            return node_class(**kwargs)
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get a list of all available node types."""
        return list(cls._node_types.keys())
