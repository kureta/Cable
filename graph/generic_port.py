"""
Generic Port System - Domain-agnostic port abstraction

This module provides a generic port system that can be used for any type of
data flow: numbers, strings, audio streams, video frames, objects, etc.

It completely decouples ports from audio/JACK concepts and makes them work
for arbitrary data types and computations.
"""

from __future__ import annotations
from typing import Any, Optional, Callable, TYPE_CHECKING
from enum import Enum, auto

if TYPE_CHECKING:
    pass


class PortDirection(Enum):
    """Direction of data flow for a port."""
    INPUT = auto()   # Port receives data
    OUTPUT = auto()  # Port sends data


class PortDataType(Enum):
    """
    Generic data types that can flow through ports.
    
    This is extensible - applications can define their own types.
    """
    ANY = auto()         # Accept any data type
    NUMBER = auto()      # Numeric values (int, float)
    STRING = auto()      # Text strings
    BOOLEAN = auto()     # True/False
    OBJECT = auto()      # Arbitrary Python objects
    LIST = auto()        # Lists/arrays
    DICT = auto()        # Dictionaries/maps
    
    # Audio-specific (optional, for backwards compatibility)
    AUDIO_STREAM = auto()
    MIDI_STREAM = auto()
    
    # Custom types can be added by applications
    CUSTOM = auto()


class GenericPort:
    """
    Generic port that can carry any type of data.
    
    This is a pure data model - no UI, no framework-specific code.
    It represents a connection point for data flow between nodes.
    
    Attributes:
        name: Unique identifier for the port
        direction: INPUT or OUTPUT
        data_type: What kind of data this port accepts/produces
        value: Current value held by the port (for inputs)
        connected_to: List of ports this port is connected to
        metadata: Application-specific additional data
    """
    
    def __init__(self, 
                 name: str,
                 direction: PortDirection,
                 data_type: PortDataType = PortDataType.ANY,
                 default_value: Any = None,
                 metadata: dict = None):
        """
        Initialize a generic port.
        
        Args:
            name: Unique name/identifier
            direction: INPUT or OUTPUT
            data_type: Type of data this port handles
            default_value: Default value for input ports
            metadata: Optional dictionary for application-specific data
        """
        self.name = name
        self.direction = direction
        self.data_type = data_type
        self.value = default_value
        self.connected_to: list[GenericPort] = []
        self.metadata = metadata or {}
        
        # Optional validation and transformation functions
        self.validator: Optional[Callable[[Any], bool]] = None
        self.transformer: Optional[Callable[[Any], Any]] = None
    
    @property
    def is_input(self) -> bool:
        """Check if this is an input port."""
        return self.direction == PortDirection.INPUT
    
    @property
    def is_output(self) -> bool:
        """Check if this is an output port."""
        return self.direction == PortDirection.OUTPUT
    
    @property
    def is_connected(self) -> bool:
        """Check if this port has any connections."""
        return len(self.connected_to) > 0
    
    def set_value(self, value: Any, validate: bool = True):
        """
        Set the port's value.
        
        Args:
            value: New value to set
            validate: Whether to run validation (default True)
            
        Raises:
            ValueError: If validation fails
        """
        if validate and self.validator and not self.validator(value):
            raise ValueError(f"Value {value} failed validation for port {self.name}")
        
        # Apply transformation if defined
        if self.transformer:
            value = self.transformer(value)
        
        self.value = value
    
    def get_value(self) -> Any:
        """Get the current port value."""
        return self.value
    
    def can_connect_to(self, other: GenericPort) -> bool:
        """
        Check if this port can connect to another port.
        
        Rules:
        - Input can only connect to Output (and vice versa)
        - Data types must be compatible
        
        Args:
            other: The other port to check
            
        Returns:
            bool: True if connection is allowed
        """
        # Check direction compatibility
        if self.direction == other.direction:
            return False  # Can't connect input to input or output to output
        
        # Check data type compatibility
        if self.data_type == PortDataType.ANY or other.data_type == PortDataType.ANY:
            return True  # ANY type is compatible with everything
        
        return self.data_type == other.data_type
    
    def connect(self, other: GenericPort):
        """
        Connect this port to another port.
        
        Args:
            other: Port to connect to
            
        Raises:
            ValueError: If connection is not allowed
        """
        if not self.can_connect_to(other):
            raise ValueError(f"Cannot connect {self.name} ({self.direction}, {self.data_type}) "
                           f"to {other.name} ({other.direction}, {other.data_type})")
        
        if other not in self.connected_to:
            self.connected_to.append(other)
        
        if self not in other.connected_to:
            other.connected_to.append(self)
    
    def disconnect(self, other: GenericPort):
        """
        Disconnect this port from another port.
        
        Args:
            other: Port to disconnect from
        """
        if other in self.connected_to:
            self.connected_to.remove(other)
        
        if self in other.connected_to:
            other.connected_to.remove(self)
    
    def disconnect_all(self):
        """Disconnect from all connected ports."""
        for other in list(self.connected_to):
            self.disconnect(other)
    
    def __repr__(self) -> str:
        return f"GenericPort({self.name}, {self.direction.name}, {self.data_type.name})"


class PortRegistry:
    """
    Registry for managing ports in a node graph.
    
    This is useful for lookups, validation, and serialization.
    """
    
    def __init__(self):
        self.ports: dict[str, GenericPort] = {}
    
    def register(self, port: GenericPort) -> bool:
        """
        Register a port.
        
        Args:
            port: Port to register
            
        Returns:
            bool: True if registered, False if already exists
        """
        if port.name in self.ports:
            return False
        
        self.ports[port.name] = port
        return True
    
    def unregister(self, port_name: str) -> bool:
        """
        Unregister a port.
        
        Args:
            port_name: Name of port to unregister
            
        Returns:
            bool: True if unregistered, False if not found
        """
        if port_name in self.ports:
            port = self.ports.pop(port_name)
            port.disconnect_all()
            return True
        return False
    
    def get(self, port_name: str) -> Optional[GenericPort]:
        """Get a port by name."""
        return self.ports.get(port_name)
    
    def get_all_inputs(self) -> list[GenericPort]:
        """Get all input ports."""
        return [p for p in self.ports.values() if p.is_input]
    
    def get_all_outputs(self) -> list[GenericPort]:
        """Get all output ports."""
        return [p for p in self.ports.values() if p.is_output]
    
    def clear(self):
        """Remove all ports."""
        for port in list(self.ports.values()):
            port.disconnect_all()
        self.ports.clear()


# Convenience functions for creating common port types

def create_number_port(name: str, direction: PortDirection, default: float = 0.0) -> GenericPort:
    """Create a port for numeric values."""
    port = GenericPort(name, direction, PortDataType.NUMBER, default)
    port.validator = lambda x: isinstance(x, (int, float))
    return port


def create_string_port(name: str, direction: PortDirection, default: str = "") -> GenericPort:
    """Create a port for string values."""
    port = GenericPort(name, direction, PortDataType.STRING, default)
    port.validator = lambda x: isinstance(x, str)
    return port


def create_boolean_port(name: str, direction: PortDirection, default: bool = False) -> GenericPort:
    """Create a port for boolean values."""
    port = GenericPort(name, direction, PortDataType.BOOLEAN, default)
    port.validator = lambda x: isinstance(x, bool)
    return port


def create_any_port(name: str, direction: PortDirection) -> GenericPort:
    """Create a port that accepts any data type."""
    return GenericPort(name, direction, PortDataType.ANY)
