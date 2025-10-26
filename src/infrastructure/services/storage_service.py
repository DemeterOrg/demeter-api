"""Serviço de armazenamento de arquivos."""

import os
import secrets
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile, HTTPException, status

from src.config.logging.logger import get_logger

logger = get_logger(__name__)


class StorageService:
    """Gerencia upload e armazenamento de imagens."""

    UPLOAD_DIR = Path("uploads/classifications")
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def save_image(self, user_id: int, file: UploadFile) -> str:
        """Salva imagem e retorna caminho relativo."""
        self._validate_file(file)

        user_dir = self.UPLOAD_DIR / f"user_{user_id}"
        user_dir.mkdir(exist_ok=True)

        extension = Path(file.filename).suffix.lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = secrets.token_hex(8)
        filename = f"{timestamp}_{random_hash}{extension}"

        file_path = user_dir / filename

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        relative_path = str(file_path.relative_to("uploads"))
        logger.info("Image saved", user_id=user_id, path=relative_path)

        return f"/uploads/{relative_path}"

    def delete_image(self, image_path: str) -> bool:
        """Remove imagem do disco."""
        try:
            full_path = Path(image_path.lstrip("/"))
            if full_path.exists():
                full_path.unlink()
                logger.info("Image deleted", path=image_path)
                return True
            return False
        except Exception as e:
            logger.error("Failed to delete image", path=image_path, error=str(e))
            return False

    def _validate_file(self, file: UploadFile) -> None:
        """Valida extensão e tamanho do arquivo."""
        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato não permitido. Use: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        if file.size and file.size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Arquivo muito grande. Máximo: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
