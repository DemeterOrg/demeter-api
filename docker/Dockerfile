# ============================================
# DEMETER API - Dockerfile (com uv)
# ============================================

FROM python:3.13-slim

# ========================
# Variáveis de ambiente
# ========================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

# ========================
# Instalar dependências do sistema
# ========================
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq5 libpq-dev build-essential wget curl \
    && rm -rf /var/lib/apt/lists/*

# ========================
# Criar diretório de trabalho
# ========================
WORKDIR /app
RUN mkdir -p /app/uploads /app/logs

# ========================
# Copiar pyproject e lockfile
# ========================
COPY pyproject.toml uv.lock ./

# ========================
# Criar virtualenv, instalar uv e dependências
# ========================
RUN python -m venv /app/.venv && \
    /app/.venv/bin/pip install --upgrade pip && \
    /app/.venv/bin/pip install uv && \
    /app/.venv/bin/uv sync --no-dev --frozen

# ========================
# Copiar código da aplicação
# ========================
COPY src /app/src
COPY alembic /app/alembic
COPY alembic.ini /app/

# ========================
# Copiar scripts
# ========================
COPY docker/scripts/entrypoint.sh /app/
COPY docker/scripts/healthcheck.sh /app/
RUN chmod +x /app/entrypoint.sh /app/healthcheck.sh

# ========================
# Healthcheck
# ========================
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD ["/app/healthcheck.sh"]

# ========================
# Entrypoint e CMD
# ========================
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
