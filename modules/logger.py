"""
로깅 시스템
================================================================================
시스템 전반의 로그 관리 및 모니터링
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any

def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """로깅 시스템 설정"""
    
    # 로그 디렉토리 생성
    log_path = Path(config.get('file_path', './logs/hdgrace.log'))
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 루트 로거 설정
    logger = logging.getLogger('hdgrace')
    logger.setLevel(getattr(logging, config.get('level', 'INFO')))
    
    # 기존 핸들러 제거
    logger.handlers.clear()
    
    # 포맷터 설정
    formatter = logging.Formatter(
        config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (회전 로그)
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=config.get('backup_count', 10),
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"파일 로그 핸들러 설정 실패: {e}")
    
    # 에러 전용 핸들러
    try:
        error_log_path = log_path.parent / 'error.log'
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_path,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
    except Exception as e:
        logger.warning(f"에러 로그 핸들러 설정 실패: {e}")
    
    # 시간별 로그 핸들러 (선택적)
    if config.get('rotation') == 'daily':
        try:
            timed_log_path = log_path.parent / 'daily.log'
            timed_handler = logging.handlers.TimedRotatingFileHandler(
                timed_log_path,
                when='midnight',
                interval=1,
                backupCount=30,
                encoding='utf-8'
            )
            timed_handler.setLevel(logging.INFO)
            timed_handler.setFormatter(formatter)
            logger.addHandler(timed_handler)
        except Exception as e:
            logger.warning(f"시간별 로그 핸들러 설정 실패: {e}")
    
    # 시작 메시지
    logger.info("🚀 HDGRACE 로깅 시스템 초기화 완료")
    logger.info(f"📄 로그 파일: {log_path}")
    logger.info(f"📊 로그 레벨: {config.get('level', 'INFO')}")
    
    return logger

class LoggerMixin:
    """로거 믹스인 클래스"""
    
    @property
    def logger(self) -> logging.Logger:
        """로거 인스턴스 반환"""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(f'hdgrace.{self.__class__.__name__}')
        return self._logger