# Agent 配置界面使用指南

**版本：** v0.6.0  
**更新时间：** 2026-03-16

---

## 🎯 什么是 Agent 配置界面？

**Web 界面的 Agent 选择和配置工具**，让你可以通过可视化界面：
- ✅ 创建新工作区
- ✅ 选择需要的 Agent
- ✅ 配置 Agent 参数
- ✅ 管理工作区团队

---

## 🚀 快速开始

### 1. 打开配置界面

**方式 1：直接访问**
```
http://localhost:18770/agent-config.html
```

**方式 2：从主界面**
1. 打开 http://localhost:18770
2. 点击顶部导航的 **[+ 新建项目]**
3. 自动跳转到 Agent 配置界面

---

### 2. 创建工作区

**步骤 1：填写工作区信息**
```
工作区名称：电商系统开发
工作区描述：开发完整的 Flask 电商系统，包含用户管理、商品管理、订单处理
```

**步骤 2：选择 Agent**
- 点击 Agent 卡片选择（卡片变绿表示已选择）
- 再次点击取消选择

**推荐配置：**

**Web 开发项目：**
- ✅ FlaskDeveloper (后端)
- ✅ FrontendExpert (前端)
- ✅ DatabaseDesigner (数据库)
- ✅ Tester (测试)

**数据分析项目：**
- ✅ DataAnalyst (数据分析)
- ✅ VisualizationExpert (可视化)
- ✅ MLEngineer (机器学习)

**学习项目：**
- ✅ PythonTutor (教学)
- ✅ CodeReviewer (代码审查)
- ✅ Debugger (调试)

**步骤 3：保存配置**
点击 **[💾 保存工作区配置]** 按钮

---

## 📋 界面说明

### 顶部区域：工作区信息

```
┌─────────────────────────────────────┐
│ 📁 工作区信息                       │
├─────────────────────────────────────┤
│ 工作区名称：[电商系统开发    ]      │
│ 工作区描述：[开发完整的 Fl... ]     │
└─────────────────────────────────────┘
```

### 中间区域：Agent 选择

```
┌─────────────────────────────────────┐
│ 👥 选择 Agent (点击卡片选择)        │
├───────────┬───────────┬─────────────┤
│ 🤖        │ 🤖        │ 🤖          │
│ PythonCod │ TestExper │ CodeReviewe │
│ code_gene │ tester    │ reviewer    │
│ Python 代 │ 编写单元  │ 代码审查    │
│ [python]  │ [pytest]  │ [code_revi] │
│ [fastapi] │ [unittest]│ [security]  │
│ ✓         │           │             │
└───────────┴───────────┴─────────────┘
```

### 底部区域：已选择的 Agent

```
┌─────────────────────────────────────┐
│ 已选择的 Agent:                     │
│ [PythonCoder ✕] [Tester ✕]          │
├─────────────────────────────────────┤
│ [💾 保存] [🔄 刷新] [🗑️ 清除]       │
└─────────────────────────────────────┘
```

---

## 💡 使用技巧

### 1. 快速选择

**全选快捷键：**
- 按 `Ctrl + A` 全选所有 Agent
- 按 `Esc` 清除所有选择

**快速筛选：**
- 在搜索框输入关键词
- 实时过滤 Agent 列表

### 2. 查看 Agent 详情

**鼠标悬停：**
- 查看完整描述
- 查看所有能力标签
- 查看使用示例

### 3. 批量操作

**批量选择：**
1. 点击第一个 Agent
2. 按住 `Shift`
3. 点击最后一个 Agent
4. 批量选中

**批量取消：**
- 点击 **[🗑️ 清除所有选择]**

---

## 🎯 常见场景

### 场景 1：新建 Web 项目

**配置：**
```
工作区名称：Flask 电商系统
工作区描述：完整的电商系统开发

选择 Agent:
✅ FlaskDeveloper
✅ FrontendExpert
✅ DatabaseDesigner
✅ Tester
✅ DocWriter
```

**保存后：**
- 自动跳转到工作区
- 开始分配任务

---

### 场景 2：数据分析项目

**配置：**
```
工作区名称：销售数据分析
工作区描述：分析销售数据，生成可视化报告

选择 Agent:
✅ DataAnalyst
✅ VisualizationExpert
✅ ReportWriter
```

---

### 场景 3：学习 Python

