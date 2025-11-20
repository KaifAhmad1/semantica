"""
MCP Ingestion Module

This module provides comprehensive MCP (Model Context Protocol) server ingestion
capabilities, allowing users to ingest data from any Python-based MCP server
across diverse domains.

Key Features:
    - Generic implementation that works with ANY Python MCP server
    - Dynamic discovery of resources and tools
    - Resource-based and tool-based ingestion
    - Multiple MCP server support
    - Connection management integrated into ingestor
    - Progress tracking

Main Classes:
    - MCPIngestor: Main MCP ingestion class

Example Usage:
    >>> from semantica.ingest import MCPIngestor
    >>> ingestor = MCPIngestor()
    >>> ingestor.connect("server1", transport="stdio", command="python", args=["-m", "mcp_server"])
    >>> resources = ingestor.list_available_resources("server1")
    >>> data = ingestor.ingest_resources("server1", resource_uris=["resource://example"])
    >>> result = ingestor.ingest_tool_output("server1", tool_name="get_data", arguments={})

Author: Semantica Contributors
License: MIT
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..utils.exceptions import ProcessingError, ValidationError
from ..utils.logging import get_logger
from ..utils.progress_tracker import get_progress_tracker
from .mcp_client import MCPClient, MCPResource, MCPTool


@dataclass
class MCPData:
    """MCP data representation."""
    
    source: str
    server_name: str
    data_type: str  # "resource" or "tool_output"
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    ingested_at: datetime = field(default_factory=datetime.now)
    resource_uri: Optional[str] = None
    tool_name: Optional[str] = None


class MCPIngestor:
    """
    Generic MCP server ingestion handler.
    
    This class provides comprehensive MCP server ingestion capabilities,
    working generically with ANY Python-based MCP server. It dynamically
    discovers resources and tools from connected servers without requiring
    domain-specific code.
    
    Features:
        - Generic implementation for any Python MCP server
        - Multiple MCP server support
        - Dynamic resource and tool discovery
        - Resource-based and tool-based ingestion
        - Connection management
        - Progress tracking
    
    Example Usage:
        >>> ingestor = MCPIngestor()
        >>> ingestor.connect("db_server", transport="stdio", command="python", args=["-m", "mcp_db"])
        >>> ingestor.connect("file_server", transport="http", url="http://localhost:8000/mcp")
        >>> resources = ingestor.list_available_resources("db_server")
        >>> data = ingestor.ingest_resources("db_server", resource_uris=["resource://database/tables"])
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, **kwargs):
        """
        Initialize MCP ingestor.
        
        Sets up the ingestor with configuration. MCP servers are connected
        on-demand using the connect() method.
        
        Args:
            config: Ingestion configuration dictionary
            **kwargs: Additional configuration parameters (merged into config)
        """
        self.logger = get_logger("mcp_ingestor")
        
        # Merge configuration
        self.config = config or {}
        self.config.update(kwargs)
        
        # MCP server connections (keyed by server name)
        self._clients: Dict[str, MCPClient] = {}
        
        # Initialize progress tracker
        self.progress_tracker = get_progress_tracker()
        
        self.logger.info("MCP ingestor initialized")
    
    def connect(
        self,
        server_name: str,
        transport: str = "stdio",
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **config
    ) -> bool:
        """
        Connect to an MCP server.
        
        Args:
            server_name: Unique name for this MCP server connection
            transport: Transport method ("stdio", "http", "sse")
            command: Command for stdio transport (e.g., "python")
            args: Arguments for command (e.g., ["-m", "mcp_server"])
            url: URL for HTTP/SSE transport
            headers: Custom headers for HTTP/SSE transport
            **config: Additional configuration options
            
        Returns:
            bool: True if connection successful
            
        Raises:
            ProcessingError: If connection fails
        """
        try:
            # Check if already connected
            if server_name in self._clients:
                self.logger.warning(f"Server {server_name} already connected, reconnecting...")
                self.disconnect(server_name)
            
            # Create and connect client
            client = MCPClient(
                transport=transport,
                command=command,
                args=args,
                url=url,
                headers=headers,
                **config
            )
            
            if client.connect():
                self._clients[server_name] = client
                self.logger.info(f"Connected to MCP server: {server_name}")
                return True
            else:
                raise ProcessingError(f"Failed to connect to MCP server: {server_name}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            raise ProcessingError(f"Failed to connect to MCP server {server_name}: {e}") from e
    
    def disconnect(self, server_name: Optional[str] = None):
        """
        Disconnect from an MCP server or all servers.
        
        Args:
            server_name: Server name to disconnect (None to disconnect all)
        """
        if server_name:
            if server_name in self._clients:
                self._clients[server_name].disconnect()
                del self._clients[server_name]
                self.logger.info(f"Disconnected from MCP server: {server_name}")
            else:
                self.logger.warning(f"Server {server_name} not connected")
        else:
            # Disconnect all
            for name, client in list(self._clients.items()):
                client.disconnect()
                del self._clients[name]
            self.logger.info("Disconnected from all MCP servers")
    
    def _get_client(self, server_name: str) -> MCPClient:
        """Get MCP client for server name."""
        if server_name not in self._clients:
            raise ValidationError(f"MCP server '{server_name}' not connected. Call connect() first.")
        return self._clients[server_name]
    
    def list_available_resources(self, server_name: str) -> List[MCPResource]:
        """
        List resources available from an MCP server.
        
        Args:
            server_name: Name of connected MCP server
            
        Returns:
            List of MCPResource objects
        """
        client = self._get_client(server_name)
        return client.list_resources()
    
    def list_available_tools(self, server_name: str) -> List[MCPTool]:
        """
        List tools available from an MCP server.
        
        Args:
            server_name: Name of connected MCP server
            
        Returns:
            List of MCPTool objects
        """
        client = self._get_client(server_name)
        return client.list_tools()
    
    def read_resource(self, server_name: str, uri: str) -> Dict[str, Any]:
        """
        Read a resource from an MCP server.
        
        Args:
            server_name: Name of connected MCP server
            uri: Resource URI
            
        Returns:
            Resource data dictionary
        """
        client = self._get_client(server_name)
        return client.read_resource(uri)
    
    def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.
        
        Args:
            server_name: Name of connected MCP server
            tool_name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool result dictionary
        """
        client = self._get_client(server_name)
        return client.call_tool(tool_name, arguments or {})
    
    def ingest_resources(
        self,
        server_name: str,
        resource_uris: Optional[List[str]] = None,
        filter_func: Optional[callable] = None,
        **options
    ) -> List[MCPData]:
        """
        Ingest data from MCP server resources.
        
        Args:
            server_name: Name of connected MCP server
            resource_uris: List of resource URIs to ingest (None for all)
            filter_func: Optional function to filter resources
            **options: Additional ingestion options
            
        Returns:
            List of MCPData objects
        """
        client = self._get_client(server_name)
        
        try:
            # Get tracking ID
            tracking_id = self.progress_tracker.start_task(
                task_type="mcp_ingest_resources",
                description=f"Ingesting resources from {server_name}"
            )
            
            # List available resources
            all_resources = client.list_resources()
            
            # Filter resources if needed
            if resource_uris:
                resources = [r for r in all_resources if r.uri in resource_uris]
            elif filter_func:
                resources = [r for r in all_resources if filter_func(r)]
            else:
                resources = all_resources
            
            if not resources:
                self.logger.warning(f"No resources found for server {server_name}")
                self.progress_tracker.update_task(tracking_id, status="completed", message="No resources found")
                return []
            
            # Ingest each resource
            ingested_data = []
            total = len(resources)
            
            for idx, resource in enumerate(resources):
                try:
                    self.progress_tracker.update_task(
                        tracking_id,
                        status="in_progress",
                        progress=(idx / total) * 100,
                        message=f"Reading resource: {resource.uri}"
                    )
                    
                    # Read resource
                    resource_data = client.read_resource(resource.uri)
                    
                    # Create MCPData object
                    mcp_data = MCPData(
                        source=resource.uri,
                        server_name=server_name,
                        data_type="resource",
                        content=resource_data,
                        metadata={
                            "resource_name": resource.name,
                            "resource_description": resource.description,
                            "mime_type": resource.mime_type,
                            **resource.metadata
                        },
                        resource_uri=resource.uri
                    )
                    
                    ingested_data.append(mcp_data)
                    
                except Exception as e:
                    self.logger.error(f"Failed to ingest resource {resource.uri}: {e}")
                    self.progress_tracker.update_task(
                        tracking_id,
                        status="warning",
                        message=f"Failed to ingest resource {resource.uri}: {e}"
                    )
                    continue
            
            self.progress_tracker.update_task(
                tracking_id,
                status="completed",
                progress=100,
                message=f"Successfully ingested {len(ingested_data)} resources"
            )
            
            self.logger.info(f"Ingested {len(ingested_data)} resources from {server_name}")
            return ingested_data
            
        except Exception as e:
            self.logger.error(f"Failed to ingest resources from {server_name}: {e}")
            raise ProcessingError(f"Failed to ingest resources: {e}") from e
    
    def ingest_tool_output(
        self,
        server_name: str,
        tool_name: str,
        arguments: Optional[Dict[str, Any]] = None,
        **options
    ) -> MCPData:
        """
        Ingest data by calling an MCP tool.
        
        Args:
            server_name: Name of connected MCP server
            tool_name: Tool name to call
            arguments: Tool arguments
            **options: Additional ingestion options
            
        Returns:
            MCPData object with tool output
        """
        client = self._get_client(server_name)
        
        try:
            # Get tracking ID
            tracking_id = self.progress_tracker.start_task(
                task_type="mcp_ingest_tool",
                description=f"Calling tool {tool_name} on {server_name}"
            )
            
            self.progress_tracker.update_task(
                tracking_id,
                status="in_progress",
                message=f"Calling tool: {tool_name}"
            )
            
            # Call tool
            tool_result = client.call_tool(tool_name, arguments or {})
            
            # Create MCPData object
            mcp_data = MCPData(
                source=tool_name,
                server_name=server_name,
                data_type="tool_output",
                content=tool_result,
                metadata={
                    "tool_name": tool_name,
                    "arguments": arguments or {}
                },
                tool_name=tool_name
            )
            
            self.progress_tracker.update_task(
                tracking_id,
                status="completed",
                progress=100,
                message=f"Successfully called tool {tool_name}"
            )
            
            self.logger.info(f"Ingested data from tool {tool_name} on {server_name}")
            return mcp_data
            
        except Exception as e:
            self.logger.error(f"Failed to ingest tool output from {server_name}: {e}")
            raise ProcessingError(f"Failed to ingest tool output: {e}") from e
    
    def ingest_all_resources(
        self,
        server_name: str,
        **options
    ) -> List[MCPData]:
        """
        Ingest all resources from an MCP server.
        
        Args:
            server_name: Name of connected MCP server
            **options: Additional ingestion options
            
        Returns:
            List of MCPData objects
        """
        return self.ingest_resources(server_name, resource_uris=None, **options)
    
    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names."""
        return list(self._clients.keys())
    
    def is_connected(self, server_name: str) -> bool:
        """Check if a server is connected."""
        return server_name in self._clients and self._clients[server_name].is_connected()

