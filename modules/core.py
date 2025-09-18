"""
HDGRACE 핵심 시스템
================================================================================
전체 시스템의 핵심 로직 및 조정자 역할
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from modules.logger import LoggerMixin
from modules.config_manager import ConfigManager
from modules.database import DatabaseManager
from modules.xml_generator import XMLGenerator
from modules.validator import XMLValidator

class HDGRACESystem(LoggerMixin):
    """HDGRACE 시스템 핵심 클래스"""
    
    def __init__(self, config: ConfigManager, logger):
        self.config = config
        self._logger = logger
        self.database = None
        self.xml_generator = None
        self.validator = None
        self.is_initialized = False
        
    async def initialize(self):
        """시스템 초기화"""
        if self.is_initialized:
            return
            
        self.logger.info("🔧 HDGRACE 시스템 초기화 시작")
        
        try:
            # 데이터베이스 초기화
            self.database = DatabaseManager(self.config.get('database'))
            await self.database.initialize()
            
            # XML 생성기 초기화
            self.xml_generator = XMLGenerator(
                self.config.get('xml_generator'),
                self.database
            )
            
            # 검증기 초기화
            self.validator = XMLValidator(self.config.get('xml_generator'))
            
            # 출력 디렉토리 생성
            output_path = Path(self.config.get('xml_generator.output_path', './output'))
            output_path.mkdir(parents=True, exist_ok=True)
            
            self.is_initialized = True
            self.logger.info("✅ HDGRACE 시스템 초기화 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 초기화 실패: {e}")
            raise
    
    async def generate_xml(self, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """XML 생성"""
        if not self.is_initialized:
            await self.initialize()
        
        self.logger.info("🚀 XML 생성 프로세스 시작")
        start_time = time.time()
        
        try:
            # XML 생성
            result = await self.xml_generator.generate_complete_xml()
            
            # 생성된 XML 검증
            if self.config.get('xml_generator.validation_enabled', True):
                self.logger.info("🔍 생성된 XML 검증 중...")
                validation_result = await self.validator.validate_xml_file(result['file_path'])
                result['validation'] = validation_result
                
                if not validation_result['is_valid']:
                    self.logger.warning("⚠️ XML 검증에서 오류가 발견되었습니다")
                else:
                    self.logger.info("✅ XML 검증 통과")
            
            # 총 처리 시간 계산
            total_time = time.time() - start_time
            result['total_processing_time'] = total_time
            
            self.logger.info(f"🎉 XML 생성 완료 (총 {total_time:.2f}초)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ XML 생성 실패: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        try:
            status = {
                "initialized": self.is_initialized,
                "timestamp": datetime.now().isoformat(),
                "database": {
                    "connected": self.database.connection is not None if self.database else False,
                    "features_count": 0,
                    "accounts_count": 0
                },
                "config": {
                    "target_features": self.config.get('xml_generator.target_features'),
                    "target_size_mb": self.config.get('xml_generator.target_size_mb'),
                    "bas_version": self.config.get('xml_generator.bas_version')
                },
                "performance": {
                    "cache_enabled": self.config.get('performance.cache_enabled'),
                    "max_concurrent_tasks": self.config.get('performance.max_concurrent_tasks')
                }
            }
            
            if self.database and self.database.connection:
                status["database"]["features_count"] = await self.database.get_features_count()
                status["database"]["accounts_count"] = await self.database.get_accounts_count()
            
            return status
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 상태 조회 실패: {e}")
            return {"error": str(e)}
    
    async def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """XML 생성 기록 조회"""
        try:
            if not self.database:
                return []
            
            query = """
                SELECT * FROM xml_generations 
                ORDER BY created_at DESC 
                LIMIT ?
            """
            
            history = await self.database.fetch_all(query, (limit,))
            return history
            
        except Exception as e:
            self.logger.error(f"❌ 생성 기록 조회 실패: {e}")
            return []
    
    async def get_features_summary(self) -> Dict[str, Any]:
        """기능 요약 조회"""
        try:
            if not self.database:
                return {}
            
            # 카테고리별 기능 수
            query = """
                SELECT category, COUNT(*) as count 
                FROM features 
                GROUP BY category 
                ORDER BY count DESC
            """
            
            category_counts = await self.database.fetch_all(query)
            
            # 전체 통계
            total_query = """
                SELECT 
                    COUNT(*) as total_features,
                    SUM(CASE WHEN enabled = 1 THEN 1 ELSE 0 END) as enabled_features,
                    SUM(CASE WHEN visible = 1 THEN 1 ELSE 0 END) as visible_features
                FROM features
            """
            
            totals = await self.database.fetch_one(total_query)
            
            return {
                "totals": totals or {},
                "by_category": category_counts
            }
            
        except Exception as e:
            self.logger.error(f"❌ 기능 요약 조회 실패: {e}")
            return {}
    
    async def update_feature(self, feature_id: str, updates: Dict[str, Any]) -> bool:
        """기능 업데이트"""
        try:
            if not self.database:
                return False
            
            # 업데이트 가능한 필드들
            allowed_fields = ['name', 'description', 'enabled', 'visible', 'emoji']
            set_clauses = []
            params = []
            
            for field, value in updates.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = ?")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            params.append(feature_id)
            query = f"""
                UPDATE features 
                SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            rows_affected = await self.database.execute(query, tuple(params))
            
            if rows_affected > 0:
                self.logger.info(f"✅ 기능 업데이트 완료: {feature_id}")
                return True
            else:
                self.logger.warning(f"⚠️ 업데이트할 기능을 찾을 수 없음: {feature_id}")
                return False
            
        except Exception as e:
            self.logger.error(f"❌ 기능 업데이트 실패: {e}")
            return False
    
    async def validate_existing_xml(self, file_path: str) -> Dict[str, Any]:
        """기존 XML 파일 검증"""
        try:
            if not self.validator:
                await self.initialize()
            
            self.logger.info(f"🔍 XML 파일 검증: {file_path}")
            result = await self.validator.validate_xml_file(file_path)
            
            # 검증 보고서 생성
            report = await self.validator.generate_validation_report(result)
            result['report'] = report
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ XML 검증 실패: {e}")
            return {"error": str(e)}
    
    async def get_accounts_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """계정 데이터 조회"""
        try:
            if not self.database:
                return []
            
            query = """
                SELECT id, username, email, status, created_at, updated_at
                FROM accounts 
                ORDER BY created_at DESC 
                LIMIT ?
            """
            
            accounts = await self.database.fetch_all(query, (limit,))
            return accounts
            
        except Exception as e:
            self.logger.error(f"❌ 계정 데이터 조회 실패: {e}")
            return []
    
    async def add_account(self, account_data: Dict[str, Any]) -> bool:
        """계정 추가"""
        try:
            if not self.database:
                return False
            
            query = """
                INSERT INTO accounts (username, password, email, proxy, status, cookies, fingerprint)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                account_data.get('username'),
                account_data.get('password'),
                account_data.get('email'),
                account_data.get('proxy'),
                account_data.get('status', '정상'),
                account_data.get('cookies'),
                account_data.get('fingerprint')
            )
            
            await self.database.execute(query, params)
            self.logger.info(f"✅ 계정 추가 완료: {account_data.get('username')}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ 계정 추가 실패: {e}")
            return False
    
    async def export_data(self, data_type: str, format: str = 'json') -> Optional[str]:
        """데이터 내보내기"""
        try:
            if not self.database:
                return None
            
            export_path = Path(self.config.get('xml_generator.output_path', './output'))
            export_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if data_type == 'features':
                data = await self.database.fetch_all("SELECT * FROM features")
                filename = f"features_export_{timestamp}.{format}"
            elif data_type == 'accounts':
                data = await self.database.fetch_all("SELECT * FROM accounts")
                filename = f"accounts_export_{timestamp}.{format}"
            elif data_type == 'xml_generations':
                data = await self.database.fetch_all("SELECT * FROM xml_generations")
                filename = f"generations_export_{timestamp}.{format}"
            else:
                return None
            
            file_path = export_path / filename
            
            if format == 'json':
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            elif format == 'csv':
                import csv
                if data:
                    with open(file_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            
            self.logger.info(f"✅ 데이터 내보내기 완료: {filename}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"❌ 데이터 내보내기 실패: {e}")
            return None
    
    async def cleanup(self):
        """시스템 정리"""
        self.logger.info("🧹 시스템 정리 시작")
        
        try:
            if self.database:
                await self.database.disconnect()
            
            self.is_initialized = False
            self.logger.info("✅ 시스템 정리 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 시스템 정리 실패: {e}")
    
    async def run_background_tasks(self):
        """백그라운드 작업 실행"""
        self.logger.info("🔄 백그라운드 작업 시작")
        
        try:
            while self.is_initialized:
                # 시스템 상태 체크
                await asyncio.sleep(60)  # 1분마다
                
                # 데이터베이스 연결 상태 확인
                if self.database and not self.database.connection:
                    self.logger.warning("⚠️ 데이터베이스 연결이 끊어졌습니다. 재연결 시도...")
                    try:
                        await self.database.connect()
                        self.logger.info("✅ 데이터베이스 재연결 성공")
                    except Exception as e:
                        self.logger.error(f"❌ 데이터베이스 재연결 실패: {e}")
                
                # 로그 정리 (옵션)
                # 이전 로그 파일들 관리
                
        except asyncio.CancelledError:
            self.logger.info("🛑 백그라운드 작업 중단")
        except Exception as e:
            self.logger.error(f"❌ 백그라운드 작업 오류: {e}")