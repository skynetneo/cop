REPORT_RULES = """- Focus on the subject of the content, and how it uses or relates to the business context outlined above.
- The final Tweet/LinkedIn post will be developer focused, so ensure the report is VERY technical and detailed.
- You should include ALL relevant details in the report, because doing this will help the final post be more informed, relevant and engaging.
- Include any relevant links found in the content in the report. These will be useful for readers to learn more about the content.
- Include details about what the product does, what problem it solves, and how it works. If the content is not about a product, you should focus on what the content is about instead of making it product focused.
- Use proper markdown styling when formatting the marketing report.
- Generate the report in English, even if the content submitted is not in English."""

STRUCTURE_GUIDELINES = """<part key="1">
This is the introduction and summary of the content. This must include key details such as:
- the name of the content/product/service.
- what the content/product/service does, and/or the problems it solves.
- unique selling points or interesting facts about the content.
- a high level summary of the content/product/service.

Ensure this is section packed with details and engaging.
</part>

<part key="2">
This section should focus on how the content implements, or related to any of the business context outlined above. It should include:
- key details about how it relates to the context.
- any product(s) or service(s) used in the content.
- why the content is relevant to the business context.
- how the content is used, implemented, or related.
- why these products are important to the application.
</part>

<part key="3">
This section should cover any additional details about the content that the first two parts missed. It should include:
- a detailed technical overview of the content.
- interesting facts about the content.
- any other relevant information that may be engaging to readers.

This is the section where you should include any relevant parts of the content which you were unable to include in the first two sections.
Ensure you do NOT leave out any relevant details in the report. You want your report to be extensive and detailed. Remember, it's better to overdo it than underdo it.
</part>"""

class Prompts:
    def __init__(self):
        self.report_rules = REPORT_RULES
        self.structure_guidelines = STRUCTURE_GUIDELINES

     

def get_prompts() -> Prompts:
    # This factory function makes it easy to manage and access prompts.
    return Prompts()