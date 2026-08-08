# 后端镜像：FastAPI 数据分析服务
# 构建上下文：仓库根目录
#   minikube image build -t gdat/backend:1.0.0 -f deploy/docker/backend.Dockerfile .
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# psycopg2 需要编译环境（如不使用 PostgreSQL 可移除）
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# 先复制依赖清单，利用层缓存
COPY deploy/docker/requirements.docker.txt ./requirements.docker.txt
RUN pip install --prefix=/install --upgrade pip \
    && pip install --prefix=/install -r requirements.docker.txt

# ---------- 运行镜像 ----------
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# 运行时仅需 libpq（对应 psycopg2）与 curl（健康检查）
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 app

COPY --from=builder /install /usr/local

WORKDIR /app

# 源码与内置示例数据
COPY backend ./backend
COPY run_api.py ./
COPY Data ./Data

# 运行时可写目录（k8s 中建议挂载 emptyDir/PVC）
RUN mkdir -p TempStorage Logs ModelOutput/自动保存 ModelOutput/用户提取 ReportOutput APIOutput \
    && chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/health || exit 1

# 单 worker：会话状态与步骤锁为进程内内存态，不可多副本水平扩展（见 k8s 清单注释）
CMD ["uvicorn", "backend.Interfaces.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
