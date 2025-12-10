import random
import re
from datetime import datetime, timezone

from flask import url_for

from yacut import db
from yacut.constants import (
    ALLOWED_RE,
    MAX_GENERATION_ATTEMPTS,
    ORIGINAL_MAX_LEN,
    REDIRECT_VIEW_NAME,
    RESERVED_SHORTS,
    SHORT_ALPHABET,
    SHORT_LENGTH,
    SHORT_MAX_LEN,
)

ERR_SHORT_EXISTS = "Предложенный вариант короткой ссылки уже существует."
ERR_SHORT_INVALID = "Указано недопустимое имя для короткой ссылки"
ERR_GENERATION_FAILED = (
    "Не удалось сгенерировать уникальный короткий идентификатор "
    f"после {MAX_GENERATION_ATTEMPTS} попыток"
)
ERR_ORIGINAL_TOO_LONG = (
    f"Максимальная длина оригинального URL — {ORIGINAL_MAX_LEN} символов."
)


class URLMap(db.Model):
    """Модель для хранения оригинальных и коротких URL."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_MAX_LEN), nullable=False)
    short = db.Column(db.String(SHORT_MAX_LEN), unique=True, nullable=False)
    timestamp = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    @staticmethod
    def get_or_404(short: str):
        """Получить объект по short, если нет — 404."""
        return URLMap.query.filter_by(short=short).first_or_404()

    @staticmethod
    def get(short: str):
        """Возвращает объект URLMap по short или None, если не найден."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def generate_short() -> str:
        """Сгенерировать уникальное значение short."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short = "".join(random.choices(SHORT_ALPHABET, k=SHORT_LENGTH))
            if short not in RESERVED_SHORTS and not URLMap.get(short):
                return short
        raise RuntimeError(ERR_GENERATION_FAILED)

    @staticmethod
    def create(
        original: str,
        short: str = None,
        *,
        validate: bool = False
    ) -> "URLMap":
        """Создаёт и сохраняет объект URLMap."""
        if not validate and len(original) > ORIGINAL_MAX_LEN:
            raise ValueError(ERR_ORIGINAL_TOO_LONG)
        if short:
            if not validate and len(short) > SHORT_MAX_LEN:
                raise ValueError(ERR_SHORT_INVALID)
            if short in RESERVED_SHORTS:
                raise ValueError(ERR_SHORT_EXISTS)
            if not validate and re.match(ALLOWED_RE, short) is None:
                raise ValueError(ERR_SHORT_INVALID)
            if URLMap.get(short):
                raise ValueError(ERR_SHORT_EXISTS)
        else:
            short = URLMap.generate_short()

        mapping = URLMap(original=original, short=short)
        db.session.add(mapping)
        db.session.commit()
        return mapping

    def short_url(self) -> str:
        return url_for(
            REDIRECT_VIEW_NAME,
            short=self.short,
            _external=True
        )
