# YM-CODE Docker 使用指南

**版本：** v0.5.0  
**更新时间：** 2026-03-16

---

## 🐳 Docker 技能概述

YM-CODE 的 Docker 技能允许你通过自然语言或 API 管理 Docker 容器和镜像。

### 功能特性

- ✅ 容器管理（启动/停止/删除）
- ✅ 镜像管理（拉取/删除）
- ✅ 容器列表查看
- ✅ 日志查看
- ✅ 执行命令
- ✅ 端口映射配置

---

## 🚀 前置要求

### 1. 安装 Docker

**Windows:**
```bash
# 下载 Docker Desktop
# https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo systemctl start docker
```

**macOS:**
```bash
# 下载 Docker Desktop
# https://desktop.docker.com/mac/main/amd64/Docker.dmg
```

### 2. 验证安装

```bash
docker --version
docker ps
```

---

## 💬 通过聊天使用

### 基本对话

**查看容器：**
```
你：列出所有运行中的容器
YM-CODE: [调用 Docker 技能]

正在执行：docker ps

找到 3 个运行中的容器：
CONTAINER ID   IMAGE          STATUS
abc123         nginx:latest   Up 2 hours
def456         redis:alpine   Up 1 day
ghi789         postgres:13    Up 3 days
```

**启动容器：**
```
你：启动一个 nginx 容器，端口 80 映射到 8080
YM-CODE: [调用 Docker 技能]

正在执行：docker run -d -p 8080:80 --name web-server nginx:latest

容器启动成功！
容器 ID: abc123
访问地址：http://localhost:8080
```

**停止容器：**
```
你：停止 web-server 容器
YM-CODE: [调用 Docker 技能]

正在执行：docker stop web-server

容器已停止
```

---

## 🛠️ Docker 技能 API

### 输入参数

```json
{
  "action": "ps|images|run|stop|start|restart|rm|rmi|logs|exec",
  "container_id": "容器 ID 或名称",
  "image": "镜像名称",
  "options": "额外选项",
  "command": "执行命令（exec 时）"
}
```

---

### 1. 查看容器列表

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "ps",
    "options": "-a"  # 显示所有容器
})
```

**返回结果：**
```json
{
  "success": true,
  "containers": [
    {
      "id": "abc123",
      "name": "web-server",
      "image": "nginx:latest",
      "status": "Up 2 hours",
      "ports": "0.0.0.0:8080->80/tcp"
    }
  ],
  "count": 1
}
```

---

### 2. 查看镜像列表

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "images"
})
```

**返回结果：**
```json
{
  "success": true,
  "images": [
    {
      "repository": "nginx",
      "tag": "latest",
      "size": "142MB",
      "created": "2 weeks ago"
    },
    {
      "repository": "redis",
      "tag": "alpine",
      "size": "32MB",
      "created": "1 month ago"
    }
  ],
  "count": 2
}
```

---

### 3. 运行容器

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "run",
    "image": "nginx:latest",
    "options": "-d -p 8080:80 --name web-server"
})
```

**返回结果：**
```json
{
  "success": true,
  "container_id": "abc123",
  "name": "web-server",
  "message": "容器启动成功"
}
```

**常用选项：**
```bash
-d              # 后台运行
-p 8080:80      # 端口映射
--name my-app   # 容器名称
-v /data:/app   # 挂载卷
-e ENV=value    # 环境变量
--rm            # 退出后删除
-it             # 交互模式
```

---

### 4. 停止容器

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "stop",
    "container_id": "web-server"
})
```

**返回结果：**
```json
{
  "success": true,
  "message": "容器已停止"
}
```

---

### 5. 启动容器

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "start",
    "container_id": "web-server"
})
```

**返回结果：**
```json
{
  "success": true,
  "message": "容器已启动"
}
```

---

### 6. 重启容器

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "restart",
    "container_id": "web-server"
})
```

---

