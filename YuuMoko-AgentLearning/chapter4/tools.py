from dotenv import load_dotenv
import os

from serpapi import SerpApiClient

load_dotenv()

def search(query: str) -> str:
    print(f"正在执行[SerpApi]网页搜索:{query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误：SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn", # 国家代码
            "hl": "zh-cn" # 语言代码
        }

        client = SerpApiClient(params)
        result = client.get_dict()

        if "answer_box_list" in result:
            return "\n".join(result["answer_box_list"])
        if "answer_box" in result and "answer" in result["answer_box"]:
            return result["answer_box"]["answer"]
        if "knowledge_graph" in result and "description" in result["knowledge_graph"]:
            return result["knowledge_graph"]["description"]
        if "organic_results" in result and result["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(result["organic_results"][:3])
            ]
            return "\n\n".join(snippets)
    except Exception as e:
        return f"搜索时发生错误: {e}"
from typing import Dict, Any

class ToolExecutor:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")
    def getTool(self, name: str) -> callable:
        return self.tools.get(name, {}).get("func")
    def getAvailableTools(self):
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])

if __name__ == '__main__':
    toolExecutor = ToolExecutor()

    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)

    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())


    tool_name = "Search"
    tool_input = "今天深圳天气怎么样?"
    print(f"\n--- 执行 Action: Search['{tool_input}'] ---")

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到名为 '{tool_name}' 的工具。")