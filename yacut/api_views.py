from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.models import URLMap


ERR_NO_BODY = "Отсутствует тело запроса"
ERR_URL_REQUIRED = '"url" является обязательным полем!'
ERR_NOT_FOUND = "Указанный id не найден"

MESSAGE_KEY = "message"


@app.route("/api/id/", methods=["POST"])
def api_create_id():
    """Создаёт короткую ссылку через API."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({MESSAGE_KEY: ERR_NO_BODY}), HTTPStatus.BAD_REQUEST

    if "url" not in data or not data.get("url"):
        return jsonify({MESSAGE_KEY: ERR_URL_REQUIRED}), HTTPStatus.BAD_REQUEST

    try:
        mapping = URLMap.create(
            original=data["url"],
            short=data.get("custom_id")
        )
    except ValueError as exc:
        return jsonify({MESSAGE_KEY: str(exc)}), HTTPStatus.BAD_REQUEST

    return (
        jsonify({
            "url": data["url"],
            "short_link": mapping.short_url()
        }),
        HTTPStatus.CREATED,
    )


@app.route("/api/id/<string:short>/", methods=["GET"])
def api_get_url(short):
    """Возвращает исходный URL по короткому идентификатору."""
    mapping = URLMap.query.filter_by(short=short).first()

    if not mapping:
        return jsonify({MESSAGE_KEY: ERR_NOT_FOUND}), HTTPStatus.NOT_FOUND

    return jsonify({"url": mapping.original}), HTTPStatus.OK
