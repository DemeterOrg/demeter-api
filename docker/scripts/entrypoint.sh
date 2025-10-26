#!/bin/bash
set -e

echo "🚀 Iniciando DEMETER API..."

echo "⏳ Aguardando banco de dados..."
DB_URL_ASYNCPG=$(echo "${DATABASE_URL}" | sed 's/postgresql+asyncpg/postgresql/')
for i in {1..30}; do
    if python -c "import asyncio, asyncpg; asyncio.run(asyncpg.connect('${DB_URL_ASYNCPG}'))"; then
        echo "✅ Banco pronto!"
        break
    fi
    echo "⏳ Banco ainda não está pronto, tentando novamente..."
    sleep 2
    if [ $i -eq 30 ]; then
        echo "❌ Banco não ficou pronto após 60 segundos."
        exit 1
    fi
done

echo "Aplicando migrations..."
alembic upgrade head

echo "Criando usuário admin (se necessário)..."
python -m src.cli.create_admin \
    --email "${ADMIN_EMAIL:-admin@demeter.local}" \
    --name "${ADMIN_NAME:-Admin}" \
    --password "${ADMIN_PASSWORD:-Admin123!}" \
    --phone "${ADMIN_PHONE:-11999999999}" || true

echo "Pronto! Iniciando aplicação..."
exec "$@"
