"""Mock de classificação de grãos para demonstração."""

import random
from decimal import Decimal


class MockClassifierService:
    """Simula classificação de grãos sem IA."""

    GRAIN_TYPES = [
        "Soja",
        "Milho",
        "Feijão Preto",
        "Feijão Carioca",
        "Trigo",
        "Arroz",
        "Café",
        "Sorgo",
    ]

    def classify(self, image_path: str) -> dict:
        """Retorna classificação mockada."""
        grain_type = random.choice(self.GRAIN_TYPES)
        confidence = round(random.uniform(0.70, 0.95), 4)

        return {
            "grain_type": grain_type,
            "confidence_score": Decimal(str(confidence)),
            "extra_data": {
                "mock": True,
                "analysis": {
                    "grain_count": random.randint(50, 300),
                    "average_size": random.choice(["pequeno", "médio", "grande"]),
                    "quality": random.choice(["excelente", "boa", "regular"]),
                    "moisture": f"{random.uniform(10.0, 15.0):.1f}%",
                    "defects": f"{random.uniform(0.5, 8.0):.1f}%",
                }
            }
        }
