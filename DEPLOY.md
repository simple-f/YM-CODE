# YM-CODE 部署指南

**版本：** 1.0  
**更新时间：** 2026-03-17

---

## 🚀 快速开始

### 方式 1：Docker 一键部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/ym-code/ym-code.git
cd ym-code

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 API Keys

# 3. 启动服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f ymcode

# 5. 访问 Dashboard
# http://localhost:18770/dashboard
```

### 方式 2：本地部署

```bash
# 1. 安装 Python 3.11+
python --version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动 Dashboard
python -m ymcode.web.dashboard_api

# 4. 访问 Dashboard
# http://localhost:18770/dashboard
```

---

## 📋 环境配置

### .env 文件示例

```bash
# API Keys
DASHSCOPE_API_KEY=your_dashscope_key
OPENAI_API_KEY=your_openai_key

# 数据库配置
DATABASE_URL=sqlite:///data/ymcode.db
RAG_DATABASE_URL=sqlite:///data/rag.db

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs

# 服务配置
HOST=0.0.0.0
PORT=18770
```

---

## 🐳 Docker 部署

### 开发环境

```bash
# 启动 YM-CODE 服务
docker-compose up -d ymcode

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f ymcode

# 停止服务
docker-compose down
```

### 生产环境

```bash
# 启动所有服务（包括 PostgreSQL + Redis）
docker-compose --profile production up -d

# 查看资源使用
docker stats

# 备份数据
docker-compose exec postgres pg_dump -U ymcode ymcode > backup.sql
```

---

## 🔧 配置选项

### 数据库配置

**SQLite（默认）：**
```bash
DATABASE_URL=sqlite:///data/ymcode.db
```

**PostgreSQL（生产环境）：**
```bash
DATABASE_URL=postgresql://ymcode:password@postgres:5432/ymcode
```

### 日志配置

```bash
LOG_LEVEL=INFO  # DEBUG/INFO/WARNING/ERROR
LOG_DIR=logs
LOG_ROTATION=size  # size/time
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=7
```

### RAG 知识库配置

```bash
# 向量化模型
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# 分块配置
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# 检索配置
SEARCH_TOP_K=5
MIN_SCORE=0.5
```

---

## 📊 监控与运维

### 健康检查

```bash
# API 健康检查
curl http://localhost:18770/health

# Dashboard 健康检查
curl http://localhost:18770/dashboard
```

### 日志查看

```bash
# 实时日志
docker-compose logs -f ymcode

# 最近 100 行
docker-compose logs --tail=100 ymcode

# 导出日志
docker-compose logs ymcode > ymcode.log
```

### 数据备份

```bash
# 备份 SQLite 数据库
cp data/ymcode.db data/ymcode.db.backup.$(date +%Y%m%d)

# 备份 PostgreSQL 数据库
docker-compose exec postgres pg_dump -U ymcode ymcode > backup.sql

# 备份 RAG 知识库
cp data/rag.db data/rag.db.backup.$(date +%Y%m%d)
```

---

## 🔒 安全建议

### 生产环境

1. **修改默认密码**
   ```bash
   POSTGRES_PASSWORD=strong_password
   ```

2. **启用 HTTPS**
   ```bash
   # 使用 Nginx 反向代理
   # 配置 SSL 证书
   ```

3. **API 认证**
   ```bash
   # 启用 JWT/OAuth2
   # 配置 RBAC 权限
   ```

4. **防火墙配置**
   ```bash
   # 仅开放必要端口
   # 限制 IP 访问
   ```

---

## 📈 性能优化

### 缓存配置

```bash
# 启用 Redis 缓存
REDIS_URL=redis://redis:6379/0

# 缓存 TTL
CACHE_TTL=300  # 5 分钟
```

### 数据库优化

```bash
# PostgreSQL 连接池
POOL_SIZE=5
MAX_OVERFLOW=10

# 查询超时
QUERY_TIMEOUT=30
```

### 向量检索加速

```bash
# 使用 FAISS（可选）
pip install faiss-cpu

# 配置 FAISS 索引
FAISS_INDEX_TYPE=IVF
FAISS_NLIST=100
```

---

## 🐛 故障排查

### 常见问题

**1. 容器启动失败**
```bash
# 查看日志
docker-compose logs ymcode

# 检查配置
docker-compose config

# 重新构建
docker-compose build --no-cache
```

**2. 数据库连接失败**
```bash
# 检查 PostgreSQL 状态
docker-compose ps postgres

# 查看 PostgreSQL 日志
docker-compose logs postgres

# 测试连接
docker-compose exec postgres psql -U ymcode -c "SELECT 1"
```

**3. API 无法访问**
```bash
# 检查端口占用
netstat -tlnp | grep 18770

# 检查防火墙
ufw status

# 重启服务
docker-compose restart ymcode
```

---

## 📞 技术支持

**文档：**
- 系统评估：`memory/ymcode-system-evaluation.md`
- 后端改进：`memory/ymcode-backend-improvement-report.md`
- 安全审计：`memory/core-modules-safety-audit.md`

**联系方式：**
- GitHub Issues: https://github.com/ym-code/ym-code/issues
- 技术文档：`docs/` 目录

---

_最后更新：2026-03-17_
