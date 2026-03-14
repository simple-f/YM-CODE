# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

我们非常重视 YM-CODE 的安全性。如果你发现任何安全漏洞，请负责任地披露。

### 如何报告

1. **不要** 创建公开 Issue
2. 发送邮件到：security@ym-code.dev（待设置）
3. 或在 GitHub 上使用 [Private Vulnerability Reporting](https://github.com/your-org/ym-code/security/advisories)

### 报告内容

请提供尽可能详细的信息：

- 漏洞类型
- 复现步骤
- 影响范围
- 可能的利用方式
- 建议的修复方案（如有）

### 响应时间

- **确认收到**: 48 小时内
- **状态更新**: 每周
- **修复时间**: 根据严重程度
  - Critical: 7 天
  - High: 14 天
  - Medium: 30 天
  - Low: 60 天

## Security Best Practices

### 用户责任

- 不要提交敏感的 API Keys 到代码库
- 使用环境变量管理密钥
- 定期更新依赖
- 审查执行的命令

### 项目安全措施

- [x] 依赖漏洞扫描
- [x] 代码审查流程
- [x] 最小权限原则
- [ ] 沙箱执行（计划中）
- [ ] 审计日志（计划中）

## Known Limitations

### Shell 命令执行

YM-CODE 可以执行 Shell 命令，这存在潜在风险：

**缓解措施:**
- 命令黑名单/白名单
- 用户确认机制
- 沙箱执行（计划中）

**建议:**
- 在生产环境禁用 Shell 命令
- 使用只读模式
- 审计所有执行的命令

### API Keys

**建议:**
- 使用环境变量
- 定期轮换密钥
- 限制 API 权限
- 监控使用情况

## Security Updates

安全更新将通过以下方式通知：

- GitHub Security Advisories
- Release Notes
- 邮件列表（计划中）

## Acknowledgments

感谢以下安全研究者：

- （待添加）

---

**Last Updated:** 2026-03-14
