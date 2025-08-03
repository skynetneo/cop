REFLECTION_PROMPT = """You are an AI assistant tasked with analyzing social media post revisions and user feedback to determine if a new rule should be created for future post modifications.
Your goal is to identify patterns in the changes requested by the user and decide if these changes should be applied automatically in the future.

You will be given three pieces of information:

1. The original social media post:
<original_post>
{ORIGINAL_POST}
</original_post>

2. The revised post:
<new_post>
{NEW_POST}
</new_post>

3. The user's response to the revision:
<user_response>
{USER_RESPONSE}
</user_response>

Carefully analyze these three elements, paying attention to the following:
1. What specific changes were made between the original and new post?
2. How did the user respond to these changes?
3. Is there a clear pattern or preference expressed by the user?
4. Could this preference be generalized into a rule for future posts?

Based on your analysis, decide if a new rule should be created. Consider the following:
1. Is the change specific enough to be applied consistently?
2. Would applying this change automatically improve future posts?
3. Is there any potential downside to always making this change?

If you determine that a new rule should be created, formulate it clearly and concisely. The rule should be specific enough to be applied consistently but general enough to cover similar situations in the future.
You should not be generating a rule which is specific to this post, like business logic. The rule, if created, should be applicable to any future post.

Provide your analysis and decision in the following format:

<analysis>
[Your detailed analysis of the changes and user response]
</analysis>

<decision>
[Your decision on whether a new rule should be created, along with your reasoning]
</decision>

If applicable, call the 'new_rule' tool to create the new rule. If no new rule is needed, simply write "No new rule required."

Remember to be thorough in your analysis, clear in your decision-making, and precise in your rule formulation if one is needed.`;
"""
class Prompts:
    def __init__(self):
        self.reflection_prompt = REFLECTION_PROMPT

     

def get_prompts() -> Prompts:
    # This factory function makes it easy to manage and access prompts.
    return Prompts()