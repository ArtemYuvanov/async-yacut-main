import re

from flask import jsonify, request

from yacut import app, db
from yacut.models import URLMap
from yacut.utils import get_unique_short_id

ALLOWED_RE = r"^[A-Za-z0-9]+$"
MAX_CUSTOM_LEN = 16
RESERVED_IDS = {"files"}


def validate_custom_id(custom_id: str):
    """Проверяет корректность кастомного идентификатора."""
    if not custom_id:
        return
    candidate = custom_id.strip()
    if candidate.lower() in RESERVED_IDS:
        raise ValueError(
            "Предложенный вариант короткой ссылки уже существует."
        )
    if len(candidate) > MAX_CUSTOM_LEN or not re.match(ALLOWED_RE, candidate):
        raise ValueError("Указано недопустимое имя для короткой ссылки")
    if URLMap.query.filter_by(short=candidate).first():
        raise ValueError(
            "Предложенный вариант короткой ссылки уже существует."
        )


@app.route("/api/id/", methods=["POST"])
def api_create_id():
    """Создаёт короткую ссылку."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"message": "Отсутствует тело запроса"}), 400

    if "url" not in data or not data.get("url"):
        return jsonify({"message": '"url" является обязательным полем!'}), 400

    url = data["url"]
    custom_id = data.get("custom_id")
    if custom_id:
        try:
            validate_custom_id(custom_id)
        except ValueError as exc:
            return jsonify({"message": str(exc)}), 400
    else:
        custom_id = get_unique_short_id()
        while URLMap.query.filter_by(short=custom_id).first():
            custom_id = get_unique_short_id()
    try:
        new_map = URLMap(original=url, short=custom_id)
        db.session.add(new_map)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return (
            jsonify(
                {
                    "message": "Предложенный вариант короткой ссылки уже "
                    "существует."
                }
            ),
            400,
        )
    short_link = f"{request.host_url.rstrip('/')}/{custom_id}"
    return jsonify({"url": url, "short_link": short_link}), 201


@app.route("/api/id/<string:short_id>/", methods=["GET"])
def api_get_url(short_id):
    """Возвращает исходный URL по короткому идентификатору."""
    mapping = URLMap.query.filter_by(short=short_id).first()
    if not mapping:
        return jsonify({"message": "Указанный id не найден"}), 404

    return jsonify({"url": mapping.original}), 200
