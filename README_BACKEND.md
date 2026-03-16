# 快速开始

## 安装依赖

```bash
pip install fastapi uvicorn pydantic pyyaml
```

## 启动服务

```bash
# 方式 1: 使用 main.py
python -m backend.main

# 方式 2: 使用 uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 18770
```

## 访问 API

- API 文档：http://localhost:18770/docs
- 健康检查：http://localhost:18770/health

## API 示例

### 创建任务

```bash
curl -X POST "http://localhost:18770/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试任务",
    "description": "这是一个测试任务"
  }'
```

### 查询任务列表

```bash
curl "http://localhost:18770/api/tasks"
```

### 查询任务详情

```bash
curl "http://localhost:18770/api/tasks/{task_id}"
```
