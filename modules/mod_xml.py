#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDGRACE XML 처리 모듈
XML 파싱, 생성, 검증 기능
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import logging

try:
    from lxml import etree as lxml_etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False

logger = logging.getLogger(__name__)

class XMLProcessor:
    """XML 처리 클래스"""
    
    def __init__(self):
        self.use_lxml = LXML_AVAILABLE
        logger.info(f"XML 프로세서 초기화 (LXML: {self.use_lxml})")
    
    def validate_xml_syntax(self, xml_string):
        """XML 문법 검증"""
        try:
            if self.use_lxml:
                lxml_etree.fromstring(xml_string.encode('utf-8'))
            else:
                ET.fromstring(xml_string)
            return True, "XML 문법 올바름"
        except Exception as e:
            return False, f"XML 문법 오류: {e}"
    
    def prettify_xml(self, xml_string):
        """XML 포맷팅"""
        try:
            if self.use_lxml:
                root = lxml_etree.fromstring(xml_string.encode('utf-8'))
                return lxml_etree.tostring(root, pretty_print=True, encoding='unicode')
            else:
                root = ET.fromstring(xml_string)
                rough_string = ET.tostring(root, encoding='unicode')
                reparsed = minidom.parseString(rough_string)
                return reparsed.toprettyxml(indent="  ")
        except Exception as e:
            logger.error(f"XML 포맷팅 실패: {e}")
            return xml_string
    
    def fix_common_errors(self, xml_string):
        """일반적인 XML 오류 수정"""
        # 누락된 따옴표 수정
        xml_string = re.sub(r'(\w+)=([^"\s>]+)(?=\s|>)', r'\1="\2"', xml_string)
        
        # 특수 문자 이스케이프
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&apos;'
        }
        
        # CDATA 섹션 외부에서만 치환
        cdata_pattern = r'<!\[CDATA\[(.*?)\]\]>'
        cdata_sections = re.findall(cdata_pattern, xml_string, re.DOTALL)
        
        # CDATA 섹션을 임시로 대체
        temp_xml = xml_string
        for i, cdata in enumerate(cdata_sections):
            temp_xml = temp_xml.replace(f'<![CDATA[{cdata}]]>', f'__CDATA_{i}__')
        
        # 특수 문자 치환
        for char, replacement in replacements.items():
            temp_xml = temp_xml.replace(char, replacement)
        
        # CDATA 섹션 복원
        for i, cdata in enumerate(cdata_sections):
            temp_xml = temp_xml.replace(f'__CDATA_{i}__', f'<![CDATA[{cdata}]]>')
        
        return temp_xml
