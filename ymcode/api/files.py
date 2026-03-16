#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件浏览器 API - 文件系统操作
"""

import os
import stat
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/files", tags=["files"])


# ==================== 数据模型 ====================

class FileInfo(BaseModel):
    name: str
    path: str
    type: str  # file, directory
    size: int = 0
    modified: str = ""
    created: str = ""
    ext: str = ""


class FileListResponse(BaseModel):
    path: str
    files: List[FileInfo]
    total: int


class FileOperation(BaseModel):
    source: str
    target: Optional[str] = None
    content: Optional[str] = None


# ==================== 辅助函数 ====================

def get_file_info(path: Path) -> FileInfo:
    """获取文件信息"""
    try:
        stat_info = path.stat()
        
        # 文件类型
        file_type = "directory" if path.is_dir() else "file"
        
        # 大小
        size = stat_info.st_size if path.is_file() else 0
        
        # 时间
        modified = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        created = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        
        # 扩展名
        ext = path.suffix.lower() if path.is_file() else ""
        
        return FileInfo(
            name=path.name,
            path=str(path),
            type=file_type,
            size=size,
            modified=modified,
            created=created,
            ext=ext
        )
    except Exception as e:
        logger.error(f"获取文件信息失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


def safe_path(base: str, user_path: str) -> Path:
    """安全检查路径，防止目录遍历攻击"""
    base_path = Path(base).resolve()
    
    # 如果是绝对路径
    if Path(user_path).is_absolute():
        target = Path(user_path).resolve()
    else:
        target = (base_path / user_path).resolve()
    
    # 确保目标路径在允许范围内
    # 允许访问：工作空间、用户目录、D 盘
    allowed_bases = [
        Path.home(),
        Path.cwd(),
        Path("D:\\").resolve() if os.name == 'nt' else None,
    ]
    allowed_bases = [p for p in allowed_bases if p]
    
    is_allowed = any(str(target).startswith(str(base)) for base in allowed_bases)
    
    if not is_allowed:
        raise HTTPException(
            status_code=403,
            detail=f"无权访问该路径：{target}"
        )
    
    return target


# ==================== API 端点 ====================

@router.get("/list")
async def list_files(path: str = None):
    """列出目录内容"""
    try:
        # 默认路径
        if not path:
            path = str(Path.cwd())
        
        # 安全检查
        target_path = safe_path(Path.cwd(), path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="路径不存在")
        
        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail="不是目录")
        
        # 列出文件
        files = []
        try:
            for item in target_path.iterdir():
                try:
                    files.append(get_file_info(item))
                except Exception as e:
                    logger.warning(f"跳过文件 {item}: {e}")
        except PermissionError:
            raise HTTPException(status_code=403, detail="无权限访问该目录")
        
        # 排序：目录在前，文件在后
        files.sort(key=lambda x: (x.type == "file", x.name.lower()))
        
        return FileListResponse(
            path=str(target_path),
            files=files,
            total=len(files)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"列出文件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_file_info_endpoint(path: str):
    """获取文件/目录详情"""
    try:
        target_path = safe_path(Path.cwd(), path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return get_file_info(target_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文件信息失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/read")
async def read_file(path: str, lines: int = 100):
    """读取文件内容"""
    try:
        target_path = safe_path(Path.cwd(), path)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if not target_path.is_file():
            raise HTTPException(status_code=400, detail="不是文件")
        
        # 检查文件大小
        if target_path.stat().st_size > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="文件太大（最大 10MB）")
        
        # 读取文件
        try:
            content = target_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # 尝试 GBK 编码
            content = target_path.read_text(encoding='gbk', errors='replace')
        
        # 限制行数
        lines_list = content.split('\n')[:lines]
        content_limited = '\n'.join(lines_list)
        
        return {
            "path": str(target_path),
            "content": content_limited,
            "total_lines": len(content.split('\n')),
            "returned_lines": len(lines_list)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"读取文件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/write")
async def write_file(op: FileOperation):
    """写入文件"""
    try:
        target_path = safe_path(Path.cwd(), op.source)
        
        # 创建父目录
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入内容
        target_path.write_text(op.content or "", encoding='utf-8')
        
        return {
            "success": True,
            "path": str(target_path),
            "message": "文件已保存"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"写入文件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_file(op: FileOperation):
    """创建文件或目录"""
    try:
        target_path = safe_path(Path.cwd(), op.source)
        
        if target_path.exists():
            raise HTTPException(status_code=400, detail="文件/目录已存在")
        
        # 创建目录
        target_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(target_path),
            "type": "directory",
            "message": "目录已创建"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建文件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/delete")
async def delete_file(op: FileOperation):
    """删除文件或目录"""
    try:
        target_path = safe_path(Path.cwd(), op.source)
        
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 删除
        if target_path.is_dir():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()
        
        return {
            "success": True,
            "path": str(target_path),
            "message": "已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/move")
async def move_file(op: FileOperation):
    """移动/重命名文件"""
    try:
        if not op.target:
            raise HTTPException(status_code=400, detail="需要指定目标路径")
        
        source_path = safe_path(Path.cwd(), op.source)
        target_path = safe_path(Path.cwd(), op.target)
        
        if not source_path.exists():
            raise HTTPException(status_code=404, detail="源文件不存在")
        
        # 移动
        shutil.move(str(source_path), str(target_path))
        
        return {
            "success": True,
            "source": str(source_path),
            "target": str(target_path),
            "message": "已移动"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"移动文件失败：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/drives")
async def list_drives():
    """列出可用驱动器（Windows）"""
    if os.name != 'nt':
        # Linux/Mac
        return {
            "drives": [
                {"name": "/", "type": "root", "path": "/"}
            ]
        }
    
    # Windows
    import string
    drives = []
    
    for letter in string.ascii_uppercase:
        drive_path = f"{letter}:\\"
        if os.path.exists(drive_path):
            drives.append({
                "name": f"{letter}: 盘",
                "type": "drive",
                "path": drive_path
            })
    
    return {"drives": drives}
