UPDATE_RULES_PROMPT = """You are an AI assistant tasked with updating a ruleset based on the addition of a new rule. Your goal is to analyze the new rule in relation to the existing rules and provide an updated ruleset.

First, review the existing rules:
<existing_rules>
{EXISTING_RULES}
</existing_rules>

Now, consider the new rule:
<new_rule>
{NEW_RULE}
</new_rule>

Analyze the new rule in relation to the existing rules by considering the following:
1. Can this rule be combined with existing rules to cover similar situations?
2. Has this rule already been covered by existing rules?
3. Does this rule conflict with existing rules?

Follow these guidelines when updating the ruleset:
1. If the new rule conflicts with an existing rule, remove the existing conflicting rule and prioritize the new rule.
2. If the new rule is already covered by an existing rule, remove the new rule or combine them.
3. If the new rule can be combined with existing rules, combine them to cover similar situations.

Before providing the updated ruleset, use a <scratchpad> to think through your analysis and decision-making process. Consider each existing rule in relation to the new rule, and explain your reasoning for any changes you plan to make.

After your analysis, provide the updated ruleset in the following format:
<updated_ruleset>
1. [First updated or new rule]
2. [Second updated or new rule]
...
n. [Last updated or new rule]
</updated_ruleset>

Following the updated ruleset, provide a brief explanation of the changes made and the reasoning behind them in <explanation> tags."""
