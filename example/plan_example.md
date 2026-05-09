需要包含如下内容：
1.方案名称 
2. 方法概述(一句话) 
3.输入 
4.输出 
5.功能 
6.相关技术关键词。


2. 完整的工作流逻辑：两条路径，一个终点

  Skill 化后的 engine.py 逻辑将根据 Orchestrator 的判断，分流为“快车道”和“处理链”：

  路径 A：快车道（Fast Path - Chat/Error/Action）
   1. Orchestrator 识别出意图为 chat 或 error。
   2. Orchestrator 直接激活 Responder-Quick。
   3. Responder-Quick 生成回复内容（如：专业的拒绝语或身份声明）。
   4. Engine 直接返回 ChatResponse，流程结束。
       * 改变：现在的 direct_response 工具逻辑被封装进了 Skill，使得“拒绝话术”和“闲聊风格”更容易统一管理。

  路径 B：处理链（Processing Chain - Query/Stats/Analysis）
  这是处理多意图的核心逻辑：
   1. Orchestrator 识别出混合意图：“列出故障设备（Query），算一下占比（Stats），并分析原因（Analysis）”。
   2. Engine 执行分发：
       * 调用 Router 工具 获取所有 API 数据（此时依然保留 Function Calling）。
       * 将 API 数据存入临时看板。
   3. 并发/串行激活 Skill：
       * Data-Interpreter 产出：[设备列表 Markdown]。
       * Data-Aggregator 产出：[故障率：20%]。
       * Logical-Reasoner 产出：[分析结论：近期降雨导致传感器受潮...]。
   4. 终点：Synthesis（汇总）：
       * 最后由一个专门的 Synthesis Skill（或由 Orchestrator 再次介入）将上述三份结论整合成一段完整的话。

  ---

  3. 针对 Analysis（分析意图）的理性深度分析

  你在问题中提到的“分析原因”，是 Skill 化后收益最大的部分：
   * 当前现状：目前的 Responder 可能在一个 Prompt 里既要展示数据（Query），又要算数（Stats），还要分析（Analysis）。这会导致分析逻辑往往比较浅层，或者因为 Token        
     限制忽略了深度归因。
   * Skill 化后的改变：Logical-Reasoner Skill 可以拥有独立的 “业务知识库”。
       * 当它识别到 intent: "analysis" 时，它可以不仅看当前的 API 数据，还可以利用其 Skill 指令中定义的“故障模式库”进行匹配。
       * 结果：它的回复将从“因为数据是 X，所以有问题”进化为“基于 X 现象，结合 Y 经验，建议检查 Z 模块”。

  4. 针对 Chat 和 Error 的理性分析

  为什么要把这两个也 Skill 化，而不是留在主程序里？
   1. 安全的一致性：Error Skill 可以定义严苛的拒绝指令（防注入、防敏感信息泄露）。如果分散在各处，安全红线很难守住。
   2. 品牌人格化：Chat Skill 决定了 AI 的“性格”。通过 Skill 化，你可以轻松地给它换“皮肤”（从专业助手换成亲和助手），而不需要动任何业务逻辑代码。

  总结：Skill 化后的 Engine 架构图

    1 User Input -> [Orchestrator Skill]
    2                 |
    3                 |-- (chat/error/action) --> [Responder-Quick Skill] --|
    4                 |                                                     |
    5                 |-- (query/stats/analysis)                            |
    6                          |                                            |
    7                          |--> [Function Calling / API Fetch]          |
    8                          |            |                               |
    9                          |    [Blackboard Data Context]               |
   10                          |            |                               |
   11                          |    |-- [Data-Interpreter Skill] --|        |--> Final ChatResponse
   12                          |    |-- [Data-Aggregator Skill]  --|        |
   13                          |    |-- [Logical-Reasoner Skill] --|        |
   14                          |            |                               |
   15                          |--> [Synthesis Skill / Aggregator] ---------|