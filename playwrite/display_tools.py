import requests
import json

def print_mcp_tools(server_url: str):
    try:
        # Get the list of tools
        response = requests.get(server_url.rstrip('/') + '/.well-known/mcp/tool-manifest')
        response.raise_for_status()
        tools = response.json()

        print(f"\n✅ Tools available on MCP server at {server_url}:\n")

        for tool in tools.get("tools", []):
            print(f"🔧 Tool Name: {tool.get('name')}")
            print(f"   📄 Description: {tool.get('description', 'N/A')}")
            print(f"   📥 Input Schema:")
            print(json.dumps(tool.get("input_schema", {}), indent=4))
            print(f"   📤 Output Schema:")
            print(json.dumps(tool.get("output_schema", {}), indent=4))
            print("-" * 60)

    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to MCP server: {e}")
    except ValueError:
        print("❌ Failed to decode JSON from the MCP server response.")

# Replace with your MCP server address
server_url = "http://localhost:8123"
print_mcp_tools(server_url)
