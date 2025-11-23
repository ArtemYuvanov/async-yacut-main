from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    Regexp,
    URL
)

from yacut.constants import ALLOWED_RE, SHORT_MAX_LEN
from yacut.models import URLMap

LABEL_ORIGINAL_LINK = "Длинная ссылка"
LABEL_CUSTOM_ID = "Ваш вариант короткой ссылки"
LABEL_FILES = "Файлы"
ERR_URL_REQUIRED = "Длинная ссылка обязательна"
ERR_URL_INVALID = "Некорректный URL"
ERR_CUSTOM_INVALID = "Указано недопустимое имя для короткой ссылки"
ERR_CUSTOM_EXISTS = "Предложенный вариант короткой ссылки уже существует"
ERR_FILES_REQUIRED = "Выберите хотя бы один файл"
ERR_ORIGINAL_TOO_LONG = f"Максимум {URLMap.original.type.length} символов"
ERR_CUSTOM_TOO_LONG = f"Максимум {SHORT_MAX_LEN} символов"
SUBMIT_CREATE_LABEL = "Создать"


class URLForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = URLField(
        LABEL_ORIGINAL_LINK,
        validators=[
            DataRequired(message=ERR_URL_REQUIRED),
            URL(message=ERR_URL_INVALID),
            Length(
                max=URLMap.original.type.length,
                message=ERR_ORIGINAL_TOO_LONG
            ),
        ],
    )

    custom_id = StringField(
        LABEL_CUSTOM_ID,
        validators=[
            Optional(),
            Length(max=SHORT_MAX_LEN, message=ERR_CUSTOM_TOO_LONG),
            Regexp(ALLOWED_RE, message=ERR_CUSTOM_INVALID),
        ],
    )

    submit = SubmitField(SUBMIT_CREATE_LABEL)


class FilesForm(FlaskForm):
    """Форма для загрузки нескольких файлов."""

    files = MultipleFileField(
        LABEL_FILES,
        validators=[DataRequired(message=ERR_FILES_REQUIRED)],
    )
