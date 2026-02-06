# SAGI LAB Backend

Alert Triage System Backend - 基于 LangGraph 的告警分析工作流

## 技术栈

- FastAPI + Python 3.13
- LangGraph + LangChain
- SQLAlchemy (async) + PostgreSQL
- Jinja2 模板

## 本地开发

```bash
# 安装依赖
uv sync

# 运行服务
uv run uvicorn app.main:app --reload --port 8000
```

## 项目结构

```
app/
├── main.py                 # FastAPI 入口
├── config.py               # 配置管理
├── api/v1/                 # API 端点
├── models/                 # SQLAlchemy 模型
├── schemas/                # Pydantic schemas
├── services/               # 业务服务
├── db/                     # 数据库配置
└── triage/                 # LangGraph 工作流
    ├── state.py            # 状态定义
    ├── graph.py            # 工作流编排
    ├── nodes/              # 各节点实现
    ├── prompts/            # Jinja2 模板
    └── utils/              # 工具类
```
