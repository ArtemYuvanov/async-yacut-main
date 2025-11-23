import random
import re
from datetime import datetime, timezone

from flask import url_for
from sqlalchemy.exc import SQLAlchemyError

from yacut import db
from yacut.constants import (
    ALLOWED_RE,
    MAX_GENERATION_ATTEMPTS,
    ORIGINAL_MAX_LEN,
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
    def _is_reserved(short: str) -> bool:
        """Проверка, попадает ли идентификатор в список зарезервированных."""
        return short in RESERVED_SHORTS

    @staticmethod
    def generate_unique_short_id() -> str:
        """Попытки сгенерировать уникальный short id."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            candidate = "".join(
                random.choices(SHORT_ALPHABET, k=SHORT_LENGTH)
            )
            if URLMap.query.filter_by(short=candidate).first() is None:
                if not URLMap._is_reserved(candidate):
                    return candidate
        raise RuntimeError(ERR_GENERATION_FAILED)

    @staticmethod
    def create(original: str, short: str = None) -> "URLMap":
        """Создаёт и сохраняет в БД запись с оригинальным URL и short id."""
        if short:
            candidate = short
            if len(candidate) > SHORT_MAX_LEN:
                raise ValueError(ERR_SHORT_INVALID)
            if URLMap._is_reserved(candidate):
                raise ValueError(ERR_SHORT_EXISTS)
            if re.match(ALLOWED_RE, candidate) is None:
                raise ValueError(ERR_SHORT_INVALID)
            if URLMap.query.filter_by(short=candidate).first():
                raise ValueError(ERR_SHORT_EXISTS)
            short_id = candidate
        else:
            short_id = URLMap.generate_unique_short_id()

        mapping = URLMap(original=original, short=short_id)
        try:
            db.session.add(mapping)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            raise RuntimeError("Ошибка записи в базу данных")
        return mapping

    def short_url(self) -> str:
        """Возвращает внешний URL короткой ссылки для этого объекта."""
        return url_for("redirect_short", short=self.short, _external=True)

    @staticmethod
    def get_by_short(short):
        """Получить объект по короткой ссылке."""
        return URLMap.query.filter_by(short=short).first_or_404()
