import re

from code.chapter4.ReAct import REACT_PROMPT_TEMPLATE

from code.chapter4.llm_client import HelloAgentsLLM

from code.chapter4.tools import ToolExecutor

REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下：
{tools}

请严格按照以下格式进行回应：

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一：
- `{{tool_name}}[{{tool_input}}]`：调用一个可用工具。
- `Finish[最终答案]`：当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在`Action:`字段后使用 `Finish[最终答案]` 来输出最终答案。


现在，请开始解决以下问题：
Question: {question}
History: {history}
"""

class ReActAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor : ToolExecutor, mas_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = mas_steps
        self.history = []


    def run(self, question: str):
        self.history = []
        current_step = 0
        while current_step < self.max_steps:
            current_step += 1
            print(f"\n --- 第{current_step}步 ---")

            tool_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(tools=tools_desc, question=question, history_str)

            message = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=message)
            if not response_text:
                print("错误：LLM未能返回有效响应。"); break

            thought, action = self._parse_output(response_text)


    def _parse_output(self, text: str):

        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)

        action_match = re.search(r"Action")
