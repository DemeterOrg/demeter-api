"""
Testes para o endpoint de health check.

Verifica se a API está respondendo corretamente e se
os checks de saúde (database, disk, uploads) estão funcionando.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.smoke
@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client: AsyncClient):
    """
    Teste: Endpoint /health deve retornar status 200.

    Este é um smoke test básico que verifica se a API está
    respondendo corretamente.
    """
    response = await client.get("/health")

    assert response.status_code == 200, "Health endpoint deve retornar 200 OK"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_endpoint_structure(client: AsyncClient):
    """
    Teste: Endpoint /health deve retornar estrutura correta.

    Verifica se a resposta contém todos os campos esperados:
    - status
    - version
    - environment
    - checks
    """
    response = await client.get("/health")
    data = response.json()

    # Verificar campos principais
    assert "status" in data, "Resposta deve conter 'status'"
    assert "version" in data, "Resposta deve conter 'version'"
    assert "environment" in data, "Resposta deve conter 'environment'"
    assert "checks" in data, "Resposta deve conter 'checks'"

    # Verificar tipo dos campos
    assert isinstance(data["status"], str), "status deve ser string"
    assert isinstance(data["version"], str), "version deve ser string"
    assert isinstance(data["environment"], str), "environment deve ser string"
    assert isinstance(data["checks"], dict), "checks deve ser dict"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_endpoint_status_values(client: AsyncClient):
    """
    Teste: Status deve ser um dos valores válidos.

    Valores válidos: ok, degraded, unhealthy
    """
    response = await client.get("/health")
    data = response.json()

    valid_statuses = ["ok", "degraded", "unhealthy"]
    assert (
        data["status"] in valid_statuses
    ), f"Status deve ser um de {valid_statuses}, recebido: {data['status']}"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_database_check(client: AsyncClient):
    """
    Teste: Verifica se o check de database está presente e saudável.

    Como os testes rodam contra um DB de teste real,
    esperamos que o status seja 'healthy'.
    """
    response = await client.get("/health")
    data = response.json()

    # Verificar se database check existe
    assert "database" in data["checks"], "Checks deve conter 'database'"

    db_check = data["checks"]["database"]

    # Verificar estrutura do database check
    assert "status" in db_check, "Database check deve conter 'status'"

    # Em ambiente de teste, DB deve estar saudável
    assert (
        db_check["status"] == "healthy"
    ), f"Database deve estar healthy em testes, status: {db_check['status']}"

    # Se healthy, deve ter latency
    if db_check["status"] == "healthy":
        assert "latency_ms" in db_check, "Database check deve conter 'latency_ms'"
        assert isinstance(
            db_check["latency_ms"], (int, float)
        ), "latency_ms deve ser número"
        assert db_check["latency_ms"] >= 0, "latency_ms deve ser positivo"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_disk_check(client: AsyncClient):
    """
    Teste: Verifica se o check de disco está presente.

    Valida que o sistema está monitorando espaço em disco.
    """
    response = await client.get("/health")
    data = response.json()

    # Verificar se disk check existe
    assert "disk" in data["checks"], "Checks deve conter 'disk'"

    disk_check = data["checks"]["disk"]

    # Verificar estrutura do disk check
    assert "status" in disk_check, "Disk check deve conter 'status'"

    # Se não houver erro, deve ter informações de espaço
    if "error" not in disk_check:
        assert "free_gb" in disk_check, "Disk check deve conter 'free_gb'"
        assert "total_gb" in disk_check, "Disk check deve conter 'total_gb'"

        # Validar tipos
        assert isinstance(
            disk_check["free_gb"], (int, float)
        ), "free_gb deve ser número"
        assert isinstance(
            disk_check["total_gb"], (int, float)
        ), "total_gb deve ser número"

        # Validar valores lógicos
        assert disk_check["free_gb"] >= 0, "free_gb deve ser positivo"
        assert disk_check["total_gb"] > 0, "total_gb deve ser positivo"
        assert (
            disk_check["free_gb"] <= disk_check["total_gb"]
        ), "free_gb não pode ser maior que total_gb"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_uploads_check(client: AsyncClient):
    """
    Teste: Verifica se o check de uploads está presente.

    Valida que o diretório de uploads está acessível.
    """
    response = await client.get("/health")
    data = response.json()

    # Verificar se uploads check existe
    assert "uploads" in data["checks"], "Checks deve conter 'uploads'"

    uploads_check = data["checks"]["uploads"]

    # Verificar estrutura do uploads check
    assert "status" in uploads_check, "Uploads check deve conter 'status'"

    # Se não houver erro, deve ter path e writable
    if "error" not in uploads_check:
        assert "path" in uploads_check, "Uploads check deve conter 'path'"
        assert "writable" in uploads_check, "Uploads check deve conter 'writable'"

        # Validar tipos
        assert isinstance(uploads_check["path"], str), "path deve ser string"
        assert isinstance(
            uploads_check["writable"], bool
        ), "writable deve ser boolean"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_endpoint_performance(client: AsyncClient):
    """
    Teste: Endpoint /health deve responder rapidamente.

    Health check deve ser rápido (< 1 segundo) para não
    impactar healthcheck do Docker/Kubernetes.
    """
    import time

    start = time.time()
    response = await client.get("/health")
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 1.0, f"Health check muito lento: {elapsed:.2f}s (deve ser < 1s)"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_health_overall_status_logic(client: AsyncClient):
    """
    Teste: Status geral deve refletir estado dos checks.

    Se database está unhealthy, status geral deve ser unhealthy.
    """
    response = await client.get("/health")
    data = response.json()

    # Se database está unhealthy, status geral deve ser unhealthy
    if data["checks"]["database"]["status"] == "unhealthy":
        assert (
            data["status"] == "unhealthy"
        ), "Status geral deve ser unhealthy se database unhealthy"

    # Se database está healthy mas disk degraded, status pode ser degraded
    if (
        data["checks"]["database"]["status"] == "healthy"
        and data["checks"]["disk"]["status"] == "degraded"
    ):
        assert data["status"] in [
            "degraded",
            "ok",
        ], "Status deve refletir degradação de disk"
