import subprocess
import time
import requests
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient



app = FastAPI()

# MongoDB
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["mcp_registry"]
tools_collection = db["tools"]

# Track subprocesses
running_servers: Dict[str, subprocess.Popen] = {}
tool_cache: Dict[str, list] = {}

class MCPServerConfigRequest(BaseModel):
    command: str
    args: list
    metadata_url: Optional[str] = "http://localhost:3333/metadata"  # default MCP metadata port


@app.post("/start_mcp_server/{server_name}")
def start_mcp_server(server_name: str, req: MCPServerConfigRequest):
    if server_name in running_servers:
        raise HTTPException(status_code=400, detail=f"Server '{server_name}' is already running.")

    try:
        # Start the server process
        proc = subprocess.Popen([req.command] + req.args)
        running_servers[server_name] = proc

        # Wait for it to start (or implement better health checks)
        time.sleep(3)

        # Call /metadata
        response = requests.get(req.metadata_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get metadata from MCP server.")

        metadata = response.json()
        tools = metadata.get("tools", [])
        tool_cache[server_name] = tools

        # Save to DB
        for tool in tools:
            tool["server"] = server_name
            if not tools_collection.find_one({"name": tool["name"], "server": server_name}):
                tools_collection.insert_one(tool)

        return {"message": f"Started server '{server_name}'", "tools": [t["name"] for t in tools]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_tools/{server_name}")
def get_tools(server_name: str):
    tools = tool_cache.get(server_name)
    if tools:
        return {"tools": tools}

    tools = list(tools_collection.find({"server": server_name}, {"_id": 0}))
    if not tools:
        raise HTTPException(status_code=404, detail="No tools found.")

    return {"tools": tools}


@app.post("/stop_mcp_server/{server_name}")
def stop_mcp_server(server_name: str):
    proc = running_servers.get(server_name)
    if not proc:
        raise HTTPException(status_code=404, detail="Server not running.")

    proc.terminate()
    del running_servers[server_name]
    tool_cache.pop(server_name, None)

    return {"message": f"Stopped server '{server_name}'"}

#