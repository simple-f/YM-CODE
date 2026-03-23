# 修复 dashboard_api.py 路由
with open('dashboard_api.py.bak', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 查找并替换根路径
    if line.strip() == '@app.get("/")':
        new_lines.append('@app.get("/", response_class=HTMLResponse)\n')
        i += 1
        # 替换 docstring
        if i < len(lines) and '"""根路径"""' in lines[i]:
            new_lines.append('    """根路径 - 返回 Dashboard 页面"""\n')
            i += 1
            # 插入文件服务逻辑
            new_lines.append('    html_path = Path(__file__).parent / "agents.html"\n')
            new_lines.append('    if html_path.exists():\n')
            new_lines.append('        return FileResponse(str(html_path))\n')
            new_lines.append('    return {"error": "Dashboard page not found"}\n')
            new_lines.append('\n')
            new_lines.append('\n')
            new_lines.append('@app.get("/agents.html", response_class=HTMLResponse)\n')
            new_lines.append('async def agents_page():\n')
            new_lines.append('    """Agent 管理页面"""\n')
            new_lines.append('    html_path = Path(__file__).parent / "agents.html"\n')
            new_lines.append('    if html_path.exists():\n')
            new_lines.append('        return FileResponse(str(html_path))\n')
            new_lines.append('    raise HTTPException(status_code=404, detail="Page not found")\n')
            continue
    
    new_lines.append(line)
    i += 1

with open('dashboard_api.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Fixed!')
