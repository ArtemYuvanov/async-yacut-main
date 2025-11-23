import asyncio

import aiohttp

from settings import Config
from yacut.constants import YADISK_HEADERS_TEMPLATE


HTTP_OK = 200
HTTP_CREATED = 201

ERROR_UPLOAD = "Ошибка загрузки {file}: {status}"
ERROR_GET_HREF = "Не удалось получить публичную ссылку для {file}"
ERROR_GET_UPLOAD_LINK = "Ошибка получения ссылки для загрузки: {status} {data}"

YADISK_UPLOAD_URL = f"{Config.YADISK_API_BASE}/upload"
YADISK_DOWNLOAD_URL = f"{Config.YADISK_API_BASE}/download"


async def upload_file_to_yadisk(session, token, file_obj):
    """Загрузка одного файла на Яндекс.Диск и получение публичной ссылки."""

    headers = {
        k: v.format(token=token)
        for k, v in YADISK_HEADERS_TEMPLATE.items()
    }

    remote_path = f"app:/{file_obj.filename}"

    async with session.get(
        YADISK_UPLOAD_URL,
        headers=headers,
        params={"path": remote_path, "overwrite": "true"},
    ) as resp:
        data = await resp.json()
        if resp.status != HTTP_OK or "href" not in data:
            raise RuntimeError(
                ERROR_GET_UPLOAD_LINK.format(status=resp.status, data=data)
            )
        upload_href = data["href"]

    file_obj.stream.seek(0)
    content = file_obj.read()

    async with session.put(upload_href, data=content) as resp:
        if resp.status not in (HTTP_OK, HTTP_CREATED):
            raise RuntimeError(
                ERROR_UPLOAD.format(
                    file=file_obj.filename, status=resp.status
                )
            )

    async with session.get(
        YADISK_DOWNLOAD_URL,
        headers=headers,
        params={"path": remote_path},
    ) as info_resp:
        info = await info_resp.json()
        public_url = info.get("href")
        if not public_url:
            raise RuntimeError(ERROR_GET_HREF.format(file=file_obj.filename))

    return public_url


async def upload_files(token, files):
    """Загрузка списка файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        tasks = [upload_file_to_yadisk(session, token, f) for f in files]
        return await asyncio.gather(*tasks, return_exceptions=True)
