# YM-CODE Dockerfile
# 跨平台 AI 编程助手

FROM python:3.13-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 安装 YM-CODE
RUN pip install -e .

# 创建数据目录
RUN mkdir -p /root/.ymcode/logs /root/.ymcode/sessions

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from ymcode.cli.app import YMCodeApp; print('OK')" || exit 1

# 入口点
ENTRYPOINT ["python", "-m", "ymcode"]

# 默认无参数运行
CMD []
