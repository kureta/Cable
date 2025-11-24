"""
Audio Node Adapter - Bridge between generic nodes and audio/JACK system

This module provides adapters that connect the generic node system
to audio-specific concepts like JACK ports, audio streams, etc.

It demonstrates how to use the generic node system for a specific
domain while keeping the core system decoupled.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, TYPE_CHECKING

from .generic_node import GenericNode
from .generic_port import GenericPort, PortDirection, PortDataType

if TYPE_CHECKING:
    pass  # JACK types would be imported here


class AudioPort(GenericPort):
    """
    Specialized port for audio data that wraps a JACK port.
    
    This adapter allows JACK ports to work with the generic port system.
    """
    
    def __init__(self, jack_port: Any, name: str, direction: PortDirection):
        """
        Initialize an audio port.
        
        Args:
            jack_port: The underlying JACK port object
            name: Port name
            direction: INPUT or OUTPUT
        """
        super().__init__(
            name=name,
            direction=direction,
            data_type=PortDataType.AUDIO_STREAM
        )
        
        self.jack_port = jack_port
        self.shortname = getattr(jack_port, 'shortname', name)
        self.is_audio = True
        self.is_midi = False
        
        # Store JACK-specific properties in metadata
        self.metadata['jack_port'] = jack_port
        self.metadata['port_type'] = 'audio'


class MIDIPort(GenericPort):
    """
    Specialized port for MIDI data that wraps a JACK MIDI port.
    """
    
    def __init__(self, jack_port: Any, name: str, direction: PortDirection):
        """
        Initialize a MIDI port.
        
        Args:
            jack_port: The underlying JACK MIDI port object
            name: Port name
            direction: INPUT or OUTPUT
        """
        super().__init__(
            name=name,
            direction=direction,
            data_type=PortDataType.MIDI_STREAM
        )
        
        self.jack_port = jack_port
        self.shortname = getattr(jack_port, 'shortname', name)
        self.is_audio = False
        self.is_midi = True
        
        # Store JACK-specific properties in metadata
        self.metadata['jack_port'] = jack_port
        self.metadata['port_type'] = 'midi'


class AudioNode(GenericNode):
    """
    Specialized node for audio processing that integrates with JACK.
    
    This demonstrates how to extend GenericNode for a specific domain.
    """
    
    def __init__(self, client_name: str, jack_handler: Any = None):
        """
        Initialize an audio node.
        
        Args:
            client_name: Name of the JACK client
            jack_handler: Optional JACK handler for port management
        """
        super().__init__(client_name)
        
        self.client_name = client_name
        self.jack_handler = jack_handler
        
        # Audio-specific metadata
        self.metadata['type'] = 'audio'
        self.metadata['jack_client'] = client_name
    
    def add_audio_port(self, jack_port: Any, is_input: bool) -> bool:
        """
        Add an audio port from a JACK port.
        
        Args:
            jack_port: JACK port object
            is_input: True for input, False for output
            
        Returns:
            bool: True if added successfully
        """
        direction = PortDirection.INPUT if is_input else PortDirection.OUTPUT
        port_name = getattr(jack_port, 'name', str(jack_port))
        
        audio_port = AudioPort(jack_port, port_name, direction)
        
        if is_input:
            return self.add_input_port(audio_port)
        else:
            return self.add_output_port(audio_port)
    
    def add_midi_port(self, jack_port: Any, is_input: bool) -> bool:
        """
        Add a MIDI port from a JACK MIDI port.
        
        Args:
            jack_port: JACK MIDI port object
            is_input: True for input, False for output
            
        Returns:
            bool: True if added successfully
        """
        direction = PortDirection.INPUT if is_input else PortDirection.OUTPUT
        port_name = getattr(jack_port, 'name', str(jack_port))
        
        midi_port = MIDIPort(jack_port, port_name, direction)
        
        if is_input:
            return self.add_input_port(midi_port)
        else:
            return self.add_output_port(midi_port)
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audio nodes typically don't perform computation in Python.
        
        The actual audio processing happens in JACK. This node just
        represents the connection topology.
        """
        # For pure routing nodes, no computation needed
        # Audio processing happens in the JACK audio thread
        return {}
    
    def update_from_jack(self):
        """
        Update this node's ports from the current JACK state.
        
        This would query JACK for current ports and update accordingly.
        """
        if not self.jack_handler:
            return
        
        # This is where you'd sync with JACK
        # Implementation depends on the JACK handler API
        pass


