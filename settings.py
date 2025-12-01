import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///db.sqlite3")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DISK_TOKEN = os.getenv("DISK_TOKEN")
    YADISK_API_BASE = "https://cloud-api.yandex.net/v1/disk/resources"
