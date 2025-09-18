# Dockerfile for HDGRACE BAS Final XML Generator
FROM python:3.11-slim

LABEL maintainer="HDGRACE Team"
LABEL description="HDGRACE BAS Final XML Generator - 프로덕션 배포용 완성 코드"

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 디렉토리 생성
RUN mkdir -p logs output configs database static

# 실행 권한 설정
RUN chmod +x main.py

# 포트 노출
EXPOSE 8000

# 환경 변수
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# 애플리케이션 실행
CMD ["python", "main.py"]