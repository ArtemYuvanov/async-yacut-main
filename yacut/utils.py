import random
import string

from yacut.models import URLMap

ALPHABET = string.ascii_letters + string.digits


def get_unique_short_id(length=6):
    """
    Генерирует уникальный короткий идентификатор длиной length.
    Проверяет, что такого идентификатора ещё нет в базе.
    """
    while True:
        candidate = "".join(random.choices(ALPHABET, k=length))
        if not URLMap.query.filter_by(short=candidate).first():
            return candidate
