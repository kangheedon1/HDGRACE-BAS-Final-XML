"""
데이터베이스 모듈 테스트
"""

import pytest
import asyncio
from modules.database import DatabaseManager

@pytest.mark.asyncio
async def test_database_initialization(test_config, temp_dir):
    """데이터베이스 초기화 테스트"""
    
    # 테스트용 데이터베이스 경로 설정
    db_config = test_config['database'].copy()
    db_config['name'] = str(temp_dir / "test.db")
    
    db_manager = DatabaseManager(db_config)
    
    try:
        # 초기화
        await db_manager.initialize()
        
        # 연결 확인
        assert db_manager.connection is not None
        
        # 테이블 확인
        tables = await db_manager.fetch_all(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        
        table_names = [table['name'] for table in tables]
        expected_tables = [
            'features', 'ui_elements', 'actions', 'macros',
            'xml_generations', 'accounts', 'system_logs', 'settings'
        ]
        
        for table in expected_tables:
            assert table in table_names, f"테이블 {table}이 생성되지 않았습니다"
        
        # 기본 데이터 확인
        accounts_count = await db_manager.get_accounts_count()
        assert accounts_count > 0, "기본 계정 데이터가 삽입되지 않았습니다"
        
    finally:
        await db_manager.disconnect()

@pytest.mark.asyncio
async def test_feature_insertion(test_config, temp_dir):
    """기능 데이터 삽입 테스트"""
    
    db_config = test_config['database'].copy()
    db_config['name'] = str(temp_dir / "test_features.db")
    
    db_manager = DatabaseManager(db_config)
    
    try:
        await db_manager.initialize()
        
        # 테스트 기능 데이터
        feature_data = {
            'name': 'test_feature',
            'category': 'test_category',
            'description': '테스트용 기능',
            'enabled': True,
            'visible': True,
            'emoji': '🧪',
            'parameters': {'test': True}
        }
        
        # 기능 삽입
        feature_id = await db_manager.insert_feature(feature_data)
        assert feature_id is not None and feature_id > 0
        
        # 삽입된 데이터 확인
        inserted_feature = await db_manager.fetch_one(
            "SELECT * FROM features WHERE id = ?", (feature_id,)
        )
        
        assert inserted_feature is not None
        assert inserted_feature['name'] == feature_data['name']
        assert inserted_feature['category'] == feature_data['category']
        assert inserted_feature['enabled'] == 1  # SQLite에서는 boolean이 int로 저장
        
    finally:
        await db_manager.disconnect()

@pytest.mark.asyncio
async def test_xml_generation_logging(test_config, temp_dir):
    """XML 생성 기록 테스트"""
    
    db_config = test_config['database'].copy()
    db_config['name'] = str(temp_dir / "test_xml_log.db")
    
    db_manager = DatabaseManager(db_config)
    
    try:
        await db_manager.initialize()
        
        # 테스트 생성 기록 데이터
        generation_data = {
            'file_path': '/test/path/test.xml',
            'file_size': 1024000,  # 1MB
            'features_count': 100,
            'ui_elements_count': 100,
            'actions_count': 500,
            'macros_count': 100,
            'generation_time': 30.5,
            'status': 'completed'
        }
        
        # 기록 삽입
        log_id = await db_manager.log_xml_generation(generation_data)
        assert log_id is not None and log_id > 0
        
        # 삽입된 기록 확인
        logged_data = await db_manager.fetch_one(
            "SELECT * FROM xml_generations WHERE id = ?", (log_id,)
        )
        
        assert logged_data is not None
        assert logged_data['file_path'] == generation_data['file_path']
        assert logged_data['file_size'] == generation_data['file_size']
        assert logged_data['features_count'] == generation_data['features_count']
        assert logged_data['status'] == generation_data['status']
        
    finally:
        await db_manager.disconnect()

@pytest.mark.asyncio
async def test_data_queries(test_config, temp_dir):
    """데이터 조회 테스트"""
    
    db_config = test_config['database'].copy()
    db_config['name'] = str(temp_dir / "test_queries.db")
    
    db_manager = DatabaseManager(db_config)
    
    try:
        await db_manager.initialize()
        
        # 초기 기능 수 확인
        initial_count = await db_manager.get_features_count()
        
        # 테스트 기능 추가
        for i in range(5):
            feature_data = {
                'name': f'test_feature_{i}',
                'category': 'test_category',
                'description': f'테스트 기능 {i}',
                'enabled': True,
                'visible': True,
                'emoji': '🧪'
            }
            await db_manager.insert_feature(feature_data)
        
        # 추가 후 기능 수 확인
        final_count = await db_manager.get_features_count()
        assert final_count == initial_count + 5
        
        # 계정 수 확인
        accounts_count = await db_manager.get_accounts_count()
        assert accounts_count > 0  # 기본 계정들이 있어야 함
        
    finally:
        await db_manager.disconnect()