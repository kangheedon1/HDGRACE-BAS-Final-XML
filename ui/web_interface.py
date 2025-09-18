"""
웹 인터페이스 - 최상위 디자인 UI/UX
================================================================================
FastAPI 기반 웹 애플리케이션 및 React 프론트엔드
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.logger import LoggerMixin
from modules.core import HDGRACESystem
from modules.config_manager import ConfigManager

# Pydantic 모델들
class GenerateXMLRequest(BaseModel):
    target_features: Optional[int] = 7170
    target_size_mb: Optional[int] = 700
    validation_enabled: Optional[bool] = True
    correction_enabled: Optional[bool] = True

class UpdateFeatureRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    visible: Optional[bool] = None
    emoji: Optional[str] = None

class AddAccountRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    proxy: Optional[str] = None
    status: str = "정상"
    cookies: Optional[str] = None
    fingerprint: Optional[str] = None

class WebInterface(LoggerMixin):
    """웹 인터페이스 관리자"""
    
    def __init__(self, system: HDGRACESystem, config: ConfigManager):
        self.system = system
        self.config = config
        self.app = FastAPI(
            title="HDGRACE BAS Final XML Generator",
            description="프로덕션 배포용 완성 코드 - BAS 29.3.1 표준 준수",
            version="1.0.0"
        )
        self.server = None
        self._setup_app()
    
    def _setup_app(self):
        """FastAPI 애플리케이션 설정"""
        
        # CORS 설정
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get('security.cors_origins', ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # 정적 파일 서빙
        static_path = Path("static")
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=static_path), name="static")
        
        # API 라우트 설정
        self._setup_routes()
    
    def _setup_routes(self):
        """API 라우트 설정"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """메인 페이지"""
            return self._get_main_html()
        
        @self.app.get("/api/status")
        async def get_status():
            """시스템 상태 조회"""
            try:
                status = await self.system.get_system_status()
                return JSONResponse(content=status)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/generate-xml")
        async def generate_xml(request: GenerateXMLRequest, background_tasks: BackgroundTasks):
            """XML 생성"""
            try:
                # 백그라운드에서 XML 생성 실행
                task_id = f"xml_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # 즉시 응답 반환
                background_tasks.add_task(self._generate_xml_task, request.dict(), task_id)
                
                return JSONResponse(content={
                    "message": "XML 생성이 시작되었습니다",
                    "task_id": task_id,
                    "status": "started"
                })
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/generation-history")
        async def get_generation_history(limit: int = 10):
            """XML 생성 기록 조회"""
            try:
                history = await self.system.get_generation_history(limit)
                return JSONResponse(content=history)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/features/summary")
        async def get_features_summary():
            """기능 요약 조회"""
            try:
                summary = await self.system.get_features_summary()
                return JSONResponse(content=summary)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/api/features/{feature_id}")
        async def update_feature(feature_id: str, request: UpdateFeatureRequest):
            """기능 업데이트"""
            try:
                updates = {k: v for k, v in request.dict().items() if v is not None}
                success = await self.system.update_feature(feature_id, updates)
                
                if success:
                    return JSONResponse(content={"message": "기능이 업데이트되었습니다"})
                else:
                    raise HTTPException(status_code=404, detail="기능을 찾을 수 없습니다")
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/validate-xml")
        async def validate_xml(file: UploadFile = File(...)):
            """XML 파일 검증"""
            try:
                # 임시 파일로 저장
                temp_path = Path(f"/tmp/{file.filename}")
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                
                contents = await file.read()
                temp_path.write_bytes(contents)
                
                # 검증 실행
                result = await self.system.validate_existing_xml(str(temp_path))
                
                # 임시 파일 삭제
                temp_path.unlink(missing_ok=True)
                
                return JSONResponse(content=result)
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/accounts")
        async def get_accounts(limit: int = 100):
            """계정 데이터 조회"""
            try:
                accounts = await self.system.get_accounts_data(limit)
                return JSONResponse(content=accounts)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/accounts")
        async def add_account(request: AddAccountRequest):
            """계정 추가"""
            try:
                success = await self.system.add_account(request.dict())
                
                if success:
                    return JSONResponse(content={"message": "계정이 추가되었습니다"})
                else:
                    raise HTTPException(status_code=400, detail="계정 추가에 실패했습니다")
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/export/{data_type}")
        async def export_data(data_type: str, format: str = "json"):
            """데이터 내보내기"""
            try:
                file_path = await self.system.export_data(data_type, format)
                
                if file_path:
                    return FileResponse(
                        file_path,
                        media_type='application/octet-stream',
                        filename=Path(file_path).name
                    )
                else:
                    raise HTTPException(status_code=400, detail="내보내기에 실패했습니다")
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/download/{filename}")
        async def download_file(filename: str):
            """파일 다운로드"""
            try:
                output_path = Path(self.config.get('xml_generator.output_path', './output'))
                file_path = output_path / filename
                
                if file_path.exists():
                    return FileResponse(
                        file_path,
                        media_type='application/octet-stream',
                        filename=filename
                    )
                else:
                    raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
                    
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _generate_xml_task(self, options: Dict[str, Any], task_id: str):
        """XML 생성 백그라운드 작업"""
        try:
            self.logger.info(f"🚀 XML 생성 작업 시작: {task_id}")
            
            # 임시로 설정 업데이트
            for key, value in options.items():
                if value is not None:
                    self.config.set(f'xml_generator.{key}', value)
            
            # XML 생성 실행
            result = await self.system.generate_xml(options)
            
            self.logger.info(f"✅ XML 생성 작업 완료: {task_id}")
            
            # 결과를 어딘가에 저장하거나 알림 (여기서는 로그로 대체)
            self.logger.info(f"생성 결과: {result['file_path']} ({result['file_size_mb']:.2f}MB)")
            
        except Exception as e:
            self.logger.error(f"❌ XML 생성 작업 실패: {task_id} - {e}")
    
    def _get_main_html(self) -> str:
        """메인 페이지 HTML 반환"""
        return """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HDGRACE BAS Final XML Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p {
            font-size: 1.2rem;
            color: #666;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: transform 0.2s ease;
            margin: 5px;
        }
        
        .btn:hover {
            transform: scale(1.05);
        }
        
        .btn:active {
            transform: scale(0.95);
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-online { background-color: #4CAF50; }
        .status-offline { background-color: #f44336; }
        .status-warning { background-color: #ff9800; }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .feature-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }
        
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #000;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 1rem;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: #4CAF50;
            color: white;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1001;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.error {
            background: #f44336;
        }
        
        .notification.warning {
            background: #ff9800;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 HDGRACE BAS Final XML Generator</h1>
            <p>프로덕션 배포용 완성 코드 - BAS 29.3.1 표준 준수</p>
        </div>
        
        <div class="dashboard">
            <!-- 시스템 상태 카드 -->
            <div class="card">
                <h3>📊 시스템 상태</h3>
                <div id="system-status">
                    <div><span class="status-indicator status-warning"></span>시스템 정보 로딩 중...</div>
                </div>
                <button class="btn" onclick="refreshStatus()">상태 새로고침</button>
            </div>
            
            <!-- XML 생성 카드 -->
            <div class="card">
                <h3>🔧 XML 생성</h3>
                <div>
                    <p>BAS 29.3.1 표준 XML 파일을 생성합니다.</p>
                    <p>🎯 목표: 7,170개 기능, 700MB+ 크기</p>
                </div>
                <button class="btn" onclick="openGenerateModal()">XML 생성</button>
                <button class="btn" onclick="showGenerationHistory()">생성 기록</button>
            </div>
            
            <!-- 기능 관리 카드 -->
            <div class="card">
                <h3>⚙️ 기능 관리</h3>
                <div id="features-summary">
                    <p>기능 정보 로딩 중...</p>
                </div>
                <button class="btn" onclick="showFeatures()">기능 목록</button>
                <button class="btn" onclick="exportData('features')">기능 내보내기</button>
            </div>
            
            <!-- 계정 관리 카드 -->
            <div class="card">
                <h3>👤 계정 관리</h3>
                <div id="accounts-summary">
                    <p>계정 정보 로딩 중...</p>
                </div>
                <button class="btn" onclick="showAccounts()">계정 목록</button>
                <button class="btn" onclick="openAddAccountModal()">계정 추가</button>
            </div>
            
            <!-- 검증 도구 카드 -->
            <div class="card">
                <h3>🔍 XML 검증</h3>
                <div>
                    <p>기존 XML 파일의 무결성과 BAS 표준 준수를 검증합니다.</p>
                </div>
                <input type="file" id="xml-file" accept=".xml" style="margin-bottom: 10px;">
                <button class="btn" onclick="validateXML()">XML 검증</button>
            </div>
            
            <!-- 데이터 관리 카드 -->
            <div class="card">
                <h3>📁 데이터 관리</h3>
                <div>
                    <p>시스템 데이터를 내보내고 관리합니다.</p>
                </div>
                <button class="btn" onclick="exportData('xml_generations')">생성 기록 내보내기</button>
                <button class="btn" onclick="exportData('accounts', 'csv')">계정 CSV 내보내기</button>
            </div>
        </div>
    </div>
    
    <!-- XML 생성 모달 -->
    <div id="generate-modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('generate-modal')">&times;</span>
            <h2>🔧 XML 생성</h2>
            <form id="generate-form">
                <div class="form-group">
                    <label for="target-features">목표 기능 수:</label>
                    <input type="number" id="target-features" value="7170" min="1000" max="10000">
                </div>
                <div class="form-group">
                    <label for="target-size">목표 크기 (MB):</label>
                    <input type="number" id="target-size" value="700" min="100" max="2000">
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="validation-enabled" checked>
                        생성 후 검증 실행
                    </label>
                </div>
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="correction-enabled" checked>
                        자동 문법 교정
                    </label>
                </div>
                <button type="submit" class="btn">생성 시작</button>
            </form>
            <div id="generate-loading" class="loading">
                <div class="spinner"></div>
                <p>XML 생성 중... 이 작업은 몇 분이 소요될 수 있습니다.</p>
            </div>
        </div>
    </div>
    
    <!-- 계정 추가 모달 -->
    <div id="add-account-modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal('add-account-modal')">&times;</span>
            <h2>👤 계정 추가</h2>
            <form id="add-account-form">
                <div class="form-group">
                    <label for="username">사용자명:</label>
                    <input type="text" id="username" required>
                </div>
                <div class="form-group">
                    <label for="password">비밀번호:</label>
                    <input type="password" id="password" required>
                </div>
                <div class="form-group">
                    <label for="email">이메일:</label>
                    <input type="email" id="email">
                </div>
                <div class="form-group">
                    <label for="proxy">프록시:</label>
                    <input type="text" id="proxy" placeholder="IP:PORT;USER;PASS">
                </div>
                <div class="form-group">
                    <label for="status">상태:</label>
                    <select id="status">
                        <option value="정상">정상</option>
                        <option value="차단">차단</option>
                        <option value="점검">점검</option>
                    </select>
                </div>
                <button type="submit" class="btn">계정 추가</button>
            </form>
        </div>
    </div>
    
    <!-- 알림 -->
    <div id="notification" class="notification">
        <span id="notification-message"></span>
    </div>
    
    <script>
        // 페이지 로드 시 초기화
        document.addEventListener('DOMContentLoaded', function() {
            refreshStatus();
            loadFeaturesSummary();
            loadAccountsSummary();
        });
        
        // 시스템 상태 새로고침
        async function refreshStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                const statusElement = document.getElementById('system-status');
                const dbStatus = status.database.connected ? 'online' : 'offline';
                const initStatus = status.initialized ? 'online' : 'offline';
                
                statusElement.innerHTML = `
                    <div><span class="status-indicator status-${initStatus}"></span>시스템: ${status.initialized ? '초기화됨' : '초기화 필요'}</div>
                    <div><span class="status-indicator status-${dbStatus}"></span>데이터베이스: ${status.database.connected ? '연결됨' : '연결 안됨'}</div>
                    <div>기능 수: ${status.database.features_count || 0}개</div>
                    <div>계정 수: ${status.database.accounts_count || 0}개</div>
                    <div>BAS 버전: ${status.config.bas_version}</div>
                `;
            } catch (error) {
                console.error('상태 조회 실패:', error);
                showNotification('상태 조회에 실패했습니다.', 'error');
            }
        }
        
        // 기능 요약 로드
        async function loadFeaturesSummary() {
            try {
                const response = await fetch('/api/features/summary');
                const summary = await response.json();
                
                const summaryElement = document.getElementById('features-summary');
                const totals = summary.totals || {};
                
                summaryElement.innerHTML = `
                    <div>전체 기능: ${totals.total_features || 0}개</div>
                    <div>활성화된 기능: ${totals.enabled_features || 0}개</div>
                    <div>표시되는 기능: ${totals.visible_features || 0}개</div>
                `;
            } catch (error) {
                console.error('기능 요약 로드 실패:', error);
            }
        }
        
        // 계정 요약 로드
        async function loadAccountsSummary() {
            try {
                const response = await fetch('/api/accounts?limit=1');
                const accounts = await response.json();
                
                document.getElementById('accounts-summary').innerHTML = `
                    <div>등록된 계정: ${accounts.length}개</div>
                    <div>상태: 관리 필요</div>
                `;
            } catch (error) {
                console.error('계정 요약 로드 실패:', error);
            }
        }
        
        // 모달 열기
        function openModal(modalId) {
            document.getElementById(modalId).style.display = 'block';
        }
        
        function openGenerateModal() {
            openModal('generate-modal');
        }
        
        function openAddAccountModal() {
            openModal('add-account-modal');
        }
        
        // 모달 닫기
        function closeModal(modalId) {
            document.getElementById(modalId).style.display = 'none';
        }
        
        // XML 생성
        document.getElementById('generate-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                target_features: parseInt(document.getElementById('target-features').value),
                target_size_mb: parseInt(document.getElementById('target-size').value),
                validation_enabled: document.getElementById('validation-enabled').checked,
                correction_enabled: document.getElementById('correction-enabled').checked
            };
            
            document.getElementById('generate-loading').style.display = 'block';
            
            try {
                const response = await fetch('/api/generate-xml', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showNotification('XML 생성이 시작되었습니다. 완료까지 몇 분이 소요됩니다.');
                    closeModal('generate-modal');
                } else {
                    showNotification('XML 생성 요청에 실패했습니다: ' + result.detail, 'error');
                }
            } catch (error) {
                console.error('XML 생성 실패:', error);
                showNotification('XML 생성에 실패했습니다.', 'error');
            } finally {
                document.getElementById('generate-loading').style.display = 'none';
            }
        });
        
        // 계정 추가
        document.getElementById('add-account-form').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value,
                email: document.getElementById('email').value,
                proxy: document.getElementById('proxy').value,
                status: document.getElementById('status').value
            };
            
            try {
                const response = await fetch('/api/accounts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showNotification('계정이 추가되었습니다.');
                    closeModal('add-account-modal');
                    document.getElementById('add-account-form').reset();
                    loadAccountsSummary();
                } else {
                    showNotification('계정 추가에 실패했습니다: ' + result.detail, 'error');
                }
            } catch (error) {
                console.error('계정 추가 실패:', error);
                showNotification('계정 추가에 실패했습니다.', 'error');
            }
        });
        
        // XML 검증
        async function validateXML() {
            const fileInput = document.getElementById('xml-file');
            const file = fileInput.files[0];
            
            if (!file) {
                showNotification('검증할 XML 파일을 선택해주세요.', 'warning');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/validate-xml', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    const status = result.is_valid ? '통과' : '실패';
                    const type = result.is_valid ? 'success' : 'error';
                    
                    showNotification(`XML 검증 ${status}: ${result.errors.length}개 오류, ${result.warnings.length}개 경고`, type);
                    
                    if (result.report) {
                        console.log('검증 보고서:', result.report);
                    }
                } else {
                    showNotification('XML 검증에 실패했습니다: ' + result.detail, 'error');
                }
            } catch (error) {
                console.error('XML 검증 실패:', error);
                showNotification('XML 검증에 실패했습니다.', 'error');
            }
        }
        
        // 데이터 내보내기
        async function exportData(dataType, format = 'json') {
            try {
                const response = await fetch(`/api/export/${dataType}?format=${format}`);
                
                if (response.ok) {
                    // 파일 다운로드
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.style.display = 'none';
                    a.href = url;
                    a.download = `${dataType}_export.${format}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    
                    showNotification('데이터 내보내기가 완료되었습니다.');
                } else {
                    showNotification('데이터 내보내기에 실패했습니다.', 'error');
                }
            } catch (error) {
                console.error('데이터 내보내기 실패:', error);
                showNotification('데이터 내보내기에 실패했습니다.', 'error');
            }
        }
        
        // 생성 기록 표시
        async function showGenerationHistory() {
            try {
                const response = await fetch('/api/generation-history');
                const history = await response.json();
                
                let historyHtml = '<h3>📊 XML 생성 기록</h3>';
                
                if (history.length === 0) {
                    historyHtml += '<p>생성 기록이 없습니다.</p>';
                } else {
                    historyHtml += '<ul>';
                    history.forEach(record => {
                        historyHtml += `
                            <li>
                                <strong>${record.created_at}</strong><br>
                                파일: ${record.file_path}<br>
                                크기: ${(record.file_size / 1024 / 1024).toFixed(2)}MB<br>
                                기능: ${record.features_count}개<br>
                                상태: ${record.status}
                            </li>
                        `;
                    });
                    historyHtml += '</ul>';
                }
                
                // 간단한 알림으로 표시 (실제로는 모달이나 별도 페이지로 구현)
                alert(historyHtml.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' '));
                
            } catch (error) {
                console.error('생성 기록 조회 실패:', error);
                showNotification('생성 기록 조회에 실패했습니다.', 'error');
            }
        }
        
        // 기능 목록 표시
        function showFeatures() {
            showNotification('기능 목록은 별도 페이지에서 제공됩니다.', 'warning');
        }
        
        // 계정 목록 표시
        function showAccounts() {
            showNotification('계정 목록은 별도 페이지에서 제공됩니다.', 'warning');
        }
        
        // 알림 표시
        function showNotification(message, type = 'success') {
            const notification = document.getElementById('notification');
            const messageElement = document.getElementById('notification-message');
            
            messageElement.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        }
        
        // 모달 외부 클릭 시 닫기
        window.onclick = function(event) {
            const modals = document.getElementsByClassName('modal');
            for (let modal of modals) {
                if (event.target === modal) {
                    modal.style.display = 'none';
                }
            }
        }
    </script>
</body>
</html>
        """
    
    async def start(self):
        """웹 서버 시작"""
        try:
            import uvicorn
            
            server_config = self.config.get('server')
            
            self.logger.info(f"🌐 웹 서버 시작: http://{server_config['host']}:{server_config['port']}")
            
            # 비동기로 서버 실행
            config = uvicorn.Config(
                self.app,
                host=server_config['host'],
                port=server_config['port'],
                log_level="info"
            )
            
            self.server = uvicorn.Server(config)
            
            # 백그라운드에서 서버 실행
            asyncio.create_task(self.server.serve())
            
        except Exception as e:
            self.logger.error(f"❌ 웹 서버 시작 실패: {e}")
            raise
    
    async def stop(self):
        """웹 서버 종료"""
        if self.server:
            self.logger.info("🛑 웹 서버 종료 중...")
            self.server.should_exit = True
            await self.server.shutdown()
            self.logger.info("✅ 웹 서버 종료 완료")