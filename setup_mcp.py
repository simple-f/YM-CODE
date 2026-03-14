#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 服务器一键配置脚本

自动安装和配置常用的 MCP 服务器（GitHub、文件系统、Git 等）
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from getpass import getpass


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step, text):
    """打印步骤"""
    print(f"\n[步骤 {step}] {text}")


def check_npx():
    """检查 npx 是否可用"""
    try:
        result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ npx 已安装 (版本：{result.stdout.strip()})")
            return True
        else:
            print("❌ npx 未找到")
            return False
    except FileNotFoundError:
        print("❌ npx 未找到，请先安装 Node.js")
        print("   下载地址：https://nodejs.org/")
        return False
    except Exception as e:
        print(f"❌ 检查失败：{e}")
        return False


def get_github_token():
    """获取 GitHub Token"""
    print("\n获取 GitHub Token:")
    print("1. 访问：https://github.com/settings/tokens")
    print("2. 点击 'Generate new token (classic)'")
    print("3. 勾选权限：repo, workflow, read:org")
    print("4. 生成并复制 Token")
    print()
    
    while True:
        token = getpass("请输入 GitHub Token: ")
        if token.startswith("ghp_") or token.startswith("github_pat_"):
            print("✅ Token 格式正确")
            return token
        else:
            print("⚠️  Token 格式可能不正确，GitHub Token 通常以 'ghp_' 或 'github_pat_' 开头")
            retry = input("是否重新输入？(y/n): ").lower()
            if retry != 'y':
                return None


def get_brave_api_key():
    """获取 Brave API Key"""
    print("\n获取 Brave Search API Key:")
    print("1. 访问：https://brave.com/search/api/")
    print("2. 注册并创建 API Key")
    print("3. 复制 API Key")
    print()
    
    api_key = input("请输入 Brave API Key (可直接回车跳过): ").strip()
    return api_key if api_key else None


def create_config(github_token, brave_api_key=None):
    """创建 MCP 配置文件"""
    config_dir = Path.home() / ".ymcode" / "mcp"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        "mcpServers": {
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_TOKEN": github_token
                }
            },
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                "env": {
                    "ALLOWED_PATHS": str(Path.home())
                }
            },
            "git": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-git"]
            }
        }
    }
    
    # 如果提供了 Brave API Key，添加配置
    if brave_api_key:
        config["mcpServers"]["brave-search"] = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-brave-search"],
            "env": {
                "BRAVE_API_KEY": brave_api_key
            }
        }
    
    config_file = config_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 配置文件已创建：{config_file}")
    return config_file


def install_servers():
    """预安装 MCP 服务器"""
    print("\n预安装 MCP 服务器（加速首次启动）...")
    
    servers = [
        "@modelcontextprotocol/server-github",
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-git",
    ]
    
    for server in servers:
        print(f"  安装 {server}...")
        try:
            result = subprocess.run(
                ["npx", "-y", server, "--help"],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print(f"    ✅ {server} 安装成功")
            else:
                print(f"    ⚠️  {server} 安装警告：{result.stderr[:100]}")
        except Exception as e:
            print(f"    ⚠️  {server} 安装失败：{e}")


def test_github_connection(github_token):
    """测试 GitHub 连接"""
    print("\n测试 GitHub 连接...")
    
    try:
        import requests
        
        headers = {"Authorization": f"token {github_token}"}
        response = requests.get(
            "https://api.github.com/user",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user = response.json()
            print(f"✅ GitHub 连接成功！")
            print(f"   用户：{user['login']}")
            print(f"   名称：{user.get('name', 'N/A')}")
            return True
        else:
            print(f"❌ GitHub 连接失败：{response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  未安装 requests 库，跳过测试")
        print("   安装：pip install requests")
        return None
    except Exception as e:
        print(f"⚠️  测试失败：{e}")
        return None


def main():
    """主函数"""
    print_header("YM-CODE MCP 服务器配置向导")
    
    # 步骤 1: 检查 npx
    print_step(1, "检查环境")
    if not check_npx():
        print("\n❌ 请先安装 Node.js (https://nodejs.org/)")
        sys.exit(1)
    
    # 步骤 2: 获取 GitHub Token
    print_step(2, "配置 GitHub")
    github_token = get_github_token()
    if not github_token:
        print("\n⚠️  未配置 GitHub Token，跳过 GitHub 功能")
    
    # 步骤 3: 获取 Brave API Key（可选）
    print_step(3, "配置网络搜索（可选）")
    brave_api_key = get_brave_api_key()
    
    # 步骤 4: 创建配置文件
    print_step(4, "创建配置")
    config_file = create_config(github_token, brave_api_key)
    
    # 步骤 5: 预安装服务器
    print_step(5, "预安装 MCP 服务器")
    install_servers()
    
    # 步骤 6: 测试连接
    if github_token:
        print_step(6, "测试连接")
        test_github_connection(github_token)
    
    # 完成
    print_header("配置完成！")
    print(f"\n✅ MCP 服务器配置已完成")
    print(f"\n配置文件：{config_file}")
    print(f"\n使用方法:")
    print(f"  1. 启动 YM-CODE: python -m ymcode")
    print(f"  2. 使用 GitHub 功能：直接说 '列出我的 GitHub 仓库'")
    print(f"  3. 使用文件搜索：'搜索项目中的 Python 文件'")
    if brave_api_key:
        print(f"  4. 使用网络搜索：'搜索最新的 AI 新闻'")
    
    print(f"\n可用的 MCP 服务器:")
    print(f"  ✅ GitHub - 管理 Issues、PRs、仓库")
    print(f"  ✅ 文件系统 - 安全访问文件")
    print(f"  ✅ Git - Git 操作")
    if brave_api_key:
        print(f"  ✅ Brave Search - 网络搜索")
    
    print(f"\n查看配置详情：cat {config_file}")
    print()


if __name__ == "__main__":
    main()
