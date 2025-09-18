"""
프로젝트 설정 관리자
================================================================================
환경 설정, 데이터베이스 연결, XML 생성 옵션 등을 관리
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """설정 관리 클래스"""
    
    DEFAULT_CONFIG = {
        "app": {
            "name": "HDGRACE BAS Final XML Generator",
            "version": "1.0.0",
            "environment": "production",
            "debug": False
        },
        "server": {
            "host": "0.0.0.0",
            "port": 8000,
            "workers": 4,
            "timeout": 300
        },
        "database": {
            "type": "sqlite",
            "host": "localhost",
            "port": 5432,
            "name": "hdgrace.db",
            "user": "hdgrace",
            "password": "",
            "pool_size": 20,
            "pool_overflow": 50,
            "echo": False
        },
        "xml_generator": {
            "target_features": 7170,
            "target_size_mb": 700,
            "bas_version": "29.3.1",
            "max_generation_time": 600,
            "output_path": "./output",
            "template_path": "./templates",
            "validation_enabled": True,
            "correction_enabled": True,
            "compression_enabled": False
        },
        "features": {
            "youtube_automation": 1000,
            "proxy_management": 800,
            "security_detection": 700,
            "ui_interface": 600,
            "system_monitoring": 500,
            "optimization_algorithms": 450,
            "data_processing": 400,
            "network_communication": 350,
            "file_management": 300,
            "encryption_security": 280,
            "scheduling": 250,
            "logging": 220,
            "error_handling": 200,
            "performance_monitoring": 180,
            "automation_scripts": 160,
            "web_crawling": 140,
            "api_integration": 120,
            "database": 100,
            "email_automation": 90,
            "sms_integration": 80,
            "captcha_solving": 70,
            "image_processing": 60,
            "text_analysis": 50,
            "machine_learning": 40,
            "ai_integration": 30
        },
        "ui": {
            "theme": "modern",
            "language": "ko",
            "components": {
                "buttons": True,
                "toggles": True,
                "inputs": True,
                "selects": True,
                "charts": True,
                "tables": True,
                "modals": True,
                "notifications": True
            },
            "responsive": True,
            "dark_mode": True
        },
        "validation": {
            "schema_validation": True,
            "syntax_checking": True,
            "integrity_check": True,
            "performance_check": True,
            "security_scan": True
        },
        "correction": {
            "auto_fix": True,
            "grammar_rules": 1500000,
            "min_corrections": 59000,
            "backup_original": True
        },
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file_path": "./logs/hdgrace.log",
            "max_size": "100MB",
            "backup_count": 10,
            "rotation": "daily"
        },
        "security": {
            "secret_key": "hdgrace-secret-key-change-in-production",
            "algorithm": "HS256",
            "token_expire": 3600,
            "cors_origins": ["http://localhost:3000", "http://localhost:8000"],
            "max_requests_per_minute": 1000
        },
        "performance": {
            "cache_enabled": True,
            "cache_ttl": 3600,
            "max_concurrent_tasks": 100,
            "timeout": 300,
            "retry_attempts": 3,
            "batch_size": 1000
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "./config.json"
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 기본 설정과 사용자 설정 병합
                config = self._merge_configs(self.DEFAULT_CONFIG, user_config)
                return config
            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패: {e}")
                print("기본 설정을 사용합니다.")
        
        # 기본 설정 파일 생성
        self._save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """설정 병합"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _save_config(self, config: Dict[str, Any]):
        """설정 파일 저장"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 설정 파일 저장 실패: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 가져오기"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """설정 값 설정"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        
        # 설정 파일 저장
        self._save_config(self.config)
    
    def get_database_url(self) -> str:
        """데이터베이스 URL 생성"""
        db_config = self.get('database')
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'sqlite':
            db_path = Path(db_config.get('name', 'hdgrace.db'))
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f"sqlite:///{db_path}"
        elif db_type == 'postgresql':
            return (f"postgresql://{db_config.get('user')}:"
                   f"{db_config.get('password')}@"
                   f"{db_config.get('host')}:"
                   f"{db_config.get('port')}/"
                   f"{db_config.get('name')}")
        else:
            raise ValueError(f"지원하지 않는 데이터베이스 타입: {db_type}")
    
    def validate(self) -> bool:
        """설정 유효성 검사"""
        required_keys = [
            'app.name',
            'server.host',
            'server.port',
            'database.type',
            'xml_generator.target_features'
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                print(f"❌ 필수 설정 누락: {key}")
                return False
        
        return True