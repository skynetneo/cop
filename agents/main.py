import asyncio
from uuid import uuid4
from langchain_core.messages import HumanMessage
from agents.supervisor.graph import supervisor_agent

async def main():
    """A simple REPL to chat with the supervisor agent."""
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print("Supervisor Agent is ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        # The input to the graph is a list of messages
        events = supervisor_agent.stream(
            [HumanMessage(content=user_input)],
            config,
            stream_mode="values"
        )
        
        async for event in events:
            if "messages" in event:
                # Print out the agent's final response to the user
                last_message = event["messages"][-1]
                if last_message.type != "tool":
                    print("Supervisor:", last_message.content)

if __name__ == "__main__":
    asyncio.run(main())