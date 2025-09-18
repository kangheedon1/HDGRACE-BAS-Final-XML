"""
데이터베이스 연동 모듈
================================================================================
SQLite/PostgreSQL 데이터베이스 연결 및 관리
"""

import asyncio
import aiosqlite
import sqlite3
from typing import Dict, List, Any, Optional, AsyncGenerator
from pathlib import Path
from datetime import datetime

from modules.logger import LoggerMixin

class DatabaseManager(LoggerMixin):
    """데이터베이스 관리자"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = Path(config.get('name', 'hdgrace.db'))
        self.connection = None
        
    async def initialize(self):
        """데이터베이스 초기화"""
        self.logger.info("💾 데이터베이스 초기화 시작")
        
        # 데이터베이스 디렉토리 생성
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 연결
        await self.connect()
        
        # 테이블 생성
        await self.create_tables()
        
        # 기본 데이터 삽입
        await self.insert_default_data()
        
        self.logger.info("✅ 데이터베이스 초기화 완료")
    
    async def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            self.connection.row_factory = aiosqlite.Row
            self.logger.info(f"📂 데이터베이스 연결: {self.db_path}")
        except Exception as e:
            self.logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            raise
    
    async def disconnect(self):
        """데이터베이스 연결 해제"""
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.logger.info("🔌 데이터베이스 연결 해제")
    
    async def create_tables(self):
        """테이블 생성"""
        tables = [
            # 기능 테이블
            """
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                description TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                visible BOOLEAN DEFAULT TRUE,
                emoji TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # UI 요소 테이블
            """
            CREATE TABLE IF NOT EXISTS ui_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id INTEGER,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT,
                position_x INTEGER DEFAULT 0,
                position_y INTEGER DEFAULT 0,
                width INTEGER DEFAULT 120,
                height INTEGER DEFAULT 40,
                visible BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feature_id) REFERENCES features (id)
            )
            """,
            
            # 액션 테이블
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id INTEGER,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                parameters TEXT,
                order_index INTEGER DEFAULT 0,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feature_id) REFERENCES features (id)
            )
            """,
            
            # 매크로 테이블
            """
            CREATE TABLE IF NOT EXISTS macros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                actions TEXT,
                enabled BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # XML 생성 기록 테이블
            """
            CREATE TABLE IF NOT EXISTS xml_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                features_count INTEGER,
                ui_elements_count INTEGER,
                actions_count INTEGER,
                macros_count INTEGER,
                generation_time REAL,
                status TEXT DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 사용자 계정 테이블
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT,
                proxy TEXT,
                status TEXT DEFAULT '정상',
                cookies TEXT,
                fingerprint TEXT,
                recovery_email TEXT,
                two_factor_auth TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 시스템 로그 테이블
            """
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                function TEXT,
                line_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # 설정 테이블
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL UNIQUE,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        ]
        
        for table_sql in tables:
            try:
                await self.connection.execute(table_sql)
                await self.connection.commit()
            except Exception as e:
                self.logger.error(f"❌ 테이블 생성 실패: {e}")
                raise
        
        self.logger.info("📋 데이터베이스 테이블 생성 완료")
    
    async def insert_default_data(self):
        """기본 데이터 삽입"""
        # 기본 계정 데이터
        default_accounts = [
            ('honggildong', 'abc123', None, '123.45.67.89:11045;u;pw', '정상', 'cookieVal', 'fpVal', None, None),
            ('kimdong', '1q2w3e', None, '98.76.54.32:11045;user01;pass01', '차단', 'ckVal2', 'fpVal2', None, None),
            ('hgildong', 'a1b2c3', None, '45.153.20.233:11045;LD1S4c;zM70gq', '정상', 'cookieA', 'fpA', 'rec@mail.com', None),
            ('userbeta', 'pass789', None, '20.30.40.50:8080;uBeta;pBeta', '점검', 'cookieB', 'fpB', 'recovery@mail', None),
            ('newgmailid', 'pass789', None, '98.76.54.32:11045;u;pw', '정상', 'cookieVal', 'fpVal', 'rec@mail.com', 'JBSWY3DPEHPK3PXP'),
            ('alphauser', 'qwe123!!', None, None, '정상', None, None, 'r@mail.co', None)
        ]
        
        try:
            # 기존 데이터 확인
            async with self.connection.execute("SELECT COUNT(*) FROM accounts") as cursor:
                count = await cursor.fetchone()
                if count[0] == 0:
                    for account in default_accounts:
                        await self.connection.execute(
                            """INSERT INTO accounts 
                               (username, password, email, proxy, status, cookies, fingerprint, recovery_email, two_factor_auth)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            account
                        )
                    await self.connection.commit()
                    self.logger.info(f"👤 기본 계정 {len(default_accounts)}개 생성")
        except Exception as e:
            self.logger.error(f"❌ 기본 데이터 삽입 실패: {e}")
    
    async def execute(self, query: str, params: tuple = ()) -> Any:
        """SQL 쿼리 실행"""
        try:
            async with self.connection.execute(query, params) as cursor:
                if query.strip().upper().startswith('SELECT'):
                    return await cursor.fetchall()
                else:
                    await self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            self.logger.error(f"❌ 쿼리 실행 실패: {query[:50]}... - {e}")
            raise
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """단일 레코드 조회"""
        try:
            async with self.connection.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"❌ 단일 레코드 조회 실패: {e}")
            return None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """여러 레코드 조회"""
        try:
            async with self.connection.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"❌ 다중 레코드 조회 실패: {e}")
            return []
    
    async def insert_feature(self, feature_data: Dict[str, Any]) -> int:
        """기능 데이터 삽입"""
        query = """
            INSERT INTO features (name, category, description, enabled, visible, emoji, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            feature_data.get('name'),
            feature_data.get('category'),
            feature_data.get('description'),
            feature_data.get('enabled', True),
            feature_data.get('visible', True),
            feature_data.get('emoji'),
            str(feature_data.get('parameters', {}))
        )
        
        try:
            cursor = await self.connection.execute(query, params)
            await self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"❌ 기능 데이터 삽입 실패: {e}")
            raise
    
    async def get_features_count(self) -> int:
        """기능 수 조회"""
        result = await self.fetch_one("SELECT COUNT(*) as count FROM features")
        return result['count'] if result else 0
    
    async def get_accounts_count(self) -> int:
        """계정 수 조회"""
        result = await self.fetch_one("SELECT COUNT(*) as count FROM accounts")
        return result['count'] if result else 0
    
    async def log_xml_generation(self, generation_data: Dict[str, Any]) -> int:
        """XML 생성 기록"""
        query = """
            INSERT INTO xml_generations 
            (file_path, file_size, features_count, ui_elements_count, actions_count, macros_count, generation_time, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            generation_data.get('file_path'),
            generation_data.get('file_size'),
            generation_data.get('features_count'),
            generation_data.get('ui_elements_count'),
            generation_data.get('actions_count'),
            generation_data.get('macros_count'),
            generation_data.get('generation_time'),
            generation_data.get('status', 'completed')
        )
        
        try:
            cursor = await self.connection.execute(query, params)
            await self.connection.commit()
            return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"❌ XML 생성 기록 실패: {e}")
            raise