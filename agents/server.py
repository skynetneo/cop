import os
from fastapi import FastAPI
import uvicorn
from copilotkit.integrations.fastapi import add_fastapi_endpoint
from copilotkit import CopilotKitRemoteEndpoint, LangGraphAgent
from agents.supervisor import graph # Import your graph
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

app = FastAPI(
    title="Accessible Solutions - Local Resources Agent"
)

# Define the LangGraph agent for CopilotKit
sdk = CopilotKitRemoteEndpoint(
    agents=[
   
        LangGraphAgent(
            name="supervisor",
            description="the agent that manages the other agents and can call them like tools",
            graph=graph,
        ),
    ],
)

# Add the /copilotkit endpoint to the FastAPI app
add_fastapi_endpoint(app, sdk, "/copilotkit")

# Add a health check route
@app.get("/health")
def health():
    """Health check."""
    return {"status": "ok"}

def main():
    """Run the uvicorn server."""
    port = int(os.getenv("PORT", "8000")) # Default to port 8000
    uvicorn.run(
        "server:app", # Assumes you run `python server.py` from the `back/agent` directory
        host="0.0.0.0",
        port=port,
        reload=True,
    )

if __name__ == "__main__":
    main()