#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDGRACE UI 헬퍼 모듈
UI 기능 보조 및 유틸리티
"""

def create_theme_config():
    """테마 설정 생성"""
    return {
        "primary_color": "#007acc",
        "secondary_color": "#ff6b35", 
        "background_color": "#2b2b2b",
        "text_color": "#ffffff",
        "success_color": "#00ff00",
        "error_color": "#ff0000",
        "warning_color": "#ffaa00"
    }

def format_file_size(size_bytes):
    """파일 크기 포맷팅"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f}{size_names[i]}"

def validate_input(value, input_type):
    """입력값 검증"""
    if input_type == "number":
        try:
            return float(value) >= 0
        except ValueError:
            return False
    elif input_type == "path":
        return os.path.exists(value) if value else False
    return bool(value)