### 7. 删除容器

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "rm",
    "container_id": "web-server",
    "options": "-f"  # 强制删除
})
```

**返回结果：**
```json
{
  "success": true,
  "message": "容器已删除"
}
```

---

### 8. 删除镜像

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "rmi",
    "image": "nginx:latest",
    "options": "-f"  # 强制删除
})
```

---

### 9. 查看日志

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "logs",
    "container_id": "web-server",
    "options": "--tail 100"  # 最后 100 行
})
```

**返回结果：**
```json
{
  "success": true,
  "logs": "2026-03-16 10:00:00 Server started\n2026-03-16 10:01:00 Request received...",
  "lines": 100
}
```

---

### 10. 在容器中执行命令

**API 调用：**
```python
result = await docker_skill.execute({
    "action": "exec",
    "container_id": "web-server",
    "command": "ls -la /usr/share/nginx/html"
})
```

**返回结果：**
```json
{
  "success": true,
  "output": "total 8\ndrwxr-xr-x 2 root root 4096 Mar 16 10:00 .\ndrwxr-xr-x 1 root root 4096 Mar 16 10:00 ..\n-rw-r--r-- 1 root root  612 Mar 16 10:00 index.html",
  "exit_code": 0
}
```

---

## 📋 常用场景示例

### 场景 1：部署 Web 应用

```bash
# 1. 拉取镜像
docker pull nginx:latest

# 2. 启动容器
docker run -d -p 80:80 --name my-app nginx:latest

# 3. 查看状态
docker ps

# 4. 访问应用
# http://localhost
```

**通过 YM-CODE：**
```
你：帮我部署一个 nginx 应用
YM-CODE: 好的，我来帮你部署：

1. 拉取 nginx 镜像 ✓
2. 启动容器，端口 80 映射 ✓
3. 验证容器状态 ✓

部署完成！访问地址：http://localhost
```

---

### 场景 2：部署数据库

```bash
# PostgreSQL
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_DB=myapp \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:13
```

**通过 YM-CODE：**
```
你：部署一个 PostgreSQL 数据库，密码设置为 mypassword
YM-CODE: [调用 Docker 技能]

正在执行：docker run -d --name postgres -e POSTGRES_PASSWORD=mypassword -e POSTGRES_DB=myapp -p 5432:5432 postgres:13

数据库部署成功！
连接信息：
- 主机：localhost
- 端口：5432
- 数据库：myapp
- 用户：postgres
- 密码：mypassword
```

---

### 场景 3：多容器应用

**docker-compose.yml:**
```yaml
version: '3'
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./html:/usr/share/nginx/html
  db:
    image: postgres:13
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - db_data:/var/lib/postgresql/data

volumes:
  db_data:
```

**启动：**
```bash
docker-compose up -d
```

---

### 场景 4：查看容器日志

```bash
# 查看实时日志
docker logs -f web-server

# 查看最后 100 行
docker logs --tail 100 web-server

# 查看特定时间
docker logs --since 2026-03-16T10:00:00 web-server
```

**通过 YM-CODE：**
```
你：查看 web-server 容器的日志
YM-CODE: [调用 Docker 技能]

正在获取日志...

2026-03-16 10:00:00 Server started
2026-03-16 10:01:00 Request from 192.168.1.1
2026-03-16 10:02:00 Request from 192.168.1.2
...
```

---

### 场景 5：清理资源

```bash
# 停止所有容器
docker stop $(docker ps -aq)

# 删除所有容器
docker rm $(docker ps -aq)

# 删除所有镜像
docker rmi $(docker images -q)

# 清理悬空镜像
docker image prune -f
```

**通过 YM-CODE：**
```
你：清理所有 Docker 资源
YM-CODE: ⚠️ 警告：这将删除所有容器和镜像，确定继续？

> 是

正在停止容器...
正在删除容器...
正在删除镜像...

清理完成！释放空间：2.5GB
```

---

## 🔧 Web 界面使用

### 1. 通过 Web 终端

1. 打开 http://localhost:18770
2. 点击 **⌨️ Web 终端**
3. 输入 Docker 命令：

```bash
# 查看容器
docker ps

