"""Serviço de integração com API de ML para classificação de grãos."""

import httpx
from pathlib import Path
from decimal import Decimal

from src.config.settings import settings
from src.config.logging.logger import get_logger
from src.config.exceptions.custom_exceptions import (
    ExternalServiceError,
    ValidationError,
    RateLimitError
)

logger = get_logger(__name__)


class DemeterMLService:
    """Cliente para API de classificação de grãos via ML."""

    def __init__(self):
        self.api_url = settings.DEMETER_ML_API_URL
        self.timeout = settings.DEMETER_ML_TIMEOUT
        self.enable_fallback = settings.ENABLE_ML_FALLBACK_TO_MOCK

    async def classify(self, image_path: str) -> dict:
        """Classifica imagem de grãos usando API de IA."""
        try:
            image_data = await self._read_image(image_path)
            api_response = await self._call_api(image_data)
            return self._map_response(api_response)

        except Exception as e:
            logger.error(
                "ML classification failed",
                image_path=image_path,
                error=str(e),
                exc_info=True
            )

            if self.enable_fallback:
                return await self._fallback_to_mock(image_path, error=str(e))

            raise

    async def _read_image(self, image_path: str) -> bytes:
        """Lê imagem do disco."""
        try:
            full_path = Path(image_path.lstrip("/"))
            with open(full_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            raise ValidationError(f"Imagem não encontrada: {image_path}")

    async def _call_api(self, image_data: bytes) -> dict:
        """Chama API de ML."""
        headers = {"Content-Type": "image/jpeg"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.api_url,
                    content=image_data,
                    headers=headers
                )

                if response.status_code == 400:
                    raise ValidationError("Imagem inválida ou formato não suportado")

                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    raise RateLimitError(
                        f"Limite de requisições excedido. Tente em {retry_after}s"
                    )

                elif response.status_code >= 500:
                    raise ExternalServiceError(
                        f"Erro no serviço de IA (status {response.status_code})"
                    )

                response.raise_for_status()
                return response.json()

        except httpx.ConnectError:
            raise ExternalServiceError("Serviço de IA temporariamente indisponível")

        except httpx.TimeoutException:
            raise ExternalServiceError(
                "Classificação demorou muito. Tente uma imagem menor."
            )

    def _map_response(self, api_response: dict) -> dict:
        """Mapeia resposta da API para formato interno."""
        try:
            report = api_response["report"]

            if "error" in report:
                raise ValidationError(
                    "Não foi possível detectar grãos na imagem. "
                    "Tire uma foto mais próxima dos grãos."
                )

            total_grains = report["total_grains"]
            defects = report["defects"]
            broken = defects.get("broken", 0)
            fermented = defects.get("fermented", 0)
            total_defects = broken + fermented

            defect_percentage = (total_defects / total_grains * 100) if total_grains > 0 else 0
            confidence = max(0.0, 1.0 - (defect_percentage / 100))

            return {
                "grain_type": "Soja",
                "confidence_score": Decimal(str(round(confidence, 4))),
                "extra_data": {
                    "mock": False,
                    "job_id": api_response["job_id"],
                    "total_grains": total_grains,
                    "defects": {
                        "broken": broken,
                        "fermented": fermented,
                        "total": total_defects,
                        "percentage": round(defect_percentage, 2)
                    },
                    "llm_summary": report["llm_summary"],
                    "processed_image_available": True,
                    "analysis": {
                        "grain_count": total_grains,
                        "quality": self._extract_quality(report["llm_summary"])
                    }
                }
            }

        except (KeyError, ValueError, ZeroDivisionError) as e:
            logger.error("Failed to map ML API response", error=str(e), response=api_response)
            raise ExternalServiceError("Resposta inválida do serviço de IA")

    def _extract_quality(self, llm_summary: str) -> str:
        """Extrai qualidade do summary da IA."""
        summary_lower = llm_summary.lower()

        if any(word in summary_lower for word in ["excelente", "excellent", "ótima"]):
            return "excelente"
        elif any(word in summary_lower for word in ["boa", "good", "satisfatória"]):
            return "boa"
        elif any(word in summary_lower for word in ["regular", "média", "moderate"]):
            return "regular"
        elif any(word in summary_lower for word in ["ruim", "poor", "baixa"]):
            return "ruim"
        else:
            return "não determinada"

    async def _fallback_to_mock(self, image_path: str, error: str) -> dict:
        """Fallback para mock em caso de erro."""
        from src.infrastructure.services.mock_classifier_service import MockClassifierService

        logger.warning("Using mock fallback", reason=error)

        mock = MockClassifierService()
        result = await mock.classify(image_path)
        result["extra_data"]["fallback"] = True
        result["extra_data"]["fallback_reason"] = error

        return result
