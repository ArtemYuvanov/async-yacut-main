from http import HTTPStatus

from flask import jsonify, request

from yacut import app
from yacut.models import URLMap
from yacut.error_handlers import InvalidAPIUsage

ERR_NO_BODY = "Отсутствует тело запроса"
ERR_URL_REQUIRED = '"url" является обязательным полем!'
ERR_NOT_FOUND = "Указанный id не найден"
ERR_SHORT_INVALID = "Указано недопустимое имя для короткой ссылки"


@app.route("/api/id/", methods=["POST"])
def api_create_id():
    """Создаёт короткую ссылку через API."""
    data = request.get_json(silent=True)
    if not data:
        raise InvalidAPIUsage(ERR_NO_BODY)

    if "url" not in data or not data.get("url"):
        raise InvalidAPIUsage(ERR_URL_REQUIRED)

    try:
        return jsonify({
            "url": data["url"],
            "short_link": URLMap.create(
                original=data["url"],
                short=data.get("custom_id")
            ).short_url()
        }), HTTPStatus.CREATED

    except (ValueError, RuntimeError) as exc:
        raise InvalidAPIUsage(str(exc))


@app.route("/api/id/<string:short>/", methods=["GET"])
def api_get_url(short):
    """Возвращает исходный URL по короткому идентификатору."""
    mapping = URLMap.get(short)
    if mapping is None:
        raise InvalidAPIUsage(ERR_NOT_FOUND, status_code=HTTPStatus.NOT_FOUND)

    return jsonify({"url": mapping.original}), HTTPStatus.OK
