# 个人学习路线

> 基于 2026-05-14 知识画像定制。核心原则：**看懂原理 → 合上文档 → 自己写 → 卡住再看参考。**

---

## 阶段零：环境准备（30分钟，一次性）

在你自己的新项目 `my-agent-learning/` 里完成：

1. `python -m venv venv` 创建虚拟环境
2. `pip install openai python-dotenv`
3. 创建 `.env` 文件，配置 LLM_API_KEY、LLM_MODEL_ID、LLM_BASE_URL
4. 创建 `llm_client.py` —— 封装一个最简单的 `HelloAgentsLLM` 类

**完成标准**：能单独运行 `python llm_client.py`，打印一句 "你好，我是XXX模型" 就通过。

---

## 阶段一：核心循环 —— ReAct（预计 4-8 小时）

**这是最关键的一步。ReAct 是一切现代 Agent 的骨架。**

### 你需要理解的东西

- LLM 在循环里不断运行：思考 → 选择动作 → 执行 → 观察结果 → 再思考
- 动作分三种：调用工具 / 输出最终答案 / 无意义废话（需要被约束）
- 约束 LLM 输出格式靠的是 prompt 模板，不是代码逻辑

### 你需要亲手写的文件

```
my-agent-learning/
├── llm_client.py      # 已写好
├── tools.py           # 定义 2-3 个工具（搜索、计算器、查天气）
└── react_agent.py     # 核心：ReActAgent 类
```

### react_agent.py 的结构

```
class ReActAgent:
    def __init__(self, llm, tools, max_steps=5)
    def run(self, question) -> str
        1. 构造 prompt（模板 + 工具列表 + 问题）
        2. for step in range(max_steps):
        3.     调 LLM，解析 response
        4.     如果是 Finish[答案] → return 答案
        5.     如果是 tool_name[tool_input] → 执行工具 → 把结果加到 history
        6.     都不是 → 报错或重试
```

### 关键坑点（先告诉你，遇到不用慌）

- **输出解析**是最大的坑 —— LLM 不按格式输出时，正则匹配会失败，需要写 fallback
- **死循环** —— max_steps 是保底，实际中 LLM 可能反复调用同一个工具
- **history 膨胀** —— 每一步都把完整对话历史发回去，很快超出 token 限制

### 完成标准

给你自己的 agent 一个问题比如 "2024年诺贝尔物理学奖得主是谁？他的年龄是多少？"，agent 能自主搜索 → 获取信息 → 计算 → 输出最终答案。

**完成这个，你就跨过了从"知道"到"做到"的鸿沟。**

---

## 阶段二：对比两种范式（预计 3-5 小时）

写另外两个 agent，跟 ReAct 做对比，理解不同范式的适用场景。

### Plan-and-Solve（先规划再执行）

```
class PlanAndSolveAgent:
    1. 先让 LLM 输出完整计划（步骤列表）
    2. 逐步骤执行（每个步骤可能调用工具）
    3. 汇总所有步骤结果
```

### Reflection（自我批评）

```
class ReflectionAgent:
    1. 先让第一个 agent 执行任务
    2. 让第二个 agent（Reflector）审查结果，找出问题
    3. 把审查意见喂回第一个 agent 重新执行
    4. 循环直到满意
```

**完成标准**：同一个问题用三种 agent 跑一遍，能说出每种方案的优劣势和失败模式。

---

## 阶段三：自研框架（预计 8-15 小时，核心章节）

对应项目第7章。把前面写的东西抽象成一个可复用的框架。

### 你需要抽象出的核心组件

```
helloagents/
├── core/
│   ├── llm.py          # LLM 封装，支持多 provider
│   ├── agent.py        # BaseAgent 抽象类
│   ├── tool.py         # Tool 注册/执行
│   └── memory.py       # 对话历史管理
├── agents/
│   ├── react.py        # ReActAgent(BaseAgent)
│   ├── plan_solve.py   # PlanAndSolveAgent(BaseAgent)
│   └── reflection.py   # ReflectionAgent(BaseAgent)
└── tools/
    ├── search.py
    └── calculator.py
```

### 框架级问题你会遇到

- 工具怎么注册和发现？（用函数签名 + docstring → 自动生成 tool schema）
- 不同 LLM provider 怎么统一接口？（BaseLLM 抽象 + OpenAI/Mock 实现）
- memory 怎么设计？（短期=对话历史，长期=向量检索）
- 输出解析失败怎么统一处理？（重试机制、格式修正 prompt）

### 完成标准

你写的框架能跑通第4章的三个 agent + 一个新工具，并且换工具不用改 agent 代码。

---

## 阶段四：协议与生态（预计 5-8 小时）

对应项目第10章。当前 Agent 领域的核心基础设施。

### MCP（Model Context Protocol）

- 理解 Client-Server 架构
- 用 `mcp` Python SDK 写一个简单的 MCP Server（暴露工具）
- 让你的 agent 通过 MCP Client 调用外部 server 的工具

### A2A（Agent-to-Agent）

- 理解 Agent Card、Task 等核心概念
- 两个 agent 之间通过 A2A 通信协作

### 完成标准

你的 react_agent 能通过 MCP 协议调用另一个进程里的工具。

---

## 阶段五：综合实战（预计 10-20 小时）

对应项目第13/16章。选一个完整项目做。

**推荐：智能旅行助手**（第13章），因为它天然涉及：
- 多工具协作（查景点、订票、天气、汇率）
- MCP 协议（不同服务用不同 MCP Server）
- 多 Agent 协作（规划 agent + 执行 agent + 审查 agent）

### 完成标准

用户说 "帮我规划一个五一去成都的三天行程，预算3000"，你的系统能自主完成搜索、比价、生成行程表。

---

## 其他章节的定位（按需穿插，非主线）

| 章节 | 何时看 | 看多久 |
|------|--------|--------|
| 第3章 LLM基础 | 阶段一遇到 token 限制 / prompt 调不好时 | 1-2h 速览 |
| 第5章 低代码平台 | 阶段二完成后，想了解 Coze/Dify 做什么 | 2-3h |
| 第6章 主流框架 | 阶段三完成后，对比 LangChain/AutoGen | 3-5h |
| 第8章 Memory/RAG | 阶段三做 memory 模块时 | 2-3h |
| 第9章 上下文工程 | 阶段三之后 | 1-2h |
| 第11章 Agentic RL | 阶段五之后，想训练模型时 | 较深，按需 |
| 第12章 评估 | 阶段三做完框架需要评估时 | 2-3h |
| 第14/15章 | 阶段五完成后选做 | 各 3-5h |

---

## 时间估算

| 阶段 | 内容 | 预计时间 |
|------|------|----------|
| 零 | 环境准备 | 0.5h |
| 一 | ReAct | 4-8h |
| 二 | Plan-and-Solve + Reflection | 3-5h |
| 三 | 自研框架 | 8-15h |
| 四 | MCP/A2A | 5-8h |
| 五 | 综合实战 | 10-20h |
| **合计** | | **30-57h** |

按每周 5-15 小时，大约 **4-8 周**完成主线。

---

## 最重要的提醒

阶段一的前 2 小时是最难的。你会面对空白的 `.py` 文件不知道第一行写什么。**这是正常的，不是你的问题。** 解决方法是：

1. 先把 ReAct 循环画在纸上（一个圆圈：Think → Act → Observe → Think...）
2. 然后写伪代码注释在 `.py` 里
3. 逐行把注释翻译成代码
4. 实在卡住超过 30 分钟，看一眼 `code/chapter4/ReAct.py` 的结构就走
