# HDGRACE-BAS XML Generator Documentation
# 생성기 리팩토링 (Generator Refactoring)

## Overview

HDGRACE-BAS XML Generator는 다양한 데이터 타입을 XML 형식으로 변환하는 유연하고 확장 가능한 시스템입니다. 이 시스템은 객체지향 설계 원칙과 디자인 패턴을 적용하여 깔끔하고 유지보수가 용이한 코드로 구현되었습니다.

## Features

- **다중 생성기 지원**: 데이터, 테이블, 보고서 형태의 XML 생성
- **설정 기반**: JSON 파일을 통한 유연한 설정 관리
- **네임스페이스 지원**: XML 네임스페이스 완전 지원
- **팩토리 패턴**: 새로운 생성기 타입 쉽게 추가 가능
- **에러 핸들링**: 강력한 검증 및 에러 처리
- **한국어 지원**: 완전한 UTF-8 지원으로 한국어 처리 가능

## Architecture

### Class Hierarchy

```
XMLGenerator (Abstract Base Class)
├── DataGenerator      (구조화된 데이터용)
├── TableGenerator     (테이블 형태 데이터용)
└── ReportGenerator    (보고서 형태 데이터용)

GeneratorFactory       (팩토리 패턴 구현)
GeneratorConfig        (설정 관리)
```

### Design Patterns Used

1. **Abstract Factory Pattern**: `GeneratorFactory`를 통한 생성기 인스턴스 생성
2. **Template Method Pattern**: `XMLGenerator` 기본 클래스의 공통 메서드
3. **Strategy Pattern**: 다양한 생성기 타입별 구현
4. **Configuration Pattern**: `GeneratorConfig`를 통한 설정 분리

## Installation & Setup

```bash
# 필요한 경우 Python 3.6+ 설치
python --version

# 레포지토리 클론
git clone <repository-url>
cd HDGRACE-BAS-Final-XML

# 테스트 실행 (선택사항)
python test_generator.py

# 예제 실행
python examples.py
```

## Usage

### 1. 기본 사용법

```python
from generator import generate_xml

# 간단한 데이터 생성
data = {"name": "HDGRACE-BAS", "version": "1.0"}
xml_output = generate_xml('data', data)
print(xml_output)
```

### 2. 설정 파일 사용

```python
from generator import GeneratorConfig, GeneratorFactory

# 설정 파일에서 로드
config = GeneratorConfig.from_file('config.json')

# 생성기 생성 및 사용
generator = GeneratorFactory.create_generator('data', config)
generator.generate_content(your_data)
generator.save_to_file('output.xml')
```

### 3. 다양한 생성기 타입

#### Data Generator
구조화된 데이터를 XML로 변환:

```python
data = {
    "user": {
        "name": "홍길동",
        "age": 30,
        "preferences": ["음악", "독서", "여행"]
    }
}
xml_output = generate_xml('data', data)
```

#### Table Generator
테이블 형태 데이터를 XML로 변환:

```python
table_data = [
    {"id": 1, "name": "김철수", "department": "개발팀"},
    {"id": 2, "name": "이영희", "department": "디자인팀"}
]
xml_output = generate_xml('table', table_data)
```

#### Report Generator
보고서 형태 문서를 XML로 변환:

```python
report_data = {
    "title": "월간 보고서",
    "sections": [
        {
            "name": "summary",
            "title": "요약",
            "content": "시스템이 정상 운영되고 있습니다."
        }
    ]
}
xml_output = generate_xml('report', report_data)
```

## Configuration

### 설정 파일 형식 (config.json)

```json
{
  "root_element": "hdgrace_document",
  "namespace": "http://hdgrace.bas.system/xml/v1",
  "encoding": "UTF-8",
  "pretty_print": true,
  "custom_attributes": {
    "version": "1.0",
    "schema_version": "1.0"
  },
  "metadata": {
    "generated_by": "HDGRACE-BAS-XML-Generator",
    "system": "HDGRACE-BAS",
    "version": "1.0"
  }
}
```

### 설정 옵션

- `root_element`: 루트 XML 요소명
- `namespace`: XML 네임스페이스 (선택사항)
- `encoding`: 문자 인코딩 (기본값: UTF-8)
- `pretty_print`: 들여쓰기 여부 (기본값: true)
- `custom_attributes`: 루트 요소에 추가할 속성들
- `metadata`: 메타데이터 섹션에 포함할 정보

## Extension

### 새로운 생성기 타입 추가

```python
from generator import XMLGenerator, GeneratorFactory

class CustomGenerator(XMLGenerator):
    def generate_content(self, data):
        # 커스텀 XML 생성 로직 구현
        custom_elem = ET.SubElement(self.root, 'custom')
        # ... 구현

# 팩토리에 등록
GeneratorFactory.register_generator('custom', CustomGenerator)

# 사용
generator = GeneratorFactory.create_generator('custom', config)
```

## Testing

전체 테스트 스위트 실행:

```bash
python test_generator.py
```

개별 테스트 클래스 실행:

```bash
python -m unittest test_generator.TestDataGenerator
```

## Error Handling

시스템은 다음과 같은 에러 상황을 처리합니다:

- 잘못된 설정 파일
- 존재하지 않는 생성기 타입
- 잘못된 데이터 형식
- 파일 I/O 에러

```python
try:
    config = GeneratorConfig.from_file('invalid.json')
except ValueError as e:
    print(f"설정 로드 실패: {e}")

try:
    generator = GeneratorFactory.create_generator('invalid_type', config)
except ValueError as e:
    print(f"생성기 생성 실패: {e}")
```

## Performance Considerations

- 대용량 데이터의 경우 메모리 사용량 주의
- `pretty_print=False`로 설정하여 성능 향상 가능
- 반복적인 생성 작업 시 생성기 인스턴스 재사용 권장

## Examples

실제 사용 예제는 `examples.py` 파일을 참조하세요:

```bash
python examples.py
```

생성된 예제 파일들:
- `output_data.xml`: 구조화된 데이터 예제
- `output_table.xml`: 테이블 형태 데이터 예제  
- `output_report.xml`: 보고서 형태 문서 예제

## License

이 프로젝트는 HDGRACE-BAS 시스템의 일부로 개발되었습니다.

## Contributing

1. 새로운 기능 추가 시 테스트 코드 포함
2. 한국어 주석과 문서화 유지
3. 기존 API 호환성 보장
4. 코드 스타일 일관성 유지

## Support

문의사항이나 버그 리포트는 개발팀에 연락하세요.