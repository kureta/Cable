"""
Port Management Mixin for Node UI

This module provides reusable port management functionality that can be
mixed into node UI classes. It handles the common operations of adding,
removing, and organizing ports.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any, Optional

if TYPE_CHECKING:
    from .port_item import PortItem
    from .bulk_area_item import BulkAreaItem


class PortManagementMixin:
    """
    Mixin class providing port management functionality for nodes.
    
    This mixin expects the host class to have:
    - input_ports: Dict[str, PortItem]
    - output_ports: Dict[str, PortItem]
    - input_area_item: Optional[BulkAreaItem]
    - output_area_item: Optional[BulkAreaItem]
    - scene() method
    
    And to provide:
    - create_port_item(port_name, port_obj, is_input) -> PortItem
    - create_bulk_area_item(is_input) -> BulkAreaItem
    - layout_ports() method
    """
    
    def add_port_to_node(self, port_name: str, port_obj: Any, is_input: bool) -> bool:
        """
        Add a port to the node.
        
        This is a generic port addition method that:
        1. Checks if the port already exists
        2. Creates the bulk area item if needed
        3. Creates the port item
        4. Triggers layout if in a scene
        
        Args:
            port_name: Unique identifier for the port
            port_obj: Port data object (application-specific)
            is_input: True for input port, False for output port
            
        Returns:
            bool: True if port was added, False if it already existed
        """
        port_map = self.input_ports if is_input else self.output_ports
        
        # Check if port already exists
        if port_name in port_map:
            return False
        
        # Create bulk area item if this is the first port of its type
        if is_input and not self.input_area_item:
            self.input_area_item = self.create_bulk_area_item(is_input=True)
        elif not is_input and not self.output_area_item:
            self.output_area_item = self.create_bulk_area_item(is_input=False)
        
        # Create the port item
        port_item = self.create_port_item(port_name, port_obj, is_input)
        port_map[port_name] = port_item
        
        # Trigger layout if in scene
        if hasattr(self, 'scene') and self.scene():
            self.layout_ports()
        
        return True
    
    def remove_port_from_node(self, port_name: str) -> bool:
        """
        Remove a port from the node.
        
        This method:
        1. Finds the port in input or output ports
        2. Cleans up any connections
        3. Removes the port item from the scene
        4. Removes the bulk area if no ports remain
        5. Triggers layout
        
        Args:
            port_name: Identifier of the port to remove
            
        Returns:
            bool: True if port was removed, False if not found
        """
        port_item = None
        
        # Find the port
        if port_name in self.input_ports:
            port_item = self.input_ports.pop(port_name)
        elif port_name in self.output_ports:
            port_item = self.output_ports.pop(port_name)
        
        if not port_item:
            return False
        
        # Clean up connections
        if hasattr(port_item, 'connections'):
            for conn in list(port_item.connections):
                if hasattr(conn, 'destroy'):
                    conn.destroy()
        
        # Remove port item from scene
        if hasattr(self, 'scene') and self.scene():
            self.scene().removeItem(port_item)
        
        # Remove bulk area if no ports of this type remain
        if port_item.is_input and not self.input_ports and self.input_area_item:
            if hasattr(self, 'scene') and self.scene():
                self.scene().removeItem(self.input_area_item)
            self.input_area_item = None
        elif not port_item.is_input and not self.output_ports and self.output_area_item:
            if hasattr(self, 'scene') and self.scene():
                self.scene().removeItem(self.output_area_item)
            self.output_area_item = None
        
        # Trigger layout if in scene
        if hasattr(self, 'scene') and self.scene():
            self.layout_ports()
        
        return True
    
    def clear_all_ports(self):
        """
        Remove all ports from the node.
        
        This is useful when resetting or reinitializing a node.
        """
        # Remove all output ports
        for port_name in list(self.output_ports.keys()):
            self.remove_port_from_node(port_name)
        
        # Remove all input ports
        for port_name in list(self.input_ports.keys()):
            self.remove_port_from_node(port_name)
    
    def get_port(self, port_name: str) -> Optional[PortItem]:
        """
        Get a port by name from either input or output ports.
        
        Args:
            port_name: Name of the port to retrieve
            
        Returns:
            PortItem if found, None otherwise
        """
        return self.input_ports.get(port_name) or self.output_ports.get(port_name)
    
    def has_port(self, port_name: str) -> bool:
        """
        Check if a port exists.
        
        Args:
            port_name: Name of the port to check
            
        Returns:
            bool: True if port exists
        """
        return port_name in self.input_ports or port_name in self.output_ports
    
    def get_input_port_names(self) -> list[str]:
        """Get a list of all input port names."""
        return list(self.input_ports.keys())
    
    def get_output_port_names(self) -> list[str]:
        """Get a list of all output port names."""
        return list(self.output_ports.keys())
    
    def get_all_port_names(self) -> list[str]:
        """Get a list of all port names (input and output)."""
        return self.get_input_port_names() + self.get_output_port_names()
    
    # These methods must be implemented by the class using this mixin
    
    def create_port_item(self, port_name: str, port_obj: Any, is_input: bool) -> PortItem:
        """
        Create a port item instance.
        
        This method must be implemented by the class using this mixin.
        
        Args:
            port_name: Unique identifier for the port
            port_obj: Port data object
            is_input: True for input, False for output
            
        Returns:
            PortItem: The created port item
        """
        raise NotImplementedError("Subclass must implement create_port_item")
    
    def create_bulk_area_item(self, is_input: bool) -> BulkAreaItem:
        """
        Create a bulk connection area item.
        
        This method must be implemented by the class using this mixin.
        
        Args:
            is_input: True for input area, False for output area
            
        Returns:
            BulkAreaItem: The created bulk area item
        """
        raise NotImplementedError("Subclass must implement create_bulk_area_item")
    
    def layout_ports(self):
        """
        Recalculate and apply port layout.
        
        This method must be implemented by the class using this mixin.
        """
        raise NotImplementedError("Subclass must implement layout_ports")


class PortConnectionHelper:
    """
    Helper class for managing port connections.
    
    This provides utility methods for working with connected ports,
    which can be useful for various node operations.
    """
    
    @staticmethod
    def get_connected_ports(port_item: PortItem) -> list[PortItem]:
        """
        Get all ports connected to the given port.
        
        Args:
            port_item: The port to check
            
        Returns:
            List of connected port items
        """
        connected = []
        if hasattr(port_item, 'connections'):
            for conn in port_item.connections:
                if hasattr(conn, 'source_port') and hasattr(conn, 'dest_port'):
                    other_port = conn.dest_port if conn.source_port == port_item else conn.source_port
                    if other_port:
                        connected.append(other_port)
        return connected
    
    @staticmethod
    def has_connections(port_item: PortItem) -> bool:
        """
        Check if a port has any connections.
        
        Args:
            port_item: The port to check
            
        Returns:
            bool: True if the port has connections
        """
        return hasattr(port_item, 'connections') and len(port_item.connections) > 0
    
    @staticmethod
    def get_connection_count(port_item: PortItem) -> int:
        """
        Get the number of connections for a port.
        
        Args:
            port_item: The port to check
            
        Returns:
            int: Number of connections
        """
        if hasattr(port_item, 'connections'):
            return len(port_item.connections)
        return 0
    
    @staticmethod
    def disconnect_all(port_item: PortItem):
        """
        Disconnect all connections from a port.
        
        Args:
            port_item: The port to disconnect
        """
        if hasattr(port_item, 'connections'):
            for conn in list(port_item.connections):
                if hasattr(conn, 'destroy'):
                    conn.destroy()
