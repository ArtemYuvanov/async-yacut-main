from flask import jsonify, render_template

from . import app, db


class InvalidAPIUsage(Exception):
    """Кастомное исключение для обработки ошибок в API."""

    status_code = 400

    def __init__(self, message, status_code=None):
        """Инициализирует объект ошибки с сообщением и статусом."""
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        """Возвращает ошибку в формате словаря для JSON-ответа."""
        return {"message": self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    """Обработчик кастомных ошибок API."""
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(404)
def page_not_found(error):
    """Обработчик ошибки 404 — страница не найдена."""
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500 — внутренняя ошибка сервера."""
    db.session.rollback()
    return render_template("500.html"), 500