# 启动容器
docker run -d -p 8080:80 nginx

# 查看日志
docker logs -f <container_id>
```

---

### 2. 通过聊天

直接在聊天框输入：

```
帮我启动一个 Redis 容器
```

YM-CODE 会自动调用 Docker 技能执行。

---

## 📊 Docker 技能参数详解

### action 参数

| 值 | 说明 | 必需参数 |
|----|------|---------|
| `ps` | 列出容器 | 无 |
| `images` | 列出镜像 | 无 |
| `run` | 运行容器 | `image` |
| `stop` | 停止容器 | `container_id` |
| `start` | 启动容器 | `container_id` |
| `restart` | 重启容器 | `container_id` |
| `rm` | 删除容器 | `container_id` |
| `rmi` | 删除镜像 | `image` |
| `logs` | 查看日志 | `container_id` |
| `exec` | 执行命令 | `container_id`, `command` |

---

### options 参数常用值

**端口映射：**
```bash
-p 8080:80      # 主机 8080 -> 容器 80
-p 127.0.0.1:8080:80  # 只监听本地
```

**挂载卷：**
```bash
-v /host/path:/container/path
-v my_volume:/data
```

**环境变量：**
```bash
-e KEY=value
-e DB_PASSWORD=secret
```

**其他：**
```bash
-d              # 后台运行
-it             # 交互模式
--rm            # 退出后删除
--name my-app   # 容器名称
--network my-net # 网络
```

---

## ⚠️ 注意事项

### 1. 权限问题

**Linux:**
```bash
# 将用户添加到 docker 组
sudo usermod -aG docker $USER
# 重新登录
```

**Windows/macOS:**
- Docker Desktop 默认有权限

---

### 2. 端口冲突

**错误：** "Bind for 0.0.0.0:80 failed: address already in use"

**解决：**
```bash
# 使用其他端口
docker run -p 8080:80 nginx

# 或停止占用端口的服务
netstat -ano | findstr :80
taskkill /PID <pid> /F
```

---

### 3. 磁盘空间

**查看空间：**
```bash
docker system df
```

**清理空间：**
```bash
docker system prune -a
```

---

### 4. 网络问题

**容器无法访问外网：**
```bash
# 检查 DNS
docker run --dns 8.8.8.8 nginx

# 使用 host 网络
docker run --network host nginx
```

---

## 🎯 最佳实践

### 1. 使用具体版本

```bash
# ✅ 推荐
docker run nginx:1.21

# ❌ 不推荐（可能意外升级）
docker run nginx:latest
```

---

### 2. 限制资源

```bash
docker run -d \
  --memory="512m" \
  --cpus="1.0" \
  nginx
```

---

### 3. 健康检查

```bash
docker run -d \
  --health-cmd="curl -f http://localhost/ || exit 1" \
  --health-interval=30s \
  nginx
```

---

### 4. 日志轮转

**daemon.json:**
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

## 📝 故障排查

### 容器启动失败

```bash
# 查看日志
docker logs <container_id>

# 查看详细信息
docker inspect <container_id>

# 测试运行
docker run -it nginx bash
```

---

### 无法访问容器

```bash
# 检查端口映射
docker port <container_id>

# 检查防火墙
# Windows: 防火墙设置
# Linux: sudo ufw status

# 测试连接
curl http://localhost:8080
```

---

## 🆘 获取帮助

### Docker 命令帮助

```bash
docker --help
docker run --help
```

### YM-CODE 帮助

```
你：Docker 技能怎么用？
YM-CODE: 我可以帮你管理 Docker 容器，支持：
- 查看容器列表
- 启动/停止容器
- 查看日志
- 执行命令
...

直接告诉我你想做什么就行！
```

---

## 📚 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/)
- [YM-CODE 技能文档](docs/SKILLS.md)
- [YM-CODE API 文档](docs/API.md)

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
