#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDGRACE 핵심 로직 모듈
기능 통합 및 핵심 로직 처리
"""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터 클래스"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: float = 0.0
    active_threads: int = 0

class CoreEngine:
    """HDGRACE 핵심 엔진"""
    
    def __init__(self, max_workers=8):
        self.max_workers = max_workers
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = False
        self.metrics = SystemMetrics()
        logger.info("핵심 엔진 초기화 완료")
    
    def start_engine(self):
        """엔진 시작"""
        self.is_running = True
        logger.info("🚀 HDGRACE 핵심 엔진 시작")
        
        # 백그라운드 모니터링 시작
        self.thread_pool.submit(self._monitor_system)
    
    def stop_engine(self):
        """엔진 중지"""
        self.is_running = False
        self.thread_pool.shutdown(wait=True)
        logger.info("⏹️ HDGRACE 핵심 엔진 중지")
    
    def _monitor_system(self):
        """시스템 모니터링"""
        while self.is_running:
            try:
                import psutil
                self.metrics.cpu_usage = psutil.cpu_percent()
                self.metrics.memory_usage = psutil.virtual_memory().percent
                self.metrics.disk_usage = psutil.disk_usage('/').percent
                self.metrics.active_threads = threading.active_count()
                
                logger.debug(f"시스템 메트릭: CPU {self.metrics.cpu_usage}%, RAM {self.metrics.memory_usage}%")
                
            except ImportError:
                logger.warning("psutil 모듈이 없어 시스템 모니터링을 건너뜁니다")
                break
            except Exception as e:
                logger.error(f"시스템 모니터링 오류: {e}")
            
            time.sleep(5)  # 5초마다 체크
    
    def process_task(self, task_func, *args, **kwargs):
        """작업 처리"""
        if not self.is_running:
            logger.warning("엔진이 실행 중이 아닙니다")
            return None
        
        future = self.thread_pool.submit(task_func, *args, **kwargs)
        return future
    
    def get_system_status(self):
        """시스템 상태 반환"""
        return {
            "engine_running": self.is_running,
            "metrics": self.metrics,
            "thread_pool_size": self.max_workers
        }
