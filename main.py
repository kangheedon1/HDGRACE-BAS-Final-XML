#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDGRACE BAS Final XML Generator - 프로덕션 배포용 완성 코드
================================================================================
상업 배포 가능한 완전한 BAS 29.3.1 XML 생성 시스템
- 7,170개 실제 동작 기능 (더미/샘플 코드 금지)
- 데이터베이스 연동 및 XML 생성
- 최상위 디자인 UI/UX
- 무결성/스키마 검증/문법 오류 자동 교정
- 700MB+ XML 파일 생성
================================================================================
"""

import sys
import os
import logging
import asyncio
from pathlib import Path

# 프로젝트 루트 경로를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.core import HDGRACESystem
from modules.config_manager import ConfigManager
from modules.logger import setup_logging
from ui.web_interface import WebInterface

class HDGRACEApplication:
    """HDGRACE BAS Final XML Generator 메인 애플리케이션"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = setup_logging(self.config.get('logging'))
        self.system = HDGRACESystem(self.config, self.logger)
        self.web_interface = WebInterface(self.system, self.config)
        
    async def start(self):
        """애플리케이션 시작"""
        self.logger.info("🚀 HDGRACE BAS Final XML Generator 시작")
        self.logger.info("="*80)
        self.logger.info("📌 프로덕션 배포용 완성 코드")
        self.logger.info("🎯 7,170개 실제 동작 기능")
        self.logger.info("💾 데이터베이스 연동")
        self.logger.info("🎨 최상위 디자인 UI/UX")
        self.logger.info("🔍 무결성/스키마 검증")
        self.logger.info("📄 700MB+ XML 생성")
        self.logger.info("="*80)
        
        try:
            # 시스템 초기화
            await self.system.initialize()
            
            # 웹 인터페이스 시작
            await self.web_interface.start()
            
            self.logger.info("✅ 애플리케이션 시작 완료")
            
        except Exception as e:
            self.logger.error(f"❌ 애플리케이션 시작 실패: {e}")
            raise
    
    async def stop(self):
        """애플리케이션 종료"""
        self.logger.info("🛑 HDGRACE 애플리케이션 종료 중...")
        try:
            await self.web_interface.stop()
            await self.system.cleanup()
            self.logger.info("✅ 애플리케이션 종료 완료")
        except Exception as e:
            self.logger.error(f"❌ 애플리케이션 종료 중 오류: {e}")

async def main():
    """메인 실행 함수"""
    app = None
    try:
        app = HDGRACEApplication()
        await app.start()
        
        # 애플리케이션 실행 유지
        print("\n🌐 웹 인터페이스가 실행 중입니다.")
        print("📱 브라우저에서 http://localhost:8000 으로 접속하세요.")
        print("⏹️  종료하려면 Ctrl+C를 누르세요.\n")
        
        # 무한 대기 (웹 서버 유지)
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        logging.exception("애플리케이션 실행 중 오류")
    finally:
        if app:
            await app.stop()

if __name__ == "__main__":
    # Python 3.7+ asyncio 호환
    try:
        asyncio.run(main())
    except AttributeError:
        # Python 3.6 이하 호환
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(main())
        finally:
            loop.close()