#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edit History - 编辑历史管理（Undo/Redo）

融合课程：s07 (Task System) + 生产级编辑历史
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EditRecord:
    """编辑记录"""
    id: str
    file_path: str
    old_content: str
    new_content: str
    timestamp: str
    operation: str  # replace/insert/delete
    metadata: Dict = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EditRecord':
        """从字典创建"""
        return cls(**data)


class EditHistory:
    """编辑历史管理器"""
    
    def __init__(self, history_dir: Path = None, max_history: int = 50):
        """
        初始化编辑历史
        
        参数:
            history_dir: 历史存储目录
            max_history: 最大历史记录数
        """
        self.history_dir = history_dir or Path.home() / ".ymcode" / "edit_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_history = max_history
        self.file_histories: Dict[str, List[EditRecord]] = {}
        
        # 加载现有历史
        self._load_histories()
        
        logger.info(f"编辑历史初始化完成，目录：{self.history_dir}")
    
    def _get_history_file(self, file_path: str) -> Path:
        """
        获取历史文件路径
        
        参数:
            file_path: 原文件路径
        
        返回:
            历史文件路径
        """
        # 使用文件路径的 hash 作为历史文件名
        import hashlib
        path_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.history_dir / f"{path_hash}.json"
    
    def _load_histories(self):
        """加载所有历史"""
        for history_file in self.history_dir.glob("*.json"):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    records = [EditRecord.from_dict(r) for r in data.get("records", [])]
                    
                    # 找到原文件路径
                    if records:
                        file_path = records[0].file_path
                        self.file_histories[file_path] = records
            except Exception as e:
                logger.error(f"加载历史失败 {history_file}: {e}")
    
    def add_record(self, record: EditRecord):
        """
        添加编辑记录
        
        参数:
            record: 编辑记录
        """
        file_path = record.file_path
        
        if file_path not in self.file_histories:
            self.file_histories[file_path] = []
        
        # 添加记录
        self.file_histories[file_path].append(record)
        
        # 限制历史记录数量
        if len(self.file_histories[file_path]) > self.max_history:
            self.file_histories[file_path] = self.file_histories[file_path][-self.max_history:]
        
        # 保存到文件
        self._save_history(file_path)
        
        logger.info(f"添加编辑记录：{file_path} ({record.operation})")
    
    def _save_history(self, file_path: str):
        """
        保存历史到文件
        
        参数:
            file_path: 原文件路径
        """
        history_file = self._get_history_file(file_path)
        records = self.file_histories.get(file_path, [])
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({
                "file_path": file_path,
                "records": [r.to_dict() for r in records],
                "last_updated": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
    
    def undo(self, file_path: str) -> Optional[EditRecord]:
        """
        撤销操作
        
        参数:
            file_path: 文件路径
        
        返回:
            编辑记录（用于恢复）
        """
        if file_path not in self.file_histories:
            return None
        
        records = self.file_histories[file_path]
        if not records:
            return None
        
        # 获取最后一条记录
        last_record = records.pop()
        
        # 保存更新后的历史
        self._save_history(file_path)
        
        logger.info(f"撤销操作：{file_path}")
        
        return last_record
    
    def redo(self, file_path: str, record: EditRecord) -> bool:
        """
        重做操作
        
        参数:
            file_path: 文件路径
            record: 编辑记录
        
        返回:
            是否成功
        """
        if file_path not in self.file_histories:
            self.file_histories[file_path] = []
        
        # 添加记录
        self.file_histories[file_path].append(record)
        self._save_history(file_path)
        
        logger.info(f"重做操作：{file_path}")
        
        return True
    
    def get_history(self, file_path: str, limit: int = 10) -> List[EditRecord]:
        """
        获取历史记录
        
        参数:
            file_path: 文件路径
            limit: 返回数量
        
        返回:
            编辑记录列表
        """
        if file_path not in self.file_histories:
            return []
        
        records = self.file_histories[file_path]
        return records[-limit:]
    
    def clear_history(self, file_path: str = None):
        """
        清空历史
        
        参数:
            file_path: 文件路径（可选，清空所有）
        """
        if file_path:
            if file_path in self.file_histories:
                self.file_histories[file_path] = []
                history_file = self._get_history_file(file_path)
                if history_file.exists():
                    history_file.unlink()
        else:
            self.file_histories = {}
            for history_file in self.history_dir.glob("*.json"):
                history_file.unlink()
        
        logger.info("清空编辑历史")
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        返回:
            统计字典
        """
        total_records = sum(len(records) for records in self.file_histories.values())
        
        return {
            "total_files": len(self.file_histories),
            "total_records": total_records,
            "max_history_per_file": self.max_history,
            "history_dir": str(self.history_dir)
        }


class EditHistoryManager:
    """编辑历史管理器（工具类）"""
    
    def __init__(self, history_dir=None):
        """初始化"""
        from pathlib import Path
        self.history = EditHistory(history_dir=history_dir or Path.home() / ".ymcode" / "edit_history")
    
    def record_edit(self, file_path: str, old_content: str, new_content: str, operation: str = "replace") -> str:
        """
        记录编辑
        
        参数:
            file_path: 文件路径
            old_content: 原内容
            new_content: 新内容
            operation: 操作类型
        
        返回:
            记录 ID
        """
        import uuid
        
        record = EditRecord(
            id=str(uuid.uuid4())[:8],
            file_path=file_path,
            old_content=old_content,
            new_content=new_content,
            timestamp=datetime.now().isoformat(),
            operation=operation
        )
        
        self.history.add_record(record)
        
        return record.id
    
    def undo_last_edit(self, file_path: str) -> Optional[Dict]:
        """
        撤销最后一次编辑
        
        参数:
            file_path: 文件路径
        
        返回:
            编辑信息
        """
        record = self.history.undo(file_path)
        
        if not record:
            return None
        
        return {
            "success": True,
            "message": f"已撤销操作 {record.id}",
            "old_content": record.old_content,
            "operation": record.operation
        }
    
    def get_edit_history(self, file_path: str, limit: int = 5) -> List[Dict]:
        """
        获取编辑历史
        
        参数:
            file_path: 文件路径
            limit: 返回数量
        
        返回:
            历史记录列表
        """
        records = self.history.get_history(file_path, limit)
        
        return [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "operation": r.operation
            }
            for r in records
        ]
