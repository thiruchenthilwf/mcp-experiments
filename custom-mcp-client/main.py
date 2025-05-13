import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, command: str, args: list):
        """Connect to an MCP server via stdio.

        Args:
            command: The command to start the server (e.g., 'npx', 'python').
            args: List of arguments for the command.
        """
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        read, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def list_tools(self):
        """Retrieve the list of tools from the connected MCP server."""
        if not self.session:
            raise RuntimeError("Session not initialized. Call connect_to_server first.")
        response = await self.session.list_tools()
        return response.tools

    async def close(self):
        """Close the MCP client session and exit stack."""
        await self.exit_stack.aclose()

# Example usage
async def main():
    config = {
        "mcpServers": {
            "playwright": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"]
            }
        }
    }

    server_name = "playwright"
    server_config = config["mcpServers"][server_name]
    command = server_config["command"]
    args = server_config["args"]

    client = MCPClient()
    try:
        await client.connect_to_server(command, args)
        tools = await client.list_tools()
        print(f"Available tools from '{server_name}':")
        for tool in tools:
            print(f"- {tool.name}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
