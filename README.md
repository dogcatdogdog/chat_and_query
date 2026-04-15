# 通用大模型验证框架 (General LLM Verification Framework)

这是一个通用的 LLM 功能验证框架，旨在为基于大模型的应用提供标准化的开发底座，支持意图识别、API 模拟调用及多轮对话验证。

## 1. 项目结构

- `config/`: 配置文件（环境变量、模型参数）。
- `data/`: 模拟数据库 (`mock_db.json`)。
- `prompts/`: Prompt 模板（路由、回复生成）。
- `src/`: 核心源代码。
- `tests/`: 测试脚本。

## 2. 快速开始

### 2.1 安装依赖

建议使用虚拟环境：

```bash
# 创建并激活虚拟环境 (可选)
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2.2 配置环境变量

将 `.env.example` 复制为 `config/.env` 并填写你的 API Key：

```bash
cp .env.example config/.env
```

编辑 `config/.env`:
```text
API_KEY="your_actual_api_key"
BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL="qwen-turbo"
```

### 2.3 运行 Demo

启动交互式命令行界面：

```bash
python -m src.main
```

## 3. 核心架构与数据流 (Engine Data Flow)

系统的核心逻辑由 `src/engine.py` 中的 `ExecutionEngine` 驱动，采用 **Router-Executor-Responder** 三阶段流水线：

### 3.1 数据流向图
`User Input` -> **[Router]** -> `Tool Calls` -> **[Executor]** -> `API Results` -> **[Responder]** -> `Final Markdown`

### 3.2 模块详解
1.  **意图路由 (Router)**:
    *   **输入**: 用户原始输入 + 历史对话上下文 (`history`) + 工具定义 (`tools_registry.json`)。
    *   **处理**: 调用 LLM 匹配最合适的 API 或操作。
    *   **输出**: 标准化的 `tool_calls` (Function Calling 协议)。
2.  **执行器 (Executor)**:
    *   **输入**: `tool_calls` 及其参数。
    *   **处理**: 循环调用 `src/mock_api.py` 检索 `data/v1.1/resource_pool.json` 中的数据。
    *   **输出**: 聚合后的 API 原始结果 JSON 串。
3.  **信息加工 (Responder)**:
    *   **输入**: 原始请求 + 聚合后的 API 结果 + `responder_prompt.md`。
    *   **处理**: 执行数据审计、格式化转换（如数值加粗、回显 ID）、安全过滤。
    *   **输出**: 符合 v1.1 规范的 `ChatResponse` 对象（含 Markdown 内容、意图列表及数据来源）。

## 4. 运行测试

本项目包含完整的验证体系，核心脚本如下：

### 4.1 核心验收测试
-   `tests/final_acceptance_v1_1.py`: **最终验收脚本**。包含 19 条意图用例及 100 条安全合规压测，验证准确率、合规率及格式规范。
-   `tests/verify_v1_1_flows.py`: **全链路流程验证**。涵盖简单对话、带预警的业务查询及操作触发的完整闭环。

### 4.2 专项验证脚本
-   `tests/verify_mixed_intent.py`: **复合意图测试**。验证单次输入触发多个 API 调用（如：对比两台设备状态）的并发处理能力。
-   `tests/verify_multi_turn_logic.py`: **多轮对话测试**。验证指代消解（如：“它目前的电量”）和上下文记忆。
-   `tests/verify_error_scenarios.py`: **异常边界测试**。覆盖幻觉检测、敏感提问拦截及无关话题过滤。

### 4.3 运行方式
```bash
# 推荐：运行全链路流程验证
python tests/verify_v1_1_flows.py

# 推荐：运行最终验收测试
python tests/final_acceptance_v1_1.py
```

## 5. 扩展开发

- **修改 Prompt**: 编辑 `prompts/` 目录下的 `.md` 文件。
- **扩展 API**: 在 `src/processor.py` 中增加模拟 API 逻辑，并在 `data/mock_db.json` 中添加数据。
- **自定义业务**: 在 `src/engine.py` 中调整逻辑编排。

---
*更多细节请参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)*
