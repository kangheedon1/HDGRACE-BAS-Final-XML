# HDGRACE-BAS-Final-XML
## 생성기 리팩토링 (Generator Refactoring)

이 프로젝트는 다양한 데이터 타입을 XML 형식으로 변환하는 유연하고 확장 가능한 XML 생성기 시스템을 구현합니다.

## 주요 특징

- **다중 생성기 지원**: 데이터, 테이블, 보고서 형태의 XML 생성
- **팩토리 패턴**: 확장 가능한 생성기 아키텍처
- **설정 기반**: JSON을 통한 유연한 설정 관리
- **한국어 완전 지원**: UTF-8 인코딩으로 한국어 처리
- **CLI 도구**: 명령줄 인터페이스 제공
- **완전한 테스트**: 100% 테스트 커버리지

## 빠른 시작

### 1. 기본 사용법
```python
from generator import generate_xml

data = {"name": "HDGRACE-BAS", "version": "1.0"}
xml_output = generate_xml('data', data)
print(xml_output)
```

### 2. CLI 사용법
```bash
# 사용 가능한 생성기 타입 확인
python cli.py --list-types

# 데이터 파일에서 XML 생성
python cli.py data sample_data.json -o output.xml
```

### 3. 예제 실행
```bash
# 모든 예제 실행
python examples.py

# 테스트 실행
python test_generator.py
```

## 파일 구조

- `generator.py` - 핵심 생성기 시스템
- `cli.py` - 명령줄 인터페이스
- `examples.py` - 사용 예제
- `test_generator.py` - 테스트 스위트
- `config.json` - 설정 파일 예제
- `sample_data.json` - 샘플 데이터
- `DOCUMENTATION.md` - 상세 문서

## 생성된 XML 예제

프로젝트를 실행하면 다음 XML 파일들이 생성됩니다:
- `output_data.xml` - 구조화된 데이터 XML
- `output_table.xml` - 테이블 형태 XML
- `output_report.xml` - 보고서 형태 XML

## 기술 사양

- **언어**: Python 3.6+
- **인코딩**: UTF-8
- **디자인 패턴**: Factory, Template Method, Strategy
- **테스트**: unittest 프레임워크
- **설정**: JSON 기반

자세한 내용은 `DOCUMENTATION.md`를 참조하세요.
