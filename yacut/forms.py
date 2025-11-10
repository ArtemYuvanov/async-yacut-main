import re

from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import (
    URL,
    DataRequired,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

ALLOWED_RE = r"^[A-Za-z0-9]+$"
MAX_CUSTOM_LEN = 16
RESERVED_IDS = {"files"}


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = URLField(
        "Длинная ссылка",
        validators=[
            DataRequired(message="Длинная ссылка обязательна"),
            URL(message="Некорректный URL"),
        ],
    )
    custom_id = StringField(
        "Ваш вариант короткой ссылки",
        validators=[
            Optional(),
            Length(
                max=MAX_CUSTOM_LEN,
                message=f"Максимум {MAX_CUSTOM_LEN} символов",
            ),
            Regexp(
                ALLOWED_RE,
                message="Указано недопустимое имя для короткой ссылки",
            ),
        ],
    )
    submit = SubmitField("Создать")

    def validate_custom_id(self, field):
        """Проверяет корректность и занятость custom_id."""
        if not field.data:
            return
        candidate = field.data.strip()
        if candidate.lower() in RESERVED_IDS:
            raise ValidationError(
                "Предложенный вариант короткой ссылки уже существует."
            )
        if len(candidate) > MAX_CUSTOM_LEN or not re.match(
            ALLOWED_RE, candidate
        ):
            raise ValidationError(
                "Указано недопустимое имя для короткой ссылки"
            )
        from yacut.models import URLMap

        if URLMap.query.filter_by(short=candidate).first():
            raise ValidationError(
                "Предложенный вариант короткой ссылки уже существует."
            )


class FilesForm(FlaskForm):
    """Форма для загрузки нескольких файлов."""

    files = MultipleFileField(
        "Файлы",
        validators=[DataRequired(message="Выберите хотя бы один файл")],
    )
