# 无人机巡检问答引擎：从“单体模型”到“分布式 Skill”的架构迁移方案

## 1. 方案名称
无人机巡检智能问答引擎 v1.2：基于多专家 Skill 协作的认知重构方案

## 2. 方法概述
利用 Gemini CLI 的 Skill 机制，将单体响应逻辑解耦为具备独立认知指令集的职能 Skill，通过 Orchestrator（中枢）实现多意图规划与“专家会诊式”的数据聚合逻辑。

## 3. 输入
*   **用户指令**：包含 `query/stats/analysis/action/chat/error` 六大意图的原始文本。
*   **业务数据源 (Raw Data)**：通过 **Function Calling** 机制从后端 API 获取的结构化 JSON 数据。
*   **会话上下文**：存储于 `history` 中的多轮对话记录，用于指代消解与意图补全。

## 4. 输出
*   **标准化响应 (ChatResponse)**：包含 Markdown 格式的 content、意图标签列表 intentType、Action 跳转对象及数据溯源 dataSource。

## 5. 功能详解

### 5.1 核心职能 Skill 定义 (Expert Skill Definitions)
1.  **Intent-Orchestrator Skill (意图调度专家)**
    *   **核心逻辑**：作为系统的“流量入口”，负责全局意图识别。
    *   **任务拆解**：在识别到混合意图时，输出**执行计划 (Task Plan)**，定义后续 Skill 的激活序列与数据流转依赖。
    *   **技术价值**：将复杂的“任务规划”从代码逻辑中抽离，实现了意图识别体系的可插拔与热更新。

2.  **Interaction-Logic Skill (交互预处理专家)**
    *   **负责意图**：`chat` (闲聊), `error` (安全拒绝), `action` (操作触发)。
    *   **回复标准化**：处理非数据依赖的专业对话，并内置安全边界指令，阻断无关提问。
    *   **Action 构造**：将操作意图转化为标准的 Action 协议字段（路由、表单预填等）。

3.  **Data-Query Skill (事实性信息处理器)**
    *   **负责意图**：`query` (详情/列表)。
    *   **认知约束**：专注于 API JSON 的“无损转化”。指令集强制模型基于事实进行 Markdown 渲染，严禁任何主观推测或逻辑发散。

4.  **Statistical-Analysis Skill (统计聚合处理器)**
    *   **负责意图**：`statistics` (数据统计)。
    *   **二阶加工**：对离散数据执行数学意义上的聚合（如计算故障率、占比、趋势），产出量化指标结论，解决模型直接算数不准的痛点。

5.  **Root-Cause-Analyst Skill (归因分析专家)**
    *   **负责意图**：`analysis` (分析/建议)。
    *   **专家逻辑**：这是系统的“思考层”，拥有独立的“业务知识库”。它不仅看当前 API 数据，还匹配内置的“故障模式库”进行逻辑推导，解释“为什么”并提供改进建议。

6.  **Synthesis-Aggregator Skill (结果合成专家)**
    *   **职能描述**：负责最终响应的“缝合”与终审。
    *   **逻辑缝合**：将来自查询、统计、分析专家的中间结论，按照 [事实 > 指标 > 建议] 的优先级缝合成一段连贯、专业的 Markdown 最终文本。

### 5.2 全新 Engine 工作流逻辑 (Workflow & Execution)
Engine 角色转变为“智能数据总线”，根据 Orchestrator 的指令分流处理：

#### 路径 A：快车道 (Fast Path - 处理 Chat / Error / Action)
1.  **意图判定**：Orchestrator 识别出意图仅包含闲聊、报错或操作触发。
2.  **即时响应**：Engine 跳过工具调用，直接激活 `Interaction-Logic Skill`。
3.  **流程熔断**：获取回复或 Action 后直接返回，无需进入后续复杂计算链。

#### 路径 B：处理链 (Processing Chain - 处理 Query / Stats / Analysis)
1.  **规划 (Planning)**：Orchestrator 识别混合意图（如“查询 A 并统计占比”），生成任务清单。
2.  **获取 (Data Fetching)**：Engine 运行 **Function Calling** 获取业务 API 数据，存入**临时看板 (Blackboard)**。
3.  **分工执行 (Expert Processing)**：Engine 构建并行/串行流，激活对应的处理器 Skill。各 Skill 仅关注其职能领域，产出碎片化“中间稿”。
4.  **最终合成 (Synthesis)**：Engine 将碎片化产出喂给 `Synthesis-Aggregator`，完成最终文本的缝合与格式化。

### 5.3 分析能力的专项提升 (Analysis Improvement)
*   **当前现状**：原单体 Responder 在单一 Prompt 中兼顾多任务，受 Token 限制，分析结论往往停留于表面。
*   **Skill 化优势**：`Root-Cause-Analyst Skill` 实现了**关注点分离**。由于拥有独立的指令空间，它能进行更深度的逻辑匹配，回复从简单的“现象描述”进化为专业的“故障诊断”。

## 6. 相关技术关键词
*   **Skill**：核心功能封装机制。
*   **Function Calling**：自然语言转结构化 API 参数的技术。
*   **Prompt Engineering (提示词工程)**：定义各职能 Skill 专家指令的核心手段。
*   **JSON Schema (数据协议)**：定义 Skill 间数据交换与工具参数的标准格式。
*   **Context Management (上下文管理)**：在多专家协作流程中，负责数据流转与状态维护。
