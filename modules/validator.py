"""
무결성 검증 및 스키마 유효성 검사 모듈
================================================================================
XML 파일의 무결성, 스키마 준수, BAS 표준 호환성 검증
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime

from modules.logger import LoggerMixin

class XMLValidator(LoggerMixin):
    """XML 검증기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.bas_version = config.get('bas_version', '29.3.1')
        self.validation_rules = self._load_validation_rules()
        
    def _load_validation_rules(self) -> Dict[str, Any]:
        """BAS 29.3.1 검증 규칙 로드"""
        return {
            "required_elements": [
                "BrowserAutomationStudioProject",
                "Script",
                "Settings", 
                "Variables",
                "Features",
                "UserInterface",
                "Actions",
                "Macros",
                "Resources",
                "Log"
            ],
            "required_attributes": {
                "BrowserAutomationStudioProject": ["xmlns", "version"],
                "Feature": ["id", "name", "category", "enabled", "visible"],
                "UIElement": ["id", "type", "name", "visible", "enabled"],
                "Action": ["id", "name", "type"],
                "Macro": ["id", "name", "enabled"]
            },
            "namespace": "http://bablosoft.com/BrowserAutomationStudio",
            "version_pattern": r"^\d+\.\d+\.\d+$",
            "id_pattern": r"^[a-zA-Z_][a-zA-Z0-9_]*$",
            "max_file_size_mb": 2000,  # 최대 2GB
            "min_file_size_mb": 500,   # 최소 500MB
            "feature_categories": [
                "YouTube_자동화", "프록시_연결관리", "보안_탐지회피",
                "UI_사용자인터페이스", "시스템_관리모니터링", "고급_최적화알고리즘",
                "데이터_처리", "네트워크_통신", "파일_관리", "암호화_보안",
                "스케줄링", "로깅", "에러_처리", "성능_모니터링",
                "자동화_스크립트", "웹_크롤링", "API_연동", "데이터베이스",
                "이메일_자동화", "SMS_연동", "캡차_해결", "이미지_처리",
                "텍스트_분석", "머신러닝", "AI_통합", "추가_기능"
            ],
            "ui_types": [
                "button", "toggle", "input", "select", "checkbox", 
                "radio", "slider", "textarea", "label", "panel"
            ],
            "action_types": [
                "Navigate", "Click", "Type", "Wait", "Scroll", "Submit",
                "Extract", "Screenshot", "Upload", "Download", "Login",
                "SolveCaptcha", "ProxyRotate", "MonitorSystem"
            ]
        }
    
    async def validate_xml_file(self, file_path: str) -> Dict[str, Any]:
        """XML 파일 전체 검증"""
        self.logger.info(f"🔍 XML 파일 검증 시작: {file_path}")
        
        validation_result = {
            "file_path": file_path,
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "summary": {},
            "validation_time": datetime.now().isoformat()
        }
        
        try:
            # 1. 파일 존재 및 크기 검증
            file_check = self._validate_file_basic(file_path)
            validation_result["summary"]["file_basic"] = file_check
            if not file_check["valid"]:
                validation_result["errors"].extend(file_check["errors"])
                return validation_result
            
            # 2. XML 구문 검증
            xml_parse = await self._validate_xml_syntax(file_path)
            validation_result["summary"]["xml_syntax"] = xml_parse
            if not xml_parse["valid"]:
                validation_result["errors"].extend(xml_parse["errors"])
                return validation_result
            
            # 3. BAS 스키마 검증
            schema_check = await self._validate_bas_schema(xml_parse["root"])
            validation_result["summary"]["bas_schema"] = schema_check
            if not schema_check["valid"]:
                validation_result["errors"].extend(schema_check["errors"])
                validation_result["warnings"].extend(schema_check["warnings"])
            
            # 4. 데이터 무결성 검증
            integrity_check = await self._validate_data_integrity(xml_parse["root"])
            validation_result["summary"]["data_integrity"] = integrity_check
            if not integrity_check["valid"]:
                validation_result["errors"].extend(integrity_check["errors"])
                validation_result["warnings"].extend(integrity_check["warnings"])
            
            # 5. 성능 검증
            performance_check = await self._validate_performance(xml_parse["root"])
            validation_result["summary"]["performance"] = performance_check
            validation_result["warnings"].extend(performance_check["warnings"])
            
            # 6. 보안 검증
            security_check = await self._validate_security(xml_parse["root"])
            validation_result["summary"]["security"] = security_check
            validation_result["warnings"].extend(security_check["warnings"])
            
            # 전체 검증 결과 판정
            validation_result["is_valid"] = (
                len(validation_result["errors"]) == 0 and
                schema_check["valid"] and
                integrity_check["valid"]
            )
            
            self.logger.info(f"✅ XML 검증 완료: {'통과' if validation_result['is_valid'] else '실패'}")
            
        except Exception as e:
            self.logger.error(f"❌ XML 검증 중 오류: {e}")
            validation_result["errors"].append(f"검증 중 예외 발생: {str(e)}")
        
        return validation_result
    
    def _validate_file_basic(self, file_path: str) -> Dict[str, Any]:
        """기본 파일 검증"""
        result = {"valid": False, "errors": [], "warnings": []}
        
        try:
            file_obj = Path(file_path)
            
            # 파일 존재 확인
            if not file_obj.exists():
                result["errors"].append("파일이 존재하지 않습니다")
                return result
            
            # 파일 크기 확인
            file_size_mb = file_obj.stat().st_size / (1024 * 1024)
            min_size = self.validation_rules["min_file_size_mb"]
            max_size = self.validation_rules["max_file_size_mb"]
            
            if file_size_mb < min_size:
                result["warnings"].append(f"파일 크기가 권장 최소값({min_size}MB)보다 작습니다: {file_size_mb:.2f}MB")
            elif file_size_mb > max_size:
                result["errors"].append(f"파일 크기가 최대값({max_size}MB)을 초과합니다: {file_size_mb:.2f}MB")
                return result
            
            # 파일 확장자 확인
            if file_obj.suffix.lower() != '.xml':
                result["warnings"].append("파일 확장자가 .xml이 아닙니다")
            
            result["valid"] = True
            result["file_size_mb"] = file_size_mb
            
        except Exception as e:
            result["errors"].append(f"파일 기본 검증 실패: {str(e)}")
        
        return result
    
    async def _validate_xml_syntax(self, file_path: str) -> Dict[str, Any]:
        """XML 구문 검증"""
        result = {"valid": False, "errors": [], "warnings": [], "root": None}
        
        try:
            # XML 파싱
            tree = ET.parse(file_path)
            root = tree.getroot()
            result["root"] = root
            
            # UTF-8 인코딩 확인
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                if 'encoding="utf-8"' not in first_line.lower():
                    result["warnings"].append("XML 선언에 UTF-8 인코딩이 명시되지 않았습니다")
            
            # Well-formed XML 검증
            try:
                minidom.parse(file_path)
            except Exception as e:
                result["errors"].append(f"XML 구문 오류: {str(e)}")
                return result
            
            result["valid"] = True
            
        except ET.ParseError as e:
            result["errors"].append(f"XML 파싱 오류: {str(e)}")
        except Exception as e:
            result["errors"].append(f"XML 구문 검증 실패: {str(e)}")
        
        return result
    
    async def _validate_bas_schema(self, root: ET.Element) -> Dict[str, Any]:
        """BAS 스키마 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            # 루트 엘리먼트 검증
            if root.tag != "BrowserAutomationStudioProject":
                result["errors"].append(f"루트 엘리먼트가 올바르지 않습니다: {root.tag}")
                result["valid"] = False
            
            # 네임스페이스 검증
            xmlns = root.get("xmlns")
            expected_xmlns = self.validation_rules["namespace"]
            if xmlns != expected_xmlns:
                result["warnings"].append(f"네임스페이스가 다릅니다: {xmlns} (예상: {expected_xmlns})")
            
            # 버전 검증
            version = root.get("version")
            if not version:
                result["errors"].append("버전 속성이 누락되었습니다")
                result["valid"] = False
            elif not re.match(self.validation_rules["version_pattern"], version):
                result["errors"].append(f"버전 형식이 올바르지 않습니다: {version}")
                result["valid"] = False
            
            # 필수 엘리먼트 검증
            required_elements = self.validation_rules["required_elements"]
            existing_elements = {child.tag for child in root}
            
            for req_elem in required_elements:
                if req_elem not in existing_elements:
                    result["errors"].append(f"필수 엘리먼트가 누락되었습니다: {req_elem}")
                    result["valid"] = False
            
            # 기능 검증
            features_elem = root.find("Features")
            if features_elem is not None:
                feature_check = await self._validate_features(features_elem)
                result["errors"].extend(feature_check["errors"])
                result["warnings"].extend(feature_check["warnings"])
                if not feature_check["valid"]:
                    result["valid"] = False
            
            # UI 검증
            ui_elem = root.find("UserInterface")
            if ui_elem is not None:
                ui_check = await self._validate_ui_elements(ui_elem)
                result["errors"].extend(ui_check["errors"])
                result["warnings"].extend(ui_check["warnings"])
                if not ui_check["valid"]:
                    result["valid"] = False
            
            # 액션 검증
            actions_elem = root.find("Actions")
            if actions_elem is not None:
                actions_check = await self._validate_actions(actions_elem)
                result["errors"].extend(actions_check["errors"])
                result["warnings"].extend(actions_check["warnings"])
                if not actions_check["valid"]:
                    result["valid"] = False
            
        except Exception as e:
            result["errors"].append(f"BAS 스키마 검증 실패: {str(e)}")
            result["valid"] = False
        
        return result
    
    async def _validate_features(self, features_elem: ET.Element) -> Dict[str, Any]:
        """기능 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        feature_ids = set()
        feature_count = 0
        
        for feature in features_elem.findall("Feature"):
            feature_count += 1
            
            # ID 검증
            feature_id = feature.get("id")
            if not feature_id:
                result["errors"].append(f"기능 ID가 누락되었습니다 (Feature #{feature_count})")
                result["valid"] = False
                continue
            
            if feature_id in feature_ids:
                result["errors"].append(f"중복된 기능 ID: {feature_id}")
                result["valid"] = False
            else:
                feature_ids.add(feature_id)
            
            # 필수 속성 검증
            required_attrs = self.validation_rules["required_attributes"]["Feature"]
            for attr in required_attrs:
                if not feature.get(attr):
                    result["errors"].append(f"기능 {feature_id}: 필수 속성 누락 - {attr}")
                    result["valid"] = False
            
            # 카테고리 검증
            category = feature.get("category")
            if category and category not in self.validation_rules["feature_categories"]:
                result["warnings"].append(f"기능 {feature_id}: 알 수 없는 카테고리 - {category}")
            
            # visible 속성 검증
            visible = feature.get("visible")
            if visible and visible.lower() != "true":
                result["warnings"].append(f"기능 {feature_id}: visible이 true가 아닙니다 - {visible}")
        
        # 기능 수 검증
        expected_count = 7170
        if feature_count < expected_count:
            result["warnings"].append(f"기능 수가 목표치({expected_count})보다 적습니다: {feature_count}")
        
        return result
    
    async def _validate_ui_elements(self, ui_elem: ET.Element) -> Dict[str, Any]:
        """UI 요소 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        ui_ids = set()
        ui_count = 0
        
        for ui in ui_elem.findall("UIElement"):
            ui_count += 1
            
            # ID 검증
            ui_id = ui.get("id")
            if not ui_id:
                result["errors"].append(f"UI 요소 ID가 누락되었습니다 (UI #{ui_count})")
                result["valid"] = False
                continue
            
            if ui_id in ui_ids:
                result["errors"].append(f"중복된 UI ID: {ui_id}")
                result["valid"] = False
            else:
                ui_ids.add(ui_id)
            
            # 타입 검증
            ui_type = ui.get("type")
            if ui_type and ui_type not in self.validation_rules["ui_types"]:
                result["warnings"].append(f"UI {ui_id}: 알 수 없는 타입 - {ui_type}")
            
            # visible 속성 검증
            visible = ui.get("visible")
            if visible and visible.lower() != "true":
                result["warnings"].append(f"UI {ui_id}: visible이 true가 아닙니다 - {visible}")
            
            enabled = ui.get("enabled")
            if enabled and enabled.lower() != "true":
                result["warnings"].append(f"UI {ui_id}: enabled가 true가 아닙니다 - {enabled}")
        
        return result
    
    async def _validate_actions(self, actions_elem: ET.Element) -> Dict[str, Any]:
        """액션 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        action_ids = set()
        action_count = 0
        
        for action in actions_elem.findall("Action"):
            action_count += 1
            
            # ID 검증
            action_id = action.get("id")
            if not action_id:
                result["errors"].append(f"액션 ID가 누락되었습니다 (Action #{action_count})")
                result["valid"] = False
                continue
            
            if action_id in action_ids:
                result["errors"].append(f"중복된 액션 ID: {action_id}")
                result["valid"] = False
            else:
                action_ids.add(action_id)
            
            # 타입 검증
            action_type = action.get("type")
            if action_type and action_type not in self.validation_rules["action_types"]:
                result["warnings"].append(f"액션 {action_id}: 알 수 없는 타입 - {action_type}")
        
        return result
    
    async def _validate_data_integrity(self, root: ET.Element) -> Dict[str, Any]:
        """데이터 무결성 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            # Feature-UI 연결 무결성
            features = {f.get("id") for f in root.findall(".//Feature") if f.get("id")}
            ui_elements = root.findall(".//UIElement")
            
            for ui in ui_elements:
                feature_id = ui.get("feature_id")
                if feature_id and feature_id not in features:
                    result["warnings"].append(f"UI 요소가 존재하지 않는 기능을 참조합니다: {feature_id}")
            
            # JSON 데이터 검증
            for elem in root.iter():
                if elem.text and elem.text.strip().startswith('{'):
                    try:
                        json.loads(elem.text)
                    except json.JSONDecodeError:
                        result["warnings"].append(f"잘못된 JSON 데이터: {elem.tag}")
            
            # Config 섹션 검증
            config_elem = root.find(".//Config")
            if config_elem is not None and config_elem.text:
                try:
                    config_data = json.loads(config_elem.text)
                    if not isinstance(config_data, dict):
                        result["warnings"].append("Config 데이터가 객체 형태가 아닙니다")
                except json.JSONDecodeError:
                    result["warnings"].append("Config 섹션의 JSON이 유효하지 않습니다")
            
        except Exception as e:
            result["errors"].append(f"데이터 무결성 검증 실패: {str(e)}")
            result["valid"] = False
        
        return result
    
    async def _validate_performance(self, root: ET.Element) -> Dict[str, Any]:
        """성능 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            # 엘리먼트 수 계산
            total_elements = len(list(root.iter()))
            if total_elements > 1000000:  # 100만개 초과
                result["warnings"].append(f"XML 엘리먼트 수가 매우 많습니다: {total_elements}")
            
            # 깊이 계산
            max_depth = self._calculate_xml_depth(root)
            if max_depth > 20:
                result["warnings"].append(f"XML 구조 깊이가 깊습니다: {max_depth}")
            
            # 대용량 텍스트 노드 검사
            for elem in root.iter():
                if elem.text and len(elem.text) > 100000:  # 100KB 초과
                    result["warnings"].append(f"대용량 텍스트 노드 발견: {elem.tag}")
            
        except Exception as e:
            result["warnings"].append(f"성능 검증 중 오류: {str(e)}")
        
        return result
    
    async def _validate_security(self, root: ET.Element) -> Dict[str, Any]:
        """보안 검증"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        try:
            # 비밀번호 패턴 검사
            password_pattern = re.compile(r'(password|pwd|pass)\s*[:=]\s*["\']?([^"\'\s]+)', re.IGNORECASE)
            
            for elem in root.iter():
                if elem.text:
                    matches = password_pattern.findall(elem.text)
                    if matches:
                        result["warnings"].append(f"평문 비밀번호 가능성 발견: {elem.tag}")
                
                # 속성에서도 검사
                for attr_name, attr_value in elem.attrib.items():
                    if 'password' in attr_name.lower() and len(attr_value) > 5:
                        result["warnings"].append(f"속성에 비밀번호 가능성: {attr_name}")
            
            # API 키 패턴 검사
            api_key_pattern = re.compile(r'[A-Za-z0-9]{32,}')
            
            for elem in root.iter():
                if elem.text and api_key_pattern.search(elem.text):
                    if any(keyword in elem.tag.lower() for keyword in ['key', 'token', 'secret']):
                        result["warnings"].append(f"API 키 가능성 발견: {elem.tag}")
            
        except Exception as e:
            result["warnings"].append(f"보안 검증 중 오류: {str(e)}")
        
        return result
    
    def _calculate_xml_depth(self, element: ET.Element, current_depth: int = 0) -> int:
        """XML 구조 깊이 계산"""
        if not list(element):
            return current_depth
        
        max_child_depth = 0
        for child in element:
            child_depth = self._calculate_xml_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    async def generate_validation_report(self, validation_result: Dict[str, Any]) -> str:
        """검증 보고서 생성"""
        report_lines = []
        
        report_lines.append("="*80)
        report_lines.append("HDGRACE BAS XML 검증 보고서")
        report_lines.append("="*80)
        report_lines.append(f"파일: {validation_result['file_path']}")
        report_lines.append(f"검증 시간: {validation_result['validation_time']}")
        report_lines.append(f"검증 결과: {'✅ 통과' if validation_result['is_valid'] else '❌ 실패'}")
        report_lines.append("")
        
        # 요약
        summary = validation_result.get('summary', {})
        report_lines.append("📊 검증 요약:")
        for check_name, check_result in summary.items():
            status = "✅" if check_result.get('valid', True) else "❌"
            report_lines.append(f"  {status} {check_name}")
        report_lines.append("")
        
        # 오류
        errors = validation_result.get('errors', [])
        if errors:
            report_lines.append("❌ 오류:")
            for error in errors:
                report_lines.append(f"  • {error}")
            report_lines.append("")
        
        # 경고
        warnings = validation_result.get('warnings', [])
        if warnings:
            report_lines.append("⚠️ 경고:")
            for warning in warnings:
                report_lines.append(f"  • {warning}")
            report_lines.append("")
        
        report_lines.append("="*80)
        
        return "\n".join(report_lines)