class PortAdapter:
    """
    Adapter to convert between generic ports and application-specific ports.
    
    This is useful when you need to bridge between the generic system
    and existing application code.
    """
    
    @staticmethod
    def from_jack_port(jack_port: Any) -> GenericPort:
        """
        Create a generic port from a JACK port.
        
        Args:
            jack_port: JACK port object
            
        Returns:
            GenericPort (AudioPort or MIDIPort)
        """
        port_name = getattr(jack_port, 'name', str(jack_port))
        is_input = getattr(jack_port, 'is_input', False)
        direction = PortDirection.INPUT if is_input else PortDirection.OUTPUT
        
        # Determine if it's MIDI or audio
        is_midi = getattr(jack_port, 'is_midi', False)
        
        if is_midi:
            return MIDIPort(jack_port, port_name, direction)
        else:
            return AudioPort(jack_port, port_name, direction)
    
    @staticmethod
    def to_jack_port(generic_port: GenericPort) -> Optional[Any]:
        """
        Extract the JACK port from a generic port.
        
        Args:
            generic_port: Generic port (should be AudioPort or MIDIPort)
            
        Returns:
            JACK port object if available, None otherwise
        """
        if isinstance(generic_port, (AudioPort, MIDIPort)):
            return generic_port.jack_port
        
        # Check metadata
        return generic_port.metadata.get('jack_port')


class PortFactory:
    """
    Factory for creating ports based on application requirements.
    
    This provides a convenient way to create ports for different scenarios.
    """
    
    @staticmethod
    def create_audio_ports_from_jack_client(client_name: str, jack_handler: Any) -> Dict[str, GenericPort]:
        """
        Create all ports for a JACK client.
        
        Args:
            client_name: Name of the JACK client
            jack_handler: JACK handler to query ports
            
        Returns:
            Dict mapping port names to GenericPort objects
        """
        ports = {}
        
        if not jack_handler:
            return ports
        
        # This would query JACK and create ports
        # Implementation depends on jack_handler API
        # Example:
        # all_jack_ports = jack_handler.get_ports()
        # client_ports = [p for p in all_jack_ports if p.name.startswith(client_name + ':')]
        # for jack_port in client_ports:
        #     generic_port = PortAdapter.from_jack_port(jack_port)
        #     ports[generic_port.name] = generic_port
        
        return ports
    
    @staticmethod
    def create_generic_number_ports(count: int, prefix: str = "value") -> Dict[str, GenericPort]:
        """
        Create multiple number ports for computational nodes.
        
        Args:
            count: Number of ports to create
            prefix: Prefix for port names
            
        Returns:
            Dict of port names to GenericPort objects
        """
        from .generic_port import create_number_port
        
        ports = {}
        for i in range(count):
            port_name = f"{prefix}_{i}" if count > 1 else prefix
            port = create_number_port(port_name, PortDirection.INPUT)
            ports[port_name] = port
        
        return ports


# Example: Creating a hybrid node that combines audio and computation

class AudioProcessorNode(AudioNode):
    """
    Example of a node that combines audio routing with computation.
    
    This could represent an audio effect with parameters.
    """
    
    def __init__(self, client_name: str, jack_handler: Any = None):
        super().__init__(client_name, jack_handler)
        
        # Add audio ports (from JACK)
        # These would be added when syncing with JACK
        
        # Add parameter ports (generic number ports)
        from .generic_port import create_number_port
        self.add_input_port(create_number_port("gain", PortDirection.INPUT, 1.0))
        self.add_input_port(create_number_port("pan", PortDirection.INPUT, 0.5))
    
    def compute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process parameter changes.
        
        This could send parameter updates to the JACK processing thread.
        """
        gain = inputs.get("gain", 1.0)
        pan = inputs.get("pan", 0.5)
        
        # Send parameters to audio processing
        # (Implementation would depend on your audio framework)
        
        return {}