**配置：**
```
工作区名称：Python 入门学习
工作区描述：从零开始学习 Python

选择 Agent:
✅ PythonTutor
✅ CodeReviewer
✅ Debugger
✅ ExerciseGenerator
```

---

## 🔧 高级功能

### 1. 自定义 Agent

**在配置界面创建自定义 Agent：**

1. 点击 **[+ 创建自定义 Agent]**
2. 填写信息：
   ```
   名称：MyCustomAgent
   角色：custom_role
   描述：我的自定义 Agent
   能力：["python", "custom_logic"]
   ```
3. 点击 **[创建]**
4. 新 Agent 出现在列表中
5. 选择并保存

---

### 2. 导出工作区配置

**导出配置：**
```javascript
// 在浏览器控制台
const config = {
    name: workspace.name,
    description: workspace.description,
    agents: selectedAgents
};

console.log(JSON.stringify(config, null, 2));
```

**导入配置：**
```javascript
// 在浏览器控制台
const config = {
    name: "电商系统",
    agents: ["FlaskDeveloper", "Tester", ...]
};

// 自动填充表单
document.getElementById('workspaceName').value = config.name;
config.agents.forEach(name => toggleAgent(name));
```

---

### 3. 工作区模板

**保存为模板：**
```javascript
// 保存当前配置为模板
const template = {
    name: "Web 项目模板",
    defaultAgents: [
        "FlaskDeveloper",
        "FrontendExpert",
        "Tester"
    ]
};

localStorage.setItem('template_web', JSON.stringify(template));
```

**使用模板：**
```javascript
// 加载模板
const template = JSON.parse(
    localStorage.getItem('template_web')
);

document.getElementById('workspaceName').value = template.name;
template.defaultAgents.forEach(name => toggleAgent(name));
```

---

## 📊 Agent 推荐配置

### Web 开发

| 项目类型 | 推荐 Agent |
|---------|-----------|
| Flask 后端 | FlaskDeveloper, DatabaseDesigner, Tester |
| React 前端 | ReactDeveloper, UIExpert, Tester |
| 全栈项目 | FlaskDeveloper, ReactDeveloper, DatabaseDesigner, Tester |
| API 开发 | APIDesigner, FlaskDeveloper, DocWriter |

### 数据分析

| 项目类型 | 推荐 Agent |
|---------|-----------|
| 数据清洗 | DataAnalyst, PythonCoder |
| 可视化 | VisualizationExpert, DataAnalyst |
| 机器学习 | MLEngineer, DataAnalyst, PythonCoder |
| 报告生成 | ReportWriter, DataAnalyst |

### 学习

| 学习目标 | 推荐 Agent |
|---------|-----------|
| Python 入门 | PythonTutor, CodeReviewer |
| 算法学习 | AlgorithmTutor, Debugger |
| 项目实战 | ProjectMentor, CodeReviewer, Debugger |

---

## ❓ 常见问题

### Q: 最少需要选择几个 Agent？

**A:** 最少 1 个，推荐 3-5 个。

- 1 个：单一功能
- 3 个：基本协作
- 5 个：完整团队

---

### Q: 可以后期添加 Agent 吗？

**A:** 可以！

1. 进入工作区设置
2. 点击 **[管理 Agent]**
3. 添加新 Agent

---

### Q: Agent 选择错误怎么办？

**A:** 随时可以修改！

- 移除：点击 Agent 标签的 **✕**
- 添加：重新点击 Agent 卡片
- 重置：点击 **[🗑️ 清除所有选择]**

---

### Q: 工作区可以删除吗？

**A:** 可以！

1. 进入工作区列表
2. 点击工作区的 **[⋮]** 菜单
3. 选择 **[删除工作区]**

---

## 🎨 UI/UX 优化建议

### 1. 响应式设计

```css
/* 移动端适配 */
@media (max-width: 768px) {
    .agent-grid {
        grid-template-columns: 1fr;
    }
    
    .workspace-form {
        grid-template-columns: 1fr;
    }
}
```

### 2. 加载动画

```javascript
async function loadAgents() {
    // 显示加载动画
    showLoading();
    
    try {
        const response = await fetch(...);
        const data = await response.json();
        allAgents = data.skills;
        renderAgents();
    } finally {
        hideLoading();
    }
}
```

### 3. 错误处理

```javascript
try {
    await saveWorkspace();
} catch (error) {
    showErrorToast('保存失败：' + error.message);
}
```

---

**最后更新：** 2026-03-16  
**维护者：** YM-CODE Team
