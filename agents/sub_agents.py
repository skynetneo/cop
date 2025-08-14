from .prompts import TASK_DESCRIPTION_PREFIX, TASK_DESCRIPTION_SUFFIX
from .state import DeepAgentState
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool, tool
from typing import TypedDict, Annotated, NotRequired, List
from langchain_core.messages import ToolMessage, HumanMessage
from langgraph.types import Command
from langgraph.prebuilt import InjectedState
from langchain_core.tools import InjectedToolCallId


class SubAgent(TypedDict):
    name: str
    description: str
    prompt: str
    tools: NotRequired[List[str]]


def _create_task_tool(tools, instructions, subagents: List[SubAgent], model, state_schema):
    agents = {
        "general-purpose": create_react_agent(model, prompt=instructions, tools=tools)
    }
    tools_by_name = {tool.name: tool for tool in tools if isinstance(tool, BaseTool)}
    for t in tools:
        if not isinstance(t, BaseTool):
            wrapped_tool = tool(t)
            tools_by_name[wrapped_tool.name] = wrapped_tool

    for _agent in subagents:
        agent_tools = []
        if "tools" in _agent:
            for t_name in _agent["tools"]:
                if t_name in tools_by_name:
                    agent_tools.append(tools_by_name[t_name])
                else:
                    print(f"Warning: Tool '{t_name}' specified for subagent '{_agent['name']}' not found.")
        else:
            agent_tools = tools
            
        agents[_agent['name']] = create_react_agent(
            model, prompt=_agent['prompt'], tools=agent_tools, state_schema=state_schema
        )

    other_agents_string = "\n".join([
        f"- {_agent['name']}: {_agent['description']}" for _agent in subagents
    ])

    @tool(
        description=TASK_DESCRIPTION_PREFIX.format(other_agents=other_agents_string)
        + TASK_DESCRIPTION_SUFFIX
    )
    def task(
        description: str,
        subagent_type: str,
        state: Annotated[DeepAgentState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        Delegate a task to a specialized sub-agent.
        """
        if subagent_type not in agents:
            error_message = f"Error: invoked agent of type {subagent_type}, the only allowed types are {[f'`{k}`' for k in agents]}"
            return Command(update={"messages": [ToolMessage(content=error_message, tool_call_id=tool_call_id)]})

        sub_agent = agents[subagent_type]
        
        # Isolate state for the sub-agent
        sub_agent_state = {"messages": [HumanMessage(content=description)]}

        result = sub_agent.invoke(sub_agent_state)
        
        # Extract the final content from the sub-agent's last message
        final_content = ""
        if result.get("messages") and isinstance(result["messages"], list):
            final_content = result["messages"][-1].content

        return Command(
            update={
                "files": result.get("files", {}),
                "messages": [
                    ToolMessage(
                        content=final_content, 
                        tool_call_id=tool_call_id
                    )
                ],
            }
        )

    return task
