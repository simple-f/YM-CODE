import re

with open('dashboard_api.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_root = '@app.get("/")\nasync def root():\n    """根路径"""\n    return {\n        "name": "YM-CODE Dashboard API",\n        "version": "1.0.0",\n        "status": "running"\n    }'

new_root = '@app.get("/", response_class=HTMLResponse)\nasync def root():\n    """根路径 - 返回 Dashboard 页面"""\n    html_path = Path(__file__).parent / "agents.html"\n    if html_path.exists():\n        return FileResponse(str(html_path))\n    return {"error": "Dashboard page not found"}\n\n\n@app.get("/agents.html", response_class=HTMLResponse)\nasync def agents_page():\n    """Agent 管理页面"""\n    html_path = Path(__file__).parent / "agents.html"\n    if html_path.exists():\n        return FileResponse(str(html_path))\n    raise HTTPException(status_code=404, detail="Page not found")'

content = content.replace(old_root, new_root)

with open('dashboard_api.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
