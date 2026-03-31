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

## 3. 运行测试

本项目包含多个层级的测试脚本，可以通过以下方式运行：

### 3.1 运行所有测试 (推荐)

你可以编写一个简单的 shell 脚本或直接依次运行以下命令：

```bash
# Windows (PowerShell)
Get-ChildItem tests/test_*.py | ForEach-Object { python $_.FullName }

# Linux/macOS
for f in tests/test_*.py; do python "$f"; done
```

### 3.2 运行特定测试

- **全链路测试 (E2E)**: 验证从输入到输出的完整流程。
  ```bash
  python tests/test_e2e.py
  ```
- **路由测试 (Router Only)**: 专门验证意图识别和 API 路由逻辑。
  ```bash
  python tests/test_router_only.py
  ```
- **回复测试 (Responder)**: 验证 AI 生成回复的格式和准确性。
  ```bash
  python tests/test_responder_single.py
  python tests/test_responder_multi.py
  ```
- **异常测试**: 验证错误处理机制。
  ```bash
  python tests/test_exceptions.py
  ```

## 4. 扩展开发

- **修改 Prompt**: 编辑 `prompts/` 目录下的 `.md` 文件。
- **扩展 API**: 在 `src/processor.py` 中增加模拟 API 逻辑，并在 `data/mock_db.json` 中添加数据。
- **自定义业务**: 在 `src/engine.py` 中调整逻辑编排。

---
*更多细节请参考 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)*
