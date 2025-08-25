# Production Dockerfile for Ques Backend
FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Workdir
WORKDIR /app

# Faster apt + deb822-safe mirror replace (USTC), with retries + IPv4
RUN set -eux; \
  printf 'Acquire::Retries "5"; Acquire::ForceIPv4 "true";\n' > /etc/apt/apt.conf.d/99retries; \
  if [ -f /etc/apt/sources.list.d/debian.sources ]; then \
    sed -i -E 's#https?://deb.debian.org/debian#http://mirrors.ustc.edu.cn/debian#g' /etc/apt/sources.list.d/debian.sources; \
    sed -i -E 's#https?://security.debian.org/debian-security#http://mirrors.ustc.edu.cn/debian-security#g' /etc/apt/sources.list.d/debian.sources; \
  fi; \
  apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    gcc libpq-dev libmagic1 \
  ; rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
# pip 镜像 + 重试/超时
ENV PIP_DEFAULT_TIMEOUT=120
RUN python -m pip install --no-cache-dir --upgrade pip \
      -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 120 \
 && python -m pip install --no-cache-dir -r requirements.txt \
      -i https://pypi.tuna.tsinghua.edu.cn/simple --retries 5 --timeout 300

# App
COPY . .
RUN mkdir -p logs

# Non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)"

# Port
EXPOSE 8000

# Entrypoint
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "120"]
