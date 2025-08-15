
from ...config import get_llm, LLMConfig
from ..schemas import RouteSupervisorFeedback

async def route_supervisor_feedback(
    post: str, 
    date_or_priority: str, 
    supervisor_response: str, 
    llm_config: LLMConfig
) -> str:
    """
    Uses an LLM to decide the next step based on supervisor feedback.
    """
    # A simplified version of the original prompt
    prompt = f"""You are a routing assistant. Based on the supervisor's feedback, choose the next action.
    
    Original Post: "{post}"
    Original Schedule: "{date_or_priority}"
    Supervisor Feedback: "{supervisor_response}"

    Possible routes are:
    - 'rewrite_post': If the feedback asks for changes to the post's content or tone.
    - 'update_date': If the feedback mentions changing the schedule, date, or priority.
    - 'rewrite_with_split_url': If the feedback asks to split the URL into a reply.
    - 'accept': If the feedback is positive ('ok', 'looks good', 'ship it').
    - 'unknown_response': If the feedback is unclear or conversational.
    """

    router_model = get_llm(llm_config).with_structured_output(RouteSupervisorFeedback)
    
    result = await router_model.ainvoke(prompt)
    return result.route
