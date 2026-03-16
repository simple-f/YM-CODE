#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密工具模块

提供敏感数据加密功能
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os
import json
from pathlib import Path
from typing import Optional

class Encryptor:
    """加密工具类"""
    
    def __init__(self, key: Optional[str] = None):
        """
        初始化加密器
        
        参数:
            key: 加密密钥（不提供则自动生成）
        """
        if key:
            self.key = key.encode()
        else:
            # 生成新密钥
            self.key = Fernet.generate_key()
        
        self.fernet = Fernet(self.key)
    
    @staticmethod
    def generate_key() -> str:
        """
        生成加密密钥
        
        返回:
            密钥字符串（base64 编码）
        """
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key(password: str, salt: Optional[bytes] = None) -> tuple:
        """
        从密码派生密钥
        
        参数:
            password: 密码
            salt: 盐（可选，不提供则自动生成）
        
        返回:
            (key, salt) 元组
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), salt
    
    def encrypt(self, data: str) -> str:
        """
        加密字符串
        
        参数:
            data: 要加密的字符串
        
        返回:
            加密后的字符串（base64 编码）
        """
        encrypted = self.fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字符串
        
        参数:
            encrypted_data: 加密的字符串
        
        返回:
            解密后的原始字符串
        """
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.fernet.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败：{str(e)}")
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        加密文件
        
        参数:
            file_path: 源文件路径
            output_path: 输出文件路径（可选，默认为原文件.enc）
        
        返回:
            加密文件路径
        """
        if output_path is None:
            output_path = str(file_path) + '.enc'
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.fernet.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        return output_path
    
    def decrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        解密文件
        
        参数:
            file_path: 加密文件路径
            output_path: 输出文件路径（可选，默认为原文件去.enc）
        
        返回:
            解密文件路径
        """
        if output_path is None:
            output_path = str(file_path).replace('.enc', '')
        
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted = self.fernet.decrypt(encrypted_data)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        return output_path


# 全局加密器实例
_encryptor_instance: Optional[Encryptor] = None

def get_encryptor(key: Optional[str] = None) -> Encryptor:
    """获取全局加密器实例"""
    global _encryptor_instance
    if _encryptor_instance is None:
        _encryptor_instance = Encryptor(key)
    return _encryptor_instance

def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据"""
    return get_encryptor().encrypt(data)

def decrypt_sensitive_data(encrypted: str) -> str:
    """解密敏感数据"""
    return get_encryptor().decrypt(encrypted)
