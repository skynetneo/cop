import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv

# New CopilotKit/AG‑UI imports
from copilotkit import LangGraphAGUIAgent
from ag_ui_langgraph import add_langgraph_fastapi_endpoint

# Your LangGraph graph
from agents.supervisor import graph

load_dotenv()

app = FastAPI(title="Accessible Solutions - Local Resources Agent")

# Attach the new AG‑UI endpoint
add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name="supervisor",             # your agent name
        description="Orchestrates sub‑agents",
        graph=graph,
    ),
    path="/copilotkit/supervisor",
)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="localhost", port=port, reload=True)