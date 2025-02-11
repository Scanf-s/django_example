# Python 3.12 slim 이미지를 기반으로 사용
FROM python:3.12-slim AS builder

# 이미지의 유지 관리자를 지정
LABEL maintainer="sullungim"

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    TZ=Asia/Seoul \
    POETRY_HOME=/opt/poetry \
    PATH="/opt/poetry/bin:$PATH" \
    POETRY_VIRTUALENVS_CREATE=false

# 필요한 패키지 설치 및 Poetry 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 파일 복사
COPY pyproject.toml poetry.lock ./

# 프로젝트 의존성 설치
RUN poetry install --no-root --no-interaction

# Deploy stage
FROM python:3.12-slim AS deploy

LABEL maintainer="sullungim"

# Health Check를 위한 CURL 설치
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 환경변수 설정
ENV PATH="/opt/poetry/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false
#ENV PYTHONUNBUFFERED=1
#ENV DJANGO_DEBUG_MODE=false

# 사용자 추가 및 권한 설정
RUN useradd --no-create-home --uid 1000 django-user

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 스테이지에서 필요한 파일 복사
COPY --from=builder --chown=django-user:django-user /opt/poetry /opt/poetry
COPY --from=builder --chown=django-user:django-user /app /app
COPY --from=builder --chown=django-user:django-user /usr/local/lib /usr/local/lib
COPY --from=builder --chown=django-user:django-user /usr/local/bin /usr/local/bin
RUN chown django-user:django-user /app

# 프로젝트 파일 복사
COPY --chown=django-user:django-user . .

# 로그 디렉토리 설정
RUN mkdir -p /app/logs && \
    chown -R django-user:django-user /app/logs

# 포트 노출
EXPOSE 8000

# 사용자 전환
USER django-user

# 테스트 전용 Django 프로젝트 실행
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]