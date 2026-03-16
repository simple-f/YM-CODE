#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YM-CODE 初始化脚本

功能：
1. 检查系统要求
2. 创建必要的目录
3. 生成配置文件
4. 验证安装
5. 初始化数据库
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Optional

# 颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.OKGREEN}[OK] {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.WARNING}[WARN] {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.FAIL}[ERROR] {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.OKCYAN}[INFO] {text}{Colors.ENDC}")


class YMCodeInitializer:
    """YM-CODE 初始化器"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.home_dir = Path.home()
        self.ymcode_dir = self.home_dir / ".ymcode"
        self.errors = []
        self.warnings = []
        
    def run(self):
        """运行初始化流程"""
        print_header("YM-CODE 初始化向导")
        
        steps = [
            ("检查系统要求", self.check_requirements),
            ("创建目录结构", self.create_directories),
            ("生成配置文件", self.generate_configs),
            ("初始化数据库", self.init_database),
            ("验证安装", self.verify_installation),
        ]
        
        for step_name, step_func in steps:
            print_info(f"执行：{step_name}")
            try:
                step_func()
            except Exception as e:
                print_error(f"{step_name} 失败：{e}")
                self.errors.append(f"{step_name}: {e}")
        
        # 显示总结
        self.show_summary()
        
        return len(self.errors) == 0
    
    def check_requirements(self):
        """检查系统要求"""
        # Python 版本
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 10:
            raise Exception(f"Python 3.10+ required, found {python_version.major}.{python_version.minor}")
        print_success(f"Python 版本：{python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查依赖
        required_packages = ['fastapi', 'uvicorn', 'pytest', 'pydantic']
        for package in required_packages:
            try:
                __import__(package)
                print_success(f"已安装：{package}")
            except ImportError:
                raise Exception(f"缺少依赖：{package}，请运行：pip install -r requirements.txt")
        
        # 检查磁盘空间
        import shutil
        total, used, free = shutil.disk_usage(self.base_dir)
        free_gb = free / (1024 ** 3)
        if free_gb < 0.5:
            print_warning(f"磁盘空间不足：{free_gb:.2f}GB (建议 1GB+)")
        else:
            print_success(f"可用磁盘空间：{free_gb:.2f}GB")
    
    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.ymcode_dir,
            self.ymcode_dir / "sessions",
            self.ymcode_dir / "memory",
            self.ymcode_dir / "logs",
            self.ymcode_dir / "cache",
        ]
        
        for dir_path in directories:
            dir_path.mkdir(parents=True, exist_ok=True)
            print_success(f"创建目录：{dir_path}")
    
    def generate_configs(self):
        """生成配置文件"""
        # 1. 生成 .env 文件（如果不存在）
        env_file = self.base_dir / ".env"
        env_example = self.base_dir / ".env.example"
        
        if not env_file.exists():
            if env_example.exists():
                shutil.copy(env_example, env_file)
                print_success("生成 .env 文件")
                print_warning("请编辑 .env 文件配置 API Key")
            else:
                # 创建默认 .env
                default_env = """# YM-CODE 环境配置

# LLM API 配置（必需）
DASHSCOPE_API_KEY=sk-your-api-key-here

# 可选配置
# OPENAI_API_KEY=sk-xxx
# MOONSHOT_API_KEY=sk-xxx

# YM-CODE 配置
YM_CODE_MAX_ITERATIONS=30
YM_CODE_TIMEOUT=300
YM_CODE_LOG_LEVEL=INFO

# 服务器配置
YM_CODE_HOST=0.0.0.0
YM_CODE_PORT=18770
YM_CODE_DEBUG=false
"""
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(default_env)
                print_success("生成 .env 文件")
                print_warning("请编辑 .env 文件配置 API Key")
        else:
            print_success(".env 文件已存在")
        
        # 2. 生成 config.json（如果不存在）
        config_file = self.base_dir / "config.json"
        if not config_file.exists():
            default_config = {
                "model": {
                    "primary": "qwen3.5-plus",
                    "fallback": "qwen-plus"
                },
                "features": {
                    "file_browser": True,
                    "web_terminal": True,
                    "task_manager": True,
                    "skills_market": True
                },
                "storage": {
                    "sessions_db": str(self.ymcode_dir / "sessions.db"),
                    "memory_dir": str(self.ymcode_dir / "memory")
                },
                "ui": {
                    "theme": "dark",
                    "language": "zh-CN"
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print_success("生成 config.json 文件")
        else:
            print_success("config.json 已存在")
    
    def init_database(self):
        """初始化数据库"""
        try:
            from ymcode.storage.session_store import SessionStore
            
            db_path = self.ymcode_dir / "sessions.db"
            store = SessionStore(str(db_path))
            
            # 创建表
            store.create_tables()
            
            print_success(f"初始化数据库：{db_path}")
            print_success("创建表：sessions, messages, memories")
        except Exception as e:
            print_warning(f"数据库初始化跳过：{e}")
            self.warnings.append(f"数据库初始化：{e}")
    
    def verify_installation(self):
        """验证安装"""
        print_info("验证系统组件...")
        
        # 1. 检查核心模块
        core_modules = [
            'ymcode.core',
            'ymcode.agents',
            'ymcode.skills',
            'ymcode.mcp',
            'ymcode.api',
        ]
        
        for module in core_modules:
            try:
                __import__(module)
                print_success(f"核心模块：{module}")
            except ImportError as e:
                print_error(f"核心模块缺失：{module} - {e}")
                self.errors.append(f"模块 {module}: {e}")
        
        # 2. 检查技能
        try:
            from ymcode.skills import get_all_skills
            skills = get_all_skills()
            print_success(f"已加载技能：{len(skills)} 个")
        except Exception as e:
            print_error(f"技能加载失败：{e}")
            self.errors.append(f"技能：{e}")
        
        # 3. 检查 API Key
        from dotenv import load_dotenv
        load_dotenv(self.base_dir / ".env")
        
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if api_key and api_key != 'sk-your-api-key-here':
            print_success("API Key 已配置")
        else:
            print_warning("API Key 未配置，请编辑 .env 文件")
            self.warnings.append("API Key 未配置")
        
        # 4. 检查 Web 界面
        web_index = self.base_dir / "web" / "index.html"
        if web_index.exists():
            print_success("Web 界面：已安装")
        else:
            print_error("Web 界面：缺失")
            self.errors.append("Web 界面缺失")
    
    def show_summary(self):
        """显示总结"""
        print_header("初始化完成")
        
        if self.errors:
            print_error(f"发现 {len(self.errors)} 个错误:")
            for error in self.errors:
                print(f"  - {error}")
            print("\n请修复上述错误后重新运行。")
        else:
            print_success("所有检查通过！")
        
        if self.warnings:
            print_warning(f"\n发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  - {warning}")
            print("\n警告不影响基本功能，但建议处理。")
        
        # 显示下一步
        print_info("\n下一步:")
        print("  1. 编辑 .env 文件配置 API Key")
        print("  2. 运行：python start-web.py")
        print("  3. 访问：http://localhost:18770")
        print("\n  更多帮助请查看：QUICKSTART.md")


def main():
    """主函数"""
    initializer = YMCodeInitializer()
    success = initializer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
