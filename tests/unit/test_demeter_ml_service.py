from decimal import Decimal
from unittest.mock import AsyncMock, patch, mock_open

import httpx
import pytest

from src.infrastructure.services.demeter_ml_service import DemeterMLService
from src.config.exceptions.custom_exceptions import (
    ExternalServiceError,
    ValidationError,
    RateLimitError
)


@pytest.fixture
def ml_service():
    return DemeterMLService()


@pytest.fixture
def mock_api_success_response():
    return {
        "job_id": "123e4567-e89b-12d3-a456-426614174000",
        "report": {
            "total_grains": 150,
            "defects": {
                "broken": 5,
                "fermented": 2
            },
            "llm_summary": "Análise de qualidade: amostra apresenta boa qualidade com baixo índice de defeitos."
        },
        "processed_image_base64": "iVBORw0KGgoAAAANS..."
    }


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_success(ml_service, mock_api_success_response):
    with patch("builtins.open", mock_open(read_data=b"fake_image_data")):
        with patch.object(ml_service, "_call_api", return_value=mock_api_success_response):
            result = await ml_service.classify("/uploads/test.jpg")

    assert result["grain_type"] == "Soja"
    assert isinstance(result["confidence_score"], Decimal)
    assert result["confidence_score"] == Decimal("0.9533")
    assert result["extra_data"]["mock"] is False
    assert result["extra_data"]["job_id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert result["extra_data"]["total_grains"] == 150
    assert result["extra_data"]["defects"]["broken"] == 5
    assert result["extra_data"]["defects"]["fermented"] == 2
    assert result["extra_data"]["defects"]["total"] == 7
    assert result["extra_data"]["defects"]["percentage"] == 4.67
    assert "llm_summary" in result["extra_data"]
    assert result["extra_data"]["processed_image_available"] is True
    assert result["extra_data"]["analysis"]["grain_count"] == 150
    assert result["extra_data"]["analysis"]["quality"] == "boa"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_calculates_confidence_correctly(ml_service):
    response_zero_defects = {
        "job_id": "test-id",
        "report": {
            "total_grains": 100,
            "defects": {"broken": 0, "fermented": 0},
            "llm_summary": "Excelente qualidade"
        },
        "processed_image_base64": "abc"
    }

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch.object(ml_service, "_call_api", return_value=response_zero_defects):
            result = await ml_service.classify("/test.jpg")

    assert result["confidence_score"] == Decimal("1.0000")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_high_defects_lowers_confidence(ml_service):
    response_high_defects = {
        "job_id": "test-id",
        "report": {
            "total_grains": 100,
            "defects": {"broken": 25, "fermented": 25},
            "llm_summary": "Qualidade ruim"
        },
        "processed_image_base64": "abc"
    }

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch.object(ml_service, "_call_api", return_value=response_high_defects):
            result = await ml_service.classify("/test.jpg")

    assert result["confidence_score"] == Decimal("0.5000")
    assert result["extra_data"]["defects"]["percentage"] == 50.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_no_grains_detected(ml_service):
    ml_service.enable_fallback = False

    response_no_grains = {
        "job_id": "test-id",
        "report": {
            "error": "Nenhum grão detectado",
            "llm_summary": "Não foi possível detectar grãos na imagem."
        },
        "processed_image_base64": "abc"
    }

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch.object(ml_service, "_call_api", return_value=response_no_grains):
            with pytest.raises(ValidationError, match="Não foi possível detectar grãos"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_image_not_found(ml_service):
    ml_service.enable_fallback = False

    with pytest.raises(ValidationError, match="Imagem não encontrada"):
        await ml_service.classify("/uploads/nonexistent.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_api_timeout(ml_service):
    ml_service.enable_fallback = False

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch("httpx.AsyncClient.post", side_effect=httpx.TimeoutException("timeout")):
            with pytest.raises(ExternalServiceError, match="Classificação demorou muito"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_api_connection_error(ml_service):
    ml_service.enable_fallback = False

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("connection failed")):
            with pytest.raises(ExternalServiceError, match="temporariamente indisponível"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_api_400_bad_request(ml_service):
    ml_service.enable_fallback = False

    mock_response = AsyncMock()
    mock_response.status_code = 400

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(ValidationError, match="Imagem inválida"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_api_429_rate_limit(ml_service):
    ml_service.enable_fallback = False

    mock_response = AsyncMock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(RateLimitError, match="Limite de requisições excedido"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_api_500_internal_error(ml_service):
    ml_service.enable_fallback = False

    mock_response = AsyncMock()
    mock_response.status_code = 500

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch("httpx.AsyncClient.post", return_value=mock_response):
            with pytest.raises(ExternalServiceError, match="Erro no serviço de IA"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_malformed_response_missing_fields(ml_service):
    ml_service.enable_fallback = False

    malformed_response = {
        "job_id": "test-id",
        "report": {}
    }

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch.object(ml_service, "_call_api", return_value=malformed_response):
            with pytest.raises(ExternalServiceError, match="Resposta inválida"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_fallback_enabled(ml_service, mock_api_success_response):
    ml_service.enable_fallback = True

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch.object(ml_service, "_call_api", side_effect=ExternalServiceError("API down")):
            result = await ml_service.classify("/test.jpg")

    assert result["extra_data"]["fallback"] is True
    assert "API down" in result["extra_data"]["fallback_reason"]
    assert result["extra_data"]["mock"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_classify_fallback_disabled(ml_service):
    ml_service.enable_fallback = False

    with patch("builtins.open", mock_open(read_data=b"fake")):
        with patch.object(ml_service, "_call_api", side_effect=ExternalServiceError("API down")):
            with pytest.raises(ExternalServiceError, match="API down"):
                await ml_service.classify("/test.jpg")


@pytest.mark.unit
def test_extract_quality_excelente(ml_service):
    summary = "A amostra apresenta excelente qualidade com grãos uniformes."
    quality = ml_service._extract_quality(summary)
    assert quality == "excelente"


@pytest.mark.unit
def test_extract_quality_boa(ml_service):
    summary = "Análise indica boa qualidade dos grãos."
    quality = ml_service._extract_quality(summary)
    assert quality == "boa"


@pytest.mark.unit
def test_extract_quality_regular(ml_service):
    summary = "A qualidade está regular, com alguns defeitos visíveis."
    quality = ml_service._extract_quality(summary)
    assert quality == "regular"


@pytest.mark.unit
def test_extract_quality_ruim(ml_service):
    summary = "Qualidade ruim devido ao alto índice de defeitos."
    quality = ml_service._extract_quality(summary)
    assert quality == "ruim"


@pytest.mark.unit
def test_extract_quality_not_determined(ml_service):
    summary = "Análise técnica dos grãos sem indicação clara de qualidade."
    quality = ml_service._extract_quality(summary)
    assert quality == "não determinada"
