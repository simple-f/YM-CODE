# YM-CODE 安装指南

**版本：** v1.0.0  
**更新时间：** 2026-03-16

---

## 📋 系统要求

### 最低要求

- **Python:** 3.10+
- **内存:** 2GB
- **磁盘:** 500MB

### 推荐配置

- **Python:** 3.13
- **内存:** 4GB+
- **磁盘:** 1GB+

---

## 🚀 快速安装

### 1. 克隆仓库

```bash
git clone https://github.com/simple-f/YM-CODE.git
cd YM-CODE
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化系统

```bash
python init.py
```

### 5. 配置 API Key

编辑 `.env` 文件：

```bash
DASHSCOPE_API_KEY=sk-your-api-key-here
```

### 6. 启动服务

```bash
python start-web.py
```

### 7. 访问 Web 界面

```
http://localhost:18770
```

---

## 🔧 可选安装

### 代码分析工具

```bash
pip install pylint black flake8
```

### 本地模型支持

```bash
pip install llama-cpp-python
```

### Git 集成

确保 Git 已安装：

```bash
git --version
```

### Node.js（VSCode 插件开发）

```bash
# 安装 Node.js
# https://nodejs.org/

# 验证
node --version
npm --version
```

---

## 📦 VSCode 插件安装

### 方式 1：从市场安装（待发布）

```bash
# 在 VSCode 扩展市场搜索 "YM-CODE"
```

### 方式 2：手动安装

```bash
cd extensions/vscode
npm install
npm run compile

# 在 VSCode 中加载
# 开发者工具 → 加载未打包的扩展
```

---

## 🐛 故障排查

### 问题 1：依赖安装失败

**解决：**

```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt --force-reinstall
```

### 问题 2：API Key 未配置

**解决：**

```bash
# 检查 .env 文件
cat .env

# 确保 API Key 正确
DASHSCOPE_API_KEY=sk-xxx
```

### 问题 3：端口被占用

**解决：**

```bash
# 修改端口
echo "YM_CODE_PORT=18771" >> .env

# 或杀死占用端口的进程
netstat -ano | findstr :18770
taskkill /PID <pid> /F
```

### 问题 4：中文乱码

**解决：**

```bash
# Windows 设置控制台编码
chcp 65001

# 或在 .env 中添加
PYTHONIOENCODING=utf-8
```

---

## 🎯 验证安装

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定版本测试
python tests/test_v070.py
python tests/test_v080.py
python tests/test_v090.py
```

### 检查系统状态

```bash
# 访问健康检查端点
curl http://localhost:18770/health
```

---

## 📝 下一步

- [ ] 阅读 [使用指南](docs/USAGE.md)
- [ ] 查看 [技能系统](docs/SKILLS.md)
- [ ] 配置 [VSCode 插件](extensions/vscode/README.md)

---

**安装完成！开始使用 YM-CODE！** 🎉
