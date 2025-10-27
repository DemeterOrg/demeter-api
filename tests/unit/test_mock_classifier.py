from decimal import Decimal

import pytest

from src.infrastructure.services.mock_classifier_service import MockClassifierService


@pytest.mark.unit
def test_classify_returns_valid_result():
    service = MockClassifierService()
    result = service.classify("fake_image_path.jpg")

    assert "grain_type" in result
    assert "confidence_score" in result
    assert "extra_data" in result

    assert result["grain_type"] in MockClassifierService.GRAIN_TYPES

    confidence = result["confidence_score"]
    assert isinstance(confidence, Decimal)
    assert Decimal("0.70") <= confidence <= Decimal("0.95")

    assert result["extra_data"]["mock"] is True
    assert "analysis" in result["extra_data"]

    analysis = result["extra_data"]["analysis"]
    assert "grain_count" in analysis
    assert "quality" in analysis
    assert "moisture" in analysis
    assert "defects" in analysis
