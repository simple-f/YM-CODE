"""
主应用入口

启动 YM-CODE 后端服务
"""

import logging
import yaml
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.task_api import router as task_router
from .api.plugin_api import router as plugin_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def load_config() -> dict:
    """加载配置文件"""
    config_path = Path(__file__).parent.parent.parent / "configs" / "config.yaml"
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # 默认配置
    return {
        "server": {
            "host": "0.0.0.0",
            "port": 18770,
            "debug": True
        }
    }


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    config = load_config()
    
    app = FastAPI(
        title="YM-CODE API",
        description="YM-CODE AI Agent Platform API",
        version="2.0.0"
    )
    
    # CORS 配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 注册路由
    app.include_router(task_router, prefix="/api", tags=["tasks"])
    app.include_router(plugin_router, prefix="/api", tags=["plugins"])
    
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "name": "YM-CODE API",
            "version": "2.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy"}
    
    logger.info("YM-CODE API 应用创建完成")
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    config = load_config()
    server_config = config.get("server", {})
    
    logger.info("启动 YM-CODE API 服务...")
    logger.info(f"Host: {server_config.get('host', '0.0.0.0')}")
    logger.info(f"Port: {server_config.get('port', 18770)}")
    logger.info(f"Debug: {server_config.get('debug', False)}")
    
    uvicorn.run(
        "backend.main:app",
        host=server_config.get("host", "0.0.0.0"),
        port=server_config.get("port", 18770),
        reload=server_config.get("debug", False)
    )
